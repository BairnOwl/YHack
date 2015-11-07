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


@view_config(route_name='interest_match', renderer='json')
def interest_match_view(request):
    username = request.matchdict['username']
    interest_id = int(request.matchdict['interest_id'])
    user = request.db.get_user(username)
    interest = next(i for i in user.interests if i.facebook_id == interest_id)
    return list(request.db.others_with_interest(user, interest))

