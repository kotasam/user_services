import uuid

from django.db import models


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    status = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    organisation = models.CharField(max_length=100, blank=False, null=False)

    deleted_by = models.CharField(max_length=100, blank=True, null=True)
    deleted_at = models.DateTimeField("Deleted at", blank=True, null=True)

    created_by = models.CharField(
        max_length=100, blank=False, null=False, default="NULL"
    )
    created_at = models.DateTimeField("Created at", auto_now_add=True)

    updated_by = models.CharField(
        max_length=100, blank=False, null=False, default="NULL"
    )
    updated_at = models.DateTimeField("Updated at", auto_now=True)

    info = models.JSONField(blank=True, null=True, default=dict)

    class Meta:
        abstract = True
