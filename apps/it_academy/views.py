from django.shortcuts import render

from apps.content.models import GalleryItem, NewsPost, Teacher
from .models import GameModule, ITCourse, ITProject


def it_academy_view(request):
    """IT Akademiya: IT ustozi, kurslar, IT WORLD o'yin metodikasi va loyihalar."""
    courses = ITCourse.objects.filter(is_active=True)
    projects = ITProject.objects.filter(is_published=True).select_related("course", "branch")
    it_photos = GalleryItem.objects.filter(is_published=True, category="it_lab")
    it_news = NewsPost.objects.filter(is_published=True).order_by("-published_at")[:3]
    it_teacher = Teacher.objects.filter(is_active=True, static_photo_path="official_media/teacher-aliyev.jpg").first()
    if not it_teacher:
        it_teacher = Teacher.objects.filter(is_active=True, subject_or_role__icontains="IT").first()

    active_category = request.GET.get("turkum", "").strip()
    games_qs = GameModule.objects.filter(is_active=True)
    valid_cats = {c[0] for c in GameModule.CATEGORY_CHOICES}
    if active_category in valid_cats:
        games_qs = games_qs.filter(category=active_category)
    else:
        active_category = ""

    return render(
        request,
        "it_academy/index.html",
        {
            "courses": courses,
            "projects": projects,
            "it_photos": it_photos,
            "it_news": it_news,
            "it_teacher": it_teacher,
            "games": games_qs,
            "game_categories": GameModule.CATEGORY_CHOICES,
            "active_category": active_category,
        },
    )
