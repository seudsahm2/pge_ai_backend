from rest_framework import generics, permissions, viewsets, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.db.models import Q

from .serializers import (
	UserRegisterSerializer,
	UserSerializer,
	ProjectSerializer,
	DocumentSerializer,
	DocumentChunkSerializer,
)
from .models import Project, Document, DocumentChunk
from .services.ingestion import process_document


class RegisterView(generics.CreateAPIView):
	queryset = User.objects.all()
	serializer_class = UserRegisterSerializer
	permission_classes = [permissions.AllowAny]


class MeView(generics.RetrieveAPIView):
	serializer_class = UserSerializer
	permission_classes = [permissions.IsAuthenticated]

	def get_object(self):
		return self.request.user


class ProjectViewSet(viewsets.ModelViewSet):
	serializer_class = ProjectSerializer
	permission_classes = [permissions.IsAuthenticated]

	def get_queryset(self):
		return Project.objects.filter(owner=self.request.user).order_by('-created_at')

	def perform_create(self, serializer):
		serializer.save(owner=self.request.user)


class DocumentViewSet(viewsets.ModelViewSet):
	serializer_class = DocumentSerializer
	permission_classes = [permissions.IsAuthenticated]

	def get_queryset(self):
		return Document.objects.filter(project__owner=self.request.user).order_by('-uploaded_at')

	def perform_create(self, serializer):
		project = serializer.validated_data['project']
		if project.owner != self.request.user:
			raise PermissionDenied("Not your project")
		doc = serializer.save(status='processing')
		try:
			process_document(doc)
		except (OSError, ValueError):
			doc.status = 'failed'
			doc.save(update_fields=['status'])


class SearchChunksView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def get(self, request):
		query = request.query_params.get('q', '').strip()
		project_id = request.query_params.get('project')
		if not query:
			return Response({'detail': 'q parameter required'}, status=status.HTTP_400_BAD_REQUEST)
		chunks = DocumentChunk.objects.filter(
			Q(chunk_text__icontains=query),
			document__project__owner=request.user,
		)
		if project_id:
			chunks = chunks.filter(document__project_id=project_id)
		chunks = chunks.select_related('document')[:20]
		data = DocumentChunkSerializer(chunks, many=True).data
		return Response({'results': data, 'count': len(data)})


