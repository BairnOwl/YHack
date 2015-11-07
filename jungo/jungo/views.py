import logging
log = logging.getLogger(__name__)

from pyramid.view import view_config


# @view_config(route_name='home', renderer='templates/mytemplate.pt')
@view_config(route_name='home', renderer='templates/fb_login.pt')
def my_view(request):
    log.debug('Hello, World!')
    users = list(request.db['user'].find())
    log.debug('Users: %s' % users)
    return {'project': 'jungo'}