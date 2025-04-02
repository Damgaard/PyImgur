"""Set your windows Desktop background to a beautiful image

Utilizes PYimgur to find a random image from a number of subreddits, dedicated to beautiful
inspirering images. Known as the SFW ( safe for work ) Porn network.

Run the script with the client ID from Imgur.

  python set_background.py --client-id YOUR_CLIENT_ID

Client_secret and refresh_token are not required for this script.

"""

import ctypes
import os
from pathlib import Path
import random
import argparse

from pyimgur import Imgur


def set_wallpaper(image_path):
    """
    Set the Windows desktop background to the specified image.

    Args:
        image_path (str): Path to the image file
    """
    # Convert path to absolute path
    image_path = str(Path(image_path).absolute())

    # Check if file exists
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")

    # Windows API constants
    SPI_SETDESKWALLPAPER = 0x0014  # pylint: disable=invalid-name
    SPIF_UPDATEINIFILE = 0x01  # pylint: disable=invalid-name
    SPIF_SENDCHANGE = 0x02  # pylint: disable=invalid-name

    # Load the image path into a ctypes string
    image_path = ctypes.create_unicode_buffer(image_path)

    # Call the Windows API function
    result = ctypes.windll.user32.SystemParametersInfoW(
        SPI_SETDESKWALLPAPER, 0, image_path, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
    )

    if not result:
        raise ctypes.WinError()


def get_random_image(subreddit):
    """Pick a random image from the subreddit, which would look good as a wallpaper"""
    images = IM.get_subreddit_gallery(subreddit, limit=10)

    attemps = 0
    while attemps < 10:
        image = random.choice(images)

        if not any((image.is_ad, image.is_nsfw, image.is_animated)):
            break

        attemps += 1

    return image


IM = None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--client-id", required=True, help="Imgur client ID")
    args = parser.parse_args()

    IM = Imgur(args.client_id)

    possible_subreddits = [
        "earthporn",
        "spaceporn",
        "MegalithPorn",
        "FuturePorn",
        "ViewPorn",
    ]
    random_subreddit = random.choice(possible_subreddits)
    chosen_image = get_random_image(random_subreddit)
    downloaded_image_name = chosen_image.download()

    set_wallpaper(downloaded_image_name)
