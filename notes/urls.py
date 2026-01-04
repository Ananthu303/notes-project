from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import NotePageView, NoteVersionView, NoteViewSet, UserViewSet

router = DefaultRouter()
router.register("notes", NoteViewSet, basename="notes")
router.register("users", UserViewSet, basename="users")

urlpatterns = [
    path("", include(router.urls)),
    path("note-index/<int:note_id>/", NotePageView.as_view(), name="note_page"),
    path("notes/<int:note_id>/versions/", NoteVersionView.as_view(), name="note-versions"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token-refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
