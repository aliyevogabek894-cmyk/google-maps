"""Hisoblar va audit jurnali servislari."""
import logging

from django.contrib.auth.models import Group

from .models import ALL_STAFF_ROLES, AdminAuditLog

logger = logging.getLogger("turon.accounts")


def ensure_default_roles():
    """Standart rollarni (Superadmin, Muharrir, Fikr moderatori) yaratadi."""
    created = []
    for role_name in ALL_STAFF_ROLES:
        _, was_created = Group.objects.get_or_create(name=role_name)
        if was_created:
            created.append(role_name)
    return created


def log_admin_action(
    request,
    action: str,
    summary: str,
    target_model: str = "",
    target_id: str = "",
    details: dict | None = None,
    actor=None,
):
    """Administrator yoki moderator amalini AdminAuditLog'ga yozadi."""
    from apps.core.security import get_client_ip_hash

    resolved_actor = actor
    if resolved_actor is None and request is not None and getattr(request, "user", None):
        if request.user.is_authenticated:
            resolved_actor = request.user

    username = resolved_actor.get_username() if resolved_actor else ""
    ip_hash = get_client_ip_hash(request) if request is not None else ""

    try:
        return AdminAuditLog.objects.create(
            actor=resolved_actor,
            actor_username=username,
            action=action,
            target_model=target_model,
            target_id=str(target_id) if target_id else "",
            summary=summary[:255],
            details=details or {},
            ip_hash=ip_hash,
        )
    except Exception:
        logger.exception("Audit log yozishda xatolik yuz berdi: %s", summary)
        return None
