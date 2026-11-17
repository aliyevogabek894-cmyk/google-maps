from django.shortcuts import render

from apps.content.models import GalleryItem, NewsPost, Teacher
from .models import ITCourse, ITProject


def it_academy_view(request):
    """IT Akademiya: IT xona, real o'qitiladigan kurslar, loyihalar va ustozlar."""
    courses = ITCourse.objects.filter(is_active=True)
    projects = ITProject.objects.filter(is_published=True).select_related("course", "branch")
    it_photos = GalleryItem.objects.filter(is_published=True, category="it_lab")
    it_news = NewsPost.objects.filter(is_published=True).order_by("-published_at")[:3]
    teachers = Teacher.objects.filter(is_active=True)

    return render(
        request,
        "it_academy/index.html",
        {
            "courses": courses,
            "projects": projects,
            "it_photos": it_photos,
            "it_news": it_news,
            "teachers": teachers,
        },
    )
