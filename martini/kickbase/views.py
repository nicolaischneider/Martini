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

#k_user: User = None

# error response for not being logged in
ERR_JSON = {
    "error": "You need to login first or your Request was wrong"
}
ERR_BAD_REQ = {"m": "Bad Request"}

def home_view(request, *args, **kwargs):
    return HttpResponse("<h1>Welcome to the Martini API</h1>")

# login
def login_with_credentials(body):
    k_user = User()

    #if k_user.isLoggedIn == True:
    #    return True
    try:
        json_body = json.loads(body)
        login_body = json_body['LOGIN']
        email = login_body['email']
        pw = login_body['pw']

        isLoggedIn = k_user.login(email, pw)
        if isLoggedIn == False:
            print("Login failed")
        return (isLoggedIn, k_user)
    except:
        return (False, k_user)

# Create your views here.
@csrf_exempt
def login(request, *args, **kwargs):
    if request.method != 'POST':
        return JsonResponse(ERR_BAD_REQ) # change to http error response

    k_user = User()

    try:
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
    except:
        return JsonResponse(ERR_BAD_REQ)

def logout(request, *args, **kwargs):
    #initialize_user()

    #if k_user.isLoggedIn == False:
    #    return JsonResponse(ERR_JSON)
        
    #k_user.logout()
    resp =  {
        "m": "Logged out",
    }
    return JsonResponse(resp)

@csrf_exempt
def getUser(request, *args, **kwargs):
    if request.method != 'POST':
        return JsonResponse(ERR_BAD_REQ) # change to http error response

    isLoggedIn, k_user = login_with_credentials(request.body)
    if isLoggedIn == False:
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

@csrf_exempt
def getUserStats(request, *args, **kwargs):
    if request.method != 'POST':
        return JsonResponse(ERR_BAD_REQ) # change to http error response

    isLoggedIn, k_user = login_with_credentials(request.body)
    if isLoggedIn == False:
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

@csrf_exempt
def getPlayers(request, *args, **kwargs):
    if request.method != 'POST':
        return JsonResponse(ERR_BAD_REQ) # change to http error response

    isLoggedIn, k_user = login_with_credentials(request.body)
    if isLoggedIn == False:
        return JsonResponse(ERR_JSON)

    players = k_user.getUserPlayer()
    return JsonResponse(players)

@csrf_exempt
def getTransactions(request, *args, **kwargs):
    if request.method != 'POST':
        return JsonResponse(ERR_BAD_REQ) # change to http error response

    isLoggedIn, k_user = login_with_credentials(request.body)
    if isLoggedIn == False:
        return JsonResponse(ERR_JSON)

    transactions = k_user.getListOfTransactions()
    return JsonResponse(transactions)

@csrf_exempt
def getPrediction(request, *args, **kwargs):
    if request.method != 'POST':
        return JsonResponse(ERR_BAD_REQ) # change to http error response

    isLoggedIn, k_user = login_with_credentials(request.body)
    if isLoggedIn == False:
        return JsonResponse(ERR_JSON)

    try:
        body = json.loads(request.body)
    except:
        return JsonResponse(ERR_BAD_REQ)

    hasConfig = False
    if 'BUY' in body:
        hasConfig = True
    
    if hasConfig == False:
        default_params = {
            "BUY": {
                "type": "LOGIC_BUY",
                "default": True,
                "complex_eval": False,
                "considered_days": 3
            },
            "SELL": {
                "default": True,
                "min_profit": 20
            }
        }
        buy_params = default_params['BUY']
        sell_params = default_params['SELL']

        predBuy = k_user.getPredictionBuy(buy_params)
        predSell = k_user.getPredictionSell(sell_params)

        prediction = {
            "Buy": predBuy,
            "Sell": predSell
        }
        return JsonResponse(prediction)

    else:
        # parse request
        try:
            body = json.loads(request.body)
            buy_params = body['BUY']
            sell_params = body['SELL']

            # buy
            if buy_params["type"] == "ML":
                predBuy = k_user.getPredictionBuyML()
            
            if buy_params["type"] == "LOGIC_BUY":
                predBuy = k_user.getPredictionBuy(buy_params)

            # sell
            predSell = k_user.getPredictionSell(sell_params)

            prediction = {
                "Buy": predBuy,
                "Sell": predSell
            }

            return JsonResponse(prediction)
        except:
            return JsonResponse({"m": "Issue with prediction"})

@csrf_exempt
def trade(request, *args, **kwargs):
    if request.method != 'POST':
        return JsonResponse(ERR_BAD_REQ) # change to http error response

    isLoggedIn, k_user = login_with_credentials(request.body)
    if isLoggedIn == False:
        return JsonResponse(ERR_JSON)

    try:
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
    except:
        return JsonResponse(ERR_BAD_REQ)

@csrf_exempt
def getOffers(request, *args, **kwargs):
    if request.method != 'POST':
        return JsonResponse(ERR_BAD_REQ) # change to http error response

    isLoggedIn, k_user = login_with_credentials(request.body)
    if isLoggedIn == False:
        return JsonResponse(ERR_JSON)

    offers = k_user.getOffers()
    return JsonResponse(offers)

@csrf_exempt
def acceptOffer(request, *args, **kwargs):
    if request.method != 'POST':
        return JsonResponse(ERR_BAD_REQ) # change to http error response

    isLoggedIn, k_user = login_with_credentials(request.body)
    if isLoggedIn == False:
        return JsonResponse(ERR_JSON)

    try:
        body = json.loads(request.body)
        offer_id = body["offer_id"]
        player_id = body["player_id"]
        resp = k_user.acceptOffer(offer_id, player_id)
        return JsonResponse(resp)
    except:
        return JsonResponse(ERR_BAD_REQ)

@csrf_exempt
def get_players_val(request, *args, **kwargs):
    if request.method != 'POST':
        return JsonResponse({"m": "Bad Request"}) # change to http error response

    isLoggedIn, k_user = login_with_credentials(request.body)
    if isLoggedIn == False:
        return JsonResponse(ERR_JSON)

    try:
        body = json.loads(request.body)
        #ids = body["ids"]
        players = k_user.get_player_val(body["id"])
        return JsonResponse({"p":players})
    except:
        return JsonResponse(ERR_BAD_REQ)

def get_player_stats_prediction(request, *args, **kwargs):
    isLoggedIn, k_user = login_with_credentials(request.body)
    if isLoggedIn == False:
        return JsonResponse(ERR_JSON)
    stats = k_user.getStatsForPrediction()
    return JsonResponse(stats)