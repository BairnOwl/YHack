ADMINS = ['bnavetta']

def groupfinder(userid, request):
    if userid in ADMINS:
        return ['group:admins']
    user = request.db.get_user(userid)
    if user:
        return []
    else:
        return None