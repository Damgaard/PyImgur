"""
Delete any of the authenticated users albums that doesn't contain at least one image.

Usage:
    python delete_empty_albums.py --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET --refresh-token YOUR_REFRESH_TOKEN
"""

import argparse

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
    parser = argparse.ArgumentParser(
        description="Delete all of the authenticated user's albums that doesn't contain at least one image"
    )
    parser.add_argument("--client-id", required=True, help="Imgur client ID")
    parser.add_argument("--client-secret", required=True, help="Imgur client secret")
    parser.add_argument("--refresh-token", required=True, help="Imgur refresh token")
    args = parser.parse_args()

    delete_empty_albums(args.client_id, args.client_secret, args.refresh_token)
