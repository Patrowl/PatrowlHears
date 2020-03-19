from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import ugettext_lazy as _
from organizations.mixins import OrganizationMixin, AdminRequiredMixin


class OrganizationAdminOnly(LoginRequiredMixin, OrganizationMixin):
    def dispatch(self, request, *args, **kwargs):
        print("dispatch")
        self.request = request
        self.args = args
        self.kwargs = kwargs
        self.organization = self.get_organization()
        self.service_provider = self.organization.provider
        if not self.organization.is_admin(request.user) and not \
                self.service_provider.is_member(request.user):
            raise PermissionDenied(_("Sorry, org admins only"))
        return super(AdminRequiredMixin, self).dispatch(request, *args, **kwargs)
