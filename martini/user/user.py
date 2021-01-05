import os
import json
from kickbase.models import Transaction
from kickbase.models import OwnedPlayer

# kickbase
from kickbase_api.kickbase import Kickbase
from kickbase_api import models as k_models
from kickbase_api.models.player import Player
from kickbase_api.models.player import PlayerStatus
from kickbase_api.models.player_marketvalue_history import PlayerMarketValueHistory
from kickbase_api.models.market_player import MarketPlayer
from kickbase_api.models.market import Market

# prediction
from prediction.predict_buy import PredictBuy
from prediction.predict_sell import PredictSell

kickbase = Kickbase()

# Create your models here.
class User():

    user = None
    leagueData = None
    userLeagueData: k_models.league_me = None

    transactions = []
    transactionsDict = {}

    def __init__(self):
        self.login()
        self.getUserStats()
        self.getTransactions()
        self.updateOwnedPlayer()

    @classmethod
    def login(self):
        if kickbase._is_token_valid == True:
            print("already logged in")
            pass

        try:
            user, leagues = kickbase.login("awt_3@yahoo.com", "ilovesoccer3")
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

    @classmethod
    def getTransactions(self):
        try:
            meta_feed = kickbase.league_feed(0, self.leagueData)
            print("meta data was retrieved")
        except:
            print("Something went wrong while retrieving meta data")
            return

        # iterate through feed
        for item in meta_feed:

            meta = item.meta
            user_name = self.user.name
            value: int = -1

            if str(item.type.name) == "BUY":
                if meta.buyer_name == user_name:
                    transaction_type = "BUY"
                    value = meta.buy_price
                    traded_player_id = meta.player_id
                    traded_player_name = meta.player_last_name
                else:
                    continue

            if str(item.type.name) == "SALE":
                if meta.seller_name == user_name:
                    transaction_type = "SALE"
                    value = meta.sell_price
                    traded_player_id = meta.player_id
                    traded_player_name = meta.player_last_name
                else:
                    continue

            # if transaction was found: add
            if value > 0:
                t = Transaction.objects.filter(traded_player_id=traded_player_id,value=value)
                if len(t) > 0:
                    print("transaction already exists: " + traded_player_name + ", Price: " + str(value))
                else:
                    trans = Transaction(
                        transaction_type=transaction_type,
                        traded_player_id=traded_player_id,
                        traded_player_name=traded_player_name,
                        value=value
                    )
                    trans.save()
                    print("added new transaction: " + traded_player_name + ", Price: " + str(value))

        self.transactions = Transaction.objects.all()

    @classmethod
    def updateOwnedPlayer(self):
        # create dictionary with transactions
        self.transactionsDict = {}
        if len(self.transactions) > 0:
            for tran in self.transactions:
                transaction_type = tran.transaction_type
                if str(transaction_type) == "BUY":
                    traded_player_id = tran.traded_player_id
                    value = tran.value
                    self.transactionsDict.update({traded_player_id : value})

        # check if some players were sold ?
        try:
            player = kickbase.league_user_players(self.leagueData, self.user)
        except:
            print("could not extract player")
            return

        stored_player = OwnedPlayer.objects.all()
        for op in stored_player:
            id_player_stored = op.traded_player_id
            still_owned = False

            for p in player:
                id_player = p.id
                if id_player == id_player_stored:
                    still_owned = True
                    break

            if still_owned == False:
                op.delete()
        
        # add player to database (if not existent)
        for p in player:
            id_player = p.id
            market_val = p.market_value

            owned_player = OwnedPlayer.objects.filter(traded_player_id=id_player)
            if len(owned_player) > 0:
                print("player with id " + id_player + " is already stored")
            else:
                if id_player in self.transactionsDict:
                    print("found purchase value in transactions")
                    new_owned_player_val = self.transactionsDict[id_player]
                else:
                    print("didn't find purchase value in transactions")
                    new_owned_player_val = market_val
                
                new_owned_player = OwnedPlayer(
                    traded_player_id=id_player,
                    market_value_purchased=new_owned_player_val
                )
                new_owned_player.save()

    # GETTER
    def getPredictionBuy(self):
        predict = PredictBuy()
        prediction = predict.predict(player_tm=self.getPlayerOnTradeMarket())
        return prediction

    def getPlayerOnTradeMarket(self):
        # get players from market
        try:
            market = kickbase.market(self.leagueData)
            print("received market")
        except:
            print("something went wrong witrh tm")
            return

        # retrieve player struct and offers (if existing) from market player
        player_from_market = []
        for m_player in market.players:
            try:
                # ectract player from id
                player = kickbase.player_info(self.leagueData, str(m_player.id))
            except:
                print("something went wrong with extracting player from id")
                continue

            try:
                # get price
                p_highest_offer: int = 0
                additional_price = 100
                if len(m_player.offers) > 0:
                    for offer in m_player.offers:
                        # check if user name is samsies
                        if self.user.name == offer.user_name:
                            print("offer mady by user already")
                            continue

                        # update highest offer
                        if offer.price > p_highest_offer:
                            p_highest_offer = offer.price

                    p_highest_offer += additional_price

                if p_highest_offer <= additional_price:
                    p_highest_offer = player.market_value + additional_price
                
                # check if user can afford player
                if self.userLeagueData.budget < p_highest_offer:
                    continue

                # get stats of player
                player_stats = self.getStatsHistoryOfPlayer(player)

                if player_stats is None:
                    continue

                if player.status != PlayerStatus.NONE:
                    print("player not added because currently not playing")
                    continue

                optional_player = {
                    'first_name': player.first_name,
                    'last_name': player.last_name,
                    'player_id': player.id,
                    'value': p_highest_offer,
                    'stats': player_stats
                }

                player_from_market.append(optional_player)
            except:
                print("something went wrong with extracting offer from player")
                pass
        
        return player_from_market

    def getStatsHistoryOfPlayer(self, player: Player):
        try:
            player_stats = kickbase.player_stats(player)
            return player_stats
        except:
            print("Something went wrong with the retrieval of player stats")
            pass

    def getMarketValueHistoryOfPlayer(self, player: Player):
        try:
            player_marketvalue_hist = kickbase.league_player_marketvalue_history(self.leagueData, player)
            print("player marketvals were retrieved")
            return player_marketvalue_hist
        except:
            print("Something went wrong with the retrieval of player market vals")
            pass

    # return json (!!!)
    def getPlayerFeed(self, player: Player):
        try:
            player_feed = kickbase.league_players_feed(self.leagueData, player)
            print("player feed was retrieved successfully")
            return player_feed
        except:
            print("Something went wrong with player feed retrieval")
            pass

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
            player = kickbase.league_user_players(self.leagueData, self.user)
        except:
            print("could not extract player")
            pass

        playerArr = []
        for p in player:
            first_name = p.first_name
            last_name = p.last_name
            market_val = p.market_value

            # 2: value trend going down
            # 1: value trend going up
            # 0: no change
            market_value_trend = p.market_value_trend
            if market_value_trend == 0:
                market_value_trend_string = "-"
            elif market_value_trend == 1:
                market_value_trend_string = "UP"
            else:
                market_value_trend_string = "DOWN"
            
            position = str(p.position.name)
            points = p.totalPoints
            status = str(p.status.name)
            id_player = p.id

            market_value_purchased = "--"
            owned_player = OwnedPlayer.objects.filter(traded_player_id=id_player)
            if len(owned_player) == 1:
                for op in owned_player:
                    market_value_purchased = op.market_value_purchased
            else:
                market_value_purchased = "-"

            playerStruct = {
                "first_name": first_name,
                "last_name": last_name,
                "market_val": market_val,
                "market_val_purchased": market_value_purchased,
                "market_value_trend": market_value_trend_string,
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

    def getListOfTransactions(self):
        if len(self.transactions) > 0:
            transactionArray = []
            for tran in self.transactions:
                transaction_type = tran.transaction_type
                traded_player_id = tran.traded_player_id
                traded_player_name = tran.traded_player_name
                value = tran.value

                transactionStruct = {
                    "transaction_type": transaction_type,
                    "traded_player_id": traded_player_id,
                    "traded_player_name": traded_player_name,
                    "value": value
                }
                transactionArray.append(transactionStruct)

            transactionJSON = {
                "transactions": transactionArray
            }
            return transactionJSON