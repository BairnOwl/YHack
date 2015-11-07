import logging
log = logging.getLogger(__name__)

from pyramid.view import view_config

from .model import User

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

#######
# API #
#######

@view_config(route_name='api_add_user', renderer='json')
def api_add_user(request):
    if isinstance(request.json_body, dict):
        if 'name' in request.json_body:
            name = request.json_body['name']
        else:
            request.response.status_code = 400
            return {'error': 'Missing name'}

        if 'username' in request.json_body:
            username = request.json_body['username']
        else:
            request.response.status_code = 400
            return {'error': 'Missing username'}

        if 'facebook_id' in request.json_body:
            facebook_id = request.json_body['facebook_id']
        else:
            request.response.status_code = 400
            return {'error': 'Missing facebook_id'}

        interests = []
        if 'interests' in request.json_body:
            if isinstance(request.json_body['interests'], list):
                for interest in request.json_body['interests']:
                    if 'name' not in interest:
                        request.response.status_code = 400
                        return {'error': 'Missing name of interest'}
                    if 'facebook_id' not in interest:
                        request.response.status_code = 400
                        return {'error': 'Missing facebook_id of interest'}
                    interests.append({'name': interest['name'], 'facebook_id': interest['facebook_id']})
            else:
                request.response.status_code = 400
                return {'error': 'interests must be an array'}

        user = User({
            'name': name,
            'username': username,
            'facebook_id': facebook_id,
            'interests': interests
        })
        request.db.insert_user(user)
        request.response.status_code = 201
        request.response.location = request.route_url('api_user', username=username)
        return user

@view_config(route_name='api_user', renderer='json')
def api_user(request):
    username = request.matchdict['username']
    user = request.db.get_user(username)
    if user is not None:
        return user
    else:
        request.response.status_code = 404
        return {'error': 'Unknown user "{}"'.format(username)}

@view_config(route_name='api_add_interests', renderer='json')
def api_add_interests(request):
    username = request.matchdict['username']
    if isinstance(request.json_body, list):
        for interest in request.json_body:
            if 'name' not in interest or 'facebook_id' not in interest:
                request.response.status_code = 400
                return {'error': 'Must specify name and facebook_id'}
        request.db.add_interests(username, request.json_body)
        request.response.location = request.route_url('api_user', username=username)
        return {'username': username, 'added_interests': request.json_body}
    else:
        request.response.status_code = 400
        return {'error': 'Expected array of interests'}

@view_config(route_name='api_common_interests', renderer='json')
def api_common_interests(request):
    if 'limit' in request.GET:
        limit = int(request.GET['limit'])
    else:
        limit = 5
    return {'interests': request.db.common_interests(limit)}