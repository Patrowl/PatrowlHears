from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
admin_user = get_user_model().objects.filter(username='admin').first()
if admin_user is None:
    admin_user = get_user_model().objects.create_superuser('admin', 'admin@dev.patrowl.io', 'Bonjour1!')

# Create an authtoken if needed
Token.objects.get_or_create(user=admin_user)[0]