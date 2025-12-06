from django.shortcuts import render, get_object_or_404
from django.db.models import F, Q
from django.views.decorators.cache import cache_page
from django.utils.text import slugify

from .models import Post, Tag
from .models import Category
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required


# -------------------------------
# HOMEPAGE
# -------------------------------

@cache_page(30)  # cache homepage for 30 seconds to reduce DB load
def index(request):
    posts = (
        Post.objects.filter(status="PUBLISHED")
        .select_related("author")
        .prefetch_related("tags", "categories")
        .order_by("-published_at")[:9]
    )

    trending = (
        Post.objects.filter(status="PUBLISHED")
        .order_by("-views")[:3]
    )

    return render(request, "blog/index.html", {
        "posts": posts,
        "trending": trending,
        "page_title": "Home — MyBlog",
        "meta_description": "Read the latest articles, tutorials, and insights from MyBlog.",
    })


# -------------------------------
# POST DETAIL PAGE
# -------------------------------

def post_detail(request, slug):
    post = get_object_or_404(
        Post.objects.select_related("author").prefetch_related("tags", "categories"),
        slug=slug,
        status="PUBLISHED"
    )

    # Increment views (safe, atomic update)
    Post.objects.filter(id=post.id).update(views=F("views") + 1)

    # Related posts by tag or category
    related_posts = (
        Post.objects.filter(
            Q(tags__in=post.tags.all()) | Q(categories__in=post.categories.all()),
            status="PUBLISHED"
        )
        .exclude(id=post.id)
        .distinct()
        .order_by("-published_at")[:3]
    )

    # SEO metadata
    meta_description = post.excerpt if post.excerpt else post.body[:150]

    return render(request, "blog/post_detail.html", {
        "post": post,
        "related_posts": related_posts,
        "page_title": f"{post.title} — MyBlog",
        "meta_description": meta_description,
    })


# -------------------------------
# CATEGORIES & AUTHORS
# -------------------------------

def categories_list(request):
    categories = Category.objects.all()
    return render(request, "blog/categories.html", {
        "categories": categories,
        "page_title": "Categories — MyBlog",
    })


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = (
        Post.objects.filter(categories=category, status="PUBLISHED")
        .select_related("author")
        .prefetch_related("tags")
        .order_by("-published_at")
    )
    return render(request, "blog/category_detail.html", {"category": category, "posts": posts})


def authors_list(request):
    User = get_user_model()
    authors = User.objects.filter(is_active=True)
    return render(request, "blog/authors.html", {"authors": authors})


def author_detail(request, username):
    User = get_user_model()
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=author, status="PUBLISHED").order_by("-published_at")
    return render(request, "blog/author_detail.html", {"author": author, "posts": posts})


@login_required
def editor_view(request):
    return render(request, "blog/editor.html")
