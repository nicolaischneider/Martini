# import torch etc

class PredictBuyML:

    model = None

    def __init__(self):
        # load ml model using path to model file
        self.model = 1 # change

    def predict(self, player_tm: [dict] = []) -> [dict]:
        if len(player_tm) == 0:
            return []

        # for each player
        #   predict if player is expected tto have an increased market value

        # Return a list of players that are predicted to increase in market value
        '''
        [
            {
                'first_name': p[0],
                'last_name': p[1],
                'player_id': p[2],
                'price': p[3]
            },
            ...
        ]
        '''
        return []