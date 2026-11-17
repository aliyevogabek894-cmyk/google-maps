"""Barcha shablonlarda mavjud bo'ladigan umumiy sayt konteksti."""
from django.utils import timezone

from apps.accounts.permissions import is_staff_portal_user, user_role_capabilities
from apps.branches.models import Branch
from .models import SiteSettings


def site_context(request):
    """Sayt sozlamalari, asosiy filial va xodim ruxsatlarini uzatadi."""
    try:
        settings_obj = SiteSettings.get_solo()
    except Exception:
        settings_obj = None

    try:
        active_branches = list(Branch.objects.filter(is_active=True).order_by("-is_primary", "name"))
        primary_branch = active_branches[0] if active_branches else None
    except Exception:
        active_branches = []
        primary_branch = None

    portal_caps = None
    if getattr(request, "user", None) and request.user.is_authenticated and is_staff_portal_user(request.user):
        portal_caps = user_role_capabilities(request.user)

    return {
        "site_settings": settings_obj,
        "primary_branch": primary_branch,
        "active_branches": active_branches,
        "portal_caps": portal_caps,
        "current_year": timezone.localdate().year,
    }
