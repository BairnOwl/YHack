from pyramid.config import Configurator

import pymongo

import urlparse

from .model import DataStore

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')
    config.include('pyramid_chameleon')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('fb', '/fb')
    config.add_route('interest_match', '/interest-match/{username}/{interest_id}')

    config.add_route('api_add_user', '/api/user', request_method='POST')
    config.add_route('api_user', '/api/user/{username}', request_method='GET')

    db_url = settings['mongo_uri']

    config.registry.client = pymongo.MongoClient(db_url)

    def add_db(request):
        uri = urlparse.urlparse(db_url)
        db = config.registry.client[uri.path[1:]]
        if uri.username and uri.password:
            db.authenticate(uri.username, uri.password)
        return DataStore(db)

    config.add_request_method(add_db, 'db', reify=True)

    config.scan()

    return config.make_wsgi_app()
