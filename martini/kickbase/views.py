from django.shortcuts import render
from kickbase_api.kickbase import Kickbase
from django.http import JsonResponse
from kickbase import models
from django.http import HttpResponse

k_user = models.User()

def home_view(request, *args, **kwargs):
    return HttpResponse("<h1>Welcome to the Martini API</h1>")

# Create your views here.
def getUser(request, *args, **kwargs):
    usr = k_user.getUser()
    data = k_user.getLeagueData()
    userData = {
        "user_name": usr.name,
        "user_mail": usr.email,
        "user_id": usr.id,
        "league_creators": data.creator
    }
    return JsonResponse(userData)

def getUserStats(request, *args, **kwargs):
    usr = k_user.getUser()    
    stats = k_user.getLeagueMe()
    userValues = {
        "user_name": usr.name,
        "budget": stats.budget,
        "points": stats.points,
        "team_value": stats.team_value
    }
    return JsonResponse(userValues)

def getPlayers(request, *args, **kwargs):
    players = k_user.getUserPlayer()
    
    #for player in players:
    #    print(player.last_name)

    pi = models.JSONParser()
    content = pi.getPlayerAsJSON(player=players)

    return JsonResponse(content)
