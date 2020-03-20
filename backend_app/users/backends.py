from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.conf import settings
from django.db.models import Q
from organizations.backends.defaults import InvitationBackend, RegistrationBackend


class CustomRegistrations(RegistrationBackend):
    registration_form_template = 'aregister_form.html'
    activation_success_template = 'organizations/register_success.html'


class CustomInvitations(InvitationBackend):
    invitation_subject = 'email/invitation_subject.txt'
    invitation_body = 'email/invitation_body.html'

    def invite_by_email(self, email, sender=None, request=None, **kwargs):
        try:
            user = self.user_model.objects.get(email=email)
        except self.user_model.DoesNotExist:
            user = self.user_model.objects.create(
                email=email,
                username=email,
                password=self.user_model.objects.make_random_password())
            user.is_active = False
            user.save()
        kwargs.update({'BASE_URL': settings.BASE_URL})
        self.send_invitation(user, sender, **kwargs)
        return user


class EmailOrUsernameModelBackend(ModelBackend):
    """
    Authentication backend which allows users to authenticate using either their
    username or email address

    Source: https://stackoverflow.com/a/35836674/59984
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # n.b. Django <2.1 does not pass the `request`

        user_model = get_user_model()

        if username is None:
            username = kwargs.get(user_model.USERNAME_FIELD)

        # The `username` field is allows to contain `@` characters so
        # technically a given email address could be present in either field,
        # possibly even for different users, so we'll query for all matching
        # records and test each one.
        users = user_model._default_manager.filter(
            Q(**{user_model.USERNAME_FIELD: username}) | Q(email__iexact=username)
        )

        # Test whether any matched user has the provided password:
        for user in users:
            if user.check_password(password):
                return user
        if not users:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (see
            # https://code.djangoproject.com/ticket/20760)
            user_model().set_password(password)
