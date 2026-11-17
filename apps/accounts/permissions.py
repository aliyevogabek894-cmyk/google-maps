"""Rolga asoslangan ruxsatlar va dekoratorlar."""
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

from .models import ALL_STAFF_ROLES, ROLE_EDITOR, ROLE_MODERATOR, ROLE_SUPERADMIN


def get_user_roles(user):
    """Foydalanuvchiga biriktirilgan rollar to'plamini qaytaradi."""
    if not user or not user.is_authenticated:
        return set()
    roles = set(user.groups.values_list("name", flat=True))
    if user.is_superuser:
        roles.add(ROLE_SUPERADMIN)
    return roles


def has_any_role(user, allowed_roles):
    """Foydalanuvchida ko'rsatilgan rollardan biri borligini tekshiradi."""
    if not user or not user.is_authenticated or not user.is_active:
        return False
    if user.is_superuser:
        return True
    user_roles = get_user_roles(user)
    if ROLE_SUPERADMIN in user_roles:
        return True
    return bool(user_roles.intersection(set(allowed_roles)))


def is_staff_portal_user(user):
    """Xodimlar boshqaruv portaliga kirish huquqini tekshiradi."""
    return has_any_role(user, ALL_STAFF_ROLES)


def role_required(*allowed_roles):
    """Funksiya ko'rinishidagi view'lar uchun rol tekshiruvi dekoratori."""
    target_roles = allowed_roles or ALL_STAFF_ROLES

    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not has_any_role(request.user, target_roles):
                messages.error(request, "Sizda ushbu bo'limga kirish huquqi mavjud emas.")
                raise PermissionDenied("Ruxsat etilmagan rol.")
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator


class RoleRequiredMixin(LoginRequiredMixin):
    """Class-based view'lar uchun rolga asoslangan kirish cheklovi."""

    allowed_roles = ALL_STAFF_ROLES

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not has_any_role(request.user, self.allowed_roles):
            messages.error(request, "Ushbu bo'lim uchun sizda yetarli huquq yo'q.")
            raise PermissionDenied("Ushbu bo'lim uchun ruxsat yo'q.")
        return super().dispatch(request, *args, **kwargs)


def user_role_capabilities(user):
    """Shablonlar uchun foydalanuvchi ruxsatlari lug'atini qaytaradi."""
    roles = get_user_roles(user)
    is_super = user.is_superuser or ROLE_SUPERADMIN in roles
    return {
        "roles": sorted(roles),
        "is_superadmin": is_super,
        "can_manage_branches": is_super,
        "can_manage_content": is_super or ROLE_EDITOR in roles,
        "can_moderate_reviews": is_super or ROLE_MODERATOR in roles,
        "can_import_platform_stats": is_super,
        "can_export_reports": is_super or ROLE_EDITOR in roles or ROLE_MODERATOR in roles,
        "can_view_audit": is_super,
    }
