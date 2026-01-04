from django.contrib import admin
from .models import Note, NoteVersion
# Register your models here.

admin.site.register(Note)
admin.site.register(NoteVersion)
