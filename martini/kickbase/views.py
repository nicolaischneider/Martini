from django.shortcuts import render
from kickbase_api.kickbase import Kickbase
from django.http import JsonResponse
from kickbase import models
from user.user import User
import json
from django.http import HttpResponse
from kickbase_api.models.player_marketvalue_history import PlayerMarketValueHistory
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect

k_user = User()

# error response for not being logged in
ERR_JSON = {
    "error": "You need to login first"
}

def home_view(request, *args, **kwargs):
    return HttpResponse("<h1>Welcome to the Martini API</h1>")

# Create your views here.
@csrf_exempt
def login(request, *args, **kwargs):
    if request.method != 'POST':
        return JsonResponse({"m": "Bad Request"}) # change to http error response

    body = json.loads(request.body)
    email = body['email']
    pw = body['pw']

    isLoggedIn = k_user.login(email, pw)
    if isLoggedIn == True:
        responseString = "Logged in succesfully"
    else:
        responseString = "Something went wrong during Login"

    resp =  {
        "m": responseString,
        "loggedIn": isLoggedIn
    }
    return JsonResponse(resp)

def logout(request, *args, **kwargs):
    if k_user.isLoggedIn == False:
        return JsonResponse(ERR_JSON)
        
    k_user.logout()
    resp =  {
        "m": "Logged out",
    }
    return JsonResponse(resp)

def getUser(request, *args, **kwargs):
    if k_user.isLoggedIn == False:
        return JsonResponse(ERR_JSON)

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
    if k_user.isLoggedIn == False:
        return JsonResponse(ERR_JSON)

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
    if k_user.isLoggedIn == False:
        return JsonResponse(ERR_JSON)

    players = k_user.getUserPlayer()
    return JsonResponse(players)

def getTransactions(request, *args, **kwargs):
    if k_user.isLoggedIn == False:
        return JsonResponse(ERR_JSON)

    transactions = k_user.getListOfTransactions()
    return JsonResponse(transactions)

def getPrediction(request, *args, **kwargs):
    if k_user.isLoggedIn == False:
        return JsonResponse(ERR_JSON)

    predBuy = k_user.getPredictionBuy()
    predSell = k_user.getPredictionSell()
    prediction = {
        "Buy": predBuy,
        "Sell": predSell
    }
    return JsonResponse(prediction)

@csrf_exempt
def trade(request, *args, **kwargs):
    if request.method != 'POST':
        return JsonResponse({"m": "Bad Request"}) # change to http error response

    if k_user.isLoggedIn == False:
        return JsonResponse(ERR_JSON)

    body = json.loads(request.body)
    trade_type = body["type"]
    player_id = body["player_id"]
    price = body["price"]

    if trade_type == "BUY":
        res = k_user.buyPlayer(str(player_id), int(price))
        return JsonResponse(res)

    if trade_type == "SELL":
        res = k_user.sellPlayer(str(player_id))
        return JsonResponse(res)

    return JsonResponse({"m": "Trade type has to be BUY or SELL"})

def get_player_stats_prediction(request, *args, **kwargs):
    if k_user.isLoggedIn == False:
        return JsonResponse(ERR_JSON)
    stats = k_user.getStatsForPrediction()
    return JsonResponse(stats)