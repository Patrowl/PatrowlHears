from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User#, Team, TeamUser, TeamOwner

admin.site.register(User, UserAdmin)
# admin.site.register(Team)
# admin.site.register(TeamUser)
# admin.site.register(TeamOwner)
