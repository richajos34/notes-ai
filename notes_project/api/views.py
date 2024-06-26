# notes_project/api/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Note
from .serializers import NoteSerializer
from supabase_client import supabase

class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        title = data.get('title')
        content = data.get('content')

        # Insert into Supabase
        supabase.table('notes').insert({"title": title, "content": content}).execute()

        # Create the note in Django
        note = Note.objects.create(title=title, content=content)
        serializer = NoteSerializer(note)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        # Fetch from Supabase
        response = supabase.table('notes').select('*').execute()
        data = response.data

        return Response(data, status=status.HTTP_200_OK)
