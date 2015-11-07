import logging
log = logging.getLogger(__name__)

import urlparse

class Interest(object):
    __slots__ = ['data']

    def __init__(self, data):
        self.data = data

    @property
    def name(self):
        return self.data['name']

    @name.setter
    def set_name(self, name):
        self.data['name'] = name

    @property
    def facebook_id(self):
        return self.data['facebook_id']

    @facebook_id.setter
    def set_facebook_id(self, facebook_id):
        self.data['facebook_id'] = facebook_id

    def __repr__(self):
        return "<Interest '{}' facebook_id = {}>".format(self.name, self.facebook_id)

    def __str__(self):
        return self.name


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

    @property
    def interests(self):
        return map(Interest, self.data['interests'])

    @interests.setter
    def set_interests(self, interests):
        self.data['interests'] = map(lambda i: i.data, interests)

    @property
    def id(self):
        return self.data['_id']

    @id.setter
    def set_id(self, id):
        self.data['id'] = id

    def __str__(self):
        return "{} ({})".format(self.name, self.username)

    def __repr__(self):
        return "User<{}, name = '{}', facebook_id = {}, interests = {}>"\
            .format(self.username, self.name, self.facebook_id, self.interests)

    def __json__(self, request):
        return {
            'name': self.name,
            'username': self.username,
            'facebook_id': self.facebook_id,
            'interests': self.data['interests']
        }

class DataStore(object):
    __slots__ = ['db']

    def __init__(self, db):
        self.db = db
        log.info("Initializing with {}".format(db))

    def create_indices(self):
        self.db.user.create_index("username", unique=True)

    def users(self):
        for user in self.db.user.find():
            yield User(user)

    def get_user(self, username):
        data = self.db.user.find_one({"username": username})
        if data is not None:
            return User(data)
        else:
            return None

    # Shouldn't be used for updates if possible  - use Mongo's actual update API
    def insert_user(self, user):
        return self.db.user.insert_one(user.data).inserted_id

    def others_with_interest(self, user, interest):
        for user in self.db.user.find({"_id": {"$ne": user.id}, "interests": {"$in": [interest.data]}}):
            yield User(user)

    def add_interests(self, username, interests):
        self.db.user.update_one({"username": username}, {"$push": {"interests": {"$each": interests}}})

    def common_interests(self, limit):
        pipeline = [
            {"$unwind": "$interests"},
            {"$group": {"_id": "$interests.name", "facebook_id": {"$first": "$interests.facebook_id"}, "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]
        return list(self.db.user.aggregate(pipeline))