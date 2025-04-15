import os

from requests import HTTPError

from pyimgur import Gallery_album, Gallery_image, Imgur, User
from tests.data import (
    MOCKED_GALLERY_ALBUM_DATA,
    MOCKED_GALLERY_IMAGE_DATA,
    MOCKED_USER_DATA,
)

try:
    from authentication import client_id, client_secret, refresh_token
except ImportError:
    client_id = None
    client_secret = None
    refresh_token = None

import pyimgur

IMAGE_IDS = ["4UoRzGc", "wHxiibZ", "w5pB7vT"]

im = pyimgur.Imgur(
    client_id=client_id, client_secret=client_secret, refresh_token=refresh_token
)
unauthed_im = pyimgur.Imgur(client_id=client_id, client_secret=client_secret)
user = None  # pylint: disable=invalid-name

FAST_TESTS = os.getenv("FAST_TESTS") == "TRUE"

if refresh_token and not FAST_TESTS:
    try:
        im.refresh_access_token()
        user = im.get_user("me")
    except HTTPError:
        # By passing this error, User will remain None and therefore
        # it will be set that the user is not authenticated and the
        # tests will skip without errors.
        pass

USER_NOT_AUTHENTICATED = refresh_token is None or user is None
MOCKED_UNAUTHED_IMGUR = Imgur("fake_client_id")
MOCKED_AUTHED_IMGUR = Imgur(
    "fake_client_id",
    "fake_client_secret",
    refresh_token="fake refresh token",
    access_token="fake access token",
)
MOCKED_USER = User(MOCKED_USER_DATA, MOCKED_AUTHED_IMGUR)
MOCKED_GALLERY_IMAGE = Gallery_image(MOCKED_GALLERY_IMAGE_DATA, MOCKED_AUTHED_IMGUR)
MOCKED_GALLERY_ALBUM = Gallery_album(MOCKED_GALLERY_ALBUM_DATA, MOCKED_AUTHED_IMGUR)
