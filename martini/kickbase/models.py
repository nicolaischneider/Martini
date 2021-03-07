from django.db import models

class Transaction(models.Model):
    transaction_type = models.CharField(max_length=10,default="")
    traded_player_id = models.CharField(max_length=10,default="")
    traded_player_name = models.CharField(max_length=30,default="")
    value = models.IntegerField(default=-1)
    user_name = models.CharField(max_length=30)

class OwnedPlayer(models.Model):
    traded_player_id = models.CharField(max_length=10,default="")
    market_value_purchased = models.IntegerField(default=-1)
    user_name = models.CharField(max_length=30)
