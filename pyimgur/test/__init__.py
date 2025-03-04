from requests import HTTPError

try:
    from authentication import client_id, client_secret, refresh_token
except ImportError:
    client_id = None
    client_secret = None
    refresh_token = None

import pyimgur

im = pyimgur.Imgur(
    client_id=client_id, client_secret=client_secret, refresh_token=refresh_token
)
user = None

if refresh_token:
    try:
        im.refresh_access_token()
        user = im.get_user("me")
    except HTTPError:
        # By passing this error, User will remain None and therefore
        # it will be set that the user is not authenticated and the
        # tests will skip without errors.
        pass

USER_NOT_AUTHENTICATED = refresh_token is None or user is None
