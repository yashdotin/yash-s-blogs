from rest_framework import viewsets, permissions, status, parsers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Post, DraftAutosave
from .serializers import PostSerializer, DraftAutosaveSerializer
import logging

logger = logging.getLogger(__name__)


class IsAuthorOrAdmin(permissions.BasePermission):
	def has_object_permission(self, request, view, obj):
		if request.method in permissions.SAFE_METHODS:
			return True
		return obj.author == request.user or request.user.is_superuser or getattr(request.user, "is_editor", False)


class PostViewSet(viewsets.ModelViewSet):
	queryset = Post.objects.all().select_related("author").prefetch_related("tags", "categories")
	permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrAdmin]
	serializer_class = PostSerializer
	# allow multipart/form-data (file uploads) and JSON
	parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
	lookup_field = 'slug'

	def perform_create(self, serializer):
		# Set the author to current user
		logger.debug('perform_create called by user %s, data keys: %s', getattr(self.request.user, 'username', None), list(self.request.data.keys()))
		print('DEBUG: perform_create called by', getattr(self.request.user, 'username', None), 'data keys:', list(self.request.data.keys()))
		# Debug POST and FILES content (useful when diagnosing publish failures)
		try:
			print('DEBUG: request.POST:', dict(self.request.POST))
			print('DEBUG: request.FILES keys:', list(self.request.FILES.keys()))
		except Exception as e:
			print('DEBUG: error printing request data', e)
		instance = serializer.save(author=self.request.user)
		# Set published_at if status is PUBLISHED
		if instance.status == 'PUBLISHED' and not instance.published_at:
			instance.published_at = timezone.now()
			instance.save()

	def perform_update(self, serializer):
		logger.debug('perform_update called by user %s, data keys: %s', getattr(self.request.user, 'username', None), list(self.request.data.keys()))
		print('DEBUG: perform_update called by', getattr(self.request.user, 'username', None), 'data keys:', list(self.request.data.keys()))
		instance = serializer.save()
		# Set published_at if transitioning to PUBLISHED status
		if instance.status == 'PUBLISHED' and not instance.published_at:
			instance.published_at = timezone.now()
			instance.save()

	@action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
	def autosave(self, request, pk=None):
		# save an autosave for an existing post
		post = self.get_object()
		if post.author != request.user and not request.user.is_superuser and not getattr(request.user, "is_editor", False):
			return Response({"detail": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)

		data = request.data
		# create or update DraftAutosave for this user+post
		autosave, _ = DraftAutosave.objects.update_or_create(
			user=request.user,
			post=post,
			defaults={"title": data.get("title", ""), "body": data.get("body", "")},
		)
		return Response({"status": "ok", "updated_at": autosave.updated_at})


class DraftAutosaveViewSet(viewsets.ViewSet):
	permission_classes = [permissions.IsAuthenticated]

	def retrieve(self, request, pk=None):
		# pk is post id or 'new' for new drafts
		if pk == "new":
			autosave = DraftAutosave.objects.filter(user=request.user, post__isnull=True).first()
			if not autosave:
				return Response({}, status=204)
			serializer = DraftAutosaveSerializer(autosave)
			return Response(serializer.data)

		autosave = DraftAutosave.objects.filter(user=request.user, post_id=pk).first()
		if not autosave:
			return Response({}, status=204)
		serializer = DraftAutosaveSerializer(autosave)
		return Response(serializer.data)

	def create(self, request):
		# create/update autosave for new draft (post=null)
		data = request.data.copy()
		data["user"] = request.user.id
		data["post"] = None
		serializer = DraftAutosaveSerializer(data=data)
		serializer.is_valid(raise_exception=True)
		# update existing null-post autosave for user or create
		autosave, _ = DraftAutosave.objects.update_or_create(
			user=request.user, post=None, defaults={"title": data.get("title", ""), "body": data.get("body", "")}
		)
		return Response({"status": "ok", "updated_at": autosave.updated_at})

	@action(detail=True, methods=["patch"], permission_classes=[permissions.IsAuthenticated])
	def autosave(self, request, pk=None):
		"""Patch autosave by id (allows quick updates from client-side autosave JS)."""
		autosave = get_object_or_404(DraftAutosave, pk=pk, user=request.user)
		title = request.data.get("title")
		body = request.data.get("body")
		changed = False
		if title is not None and title != autosave.title:
			autosave.title = title
			changed = True
		if body is not None and body != autosave.body:
			autosave.body = body
			changed = True
		if changed:
			autosave.save()
		return Response({"status": "ok", "updated_at": autosave.updated_at})