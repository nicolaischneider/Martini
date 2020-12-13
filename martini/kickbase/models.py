from django.db import models
from kickbase_api.kickbase import Kickbase
from kickbase_api import models
import os
import json

kickbase = Kickbase()

# Create your models here.
class User():
    user = None
    leagueData = None
    userLeagueData: models.league_me = None

    def __init__(self):
        self.login()
        self.getUserStats()

    @classmethod
    def login(self):
        if kickbase._is_token_valid == True:
            print("already logged in")
            pass

        try:
            user, leagues = kickbase.login("", "")
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
    def getPlayerAsJSON(self, player: models.player):
        playerArr = []
        for p in player:
            name = p.first_name + " " + p.last_name
            market_val = p.market_value
            playerStruct = {
                "name":name,
                "market_val":market_val
            }
            playerArr.append(playerStruct)
        
        playerJSON = {
            "player": playerArr
        }

        return playerJSON
