from django.contrib import admin
from .models import Player
from .models import Transaction

# Register your models here.
admin.site.register(Player)
admin.site.register(Transaction)