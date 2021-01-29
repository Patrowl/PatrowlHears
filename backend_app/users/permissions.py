from django.conf import settings
from rest_framework import permissions


class AllowManageMetadata(permissions.BasePermission):
    def has_permission(self, request, view):
        """Check if user has permissions to access Metadata apis."""
        if settings.RESTRICTED_MODE is False or request.user.is_superuser:
            return True
        if request.user.is_authenticated and \
            'manage_metadata' in request.user.profile.keys() and \
            request.user.profile['manage_metadata'] is True:
            return True
        return False


class AllowManageOrganization(permissions.BasePermission):
    def has_permission(self, request, view):
        """Check if user has permissions to access ManageOrganization apis."""
        if settings.RESTRICTED_MODE is False or request.user.is_superuser:
            return True
        if request.user.is_authenticated and \
            'manage_organization' in request.user.profile.keys() and \
            request.user.profile['manage_organization'] is True:
            return True
        return False


class AllowManageAlertEmail(permissions.BasePermission):
    def has_permission(self, request, view):
        """Check if user has permissions to access ManageAlertEmail apis."""
        if settings.RESTRICTED_MODE is False or request.user.is_superuser:
            return True
        if request.user.is_authenticated and \
            'manage_alert_email' in request.user.profile.keys() and \
            request.user.profile['manage_alert_email'] is True:
            return True
        return False


class AllowManageAlertSlack(permissions.BasePermission):
    def has_permission(self, request, view):
        """Check if user has permissions to access ManageAlertSlack apis."""
        if settings.RESTRICTED_MODE is False or request.user.is_superuser:
            return True
        if request.user.is_authenticated and \
            'manage_alert_slack' in request.user.profile.keys() and \
            request.user.profile['manage_alert_slack'] is True:
            return True
        return False


class AllowDataSync(permissions.BasePermission):
    def has_permission(self, request, view):
        """Check if user has permissions to access DataSync apis"""
        if settings.RESTRICTED_MODE is False or request.user.is_superuser:
            return True
        if request.user.is_authenticated and \
            'enable_server_datasync' in request.user.profile.keys() and \
            request.user.profile['enable_server_datasync'] is True:
            return True
        return False
