"""
User Analysis Example

This script demonstrates how to use PyImgur to fetch and display information about an Imgur user.
It requires a client_id and username to be provided as command-line arguments.

Usage:
    python user_analysis.py --client-id YOUR_CLIENT_ID --username USERNAME
"""

import argparse
from datetime import datetime
import pprint

from pyimgur import Imgur


def print_general_information(user):
    """Print general meta information, like username or reputation."""

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


def print_last_few_posts(user, amount=10):
    """Print the last few posts of the user."""
    print(f"\n=== Last {amount} Posts ===")
    posts = user.get_submissions(limit=amount)
    if posts:
        for i, post in enumerate(posts, 1):
            print(f"{i}. {post.title[:100]}{'...' if len(post.title) > 100 else ''}")
    else:
        print("No posts found.")


def print_last_few_comments(user, amount=10):
    """Print the last few comments of the user."""
    print(f"\n=== Last {amount} Comments ===")
    comments = user.get_comments()
    if comments:
        for i, comment in enumerate(comments[:amount], 1):
            print(
                f"{i}. {comment.text[:100]}{'...' if len(comment.text) > 100 else ''}"
            )
    else:
        print("No comments found.")


def print_last_few_gallery_favorites(user, amount=10):
    """Print the last few gallery favorites of the user."""
    print(f"\n=== Last {amount} Gallery Favorites ===")
    gallery_favorites = user.get_gallery_favorites(sort="newest", limit=amount)
    for i, gallery_favorite in enumerate(gallery_favorites, 1):
        print(f"{i}. {gallery_favorite.title}")


def print_user_analysis(client_id, username):
    """Print all analysis about the user."""
    imgur = Imgur(client_id=client_id)
    user = imgur.get_user(username)

    print_general_information(user)
    print_last_few_posts(user)
    print_last_few_comments(user)
    print_last_few_gallery_favorites(user)


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Fetch and display information about an Imgur user"
    )
    parser.add_argument("--client-id", required=True, help="Your Imgur API client ID")
    parser.add_argument(
        "--username", required=True, help="The Imgur username to analyze"
    )
    args = parser.parse_args()
    print_user_analysis(args.client_id, args.username)
