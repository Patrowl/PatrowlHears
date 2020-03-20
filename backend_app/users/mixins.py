from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import ugettext_lazy as _
from organizations.mixins import OrganizationMixin


class OrganizationAdminOnly(LoginRequiredMixin, OrganizationMixin):
    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs
        self.organization = self.get_organization()
        if not request.user.is_superuser and not self.organization.is_admin(request.user):
            raise PermissionDenied(_("Sorry, (org) admins only"))
        return super(OrganizationAdminOnly, self).dispatch(request, *args, **kwargs)
