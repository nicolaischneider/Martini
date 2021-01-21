from kickbase_api.kickbase import Kickbase
from kickbase_api.models.player import Player
import operator

class PredictSell:

    TOP_PLAYER = 3
    EVAL_THRESHOLD = 20

    def predict(self, player_op: [dict] = []) -> [dict]:
        #player_op: all players that the user currently owns are in player_op
        
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
            
            if evaluation > self.EVAL_THRESHOLD:
                evaluated_players.append(evaluatedPlayer)
            else:
                print("player not worth selling due to eval score " + str(evaluation))

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

        if profit_perc < 0:
            return -1

        #normalize
        #profit_norm = profit / int(player['market_val_purchased'])

        #add to score
        #at the current state: just adds the percentage of market value decrease to the score
        score += int(100 * profit_perc)

        return score
