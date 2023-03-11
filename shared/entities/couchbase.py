class CouchbaseParams:
    def __init__(self,  username="username", password="password"):
        self.username = username
        self.password = password


    def __str__(self):
        return f"CouchbaseParams(username={self.username}, password={self.password})"
