from rest_framework import serializers
from .models import Note, NoteVersion
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Note, NoteVersion
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password")

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )
        return user


class NoteSerializer(serializers.ModelSerializer):
    version = serializers.IntegerField(write_only=True, required=False)
    collaborators = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), required=False
    )

    class Meta:
        model = Note
        fields = (
            "id",
            "title",
            "content",
            "owner",
            "collaborators",
            "version",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("owner", "created_at", "updated_at")

    def create(self, validated_data):
        collaborators = validated_data.pop("collaborators", [])
        validated_data.pop("version", None)

        note = Note.objects.create(owner=self.context["request"].user, **validated_data)

        if collaborators:
            note.collaborators.set(collaborators)

        NoteVersion.objects.create(
            note=note,
            title=note.title,
            content=note.content,
            version_number=1,
        )

        return note

    def update(self, instance, validated_data):
        collaborators = validated_data.pop("collaborators", None)
        validated_data.pop("version", None)
        instance.title = validated_data.get("title", instance.title)
        instance.content = validated_data.get("content", instance.content)
        instance.version += 1
        instance.save()

        if collaborators is not None:
            instance.collaborators.set(collaborators)

        NoteVersion.objects.create(
            note=instance,
            title=instance.title,
            content=instance.content,
            version_number=instance.version,
        )

        self._broadcast_update(instance)
        return instance

    def _broadcast_update(self, note):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"note_{note.id}",
            {
                "type": "note_update",
                "data": {
                    "note_id": note.id,
                    "title": note.title,
                    "content": note.content,
                    "version": note.version,
                },
            },
        )


class NoteVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteVersion
        fields = "__all__"
