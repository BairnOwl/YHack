import logging

log = logging.getLogger(__name__)

class User(object):
    __slots__ = ['data']

    def __init__(self, data):
        self.data = data

    @property
    def facebook_id(self):
        return self.data['facebook_id']

    @facebook_id.setter
    def set_facebook_id(self, facebook_id):
        self.data['facebook_id'] = facebook_id

    @property
    def name(self):
        return self.data['name']

    @name.setter
    def set_name(self, name):
        self.data['name'] = name

    @property
    def username(self):
        return self.data['username']

    @username.setter
    def set_username(self, username):
        self.data['username'] = username

    def __str__(self):
        return "User<{}, name = '{}', facebook_id = {}>".format(self.username, self.name, self.facebook_id)

    def __repr__(self):
        return self.__str__()

class DataStore(object):
    __slots__ = ['db']

    def __init__(self, db):
        self.db = db
        log.info("Initializing with DB {}".format(db))

    def users(self):
        for user in self.db.user.find():
            yield User(user)

    # Shouldn't be used for updates if possible  - use Mongo's actual update API
    def insert_user(self, user):
        self.db.user.insert_one(user.data)