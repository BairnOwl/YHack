from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.session import SignedCookieSessionFactory

import pymongo

import logging.config
import urlparse

from .model import DataStore
from .security import groupfinder

session_factory = SignedCookieSessionFactory('cookie secret - changeme')

def main(global_config, **settings):
    logging.config.fileConfig(settings['logging.config'], disable_existing_loggers=False)
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings, root_factory='jungo.model.RootFactory')
    config.include('pyramid_chameleon')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/old-home')
    config.add_route('search', '/')
    config.add_route('common_interests', '/common-interests')
    config.add_route('profile', '/me')

    config.add_route('login', '/login')
    config.add_route('logout', '/logout')

    config.add_route('interest_match', '/interest-match/{username}/{interest_id}')
    config.add_route('api_add_user', '/api/user', request_method='POST')
    config.add_route('api_user', '/api/user/{username}', request_method='GET')
    config.add_route('api_add_interests', '/api/user/{username}/interests', request_method='POST')
    config.add_route('api_common_interests', '/api/common-interests', request_method='GET')

    authn_policy = AuthTktAuthenticationPolicy('super secret magic', callback=groupfinder, hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

    config.set_session_factory(session_factory)

    db_url = settings['mongo_uri']

    config.registry.client = pymongo.MongoClient(db_url)

    def add_db(request):
        uri = urlparse.urlparse(db_url)
        db = config.registry.client[uri.path[1:]]
        if uri.username and uri.password:
            db.authenticate(uri.username, uri.password)
        return DataStore(db)

    add_db(None).create_indices()

    config.add_request_method(add_db, 'db', reify=True)

    config.scan()

    return config.make_wsgi_app()

'''
POST /api/user
{
    name: ...
    username: ...
    facebook_id = ...
    interests = [
        {name: ..., facebook_id: ...},
        {name: ..., facebook_id: ...},
        ...
    ]
}

$('#display').append('<div class="item">' + '<p>' + name + '</p>' + '<p>' + about + '</p>' + '<p>' + description + '</p>' + '</div>');

    '<button id="fb-add-' + interest_id + '"></button>'
    $("#fb-add-" + interest_id).click(function() {
    // do something with interest_id
    })
});
'''