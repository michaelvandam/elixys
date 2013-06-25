
from functools import wraps
from flask import request, Response
import logging

log = logging.getLogger("elixys.web")

def check_auth(username, password):
    """
    Function checks is username and password is valid
    """
    return username == 'devel' and password == 'devel'

def authenticate():
    """
    Sends a 401 response that enables basic auth
    """
    log.info("Authenticate")
    return Response(
            'Could not verify your access level for elixys\n'
            'You must have proper credentials', 401,
            {'WWW-Authenticate':'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            log.debug("Requires auth")
            return authenticate()
        log.debug("username:%s" % auth.username)
        return f(*args, **kwargs)
    return decorated

