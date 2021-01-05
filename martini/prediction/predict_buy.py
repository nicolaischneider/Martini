from kickbase_api.kickbase import Kickbase
from kickbase_api.models.player import Player
from kickbase_api.models.player_stats import PlayerStats
import operator

class PredictBuy:

    TOP_PLAYER = 3
    LAST_GAMES = 3

    # PENALTIES/EXTRA SCORE
    POINT_PENALTY = 0.2
    PLAY_TIME_PENALTY = 0.1

    # vars
    MAX_PLAY_TIME = 5400

    # INPUT
    ''' #for optional_player in player_tm:
    optional_player = {
        'player': id,               # str
        'value': p_highest_offer,   # int
        'stats': player_stats       # Player_Stats
    }
    '''

    def predict(self, player_tm: [dict] = []) -> [dict]:
        top_player: [dict] = []

        # case: no playwr in trade market
        if len(player_tm) == 0:
            return []

        # get list of evaluated player
        evaluatedPlayerArray = []
        for player in player_tm:
            evaluation = self.evaluatePlayer(player['stats'])
            evaluatedPlayer = (player['first_name'], player['last_name'], player['player_id'], player['value'], evaluation)
            if evaluation > 0:
                evaluatedPlayerArray.append(evaluatedPlayer)

        # sort list by highest evaluation and choose top n player
        evaluatedPlayerArray.sort(key=operator.itemgetter(4))
        evaluatedPlayerArray.reverse()
        for i in range(0,self.TOP_PLAYER):
            if i < len(evaluatedPlayerArray):
                p = evaluatedPlayerArray[i]
                predicted = {
                    'first_name': p[0],
                    'last_name': p[1],
                    'player_id': p[2],
                    'price': p[3],
                    'eval': p[4]
                }
                top_player.append(predicted)

        #print(top_player)

        return top_player

    def evaluatePlayer(self, stats: PlayerStats) -> int:
        score = 0

        # get stats of last n games
        relevant_stats = []
        current_season_stats: [dict] = []
        current_season = self.getCurrentSeason()
        for season in stats.stats:
            if current_season in season:
                current_season_stats = season[current_season]
                current_season_stats.reverse()
                break
        
        if len(current_season_stats) == 0:
            print("no data for current season")
            return -1

        for i in range(0,self.LAST_GAMES):
            if i < len(current_season_stats):
                relevant_stats.append(current_season_stats[i])
        relevant_stats.reverse()
        
        # compute score points
        num_neg_pts = 0
        for stats_day in relevant_stats:
            if stats_day['points'] < 0:
                num_neg_pts += 1

            score += stats_day['points']

        score = int(score * (1-(num_neg_pts * self.POINT_PENALTY)))

        # compute playtime points
        last_play_time = -1
        for stats_day in relevant_stats:
            # fill play time
            if stats_day['play_time'] == self.MAX_PLAY_TIME:
                last_play_time = stats_day['play_time']
                score = int(score * (1+self.PLAY_TIME_PENALTY))
                continue

            # no play time
            if stats_day['play_time'] == 0:
                last_play_time = stats_day['play_time']
                score = int(score * (1-self.PLAY_TIME_PENALTY))
                continue

            # first day
            if last_play_time == -1:
                last_play_time = stats_day['play_time']
                continue

            # compare to last play time
            new_penalty_reward = (stats_day['play_time'] / self.MAX_PLAY_TIME) * self.PLAY_TIME_PENALTY
            if last_play_time > stats_day['play_time']:
                score = int(score * (1-new_penalty_reward))
            else:
                score = int(score * (1+new_penalty_reward))
            
            last_play_time = stats_day['play_time']

        return score

    def getCurrentSeason(self) -> str:
        return '2021'

    def getCurrentMatchday(self) -> int:
        return 14