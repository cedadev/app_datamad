from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models.grants import ImportedGrant, Grant
from .models.users import User, DataCentre
from .models.jira import Subtask, JIRAIssueType, JIRATicket
from .models.document_store import Document
from .models.data_management_plans import *


################################################################################
#                                                                              #
#                                 Inlines                                      #
#                                                                              #
################################################################################
class DocumentInline(admin.TabularInline):
    model = Document
    extra = 0


class SubtaskInline(admin.TabularInline):
    model = Subtask
    extra = 0


class JIRAIssueTypeInline(admin.TabularInline):
    model = JIRAIssueType
    extra = 0

    def has_add_permission(self, request, obj=None):
        permission = super().has_add_permission(request, obj)

        if obj:
            if obj.jiraissuetype_set.count() > 0:
                permission = False

        return permission


class JIRATicketInline(admin.TabularInline):
    model = JIRATicket
    extra = 0


class DocumentTemplateInline(admin.TabularInline):
    model = DocumentTemplate
    extra = 0


class DataFormatInline(admin.TabularInline):
    model = DataFormat


class PreservationPlanInline(admin.TabularInline):
    model = PreservationPlan


################################################################################
#                                                                              #
#                               Admin Classes                                  #
#                                                                              #
################################################################################

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ( 'first_name', 'last_name', 'email','data_centre', 'is_admin')
    search_fields = ('email',)
    ordering = ('email',)
    list_filter = ('data_centre','is_admin')
    fieldsets = (
        (None, {'fields': ('email', 'first_name', 'last_name', 'password', 'data_centre')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_admin', 'is_superuser', 'groups','user_permissions')}),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }),
    )


@admin.register(ImportedGrant)
class ImportedGrantAdmin(admin.ModelAdmin):
    search_fields = ['grant_ref', 'title']
    list_display = ('grant_ref', 'title', 'creation_date')

    def __init__(self, *args, **kwargs):
        admin.ModelAdmin.__init__(self, *args, **kwargs)

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Grant)
class GrantAdmin(admin.ModelAdmin):
    readonly_fields = ['updated_imported_grant', 'science_area']
    search_fields = ['grant_ref', 'importedgrant__title']
    inlines = [
        JIRATicketInline,
        DocumentInline
    ]

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(DataProduct)
class DataProductAdmin(admin.ModelAdmin):
    pass


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'grant')

    search_fields = ['title', 'grant__grant_ref']
    autocomplete_fields = ['grant']


@admin.register(DataCentre)
class DataCentreAdmin(admin.ModelAdmin):
    inlines = [
        JIRAIssueTypeInline,
        SubtaskInline,
        DocumentTemplateInline,
        DataFormatInline,
        PreservationPlanInline,
    ]
