class PlayerFeed():
    date: str = None
    feed_type: int = None
    source: int = None
    meta: {} = None

    def __init__(self, d: dict = {}):
        self.date = ""
        self.feed_type = 0
        self.source = 0
        self.meta = {}
        # news can be accessed from meta

# TO BE DONE