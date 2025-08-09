from rest_framework import generics, permissions, viewsets
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth.models import User

from .serializers import (
	UserRegisterSerializer,
	UserSerializer,
	ProjectSerializer,
	DocumentSerializer,
)
from .models import Project, Document


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
		serializer.save()


