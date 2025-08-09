from django.db import models
from django.contrib.auth.models import User
from pgvector.django import VectorField

class Project(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Document(models.Model):
    project = models.ForeignKey(Project, related_name='documents', on_delete=models.CASCADE)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='processing') # processing, ready, failed

    def __str__(self):
        return self.file.name

class DocumentChunk(models.Model):
    document = models.ForeignKey(Document, related_name='chunks', on_delete=models.CASCADE)
    chunk_text = models.TextField()
    # The Gemini embedding model 'text-embedding-004' produces vectors with 768 dimensions.
    embedding = VectorField(dimensions=768)

    def __str__(self):
        return f"Chunk from {self.document.file.name}"