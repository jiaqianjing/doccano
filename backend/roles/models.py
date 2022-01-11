from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Manager

from api.models import Project


class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class RoleMappingManager(Manager):

    def can_update(self, project: int, mapping_id: int, new_role: str) -> bool:
        """The project needs at least 1 admin.

        Args:
            project: The project id.
            mapping_id: The mapping id.
            new_role: The new role name.

        Returns:
            Whether the mapping can be updated or not.
        """
        queryset = self.filter(
            project=project, role__name=settings.ROLE_PROJECT_ADMIN
        )
        if queryset.count() > 1:
            return True
        else:
            mapping = queryset.first()
            if mapping.id == mapping_id and new_role != settings.ROLE_PROJECT_ADMIN:
                return False
            return True


class RoleMapping(models.Model):
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='role_mappings'
    )
    project = models.ForeignKey(
        to=Project,
        on_delete=models.CASCADE,
        related_name='role_mappings'
    )
    role = models.ForeignKey(
        to=Role,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = RoleMappingManager()

    def clean(self):
        other_rolemappings = self.project.role_mappings.exclude(id=self.id)

        if other_rolemappings.filter(user=self.user, project=self.project).exists():
            message = 'This user is already assigned to a role in this project.'
            raise ValidationError(message)

    class Meta:
        unique_together = ("user", "project")
