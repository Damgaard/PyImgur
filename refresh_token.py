"""Helper function to get refresh tokens

These are needed both in the general testing library and for
general development of library.

"""

from pathlib import Path

import pyimgur


def get_refresh_token():
    """Get and set refresh token for authentication with Imgur"""
    im = pyimgur.Imgur(
        client_id, client_secret  # pylint: disable=used-before-assignment)
    )
    auth_url = im.authorization_url("pin")

    print("Go to the following url to authenticate with your app")
    print(auth_url)

    pin = input("What is the pin? ")
    access_token, refresh_token = im.exchange_pin(pin)

    print("You have succesfully authenticated")
    print(f"Refresh Token: {refresh_token}")
    print(f"Access Token: {access_token}")

    with open("authentication.py", "wb") as outfile:
        outfile.write(f'client_id = "{client_id}"\n')
        outfile.write(f'client_secret = "{client_secret}"\n')
        outfile.write(f'refresh_token = "{refresh_token}"\n')

    print()
    print("Authentication.py file has been created with credentials.")
    print("It is needed for test suite and for development.")


if __name__ == "__main__":
    if not Path("authentication.py").exists():
        print("ERROR: Cannot get refresh token without knowing client_id and secret")
        print("Create a file called authentication.py and set client_id and")
        print("client_secret in it.")

    else:
        from authentication import (  # pylint: disable=import-error
            client_id,
            client_secret,
        )

        get_refresh_token()
