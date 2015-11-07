import logging
log = logging.getLogger(__name__)

from pyramid.security import Allow, Authenticated, ALL_PERMISSIONS

class RootFactory(object):

    __name__ = 'RootFactory'

    __acl__ = [(Allow, Authenticated, 'view'),
               (Allow, 'group:admins', ALL_PERMISSIONS)]
    def __init__(self, request):
        pass

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
    __slots__ = ['data', '__name__']

    __parent__ = None

    def __init__(self, data):
        self.data = data
        if 'username' in data:
            self.__name__ = self.username

    def __acl__(self):
        return [
            (Allow, Authenticated, 'view'),
            (Allow, self.username, 'match'),
            (Allow, self.username, 'edit'),
            (Allow, 'group:admins', ALL_PERMISSIONS),
        ]

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
        self.__name__ = username

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

    def others_with_interest(self, username, interest):
        for user in self.db.user.find({"username": {"$ne": username}, "interests": {"$elemMatch": {"facebook_id": interest}}}):
            yield User(user)

    def add_interests(self, username, interests):
        self.db.user.update_one({"username": username}, {"$push": {"interests": {"$each": interests}}})

    def common_interests(self, limit):
        pipeline = [
            {"$unwind": "$interests"},
            {"$group": {"_id": "$interests.name", "facebook_id": {"$first": "$interests.facebook_id"}, "count": {"$sum": 1}}},
            {"$project": {"_id": 0, "name": "$_id", "facebook_id": 1, "count": 1}},
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]
        return list(self.db.user.aggregate(pipeline))