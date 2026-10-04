from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.permissions import LEGACY_ROLE_ALIASES, PERMISSIONS, ROLE_DEFINITIONS
from app.models.role import Permission, Role
from app.models.user import User


def seed_rbac(db: Session) -> None:
    permission_by_code = {p.code: p for p in db.scalars(select(Permission)).all()}
    for code, name in PERMISSIONS.items():
        if code not in permission_by_code:
            permission = Permission(code=code, name=name)
            db.add(permission)
            db.flush()
            permission_by_code[code] = permission

    role_by_slug = {r.slug: r for r in db.scalars(select(Role)).all()}
    for slug, definition in ROLE_DEFINITIONS.items():
        role = role_by_slug.get(slug)
        if role is None:
            role = Role(slug=slug, name=definition["name"], description=definition["description"])
            db.add(role)
            db.flush()
            role_by_slug[slug] = role
        else:
            role.name = definition["name"]
            role.description = definition["description"]

        desired = [permission_by_code[code] for code in definition["permissions"]]
        if not role.permissions:
            role.permissions = desired

    db.flush()

    # Map accounts created during the early S1-01 prototype to the new multi-role model.
    for user in db.scalars(select(User)).all():
        if not user.roles:
            slug = LEGACY_ROLE_ALIASES.get(user.role, user.role or "student")
            role = role_by_slug.get(slug) or role_by_slug.get("student")
            if role:
                user.roles.append(role)
        if not user.full_name:
            user.full_name = user.email.split("@", 1)[0]
        if user.status not in {"active", "pending", "locked"}:
            user.status = "active" if user.is_active else "locked"

    db.commit()
