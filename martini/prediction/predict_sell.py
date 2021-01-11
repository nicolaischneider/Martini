from kickbase_api.kickbase import Kickbase
from kickbase_api.models.player import Player
import operator

class PredictSell:

    EVAL_THRESHOLD = 1

    def predict(self, player_op: [dict] = []) -> [dict]:
        #player_op: all players that the user currently owns are in player_op
        
        #list of recommended players to sell
        players_to_sell = []

        #list of evaluated players
        evaluated_players = []
        
        #compute a score for each player (higher score = higher urge to sell the player)
        for player in player_op:
            #evaluation = self.evaluatePlayer(player['stats'])
            evaluation = self.evaluatePlayer(player)
            #market_val = player['market_val']

            profit = int(player['market_val']) - int(player['market_val_purchased'])
            #specify stats to pass through
            evaluatedPlayer = (player['market_value_trend'], player['first_name'], player['last_name'], player['id_player'], player['market_val_purchased'], player['market_val'], profit, evaluation)
            
            if evaluation > 10:
                evaluated_players.append(evaluatedPlayer)

        #use tresholds to decide which players should be recommended for sell
        for player in evaluated_players:
            if evaluation > self.EVAL_THRESHOLD:
                players_to_sell.append(player)

        
        return evaluated_players
        #return []


    def evaluatePlayer(self, player) -> int:
        score = 0

        #check trend
        if player['market_value_trend'] == 'DOWN':
        	score += 10

        #check profit
        profit = int(player['market_val']) - int(player['market_val_purchased'])

        #normalize
        profit_norm = profit / int(player['market_val_purchased'])

        #add to score
        #at the current state: just adds the percentage of market value decrease to the score
        score -= 100 * profit_norm

        return score
