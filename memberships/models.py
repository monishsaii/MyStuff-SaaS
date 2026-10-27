from django.db import models
from django.conf import settings
from organizations.models import Organization


class Membership(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.PROTECT,
        related_name = "memberships"
    )
    
    organization = models.ForeignKey(
        Organization,
        on_delete = models.PROTECT
    )

    class Role(models.TextChoices):
        ADMIN = "ADMIN"
        OWNER = "OWNER"
        MANAGER = "MANAGER"
        MEMBER = "MEMBER"
    
    role = models.CharField(
        max_length = 7,
        choices = Role.choices
    )

    class Status(models.TextChoices):
        INVITED = "INVITED"
        ACTIVE = "ACTIVE"
        REMOVED = "REMOVED"

    status = models.CharField(
        max_length = 7,
        choices = Status.choices,
        default = Status.INVITED
    )

    joined_at = models.DateTimeField(
        null=True,
        blank=True
    )

    invited_by =models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null = True,
        blank = True,
        on_delete = models.PROTECT,
        related_name = "invited_memberships"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "organization"],
                name="unique_user_organization_membership"
            ),
            models.CheckConstraint(
                condition=models.Q(role__in=["ADMIN", "OWNER", "MANAGER", "MEMBER"]),
                name="valid_membership_role"
            ),
            models.CheckConstraint(
                condition=models.Q(status__in=["INVITED", "ACTIVE", "REMOVED"]),
                name="valid_membership_status"
            ),
        ]
