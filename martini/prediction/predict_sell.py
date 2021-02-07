from kickbase_api.kickbase import Kickbase
from kickbase_api.models.player import Player
from kickbase_api.exceptions import KickbaseException
import operator

class PredictSell:

    # const
    TOP_PLAYER = 3

    # params
    MIN_PROFIT: int = None
    CHECK_TREND: bool = None

    # defaults
    DEFAULT = {
        "min_profit": 15,
        "check_trend": False
    }

    def __init__(self, params: dict):
        try:
            if params["default"] == True:
                self.MIN_PROFIT = self.DEFAULT["min_profit"]
                self.CHECK_TREND = self.DEFAULT["check_trend"]
            else:
                self.MIN_PROFIT = params["min_profit"]
                self.CHECK_TREND = params["check_trend"]
        except:
            raise KickbaseException()

    def predict(self, player_op: [dict] = []) -> [dict]:
        #list of recommended players to sell
        players_to_sell = []

        #list of evaluated players
        evaluated_players = []
        
        #compute a score for each player (higher score = higher urge to sell the player)
        for player in player_op:
            evaluation = self.evaluatePlayer(player)
            profit = int(player['market_val']) - int(player['market_val_purchased'])
            profit_perc = ((float(player['market_val'] / player['market_val_purchased']))-1) * 100
            
            # specify stats to pass through
            evaluatedPlayer = (player['first_name'], player['last_name'], player['id_player'], profit, profit_perc, evaluation)
            
            if evaluation >= 0:
                evaluated_players.append(evaluatedPlayer)
            else:
                print("player not worth selling due to eval score " + str(evaluation))

        if len(evaluated_players) == 0:
            return []

        # sort list by highest evaluation and choose top n player
        evaluated_players.sort(key=operator.itemgetter(5))
        evaluated_players.reverse()

        for i in range(0,self.TOP_PLAYER):
            if i < len(evaluated_players):
                p = evaluated_players[i]
                predicted = {
                    'first_name': p[0],
                    'last_name': p[1],
                    'player_id': p[2],
                    'profit': p[3],
                    'profit_percentage': p[4],
                    'eval': p[5]
                }
                players_to_sell.append(predicted)

        return players_to_sell

    def evaluatePlayer(self, player) -> int:
        score = 0

        #check trend
        if player['market_value_trend'] == 'UP':
        	score -= 10
        elif player['market_value_trend'] == 'DOWN':
            score += 10

        #check profit
        profit_perc = ((float(player['market_val'] / player['market_val_purchased']))-1)
        if float((profit_perc*100)) < float(self.MIN_PROFIT):
            return -1

        #add to score
        #at the current state: just adds the percentage of market value decrease to the score
        score += int(100 * profit_perc)
        return score
