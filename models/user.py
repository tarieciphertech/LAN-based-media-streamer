
class User:
    def __init__(self, row):
        self.id = row["id"]
        self.username = row["username"]
        self.role = row["role"]

    def can_upload(self):
        return self.role == "admin"


class KidsUser(User):
    def can_upload(self):
        return False
