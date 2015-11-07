from pyramid.config import Configurator

from gridfs import GridFS
import pymongo

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')
    config.include('pyramid_chameleon')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')

    db_url = settings['mongo_uri']
    db_name = settings['mongo_db']
    config.registry.client = pymongo.MongoClient(db_url)
    config.registry.db = config.registry.client[db_name]

    def add_db(request):
        db = config.registry.db[db_url.path[1:]]
        if db_url.username and db_url.password:
            db.authenticate(db_url.username, db_url.password)
        return db

    def add_fs(request):
        return GridFS(request.db)

    config.add_request_method(add_db, 'db', reify=True)
    config.add_request_method(add_fs, 'gridfs', reify=True)

    config.scan()
    return config.make_wsgi_app()
