from django.db import models
from kickbase_api.kickbase import Kickbase
from kickbase_api import models as k_models
import os
import json

kickbase = Kickbase()

# Create your models here.
class User():
    user = None
    leagueData = None
    userLeagueData: k_models.league_me = None

    def __init__(self):
        self.login()
        self.getUserStats()

    @classmethod
    def login(self):
        if kickbase._is_token_valid == True:
            print("already logged in")
            pass

        try:
            user, leagues = kickbase.login("<mail>", "<password>")
            self.user = user
            self.leagueData = leagues[0]
        except:
            print("Something went wrong with the retrieval of login data")
            pass

    @classmethod
    def getUserStats(self):
        if self.userLeagueData is not None:
            print("user stats already retrieved")
            pass

        try:
            self.userLeagueData = kickbase.league_me(self.leagueData)
            print("user stats were retrieved")
        except:
            print("Something went wrong with the retrieval of user stats")
            pass


    # GETTER
    def getUser(self):
        if self.user is not None:
            return self.user

    def getLeagueData(self):
        if self.leagueData is not None:
            return self.leagueData

    def getLeagueMe(self):
        if self.userLeagueData is not None:
            return self.userLeagueData

    def getUserPlayer(self):
        try:
            players = kickbase.league_user_players(self.leagueData, self.user)
            return players
        except:
            print("could not extract player")
            pass

class JSONParser():
    def getPlayerAsJSON(self, player: k_models.player):
        playerArr = []
        for p in player:

            first_name = p.first_name
            last_name = p.last_name
            market_val = p.market_value
            market_value_purchased = "-"
            market_value_trend = p.market_value_trend
            position = str(p.position.name)
            points = p.totalPoints
            status = str(p.status.name)
            id_player = p.id

            playerStruct = {
                "first_name": first_name,
                "last_name": last_name,
                "market_val": market_val,
                "market_val_purchased": market_value_purchased,
                "market_value_trend": market_value_trend,
                "position": position,
                "points": points,
                "status": status,
                "id_player": id_player
            }
            playerArr.append(playerStruct)
        
        playerJSON = {
            "player": playerArr
        }

        return playerJSON

class Player(models.Model):
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    totalPoints = models.IntegerField()
    market_val = models.DecimalField(max_digits=15, decimal_places=2)
