from kickbase_api.kickbase import Kickbase
from kickbase_api.models.player import Player
from kickbase_api.exceptions import KickbaseException
from prediction.predict_buy import PredictBuy
import operator
from enum import IntEnum

# analysis
class AnalysisSell(IntEnum):
    SELL = 1
    MAYBE = 2
    HOLD = 3
    NO_DATA = -1

class PredictSell:

    # params
    MIN_PROFIT: int = None

    # defaults
    DEFAULT = {
        "min_profit": 15,
    }

    def __init__(self, params: dict):
        try:
            if params["default"] == True:
                self.MIN_PROFIT = self.DEFAULT["min_profit"]
            else:
                self.MIN_PROFIT = params["min_profit"]
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
            
            if 'stats' in player:
                stats = player['stats']
            else:
                stats = None

            # specify stats to pass through
            evaluatedPlayer = (player['first_name'], player['last_name'], player['id_player'], profit, profit_perc, evaluation, player['market_val'], stats)
            
            if evaluation >= 0:
                evaluated_players.append(evaluatedPlayer)
            else:
                print("player not worth selling due to eval score " + str(evaluation))

        if len(evaluated_players) == 0:
            return []

        # sort list by highest evaluation and choose top n player
        evaluated_players.sort(key=operator.itemgetter(5))
        evaluated_players.reverse()

        for i in range(0, len(evaluated_players)):
            p = evaluated_players[i]
            predicted = {
                'first_name': p[0],
                'last_name': p[1],
                'player_id': p[2],
                'profit': p[3],
                'profit_percentage': p[4],
                'eval': p[5],
                'value': p[6],
                'stats': p[7]
            }
            players_to_sell.append(predicted)

        analyzed_player = self.analyze_player(players_to_sell)

        return analyzed_player

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

    def analyze_player(self, player) -> [dict]:
        # predict parameter
        params = {
            "type": "LOGIC_BUY",
            "default": True,
            "complex_eval": False,
            "considered_days": 3
        }

        # analyze player
        evaluator = PredictBuy(params, True)
        player_with_stats = []
        for p in player:
            if p['stats'] is not None:
                player_with_stats.append(p)
        analyzed_player = evaluator.predict(player_with_stats)

        # add analysis to player
        players = []
        for p in player:
            # get analysis
            analysis = AnalysisSell.NO_DATA
            for ap in analyzed_player:
                if p['player_id'] == ap['player_id']:
                    eval_score = ap['eval']
                    analysis = self.analyze_score(eval_score)

            predicted_player = {
                'first_name': p['first_name'],
                'last_name': p['last_name'],
                'player_id': p['player_id'],
                'profit': p['profit'],
                'profit_percentage': p['profit_percentage'],
                'eval': p['eval'],
                'analysis': analysis,
            }
            players.append(predicted_player)
        
        return players

    def analyze_score(self, score: int) -> AnalysisSell:
        if score < 100:
            return AnalysisSell.SELL
        elif score < 200:
            return AnalysisSell.MAYBE
        elif score >= 200:
            return AnalysisSell.HOLD
        
        return AnalysisSell.NO_DATA

