"""
User Analysis Example

This script demonstrates how to use PyImgur to fetch and display information about an Imgur user.
It requires a client_id and username to be provided as command-line arguments.

Usage:
    python user_analysis.py --client_id YOUR_CLIENT_ID --username USERNAME
"""

import argparse
import pprint
from pyimgur import Imgur
from datetime import datetime


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Fetch and display information about an Imgur user"
    )
    parser.add_argument("--client_id", required=True, help="Your Imgur API client ID")
    parser.add_argument(
        "--username", required=True, help="The Imgur username to analyze"
    )
    args = parser.parse_args()

    # Initialize the Imgur client
    imgur = Imgur(client_id=args.client_id)
    user = imgur.get_user(args.username)

    # Print general user information
    print("\n=== User Information ===")
    user_info = {
        "Username": user.name,
        "Bio": user.bio,
        "Reputation": user.reputation,
        "Reputation Name": user.reputation_name,
        "Created": f"{datetime.fromtimestamp(user.created).strftime('%B %d, %Y')}",
        "Pro Expiration": user.pro_expiration,
        "Is Blocked": user.is_blocked,
    }
    pprint.pprint(user_info)

    # Get and print the last 10 post
    print("\n=== Last 10 Posts ===")
    posts = user.get_submissions(limit=10)
    if posts:
        for i, post in enumerate(posts, 1):
            print(f"{i}. {post.title[:100]}{'...' if len(post.title) > 100 else ''}")
    else:
        print("No posts found.")

    # Get and print the last 10 comments
    print("\n=== Last 10 Comments ===")
    comments = user.get_comments()
    if comments:
        for i, comment in enumerate(comments[:10], 1):
            print(
                f"{i}. {comment.text[:100]}{'...' if len(comment.text) > 100 else ''}"
            )
    else:
        print("No comments found.")

    gallery_favorites = user.get_gallery_favorites(sort="newest", limit=10)
    print("\n=== Last 10 Gallery Favorites ===")
    for i, gallery_favorite in enumerate(gallery_favorites, 1):
        print(f"{i}. {gallery_favorite.title}")


if __name__ == "__main__":
    main()
