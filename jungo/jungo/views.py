import logging
log = logging.getLogger(__name__)

from pyramid.view import view_config

@view_config(route_name='home', renderer='templates/mytemplate.pt')
def my_view(request):
    log.debug('Hello, World!')
    return {'project': 'jungo', 'users': request.db.users()}

@view_config(route_name='fb', renderer='templates/fb_login.pt')
def fb_view(request):
    return dict()