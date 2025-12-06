from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import PostViewSet, DraftAutosaveViewSet
from . import views


router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')


# we'll mount a small viewset for autosaves
from rest_framework.routers import SimpleRouter
autosave_router = SimpleRouter()
autosave_router.register(r'autosaves', DraftAutosaveViewSet, basename='autosave')


urlpatterns = [
	path('', views.index, name='home'),
	path('posts/<slug:slug>/', views.post_detail, name='post_detail'),
	path('categories/', views.categories_list, name='categories'),
	path('categories/<slug:slug>/', views.category_detail, name='category_detail'),
	path('authors/', views.authors_list, name='authors'),
	path('authors/<str:username>/', views.author_detail, name='author_detail'),
	path('editor/', views.editor_view, name='editor'),
	path('api/', include(router.urls)),
	path('api/', include(autosave_router.urls)),
]