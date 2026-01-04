import json
import redis
from channels.generic.websocket import AsyncWebsocketConsumer
from jwt import ExpiredSignatureError
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

redis_client = redis.Redis()


class NoteConsumer(AsyncWebsocketConsumer):
    user = None
    note_id = None
    group_name = None

    async def connect(self):
        query_string = self.scope["query_string"].decode()
        token = None

        if query_string.startswith("token="):
            token = query_string.split("token=")[1]

        if not token or not await self.authenticate_user(token):
            await self.close()
            return

        self.note_id = self.scope["url_route"]["kwargs"]["note_id"]
        self.group_name = f"note_{self.note_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if self.note_id and self.user:
            redis_client.srem(f"typing:note:{self.note_id}", self.user.username)

        if self.group_name:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)

        if data.get("type") == "typing":
            redis_client.sadd(f"typing:note:{self.note_id}", self.user.username)
            redis_client.expire(f"typing:note:{self.note_id}", 5)

            users = list(redis_client.smembers(f"typing:note:{self.note_id}"))
            users = [u.decode() for u in users]
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "typing_indicator",
                    "users": users,
                },
            )

    async def typing_indicator(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "typing",
                    "users": event["users"],
                    "current_user": self.user.username,
                }
            )
        )
    
    async def note_update(self, event):
        """
        Handles note content updates sent via group_send
        """
        await self.send(
            text_data=json.dumps({
                "type": "note_update",
                "data": event.get("data", {})
            })
        )


    async def authenticate_user(self, token):
        try:
            from rest_framework_simplejwt.tokens import AccessToken

            access_token = AccessToken(token)
            user_id = access_token["user_id"]
            self.user = await self.get_user(user_id)
            return bool(self.user)

        except ExpiredSignatureError:
            print("JWT expired")
            return False
        except Exception as e:
            print("JWT error:", str(e))
            return False

    @database_sync_to_async
    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
