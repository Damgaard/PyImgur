"""
Delete any of the authenticated users albums that doesn't contain an image.
"""

from pyimgur import Imgur


def delete_empty_albums(client_id, client_secret, refresh_token):
    im = Imgur(
        client_id=client_id, client_secret=client_secret, refresh_token=refresh_token
    )

    user = im.get_user("me")
    for album in user.get_albums():
        if not len(album.images):
            print("Deleting album {}".format(album.id))
            album.delete()


if __name__ == "__main__":
    client_id = input("What is the client_id? ")
    client_secret = input("What is the client_secret? ")
    refresh_token = input("What is the refresh_token? ")
    delete_empty_albums(client_id, client_secret, refresh_token)
