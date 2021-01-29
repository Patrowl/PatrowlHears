from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import VPRating

admin.site.register(VPRating, SimpleHistoryAdmin)
