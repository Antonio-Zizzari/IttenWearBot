
class UserProfile:

    def __init__(self, id: str,name: str, wishlist: list = None):
        self.id = id
        self.name = name
        self.wishlist = [] if wishlist is None else wishlist