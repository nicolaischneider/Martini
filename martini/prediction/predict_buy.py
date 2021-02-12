from kickbase_api.kickbase import Kickbase
from kickbase_api.models.player import Player
from kickbase_api.models.player_stats import PlayerStats
from kickbase_api.exceptions import KickbaseException
import operator
from enum import IntEnum

# analysis
class AnalysisBuy(IntEnum):
    GOOD = 1
    HIGH = 2
    VERY_HIGH = 3

class PredictBuy:
    # const
    SCORE_TRESH = 150
    POINT_PENALTY = 0.2
    MAX_POINT_PENALTY = 0.8
    PLAY_TIME_PENALTY = 0.1
    MS_INCREASE = 0.05
    GOAL_INCREASE = 0.10
    ASSIST_H_INCREASE = 0.025

    # vars
    MAX_PLAY_TIME = 5400

    # params
    LAST_GAMES: int = None
    COMPLEX_EVAL: bool = None

    # params for sell
    FOR_SELL: bool = False

    # defaults
    DEFAULTS = {
        "last_games": 3
    }

    # INPUT
    ''' #for optional_player in player_tm:
    optional_player = {
        'first_name': player.first_name,    str
        'last_name': player.last_name,      str
        'player_id': player.id,             str
        'value': p_highest_offer,           int
        'stats': player_stats               dict
    }
    '''

    def __init__(self, params: dict, for_sell: bool = False):
        # case: sell evaluation
        if for_sell == True:
            self.LAST_GAMES = self.DEFAULTS["last_games"]
            self.COMPLEX_EVAL = False
            return

        # case: buy evaluation
        try:
            if params["default"] == True:
                self.LAST_GAMES = self.DEFAULTS["last_games"]
            else:
                self.LAST_GAMES = params["considered_days"]
            
            if "complex_eval" in params:
                self.COMPLEX_EVAL = params["complex_eval"]
            else:
                self.COMPLEX_EVAL = False
        except:
            raise KickbaseException()

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
            
            # set threshold
            threshold = self.SCORE_TRESH
            if self.FOR_SELL == True:
                threshold = 0
            
            if evaluation > threshold:
                evaluatedPlayerArray.append(evaluatedPlayer)

        # sort list by highest evaluation and choose top n player
        evaluatedPlayerArray.sort(key=operator.itemgetter(4))
        evaluatedPlayerArray.reverse()
        for i in range(0, len(evaluatedPlayerArray)):
            p = evaluatedPlayerArray[i]
            analysis = self.analyze_score(p[4])
            predicted = {
                'first_name': p[0],
                'last_name': p[1],
                'player_id': p[2],
                'price': p[3],
                'eval': p[4],
                'analysis': analysis
            }
            top_player.append(predicted)

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
        penalty_points = num_neg_pts * self.POINT_PENALTY
        if penalty_points >= self.MAX_POINT_PENALTY:
            penalty_points = self.MAX_POINT_PENALTY
        score = int(score * (1-(penalty_points)))

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

        # case simple mode: return score
        if self.COMPLEX_EVAL == False:
            return score

        # compute extra points
        num_ms_days = 0
        num_goals = 0
        num_assists_h = 0
        for stats_day in relevant_stats:
            if stats_day['ms'] == True:
                num_ms_days += 1
            num_goals += stats_day['g']
            num_assists_h += stats_day['a']
            num_assists_h += stats_day['h']
        
        # compute ms points
        ms_points = num_ms_days * self.MS_INCREASE
        score = int(score * (1+(ms_points)))

        # compute goals points
        goal_points = num_goals * self.GOAL_INCREASE
        score = int(score * (1+(goal_points)))

        # compute assist/h points
        assist_h_points = num_assists_h = self.ASSIST_H_INCREASE
        score = int(score * (1+(assist_h_points)))

        return score

    def getCurrentSeason(self) -> str:
        return '2021'

    def analyze_score(self, score: int) -> AnalysisBuy:
        if self.COMPLEX_EVAL == False:
            if score < 250:
                return AnalysisBuy.GOOD
            elif score < 500:
                return AnalysisBuy.HIGH
            elif score >= 500:
                return AnalysisBuy.VERY_HIGH

        if self.COMPLEX_EVAL == True:
            if score < 350:
                return AnalysisBuy.GOOD
            elif score < 550:
                return AnalysisBuy.HIGH
            elif score >= 550:
                return AnalysisBuy.VERY_HIGH