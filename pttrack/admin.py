from __future__ import unicode_literals
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from simple_history.admin import SimpleHistoryAdmin
from django.utils.translation import gettext_lazy as _

from . import models


class CompletionFilter(SimpleListFilter):
    title = _('Completion')
    parameter_name = 'completion_status'

    def lookups(self, request, model_admin):
        return (
            ("Complete", _('Completed')),
            ("Unresolved", _('Unresolved')),
        )

    def queryset(self, request, queryset):
        if self.value() == "Complete":
            return queryset.exclude(completion_date=None)
        if self.value() == "Unresolved":
            return queryset.filter(completion_date=None)


class NoteAdmin(SimpleHistoryAdmin):
    readonly_fields = ('written_datetime', 'last_modified')
    list_display = ('__str__', 'written_datetime', 'patient', 'author',
                    'last_modified')


class ActionItemAdmin(SimpleHistoryAdmin):
    readonly_fields = ('written_datetime', 'last_modified')
    date_hierarchy = 'due_date'
    list_display = ('__str__', 'written_datetime', 'patient', 'author',
                    'last_modified')
    list_filter = ('instruction', CompletionFilter, )


for model in [models.Language, models.Patient, models.Provider,
              models.ActionInstruction, models.Ethnicity,
              models.ReferralType, models.ReferralLocation,
              models.ContactMethod, models.DocumentType, models.Outcome]:
    if hasattr(model, "history"):
        admin.site.register(model, SimpleHistoryAdmin)
    else:
        admin.site.register(model)

admin.site.register(models.Document, NoteAdmin)
admin.site.register(models.ActionItem, ActionItemAdmin)
