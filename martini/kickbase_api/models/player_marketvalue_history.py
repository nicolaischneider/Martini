from datetime import datetime

class PlayerMarketValueHistory():
    marketvalues = []

    def __init__(self, d: dict = {}):
        marketValueArr = d['marketValues']
        for val in marketValueArr:
            date_format = "%Y-%m-%dT%H:%M:%SZ"
            date = datetime.strptime(val['d'], date_format)
            marketVal = {
                "day": date,
                "value": val['m']
            }
            self.marketvalues.append(marketVal)