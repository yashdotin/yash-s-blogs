import os
import sys
from pathlib import Path
# ensure project root is importable
proj_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(proj_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
import django
django.setup()
from django.utils import timezone
from django.contrib.auth import get_user_model
from blog.models import Post

User = get_user_model()
user, created = User.objects.get_or_create(username='demo')
if created:
    user.set_password('demo')
    user.email = 'demo@example.com'
    user.save()

post, created = Post.objects.get_or_create(
    slug='hello-world',
    defaults={
        'author': user,
        'title': 'Hello World',
        'excerpt': 'This is a demo post created for preview.',
        'body': '<p>This is some demo body content for the post. Enjoy!</p>',
        'status': 'PUBLISHED',
        'published_at': timezone.now(),
    }
)
print('Created user:', user.username, 'created_user?', created)
print('Created post:', post.title, 'created_post?', created)
