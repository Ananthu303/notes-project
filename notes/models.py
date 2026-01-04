from django.db import models
from django.contrib.auth.models import User


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Note(BaseModel):
    title = models.CharField(max_length=255)
    content = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    collaborators = models.ManyToManyField(
        User, related_name="shared_notes", blank=True
    )
    version = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.title)


class NoteVersion(BaseModel):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name="versions")
    title = models.CharField(max_length=255)
    content = models.TextField()
    version_number = models.PositiveIntegerField()

    class Meta:
        ordering = ["-version_number"]

    def __str__(self):
        return f"{self.note.title} (v{self.version_number})"
