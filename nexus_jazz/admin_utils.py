from __future__ import annotations
from django.urls import reverse
from django.utils.html import format_html


class RowActionsMixin:
    """Add inline Edit/Delete buttons to any ModelAdmin. Include 'row_actions' in list_display."""

    def row_actions(self, obj):
        app = obj._meta.app_label
        model = obj._meta.model_name
        edit_url = reverse(f"admin:{app}_{model}_change", args=[obj.pk])
        delete_url = reverse(f"admin:{app}_{model}_delete", args=[obj.pk])
        return format_html(
            '<a href="{}" style="margin-right:8px;color:var(--primary)">Edit</a>'
            '<a href="{}" style="color:#e74c3c">Delete</a>',
            edit_url,
            delete_url,
        )

    row_actions.short_description = ""
