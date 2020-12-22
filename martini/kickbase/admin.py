from django.contrib import admin
from .models import Transaction
from .models import OwnedPlayer

# Register your models here.
admin.site.register(OwnedPlayer)
admin.site.register(Transaction)