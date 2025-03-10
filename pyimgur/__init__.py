# This file is part of PyImgur.

# PyImgur is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# PyImgur is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with PyImgur.  If not, see <http://www.gnu.org/licenses/>.

"""
PyImgur - The Simple Way of Using Imgur

PyImgur is a python wrapper of the popular image hosting and sharing website
imgur.com. It makes the process of writing applications that uses Imgur faster,
easier and less frustrating by automatically handling a lot of stuff for you.
For instance you'll only need to use your client_id when you instantiate the
Imgur object and when changing authentication. For the REST API this value
needs to be sent with every request, but PyImgur handles this automatically.

Before using PyImgur, or the Imgur REST API in general, you'll need to register
your application here: https://api.imgur.com/oauth2/addclient

For more information on usage visit https://github.com/Damgaard/PyImgur
"""


from base64 import b64encode
import os.path
import re
import sys

PY3 = sys.version_info.major == 3

if PY3:
    from urllib.parse import urlparse  # pylint: disable=no-name-in-module,import-error
else:
    from urlparse import urlparse

import requests  # NOQA

from pyimgur import request  # NOQA

__version__ = "0.5.3"

MASHAPE_BASE = "https://imgur-apiv3.p.mashape.com"
IMGUR_BASE = "https://api.imgur.com"

AUTHORIZE_URL = "{}/oauth2/authorize?client_id={}&response_type={}&state={}"
EXCHANGE_URL = "{}/oauth2/token"
REFRESH_URL = "{}/oauth2/token"


def _change_object(from_object, to_object):
    from_object.__class__ = to_object.__class__
    from_object.__dict__ = to_object.__dict__
    from_object.__repr__ = to_object.__repr__


def _get_album_or_image(json, imgur):
    """Return a gallery image/album depending on what the json represent."""
    if json["is_album"]:
        return Gallery_album(json, imgur, has_fetched=False)
    return Gallery_image(json, imgur)


class Basic_object(object):
    """Contains basic functionality shared by a lot of PyImgur's classes."""

    def __getattr__(self, attribute):
        if not self._has_fetched:
            self.refresh()
            return getattr(self, attribute)
        raise AttributeError(
            "{0} instance has no attribute '{1}'".format(type(self).__name__, attribute)
        )

    def __init__(self, json_dict, imgur, has_fetched=True):
        self._has_fetched = has_fetched
        self._imgur = imgur
        self._populate(json_dict)

    def __repr__(self):
        return "<{0} {1}>".format(type(self).__name__, self.id)

    @property
    def _delete_or_id_hash(self):
        if self._imgur.access_token:
            return self.id
        else:
            return self.deletehash

    def _populate(self, json_dict):
        for key, value in json_dict.items():
            setattr(self, key, value)
        # TODO: ups will need to be likes, because that's what the webinterface
        # is. But we also have "voted" which is the current users vote on it.
        # Update certain attributes for certain objects, to be link to lazily
        # created objects rather than a string of ID or similar.
        if isinstance(self, Album) or isinstance(self, Image):
            if "favorite" in vars(self):
                self.is_favorited = self.favorite
                del self.favorite
            if "nsfw" in vars(self):
                self.is_nsfw = self.nsfw
                del self.nsfw
        if isinstance(self, Image):
            if "animated" in vars(self):
                self.is_animated = self.animated
                del self.animated
            if "link" in vars(self):
                base, sep, ext = self.link.rpartition(".")
                self.link_small_square = base + "s" + sep + ext
                self.link_big_square = base + "b" + sep + ext
                self.link_small_thumbnail = base + "t" + sep + ext
                self.link_medium_thumbnail = base + "m" + sep + ext
                self.link_large_thumbnail = base + "l" + sep + ext
                self.link_huge_thumbnail = base + "h" + sep + ext
        if isinstance(self, Album):
            if "account_url" in vars(self):
                self.author = User(
                    {"url": self.account_url}, self._imgur, has_fetched=False
                )
                del self.account_url
            if (
                "cover" in vars(self) and self.cover is not None
            ):  # pylint: disable=access-member-before-definition
                self.cover = Image({"id": self.cover}, self._imgur, has_fetched=False)
            # Looks like Imgur has broken backwards compatibility here and it is no
            # longer possible to favourite individual images. Only galleries, which
            # may be single images.
            if "images" in vars(self):
                if self.images is None:
                    self.images = []
                else:
                    self.images = [
                        Image(img, self._imgur, has_fetched=False)
                        for img in self.images
                    ]
            if "images_count" in vars(self):
                del self.images_count
        elif isinstance(self, Comment):
            if "author" in vars(self):
                self.author = User({"url": self.author}, self._imgur, has_fetched=False)
            # Problem with this naming is that children / parent are normal
            # terminology for tree structures such as this. But elsewhere the
            # children are referred to as replies, for instance a comment can
            # be replies to not procreated with. I've decided to use replies
            # and parent_comment as a compromise, where both attributes should
            # be individually obvious but their connection may not.
            if "author_id" in vars(self):
                # author_id is not used for anything, and can also be gotten
                # with comment.author.id which fits with how the id of anything
                # else is gotten. So having it here only complicates the API.
                del self.author_id
            if "children" in vars(self):
                self.replies = [Comment(com, self._imgur) for com in self.children]
                del self.children
            if "comment" in vars(self):
                self.text = self.comment
                del self.comment
            if "deleted" in vars(self):
                self.is_deleted = self.deleted
                del self.deleted
            if "image_id" in vars(self):
                self.permalink = (
                    f"http://imgur.com/gallery/{self.image_id}/comment/{self.id}"
                )
                self.image = Image(
                    {"id": self.image_id}, self._imgur, has_fetched=False
                )
                del self.image_id
            if "parent_id" in vars(self):
                if self.parent_id == 0:  # Top level comment
                    self.parent = None
                else:
                    self.parent = Comment(
                        {"id": self.parent_id}, self._imgur, has_fetched=False
                    )
                del self.parent_id
        elif isinstance(self, Gallery_image):
            if "account_url" in vars(self):
                self.author = User(
                    {"url": self.account_url}, self._imgur, has_fetched=False
                )
                del self.account_url
        elif isinstance(self, Message):
            # Should be gotten via self.author.id
            if "account_id" in vars(self):
                del self.account_id
            if "from" in vars(self):
                # Use getattr and delattr here as doing self.from gives a
                # syntax error because "from" is a protected keyword in Python.
                self.author = User(
                    {"url": getattr(self, "from")}, self._imgur, has_fetched=False
                )
                delattr(self, "from")
            if "parent_id" in vars(self):
                self.first_message = Message(
                    {"id": self.parent_id}, self._imgur, has_fetched=False
                )
                del self.parent_id
        elif isinstance(self, Notification):
            # Cannot be used for any calls.
            # Also, since Notifications can only be returned for the
            # authenticated user, the id can be found with get_user('me').id
            if "account_id" in vars(self):
                del self.account_id
            if "viewed" in vars(self):
                self.is_viewed = self.viewed
                del self.viewed
            if "content" in vars(self):
                if (
                    "subject" in self.content
                ):  # pylint: disable=access-member-before-definition
                    self.content = Message(self.content, self._imgur, True)
                elif "caption" in self.content:
                    self.content = Comment(
                        self.content, self._imgur, True
                    )  # pylint: disable=redefined-variable-type
        elif isinstance(self, User) and "url" in vars(self):
            self.name = self.url
            del self.url
            # NOTE: In the API a Images popularity is noted as it's score, but
            # referred on the webend as points. A Comment has the points
            # attribute which is simply likes - dislikes. One might think this
            # is the same thing for images, but comparing the two numbers show
            # that they are different. Usually with a small margin, but
            # sometimes a very substantial margin. I'm not sure of how score is
            # calculated and it's relationship to likes and dislikes.
            # NOTE: Image has the attribute "nsfw" which doesn't exist in
            # documentation.

    def refresh(self):
        """
        Refresh this objects attributes to the newest values.

        Attributes that weren't added to the object before, due to lazy
        loading, will be added by calling refresh.
        """
        resp = self._imgur._send_request(self._INFO_URL)
        self._populate(resp)
        self._has_fetched = True
        # NOTE: What if the object has been deleted in the meantime? That might
        # give a pretty cryptic error.


class Album(Basic_object):
    """
    An album is a collection of images.

    :ivar author: The user that authored the album. None if anonymous.
    :ivar cover: The albums cover image.
    :ivar datetime: Time inserted into the gallery, epoch time.
    :ivar deletehash: For anonymous uploads, this is used to delete the album.
    :ivar description: A short description of the album.
    :ivar id: The ID for the album.
    :ivar images: A list of the images in this album. Only set at instantiation
        if created with Imgur.get_album. But even if it isn't set, then you can
        still access the attribute. This will make PyImgur fetch the newest
        version of all attributes for this class, including images. So it will
        work as though images was set all along.
    :ivar is_favorited: Has the logged in user favorited this album?
    :ivar is_nsfw: Is the album Not Safe For Work (contains gore/porn)?
    :ivar layout: The view layout of the album.
    :ivar link: The URL link to the album.
    :ivar public: The privacy level of the album, you can only view public
        albums if not logged in as the album owner.
    :ivar section: ??? - No info in Imgur documentation.
    :ivar title: The album's title
    :ivar views: Total number of views the album has received.
    """

    def __init__(self, json_dict, imgur, has_fetched=True):
        self._INFO_URL = imgur._base_url + "/3/album/{0}".format(json_dict["id"])
        self.deletehash = None
        super(Album, self).__init__(json_dict, imgur, has_fetched)

    def add_images(self, images):
        """
        Add images to the album.

        :param images: A list of the images we want to add to the album. Can be
            Image objects, ids or a combination of the two.  Images that you
            cannot add (non-existing or not owned by you) will not cause
            exceptions, but fail silently.
        """
        params = clean_imgur_params(locals())
        url = self._imgur._base_url + f"/3/album/{self.id}/add"
        params = {"ids": images}
        return self._imgur._send_request(
            url, needs_auth=True, params=params, method="POST", alternate=True
        )

    def delete(self):
        """Delete this album."""
        url = self._imgur._base_url + f"/3/album/{self._delete_or_id_hash}"
        return self._imgur._send_request(url, method="DELETE")

    def favorite(self):
        """
        Favorite the album.

        Favoriting an already favorited album will unfavor it.
        """
        url = self._imgur._base_url + f"/3/album/{self.id}/favorite"
        return self._imgur._send_request(url, needs_auth=True, method="POST")

    def remove_images(self, images):
        """
        Remove images from the album.

        :param images: A list of the images we want to remove from the album.
            Can be Image objects, ids or a combination of the two. Images that
            you cannot remove (non-existing, not owned by you or not part of
            album) will not cause exceptions, but fail silently.
        """
        url = (
            self._imgur._base_url + f"/3/album/{self._delete_or_id_hash}/remove_images"
        )
        # NOTE: Returns True and everything seem to be as it should in testing.
        # Seems most likely to be upstream bug.
        params = {"ids": images}
        return self._imgur._send_request(
            url, params=params, method="POST", alternate=True, use_form_data=True
        )

    # Endpoint seem broken on Imgurs end. Keeping it a private function until it's fixed
    # or a wrongaround can be found.
    def _set_images(self, images):
        """
        Set the images in this album.

        :param images: A list of the images we want the album to contain.
            Can be Image objects, ids or a combination of the two. Images that
            images that you cannot set (non-existing or not owned by you) will
            not cause exceptions, but fail silently.
        """
        url = self._imgur._base_url + f"/3/album/{self._delete_or_id_hash}/"
        params = {"ids": images}
        return self._imgur._send_request(
            url,
            needs_auth=True,
            params=params,
            method="POST",
            alternate=True,
            use_form_data=True,
        )

    def submit_to_gallery(self, title, bypass_terms=False):
        """
        Add this to the gallery.

        Require that the authenticated user has accepted gallery terms and
        verified their email.

        :param title: The title of the new gallery item.
        :param bypass_terms: If the user has not accepted Imgur's terms yet,
            this method will return an error. Set this to True to by-pass the
            terms.
        """
        url = self._imgur._base_url + f"/3/gallery/{self.id}"
        payload = {"title": title, "terms": "1" if bypass_terms else "0"}
        self._imgur._send_request(url, needs_auth=True, params=payload, method="POST")
        item = self._imgur.get_gallery_album(self.id)
        _change_object(self, item)
        return self

    def update(
        self,
        title=None,
        description=None,
        images=None,
        cover=None,
        layout=None,
        privacy=None,
    ):
        """
        Update the album's information.

        Arguments with the value None will retain their old values.

        :param title: The title of the album.
        :param description: A description of the album.
        :param images: A list of the images we want the album to contain.
            Can be Image objects, ids or a combination of the two. Images that
            images that you cannot set (non-existing or not owned by you) will
            not cause exceptions, but fail silently.
        :param privacy: The albums privacy level, can be public, hidden or
            secret.
        :param cover: The id of the cover image.
        :param layout: The way the album is displayed, can be blog, grid,
            horizontal or vertical.
        """

        # TODO: Make more generic error here. Should be a decorator
        assert self._imgur.access_token is not None

        params = clean_imgur_params(locals())

        url = self._imgur._base_url + f"/3/album/{self._delete_or_id_hash}"
        is_updated = self._imgur._send_request(
            url, params=params, method="PUT", alternate=True
        )
        if is_updated:
            self.title = title or self.title
            self.description = description or self.description
            self.layout = layout or self.layout
            self.privacy = privacy or self.privacy
            if cover is not None:
                self.cover = (
                    cover
                    if isinstance(cover, Image)
                    else Image({"id": cover}, self._imgur, has_fetched=False)
                )
            if images:
                self.images = [
                    (
                        img
                        if isinstance(img, Image)
                        else Image({"id": img}, self._imgur, False)
                    )
                    for img in images
                ]
        return is_updated


class Comment(Basic_object):
    """
    A comment a user has made.

    Users can comment on Gallery album, Gallery image or other Comments.

    :ivar album_cover: If this Comment is on a Album, this will be the Albums
        cover Image.
    :ivar author: The user that created the comment.
    :ivar datetime: Time inserted into the gallery, epoch time.
    :ivar deletehash: For anonymous uploads, this is used to delete the image.
    :ivar downs: The total number of dislikes (downvotes) the comment has
        received.
    :ivar image: The image the comment belongs to.
    :ivar is_deleted: Has the comment been deleted?
    :ivar on_album: Is the image part of an album.
    :ivar parent: The comment this one has replied to, if it is a top-level
        comment i.e. it's a comment directly to the album / image then it will
        be None.
    :ivar permalink: A permanent link to the comment.
    :ivar points: ups - downs.
    :ivar replies: A list of comment replies to this comment. This variable is
        only available if the comment was returned via Album.get_comments().
        Use get_replies instead to get the replies if this variable is not
        available.
    :ivar text: The comments text.
    :ivar ups: The total number of likes (upvotes) the comment has received.
    :ivar vote: The currently logged in users vote on the comment.
    """

    def __init__(self, json_dict, imgur, has_fetched=True):
        self.deletehash = None
        self._INFO_URL = imgur._base_url + "/3/comment/{0}".format(json_dict["id"])
        super(Comment, self).__init__(json_dict, imgur, has_fetched)

    def delete(self):
        """Delete the comment."""
        url = self._imgur._base_url + f"/3/image/{self._delete_or_id_hash}"
        return self._imgur._send_request(url, method="DELETE")
        # TODO: Gives a 403 permission denied error on comment 77087313 which
        # made by me.

    def downvote(self):
        """Downvote this comment."""
        url = self._imgur._base_url + f"/3/comment/{self.id}/vote/down"
        return self._imgur._send_request(url, needs_auth=True, method="POST")

    def get_replies(self):
        """Get the replies to this comment."""
        url = self._imgur._base_url + f"/3/comment/{self.id}/replies"
        json = self._imgur._send_request(url)
        child_comments = json["children"]
        return [Comment(com, self._imgur) for com in child_comments]

    def reply(self, text):
        """Make a comment reply."""
        url = self._imgur._base_url + f"/3/comment/{self.id}"
        payload = {"image_id": self.image.id, "comment": text}
        resp = self._imgur._send_request(
            url, params=payload, needs_auth=True, method="POST"
        )
        return Comment(resp, imgur=self._imgur, has_fetched=False)

    '''
    Testing this method would give Imgur false positives.
    Discussions with Imgur will hopefully produce a way of consistently testing
    this without giving Imgur problems.
    def report(self):
        """Reply comment for being inappropriate."""
        pass
    '''

    def upvote(self):
        """Upvote this comment."""
        url = self._imgur._base_url + f"/3/comment/{self.id}/vote/up"
        return self._imgur._send_request(url, needs_auth=True, method="POST")


class Gallery_item(object):
    """Functionality shared by Gallery_image and Gallery_album."""

    def comment(self, text):
        """
        Make a top-level comment to this.

        :param text: The comment text.
        """
        url = self._imgur._base_url + "/3/comment"
        payload = {"image_id": self.id, "comment": text}
        resp = self._imgur._send_request(
            url, params=payload, needs_auth=True, method="POST"
        )
        return Comment(resp, imgur=self._imgur, has_fetched=False)

    def downvote(self):
        """
        Dislike this.

        A downvote will replace a neutral vote or an upvote. Downvoting
        something the authenticated user has already downvoted will set the
        vote to neutral.
        """
        url = self._imgur._base_url + f"/3/gallery/{self.id}/vote/down"
        return self._imgur._send_request(url, needs_auth=True, method="POST")

    def get_comments(self):
        """Get a list of the top-level comments."""
        url = self._imgur._base_url + f"/3/gallery/{self.id}/comments"
        resp = self._imgur._send_request(url)
        return [Comment(com, self._imgur) for com in resp]

    def remove_from_gallery(self):
        """Remove this image from the gallery."""
        url = self._imgur._base_url + f"/3/gallery/{self.id}"
        self._imgur._send_request(url, needs_auth=True, method="DELETE")
        if isinstance(self, Image):
            item = self._imgur.get_image(self.id)
        else:
            item = self._imgur.get_album(self.id)
        _change_object(self, item)
        return self

    def upvote(self):
        """
        Like this.

        An upvote will replace a neutral vote or an downvote. Upvoting
        something the authenticated user has already upvoted will set the vote
        to neutral.
        """
        url = self._imgur._base_url + "/3/gallery/{0}/vote/up".format(self.id)
        return self._imgur._send_request(url, needs_auth=True, method="POST")


class Image(Basic_object):
    """
    An image uploaded to Imgur.

    :ivar bandwidth: Bandwidth consumed by the image in bytes.
    :ivar datetime: Time inserted into the gallery, epoch time.
    :ivar deletehash: For anonymous uploads, this is used to delete the image.
    :ivar description: A short description of the image.
    :ivar height: The height of the image in pixels.
    :ivar id: The ID for the image.
    :ivar is_animated: is the image animated?
    :ivar is_favorited: Has the logged in user favorited this album?
    :ivar is_nsfw: Is the image Not Safe For Work (contains gore/porn)?
    :ivar link: The URL link to the image.
    :ivar link_big_square: The URL to a big square thumbnail of the image.
    :ivar link_huge_thumbnail: The URL to a huge thumbnail of the image.
    :ivar link_large_square: The URL to a large square thumbnail of the image.
    :ivar link_large_thumbnail: The URL to a large thumbnail of the image.
    :ivar link_medium_thumbnail: The URL to a medium thumbnail of the image.
    :ivar link_small_square: The URL to a small square thumbnail of the image.
    :ivar section: ??? - No info in Imgur documentation.
    :ivar size: The size of the image in bytes.
    :ivar title: The albums title.
    :ivar views: Total number of views the album has received.
    :ivar width: The width of the image in bytes.

    """

    # TODO: Looks like not all of these attributes are available still?
    # Alternatively, the lazy loading might have broken.
    def __init__(self, json_dict, imgur, has_fetched=True):
        self._INFO_URL = imgur._base_url + "/3/image/{0}".format(json_dict["id"])
        self.deletehash = None
        super(Image, self).__init__(json_dict, imgur, has_fetched)

    def delete(self):
        """Delete the image."""
        url = self._imgur._base_url + f"/3/image/{self._delete_or_id_hash}"
        return self._imgur._send_request(url, method="DELETE")

    def download(self, path="", name=None, overwrite=False, size=None):
        """
        Download the image.

        :param path: The image will be downloaded to the folder specified at
            path, if path is None (default) then the current working directory
            will be used.
        :param name: The name the image will be stored as (not including file
            extension). If name is None, then the title of the image will be
            used. If the image doesn't have a title, it's id will be used. Note
            that if the name given by name or title is an invalid filename,
            then the hash will be used as the name instead.
        :param overwrite: If True overwrite already existing file with the same
            name as what we want to save the file as.
        :param size: Instead of downloading the image in it's original size, we
            can choose to instead download a thumbnail of it. Options are
            'small_square', 'big_square', 'small_thumbnail',
            'medium_thumbnail', 'large_thumbnail' or 'huge_thumbnail'.

        :returns: Name of the new file.
        """

        def save_as(filename):
            local_path = os.path.join(path, filename)
            if os.path.exists(local_path) and not overwrite:
                raise Exception(
                    f"Trying to save as {local_path}, but file already exists."
                )
            with open(local_path, "wb") as out_file:
                out_file.write(resp.content)
            return local_path

        valid_sizes = {
            "small_square": "s",
            "big_square": "b",
            "small_thumbnail": "t",
            "medium_thumbnail": "m",
            "large_thumbnail": "l",
            "huge_thumbnail": "h",
        }
        if size is not None:
            size = size.lower().replace(" ", "_")
            if size not in valid_sizes:
                raise LookupError(
                    "Invalid size. Valid options are: {0}".format(
                        ", ".join(valid_sizes.keys())
                    )
                )
        suffix = valid_sizes.get(size, "")
        base, sep, ext = self.link.rpartition(".")
        resp = requests.get(base + suffix + sep + ext)
        if name or self.title:
            try:
                return save_as((name or self.title) + suffix + sep + ext)
            except IOError:
                pass
            # Invalid filename
        return save_as(self.id + suffix + sep + ext)

    def favorite(self):
        """
        Favorite the image.

        Favoriting an already favorited image will unfavorite it.
        """
        url = self._imgur._base_url + "/3/image/{0}/favorite".format(self.id)
        return self._imgur._send_request(url, needs_auth=True, method="POST")

    def submit_to_gallery(self, title, bypass_terms=False):
        """
        Add this to the gallery.

        Require that the authenticated user has accepted gallery terms and
        verified their email.

        :param title: The title of the new gallery item.
        :param bypass_terms: If the user has not accepted Imgur's terms yet,
            this method will return an error. Set this to True to by-pass the
            terms.
        """
        url = self._imgur._base_url + f"/3/gallery/{self.id}"
        payload = {"title": title, "terms": "1" if bypass_terms else "0"}
        self._imgur._send_request(url, needs_auth=True, params=payload, method="POST")
        item = self._imgur.get_gallery_image(self.id)
        _change_object(self, item)
        return self

    def update(self, title=None, description=None):
        """Update the image with a new title and/or description."""
        url = self._imgur._base_url + f"/3/image/{self._delete_or_id_hash}"

        # TODO: Replace with error
        assert title or description

        params = clean_imgur_params(locals())

        is_updated = self._imgur._send_request(
            url, params=params, method="POST", alternate=True
        )
        if is_updated:
            self.title = title or self.title
            self.description = description or self.description

        return is_updated


class Imgur:
    """
    The base class containing general functionality for Imgur.

    You should create an Imgur object at the start of your code and use it to
    interact with Imgur. You shouldn't directly initialize any other classes,
    but instead use the methods in this class to get them.
    """

    def __init__(
        self,
        client_id,
        client_secret=None,
        access_token=None,
        refresh_token=None,
        verify=True,
        mashape_key=None,
    ):
        """
        Initialize the Imgur object.

        Before using PyImgur, or the Imgur REST API in general, you need to
        register your application with Imgur. This can be done at
        https://api.imgur.com/oauth2/addclient

        :param client_id: Your applications client_id.
        :param client_secret: Your applications client_secret. This is only
            needed when a user needs to authorize the app.
        :param access_token: is your secret key used to access the user's data.
            It can be thought of the user's password and username combined into
            one, and is used to access the user's account. It expires after 1
            hour.
        :param refresh_token: is used to request new access_tokens. Since
            access_tokens expire after 1 hour, we need a way to request new
            ones without going through the entire authorization step again. It
            does not expire.
        :param verify: Verify SSL certificate of server
            (can result in SSLErrors)?
        """
        self.is_authenticated = False
        self.access_token = access_token
        self.client_id = client_id
        self.client_secret = client_secret
        self.DEFAULT_LIMIT = 100
        self.ratelimit_clientlimit = None
        self.ratelimit_clientremaining = None
        self.ratelimit_userlimit = None
        self.ratelimit_userremaining = None
        self.ratelimit_userreset = None
        self.refresh_token = refresh_token
        self.verify = verify
        self.mashape_key = mashape_key
        if self.mashape_key:
            self._base_url = MASHAPE_BASE
        else:
            self._base_url = IMGUR_BASE

    def _send_request(self, url, needs_auth=False, **kwargs):
        """
        Handles top level functionality for sending requests to Imgur.

        This mean
            - Raising client-side error if insufficient authentication.
            - Adding authentication information to the request.
            - Split the request into multiple request for pagination.
            - Retry calls for certain server-side errors.
            - Refresh access token automatically if expired.
            - Updating ratelimit info

        :param needs_auth: Is authentication as a user needed for the execution
            of this method?
        """
        # TODO: Add automatic test for timed_out access_tokens and
        # automatically refresh it before carrying out the request.
        if self.access_token is None and needs_auth:
            # TODO: Use inspect to insert name of method in error msg.
            raise Exception("Authentication as a user is required to use this method.")
        if self.access_token is None:
            # Not authenticated as a user. Use anonymous access.
            auth = {"Authorization": "Client-ID {0}".format(self.client_id)}
        else:
            auth = {"Authorization": "Bearer {0}".format(self.access_token)}
        if self.mashape_key:
            auth.update({"X-Mashape-Key": self.mashape_key})
        content = []
        is_paginated = False
        if "limit" in kwargs:
            is_paginated = True
            limit = kwargs["limit"] or self.DEFAULT_LIMIT
            del kwargs["limit"]
            page = 0
            base_url = url
            url.format(page)
        kwargs["authentication"] = auth
        while True:
            result = request.send_request(url, verify=self.verify, **kwargs)
            new_content, ratelimit_info = result
            if is_paginated and new_content and limit > len(new_content):
                content += new_content
                page += 1
                url = base_url.format(page)
            else:
                if is_paginated:
                    content = (content + new_content)[:limit]
                else:
                    content = new_content
                break
        # Note: When the cache is implemented, it's important that the
        # ratelimit info doesn't get updated with the ratelimit info in the
        # cache since that's likely incorrect.
        for key, value in ratelimit_info.items():
            setattr(self, key[2:].replace("-", "_"), value)
        return content

    def authorization_url(self, response, state=""):
        """
        Return the authorization url that's needed to authorize as a user.

        :param response: Can be either code or pin. If it's code the user will
            be redirected to your redirect url with the code as a get parameter
            after authorizing your application. If it's pin then after
            authorizing your application, the user will instead be shown a pin
            on Imgurs website. Both code and pin are used to get an
            access_token and refresh token with the exchange_code and
            exchange_pin functions respectively.
        :param state: This optional parameter indicates any state which may be
            useful to your application upon receipt of the response. Imgur
            round-trips this parameter, so your application receives the same
            value it sent. Possible uses include redirecting the user to the
            correct resource in your site, nonces, and
            cross-site-request-forgery mitigations.
        """
        return AUTHORIZE_URL.format(self._base_url, self.client_id, response, state)

    def change_authentication(
        self, client_id=None, client_secret=None, access_token=None, refresh_token=None
    ):
        """Change the current authentication."""
        if not ((client_id is None) == (client_secret is None)):
            # Temporary. Will add library errors.
            raise SyntaxError(
                "Must set both or none of client_id and client_secret at once"
            )

        if client_id:
            self.client_id = client_id
            self.client_secret = client_secret
            self.access_token = access_token
            self.refresh_token = refresh_token
        else:
            # Used for cases where the app switchings authentications. Ie. which user
            # it is operating on behalf of while being the same client.
            self.access_token = access_token
            self.refresh_token = refresh_token

    def create_album(self, title=None, description=None, images=None, cover=None):
        """
        Create a new Album.

        :param title: The title of the album.
        :param description: The albums description.
        :param images: A list of the images that will be added to the album
            after it's created.  Can be Image objects, ids or a combination of
            the two.  Images that you cannot add (non-existing or not owned by
            you) will not cause exceptions, but fail silently.
        :param cover: The id of the image you want as the albums cover image.

        :returns: The newly created album.
        """

        # TODO: Make more generic error here. Should be a decorator
        # TODO: Test that this is required. Would imply documentaiton is wrong
        assert self.access_token is not None

        url = self._base_url + "/3/album/"
        payload = {
            "ids": images,
            "title": title,
            "description": description,
            "cover": cover,
        }
        payload = clean_imgur_params(payload)

        resp = self._send_request(
            url, params=payload, method="POST", alternate=True, use_form_data=True
        )
        return Album(resp, self, has_fetched=False)

    '''
    Not currently implemented for 3 reasons.

    It requires recaptcha info, which makes using it via the API inconvenient.
    It is hard to test.
    It creates users on Imgur that doesn't correspond to actual users.

    def create_user(self, username):
        """Create this user on Imgur."""
        pass
    '''

    def exchange_code(self, code):
        """Exchange one-use code for an access_token and request_token."""
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code",
            "code": code,
        }
        result = self._send_request(
            EXCHANGE_URL.format(self._base_url),
            params=params,
            method="POST",
            data_field=None,
        )
        self.access_token = result["access_token"]
        self.refresh_token = result["refresh_token"]
        return self.access_token, self.refresh_token

    def exchange_pin(self, pin):
        """Exchange one-use pin for an access_token and request_token."""
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "pin",
            "pin": pin,
        }
        result = self._send_request(
            EXCHANGE_URL.format(self._base_url),
            params=params,
            method="POST",
            data_field=None,
        )
        self.access_token = result["access_token"]
        self.refresh_token = result["refresh_token"]
        return self.access_token, self.refresh_token

    def get_album(self, id):
        """Return information about this album."""
        url = self._base_url + f"/3/album/{id}"
        json = self._send_request(url)
        return Album(json, self)

    def get_at_url(self, url):
        """
        Return a object representing the content at url.

        Returns None if no object could be matched with the id.

        Works for Album, Comment, Gallery_album, Gallery_image, Image and User.

        NOTE: Imgur's documentation does not cover what urls are available.
        Some urls, such as imgur.com/<ID> can be for several different types of
        object. Using a wrong, but similair call, such as get_subreddit_image
        on a meme image will not cause an error. But instead return a subset of
        information, with either the remaining pieces missing or the value set
        to None. This makes it hard to create a method such as this that
        attempts to deduce the object from the url. Due to these factors, this
        method should be considered experimental and used carefully.

        :param url: The url where the content is located at
        """

        class NullDevice:
            def write(self, string):
                pass

        def get_gallery_item(id):
            """
            Special helper method to get gallery items.

            The problem is that it's impossible to distinguish albums and
            images from each other based on the url. And there isn't a common
            url endpoints that return either a Gallery_album or a Gallery_image
            depending on what the id represents. So the only option is to
            assume it's a Gallery_image and if we get an exception then try
            Gallery_album. Gallery_image is attempted first because there is
            the most of them.
            """
            try:
                # HACK: Problem is that send_request prints the error message
                # from Imgur when it encounters an error. This is nice because
                # this error message is more descriptive than just the status
                # code that Requests give. But since we first assume the id
                # belong to an image, it means we will get an error whenever
                # the id belongs to an album. The following code temporarily
                # disables stdout to avoid give a cryptic and incorrect error.

                # Code for disabling stdout is from
                # http://coreygoldberg.blogspot.dk/2009/05/
                # python-redirect-or-turn-off-stdout-and.html
                original_stdout = sys.stdout  # keep a reference to STDOUT
                sys.stdout = NullDevice()  # redirect the real STDOUT
                return self.get_gallery_image(id)
            # TODO: Add better error codes so I don't have to do a catch-all
            except Exception:
                return self.get_gallery_album(id)
            finally:
                sys.stdout = original_stdout  # turn STDOUT back on

        if not self.is_imgur_url(url):
            return None

        objects = {
            "album": {"regex": "a/(?P<id>[\w.]*?)$", "method": self.get_album},
            "comment": {
                "regex": "gallery/\w*/comment/(?P<id>[\w.]*?)$",
                "method": self.get_comment,
            },
            "gallery": {
                "regex": "(gallery|r/\w*?)/(?P<id>[\w.]*?)$",
                "method": get_gallery_item,
            },
            # Valid image extensions: http://imgur.com/faq#types
            # All are between 3 and 4 chars long.
            "image": {
                "regex": "(?P<id>[\w.]*?)(\\.\w{3,4})?$",
                "method": self.get_image,
            },
            "user": {"regex": "user/(?P<id>[\w.]*?)$", "method": self.get_user},
        }
        parsed_url = urlparse(url)
        for obj_type, values in objects.items():
            regex_result = re.match("/" + values["regex"], parsed_url.path)
            if regex_result is not None:
                obj_id = regex_result.group("id")
                initial_object = values["method"](obj_id)
                if obj_type == "image":
                    try:
                        # A better version might be to ping the url where the
                        # gallery_image should be with a requests.head call. If
                        # we get a 200 returned, then that means it exists and
                        # this becomes less hacky.
                        original_stdout = sys.stdout
                        sys.stdout = NullDevice()
                        if getattr(initial_object, "section", None):
                            sub = initial_object.section
                            return self.get_subreddit_image(sub, obj_id)
                        return self.get_gallery_image(obj_id)
                    except Exception:
                        pass
                    finally:
                        sys.stdout = original_stdout
                return initial_object

    def get_comment(self, id):
        """Return information about this comment."""
        url = self._base_url + f"/3/comment/{id}"
        json = self._send_request(url)
        return Comment(json, self)

    def get_gallery(
        self, section="hot", sort="viral", window="day", show_viral=True, limit=None
    ):
        """
        Return a list of gallery albums and gallery images.

        :param section: hot | top | user - defaults to hot.
        :param sort: viral | time - defaults to viral.
        :param window: Change the date range of the request if the section is
            "top", day | week | month | year | all, defaults to day.
        :param show_viral: true | false - Show or hide viral images from the
            'user' section. Defaults to true.
        :param limit: The number of items to return.
        """
        url = self._base_url + "/3/gallery/{}/{}/{}/{}?showViral={}".format(
            section, sort, window, "{}", show_viral
        )
        resp = self._send_request(url, limit=limit)
        return [_get_album_or_image(thing, self) for thing in resp]

    def get_gallery_album(self, id):
        """
        Return the gallery album matching the id.

        Note that an album's id is different from it's id as a gallery album.
        This makes it possible to remove an album from the gallery and setting
        it's privacy setting as secret, without compromising it's secrecy.
        """
        url = self._base_url + f"/3/gallery/album/{id}"
        resp = self._send_request(url)
        return Gallery_album(resp, self)

    def get_gallery_image(self, id):
        """
        Return the gallery image matching the id.

        Note that an image's id is different from it's id as a gallery image.
        This makes it possible to remove an image from the gallery and setting
        it's privacy setting as secret, without compromising it's secrecy.
        """
        url = self._base_url + f"/3/gallery/image/{id}"
        resp = self._send_request(url)
        return Gallery_image(resp, self)

    def get_image(self, id):
        """Return a Image object representing the image with the given id."""
        url = self._base_url + f"/3/image/{id}"
        resp = self._send_request(url)
        return Image(resp, self)

    def get_message(self, id):
        """
        Return a Message object for given id.

        :param id: The id of the message object to return.
        """
        url = self._base_url + f"/3/message/{id}"
        resp = self._send_request(url)
        return Message(resp, self)

    def get_notification(self, id):
        """
        Return a Notification object.

        :param id: The id of the notification object to return.
        """
        url = self._base_url + f"/3/notification/{id}"
        resp = self._send_request(url)
        return Notification(resp, self)

    def get_memes_gallery(self, sort="viral", window="week", limit=None):
        """
        Return a list of gallery albums/images submitted to the memes gallery

        The url for the memes gallery is: http://imgur.com/g/memes

        :param sort: viral | time | top - defaults to viral
        :param window: Change the date range of the request if the section is
            "top", day | week | month | year | all, defaults to week.
        :param limit: The number of items to return.
        """
        url = self._base_url + "/3/gallery/g/memes/{0}/{1}/{2}".format(
            sort, window, "{}"
        )
        resp = self._send_request(url, limit=limit)
        return [_get_album_or_image(thing, self) for thing in resp]

    '''
    This method does not seem to return any more data than get_gallery_image.
    So I'm not sure whether it needs to be included. Speaking for is that
    people may expect it to be here, speaking against is that the functionality
    already exists and duplication will reduce usability of the API.
    07-08-2013
    def get_memes_image(self, id):
        """
        Return the Gallery_image with the id submitted to the memes gallery

        :param id: The id of the image we want.
        """
        url = self._base_url + "/3/gallery/g/memes/" % id
        resp = self._send_request(url)
        return Gallery_image(resp, self)
    '''

    def get_subreddit_gallery(self, subreddit, sort="time", window="top", limit=None):
        """
        Return a list of gallery albums/images submitted to a subreddit.

        A subreddit is a subsection of the website www.reddit.com, where users
        can, among other things, post images.

        :param subreddit: A valid subreddit name.
        :param sort: time | top - defaults to top.
        :param window: Change the date range of the request if the section is
            "top", day | week | month | year | all, defaults to day.
        :param limit: The number of items to return.
        """
        url = self._base_url + "/3/gallery/r/{0}/{1}/{2}/{3}".format(
            subreddit, sort, window, "{}"
        )
        resp = self._send_request(url, limit=limit)
        return [_get_album_or_image(thing, self) for thing in resp]

    def get_subreddit_image(self, subreddit, id):
        """
        Return the Gallery_image with the id submitted to subreddit gallery

        :param subreddit: The subreddit the image has been submitted to.
        :param id: The id of the image we want.
        """
        url = self._base_url + f"/3/gallery/r/{subreddit}/{id}"
        resp = self._send_request(url)
        return Gallery_image(resp, self)

    def get_user(self, username):
        """
        Return a User object for this username.

        :param username: The name of the user we want more information about.
        """
        url = self._base_url + f"/3/account/{username}"
        json = self._send_request(url)
        return User(json, self)

    def is_imgur_url(self, url):
        """Is the given url a valid Imgur url?"""
        return re.match("(http://)?(www\.)?imgur\.com", url, re.I) is not None

    def refresh_access_token(self):
        """
        Refresh the access_token.

        The self.access_token attribute will be updated with the value of the
        new access_token which will also be returned.
        """
        if self.client_secret is None:
            raise Exception(
                "client_secret must be set to execute refresh_access_token."
            )
        if self.refresh_token is None:
            raise Exception(
                "refresh_token must be set to execute refresh_access_token."
            )
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
        }
        result = self._send_request(
            REFRESH_URL.format(self._base_url),
            params=params,
            method="POST",
            data_field=None,
        )
        self.access_token = result["access_token"]
        return self.access_token

    def search_gallery(self, q):
        """Search the gallery with the given query string."""
        url = self._base_url + f"/3/gallery/search?q={q}"
        resp = self._send_request(url)
        return [_get_album_or_image(thing, self) for thing in resp]

    def upload_image(
        self, path=None, url=None, title=None, description=None, album=None
    ):
        """
        Upload the image at either path or url.

        :param path: The path to the image you want to upload.
        :param url: The url to the image you want to upload.
        :param title: The title the image will have when uploaded.
        :param description: The description the image will have when uploaded.
        :param album: The album the image will be added to when uploaded. Can
            be either a Album object or it's id. Leave at None to upload
            without adding to an Album, adding it later is possible.
            Authentication as album owner is necessary to upload to an album
            with this function.

        :returns: An Image object representing the uploaded image.
        """
        if bool(path) == bool(url):
            raise LookupError("Either path or url must be given.")
        if path:
            with open(path, "rb") as image_file:
                binary_data = image_file.read()
                image = b64encode(binary_data)
        else:
            image = url

        payload = {
            "album_id": album,
            "image": image,
            "title": title,
            "description": description,
        }

        resp = self._send_request(
            self._base_url + "/3/image", params=payload, method="POST"
        )
        # TEMPORARY HACK:
        # On 5-08-2013 I noticed Imgur now returned enough information from
        # this call to fully populate the Image object. However those variables
        # that matched arguments were always None, even if they had been given.
        # See https://groups.google.com/forum/#!topic/imgur/F3uVb55TMGo
        resp["title"] = title
        resp["description"] = description
        if album is not None:
            resp["album"] = (
                Album({"id": album}, self, False)
                if not isinstance(album, Album)
                else album
            )
        return Image(resp, self)


class Message(Basic_object):
    """This corresponds to the messages users can send each other."""

    def __init__(self, json_dict, imgur, has_fetched=True):
        self._INFO_URL = imgur._base_url + "/3/message/{0}".format(json_dict["id"])
        super(Message, self).__init__(json_dict, imgur, has_fetched)

    """
    Maybe we cannot unblock users? Would be quite problematic if one of the
    main acounts blocked the other and it couldn't be unblocked.

    Perhaps this method should also be placed under User as its a user we
    block, not the message itself.
    def block(self):
        pass
    """

    def delete(self):
        """Delete the message."""
        url = f"{self._imgur._base_url}/3/message/{self.id}"
        return self._imgur._send_request(url, method="DELETE")

    def get_thread(self):
        """Return the message thread this Message is in."""
        url = f"{self._imgur._base_url}/3/message/{self.first_message.id}/thread"
        resp = self._imgur._send_request(url)
        return [Message(msg, self._imgur) for msg in resp]

    def reply(self, body):
        """
        Reply to this message.

        This is a convenience method calling User.send_message. See it for more
        information on usage. Note that both recipient and reply_to are given
        by using this convenience method.

        :param body: The body of the message.
        """
        return self.author.send_message(body=body, reply_to=self.id)

    '''
    Testing this method would give Imgur false positives.
    Discussions with Imgur will hopefully produce a way of consistently testing
    this without giving Imgur problems.

    Maybe this method should be placed under User as it is the user that's
    being reported. On the other hand the reason for the report is sending
    messages against Imgurs TOS. Comments can also be against the TOS, but
    there is a separate endpoint for reporting those.

    def report():
        """Report the author sending a message against the Terms of Service."""
        pass
    '''


class Notification(Basic_object):
    """
    This corresponds to the notifications a user may receive.

    A notification can come for several reasons. For instance, one may be
    received if someone replies to one of your comments.
    """

    def __init__(self, json_dict, imgur, has_fetched=True):
        # Is never gotten lazily, so _has_fetched is always True
        self._INFO_URL = imgur._base_url + "/3/notification/{0}".format(json_dict["id"])
        super(Notification, self).__init__(json_dict, imgur, has_fetched)

    def mark_as_viewed(self):
        """
        Mark the notification as viewed.

        Notifications cannot be marked as unviewed.
        """
        url = f"{self._imgur._base_url}/3/notification/{self.id}"
        return self._imgur._send_request(url, method="POST")


class User(Basic_object):
    """
    A User on Imgur.

    :ivar bio: A basic description filled out by the user, displayed in the
        gallery profile page.
    :ivar created: The epoch time of user account creation
    :ivar id: The user id.
    :ivar name: The username
    :ivar reputation: Total likes - dislikes of the user's created content.
    """

    def __init__(self, json_dict, imgur, has_fetched=True):
        self._INFO_URL = imgur._base_url + "/3/account/{0}".format(json_dict["url"])
        super(User, self).__init__(json_dict, imgur, has_fetched)

    # Overrides __repr__ method in Basic_object
    def __repr__(self):
        return "<{0} {1}>".format(type(self).__name__, self.name)

    def change_settings(
        self,
        bio=None,
        public_images=None,
        messaging_enabled=None,
        album_privacy=None,
        accepted_gallery_terms=None,
    ):
        """
        Update the settings for the user.

        :param bio: A basic description filled out by the user, is displayed in
            the gallery profile page.
        :param public_images: Set the default privacy setting of the users
            images. If True images are public, if False private.
        :param messaging_enabled: Set to True to enable messaging.
        :param album_privacy: The default privacy level of albums created by
            the user. Can be public, hidden or secret.
        :param accepted_gallery_terms: The user agreement to Imgur Gallery
            terms. Necessary before the user can submit to the gallery.
        """
        # NOTE: album_privacy should maybe be renamed to default_privacy
        # NOTE: public_images is a boolean, despite the documentation saying it
        # is a string.
        url = f"{self._imgur._base_url}/3/account/{self.name}/settings"
        resp = self._imgur._send_request(
            url, needs_auth=True, params=locals(), method="POST"
        )
        return resp

    def delete(self):
        """Delete this user. Require being authenticated as the user."""
        url = f"{self._imgur._base_url}/3/account/{self.name}"
        return self._imgur._send_request(url, needs_auth=True, method="DELETE")

    def get_albums(self, limit=None):
        """
        Return  a list of the user's albums.

        Secret and hidden albums are only returned if this is the logged-in
        user.
        """
        url = self._imgur._base_url + "/3/account/{0}/albums/{1}".format(
            self.name, "{}"
        )
        resp = self._imgur._send_request(url, limit=limit)
        return [Album(alb, self._imgur, False) for alb in resp]

    def get_comments(self):
        """Return the comments made by the user."""
        url = f"{self._imgur._base_url}/3/account/{self.name}/comments"
        resp = self._imgur._send_request(url)
        return [Comment(com, self._imgur) for com in resp]

    def get_favorites(self):
        """Return the users favorited images."""
        url = f"{self._imgur._base_url}/3/account/{self.name}/favorites"
        resp = self._imgur._send_request(url, needs_auth=True)
        return [_get_album_or_image(thing, self._imgur) for thing in resp]

    def get_gallery_favorites(self):
        """Get a list of the images in the gallery this user has favorited."""
        url = f"{self._imgur._base_url}/3/account/{self.name}/gallery_favorites"
        resp = self._imgur._send_request(url)
        return [Image(img, self._imgur) for img in resp]

    def get_gallery_profile(self):
        """Return the users gallery profile."""
        url = f"{self._imgur._base_url}/3/account/{self.name}/gallery_profile"
        return self._imgur._send_request(url)

    def has_verified_email(self):
        """
        Has the user verified that the email he has given is legit?

        Verified e-mail is required to the gallery. Confirmation happens by
        sending an email to the user and the owner of the email user verifying
        that he is the same as the Imgur user.
        """
        url = f"{self._imgur._base_url}/3/account/{self.name}/verifyemail"
        return self._imgur._send_request(url, needs_auth=True)

    def get_images(self, limit=None):
        """Return all of the images associated with the user."""
        url = self._imgur._base_url + "/3/account/{0}/images/{1}".format(
            self.name, "{}"
        )
        resp = self._imgur._send_request(url, limit=limit)
        return [Image(img, self._imgur) for img in resp]

    def get_messages(self, new=True):
        """
        Return all messages sent to this user, formatted as a notification.

        :param new: False for all notifications, True for only non-viewed
            notifications.
        """
        url = f"{self._imgur._base_url}/3/account/{self.name}/notifications/messages"
        result = self._imgur._send_request(url, params=locals(), needs_auth=True)
        return [
            Notification(msg_dict, self._imgur, has_fetched=True) for msg_dict in result
        ]

    def get_notifications(self, new=True):
        """Return all the notifications for this user."""
        url = f"{self._imgur._base_url}/3/account/{self.name}/notifications"
        resp = self._imgur._send_request(url, params=locals(), needs_auth=True)
        msgs = [
            Message(msg_dict, self._imgur, has_fetched=True)
            for msg_dict in resp["messages"]
        ]
        replies = [
            Comment(com_dict, self._imgur, has_fetched=True)
            for com_dict in resp["replies"]
        ]
        return {"messages": msgs, "replies": replies}

    def get_replies(self, new=True):
        """
        Return all reply notifications for this user.

        :param new: False for all notifications, True for only non-viewed
            notifications.
        """
        url = f"{self._imgur._base_url}/3/account/{self.name}/notifications/replies"
        return self._imgur._send_request(url, needs_auth=True)

    def get_settings(self):
        """
        Returns current settings.

        Only accessible if authenticated as the user.
        """
        url = f"{self._imgur._base_url}/3/account/{self.name}/settings"
        return self._imgur._send_request(url)

    def get_statistics(self):
        """Return statistics about this user."""
        url = f"{self._imgur._base_url}/3/account/{self.name}/stats"
        return self._imgur._send_request(url, needs_auth=True)

    def get_submissions(self, limit=None):
        """Return a list of the images a user has submitted to the gallery."""
        url = self._imgur._base_url + "/3/account/{0}/submissions/{1}".format(
            self.name, "{}"
        )
        resp = self._imgur._send_request(url, limit=limit)
        return [_get_album_or_image(thing, self._imgur) for thing in resp]

    def send_message(self, body, subject=None, reply_to=None):
        """
        Send a message to this user from the logged in user.

        :param body: The body of the message.
        :param subject: The subject of the message. Note that if the this
            message is a reply, then the subject of the first message will be
            used instead.
        :param reply_to: Messages can either be replies to other messages or
            start a new message thread. If this is None it will start a new
            message thread. If it's a Message object or message_id, then the
            new message will be sent as a reply to the reply_to message.
        """
        url = f"{self._imgur._base_url}/3/message"
        parent_id = reply_to.id if isinstance(reply_to, Message) else reply_to
        payload = {
            "recipient": self.name,
            "body": body,
            "subject": subject,
            "parent_id": parent_id,
        }
        self._imgur._send_request(url, params=payload, needs_auth=True, method="POST")

    def send_verification_email(self):
        """
        Send verification email to this users email address.

        Remember that the verification email may end up in the users spam
        folder.
        """
        url = f"{self._imgur._base_url}/3/account/{self.name}/verifyemail"
        self._imgur._send_request(url, needs_auth=True, method="POST")


# Gallery_album and Gallery_image are placed at the end as they need to inherit
# from Gallery_item, Album and Image. It's thus impossible to place them
# alphabetically without errors.
class Gallery_album(Album, Gallery_item):
    """Gallery Albums are albums submitted to the gallery."""

    def __init__(self, json_dict, imgur, has_fetched=True):
        self._INFO_URL = f"{imgur._base_url}/3/gallery/album/{json_dict['id']}"
        super(Gallery_album, self).__init__(json_dict, imgur, has_fetched)


class Gallery_image(Image, Gallery_item):
    """Gallery images are images submitted to the gallery."""

    def __init__(self, json_dict, imgur, has_fetched=True):
        self._INFO_URL = f"{imgur._base_url}/3/gallery/image/{json_dict['id']}"
        super(Gallery_image, self).__init__(json_dict, imgur, has_fetched)


# TODO: Given the name, this should probably be in requests.
# Together with the other cleaning functions there.
def clean_imgur_params(originals):
    """Clean the params before sending to Imgur.

    Remove keys set for internal purposes. Remove none
    values, that otherwise cause Imgur to throw errors.

    """
    if not originals:
        return {}

    params = {}
    for variable in originals.keys():
        if variable == "self":
            continue

        if originals[variable] is not None:
            params[variable] = originals[variable]

    return params
