import os
import sys
from pathlib import Path

# Make project root importable
proj_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(proj_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

import django
django.setup()

from blog.models import Category

categories = [
    ("AI & MACHINE LEARNING", "ai-ml"),
    ("PROGRAMMING & WEB DEVELOPMENT", "programming"),
    ("CAREER, INTERNSHIP, & TECH OPPORTUNITIES", "career"),
    ("PERSONAL GROWTH & ESSAYS", "personal-growth"),
    ("TECH NEWS, REVIEWS & OPINIONS", "tech-news"),
]

for name, slug in categories:
    obj, created = Category.objects.get_or_create(slug=slug, defaults={"name": name})
    print(f"{'Created' if created else 'Exists '}: {obj.name} ({obj.slug})")

print('Done')
