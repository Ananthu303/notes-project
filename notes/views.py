from django.contrib.auth.models import User
from django.core.cache import cache
from django.views.generic import TemplateView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import Note, NoteVersion
from .pagination import VersionPagination
from .serializers import NoteSerializer, NoteVersionSerializer, UserSerializer
from django.shortcuts import get_object_or_404
from django.db.models import Q

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class NotePageView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        note_id = self.kwargs.get("note_id")
        note = get_object_or_404(Note, id=note_id)
        context["note"] = note
        return context


class NoteViewSet(ModelViewSet):
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Note.objects.filter(Q(owner=user) | Q(collaborators=user)).distinct()


class NoteVersionView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = VersionPagination

    def get(self, request, note_id):
        page = request.query_params.get("page", 1)
        cache_key = f"note:{note_id}:versions:{page}"

        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        versions = NoteVersion.objects.filter(note_id=note_id)
        paginator = VersionPagination()
        page_data = paginator.paginate_queryset(versions, request)
        data = NoteVersionSerializer(page_data, many=True).data
        cache.set(cache_key, data, 60)
        return paginator.get_paginated_response(data)
