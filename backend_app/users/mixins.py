from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import mixins
from django.utils.translation import ugettext_lazy as _
from organizations.mixins import OrganizationMixin


class OrganizationAdminOnly(LoginRequiredMixin, mixins.CreateModelMixin, OrganizationMixin):
    def dispatch(self, request, *args, **kwargs):
        # print(dir(request))
        # print(dir(request.headers))
        # print(request.user.username)
        self.request = request
        self.args = args
        self.kwargs = kwargs
        self.organization = self.get_organization()
        # print("superuser:", request.user.is_superuser)
        # print("orgadmin:", self.organization.is_admin(request.user))
        if not request.user.is_superuser and not self.organization.is_admin(request.user):
            raise PermissionDenied(_("Sorry, (org) admins only"))
        return super(OrganizationAdminOnly, self).dispatch(request, *args, **kwargs)
