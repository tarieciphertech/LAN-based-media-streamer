class WatchHistory:
    def __init__(self, row):
        self.media_id = row["media_id"]
        self.progress = row["progress"]

    def percent(self):
        return self.progress
