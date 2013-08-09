"""
Delete any of the authenticated users albums that doesn't contain an image.
"""

import pyimgur

from authentication import client_id, client_secret, refresh_token

im = pyimgur.Imgur(client_id=client_id, client_secret=client_secret,
                   refresh_token=refresh_token)

im.refresh_access_token()
user = im.get_user('me')
for album in user.get_albums():
    if not len(album.images):
        print("Deleting album {}".format(album.id))
        album.delete()
