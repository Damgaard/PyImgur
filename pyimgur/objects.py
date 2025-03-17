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

"""All objects aside from Imgur, Image and basic_objects

It would be better if this was split into multiple files, one for
each object. However, they reference each other and attempts to
move them into multiple files have failed on circular imports.
"""

from pyimgur.basic_objects import Basic_object, _change_object
from pyimgur import Image
from pyimgur.exceptions import InvalidParameterError


class Album(Basic_object):  # pylint: disable=too-many-instance-attributes
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
        self._info_url = f"{imgur.base_url}/3/album/{json_dict['id']}"
        self.deletehash = None
        super().__init__(json_dict, imgur, has_fetched)

    def _populate(self, json_dict):
        super()._populate(json_dict)
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
                    Image(img, self._imgur, has_fetched=False) for img in self.images
                ]
        if "images_count" in vars(self):
            del self.images_count

    def add_images(self, images):
        """
        Add images to the album.

        :param images: A list of the images we want to add to the album. Can be
            Image objects, ids or a combination of the two.  Images that you
            cannot add (non-existing or not owned by you) will not cause
            exceptions, but fail silently.
        """
        url = self._imgur.base_url + f"/3/album/{self.id}/add"
        params = {"ids": images}
        return self._imgur.send_request(
            url, needs_auth=True, params=params, method="POST", as_json=True
        )

    def delete(self):
        """Delete this album."""
        url = self._imgur.base_url + f"/3/album/{self._delete_or_id_hash}"
        return self._imgur.send_request(url, method="DELETE")

    def favorite(self):
        """
        Favorite the album.

        Favoriting an already favorited album will unfavor it.
        """
        url = self._imgur.base_url + f"/3/album/{self.id}/favorite"
        return self._imgur.send_request(url, needs_auth=True, method="POST")

    def remove_images(self, images):
        """
        Remove images from the album.

        :param images: A list of the images we want to remove from the album.
            Can be Image objects, ids or a combination of the two. Images that
            you cannot remove (non-existing, not owned by you or not part of
            album) will not cause exceptions, but fail silently.
        """
        url = self._imgur.base_url + f"/3/album/{self._delete_or_id_hash}/remove_images"
        # NOTE: Returns True and everything seem to be as it should in testing.
        # Seems most likely to be upstream bug.
        params = {"ids": images}
        return self._imgur.send_request(
            url, params=params, method="POST", as_json=True, use_form_data=True
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
        url = self._imgur.base_url + f"/3/album/{self._delete_or_id_hash}/"
        params = {"ids": images}
        return self._imgur.send_request(
            url,
            needs_auth=True,
            params=params,
            method="POST",
            as_json=True,
            use_form_data=True,
        )

    def submit_to_gallery(self, title, bypass_terms=False):
        """
        Add this to the gallery.

        Require that the authenticated user has accepted gallery terms and
        verified their email.

        :param title: The title of the new gallery item.
        :param bypass_terms: If the user has not accepted Imgur's terms yet,
            this method will return an error. Set this to True to bypass the
            terms.
        """
        url = self._imgur.base_url + f"/3/gallery/{self.id}"
        payload = {"title": title, "terms": "1" if bypass_terms else "0"}
        self._imgur.send_request(url, needs_auth=True, params=payload, method="POST")
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
    ):  # pylint: disable=too-many-arguments,too-many-positional-arguments
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
        assert self._imgur.access_token is not None

        url = self._imgur.base_url + f"/3/album/{self._delete_or_id_hash}"
        is_updated = self._imgur.send_request(
            url, params=locals(), method="PUT", as_json=True
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
        self._info_url = f"{imgur.base_url}/3/comment/{json_dict['id']}"
        super().__init__(json_dict, imgur, has_fetched)

    def _populate(self, json_dict):
        super()._populate(json_dict)
        if "author" in vars(self):
            self.author = User({"url": self.author}, self._imgur, has_fetched=False)
        # Problem with this naming is that children / parent are normal
        # terminology for tree structures such as this. But elsewhere the
        # children are referred to as replies, for instance a comment can
        # be replies to not procreated with. I've decided to use replies
        # and parent_comment as a compromise, where both attributes should
        # be individually obvious but their connection may not.
        if "children" in vars(self):
            self.replies = [Comment(com, self._imgur) for com in self.children]
            del self.children
        if "image_id" in vars(self):
            self.permalink = (
                f"http://imgur.com/gallery/{self.image_id}/comment/{self.id}"
            )
            self.image = Image({"id": self.image_id}, self._imgur, has_fetched=False)
            del self.image_id
        if "parent_id" in vars(self):
            if self.parent_id == 0:  # Top level comment
                self.parent = None
            else:
                self.parent = Comment(
                    {"id": self.parent_id}, self._imgur, has_fetched=False
                )
            del self.parent_id

    def delete(self):
        """Delete the comment."""
        url = self._imgur.base_url + f"/3/image/{self._delete_or_id_hash}"
        return self._imgur.send_request(url, method="DELETE")

    def downvote(self):
        """Downvote this comment."""
        url = self._imgur.base_url + f"/3/comment/{self.id}/vote/down"
        return self._imgur.send_request(url, needs_auth=True, method="POST")

    def get_replies(self):
        """Get the replies to this comment."""
        url = self._imgur.base_url + f"/3/comment/{self.id}/replies"
        json = self._imgur.send_request(url)
        child_comments = json["children"]
        return [Comment(com, self._imgur) for com in child_comments]

    def reply(self, text):
        """Make a comment reply."""
        url = self._imgur.base_url + f"/3/comment/{self.id}"
        payload = {"image_id": self.image.id, "comment": text}
        resp = self._imgur.send_request(
            url, params=payload, needs_auth=True, method="POST"
        )
        return Comment(resp, imgur=self._imgur, has_fetched=False)

    def upvote(self):
        """Upvote this comment."""
        url = self._imgur.base_url + f"/3/comment/{self.id}/vote/up"
        return self._imgur.send_request(url, needs_auth=True, method="POST")


class Notification(Basic_object):
    """
    This corresponds to the notifications a user may receive.

    A notification can come for several reasons. For instance, one may be
    received if someone replies to one of your comments.
    """

    def __init__(self, json_dict, imgur, has_fetched=True):
        # Is never gotten lazily, so _has_fetched is always True
        self._info_url = f"{imgur.base_url}/3/notification/{json_dict['id']}"
        super().__init__(json_dict, imgur, has_fetched)

    def _populate(self, json_dict):
        super()._populate(json_dict)
        if "content" in vars(self):
            if "subject" in self.content:
                self.content = Message(self.content, self._imgur, True)
            elif "caption" in self.content:
                self.content = Comment(self.content, self._imgur, True)

    def mark_as_viewed(self):
        """
        Mark the notification as viewed.

        Notifications cannot be marked as unviewed.
        """
        url = f"{self._imgur.base_url}/3/notification/{self.id}"
        return self._imgur.send_request(url, method="POST")


class Message(Basic_object):
    """This corresponds to the messages users can send each other."""

    def __init__(self, json_dict, imgur, has_fetched=True):
        self._info_url = f"{imgur.base_url}/3/message/{json_dict['id']}"
        super().__init__(json_dict, imgur, has_fetched)

    def _populate(self, json_dict):
        super()._populate(json_dict)
        if "account_id" in vars(self):
            del self.account_id
        if "from" in vars(self):
            self.author = User(
                {"url": getattr(self, "from")}, self._imgur, has_fetched=False
            )
            delattr(self, "from")
        if "parent_id" in vars(self):
            self.first_message = Message(
                {"id": self.parent_id}, self._imgur, has_fetched=False
            )
            del self.parent_id

    def delete(self):
        """Delete the message."""
        url = f"{self._imgur.base_url}/3/message/{self.id}"
        return self._imgur.send_request(url, method="DELETE")

    def get_thread(self):
        """Return the message thread this Message is in."""
        url = f"{self._imgur.base_url}/3/message/{self.first_message.id}/thread"
        resp = self._imgur.send_request(url)
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


class Gallery_item:  # pylint: disable=invalid-name
    """Functionality shared by Gallery_image and Gallery_album."""

    def comment(self, text):
        """
        Make a top-level comment to this.

        :param text: The comment text.
        """
        url = self._imgur.base_url + "/3/comment"
        payload = {"image_id": self.id, "comment": text}
        resp = self._imgur.send_request(
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
        url = self._imgur.base_url + f"/3/gallery/{self.id}/vote/down"
        return self._imgur.send_request(url, needs_auth=True, method="POST")

    def get_comments(self):
        """Get a list of the top-level comments."""
        url = self._imgur.base_url + f"/3/gallery/{self.id}/comments"
        resp = self._imgur.send_request(url)
        return [Comment(com, self._imgur) for com in resp]

    def remove_from_gallery(self):
        """Remove this image from the gallery."""
        url = self._imgur.base_url + f"/3/gallery/{self.id}"
        self._imgur.send_request(url, needs_auth=True, method="DELETE")
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
        url = self._imgur.base_url + f"/3/gallery/{self.id}/vote/up"
        return self._imgur.send_request(url, needs_auth=True, method="POST")

    @staticmethod
    def get_album_or_image(json, imgur):
        """Return a gallery image/album depending on what the json represent."""
        if json["is_album"]:
            return Gallery_album(json, imgur, has_fetched=False)
        return Gallery_image(json, imgur)


# Gallery_album and Gallery_image are placed at the end as they need to inherit
# from Gallery_item, Album and Image. It's thus impossible to place them
# alphabetically without errors.
class Gallery_album(Album, Gallery_item):  # pylint: disable=invalid-name
    """Gallery Albums are albums submitted to the gallery."""

    def __init__(self, json_dict, imgur, has_fetched=True):
        self._info_url = f"{imgur.base_url}/3/gallery/album/{json_dict['id']}"
        super().__init__(json_dict, imgur, has_fetched)


class Gallery_image(Image, Gallery_item):  # pylint: disable=invalid-name
    """Gallery images are images submitted to the gallery."""

    def __init__(self, json_dict, imgur, has_fetched=True):
        self._info_url = f"{imgur.base_url}/3/gallery/image/{json_dict['id']}"
        super().__init__(json_dict, imgur, has_fetched)

    def _populate(self, json_dict):
        super()._populate(json_dict)
        if "account_url" in vars(self):
            self.author = User(
                {"url": self.account_url}, self._imgur, has_fetched=False
            )
            del self.account_url


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
        self._info_url = f"{imgur.base_url}/3/account/{json_dict['url']}"
        super().__init__(json_dict, imgur, has_fetched)

    # Overrides __repr__ method in Basic_object
    def __repr__(self):
        return f"<{type(self).__name__} {self.name}>"

    def change_settings(
        self,
        bio=None,
        public_images=None,
        messaging_enabled=None,
        album_privacy=None,
        accepted_gallery_terms=None,
    ):  # pylint: disable=too-many-arguments,too-many-positional-arguments
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
        payload = {
            "bio": bio,
            "public_images": public_images,
            "messaging_enabled": messaging_enabled,
            "album_privacy": album_privacy,
            "accepted_gallery_terms": accepted_gallery_terms,
        }
        url = f"{self._imgur.base_url}/3/account/{self.name}/settings"
        resp = self._imgur.send_request(
            url, needs_auth=True, params=payload, method="POST"
        )
        return resp

    def delete(self):
        """Delete this user. Require being authenticated as the user."""
        url = f"{self._imgur.base_url}/3/account/{self.name}"
        return self._imgur.send_request(url, needs_auth=True, method="DELETE")

    def get_albums(self, limit=None):
        """
        Return  a list of the user's albums.

        Secret and hidden albums are only returned if this is the logged-in
        user.
        """
        url = f"{self._imgur.base_url}/3/account/{self.name}/albums/{{}}"
        resp = self._imgur.send_request(url, limit=limit)
        return [Album(alb, self._imgur, False) for alb in resp]

    def get_comments(self):
        """Return the comments made by the user."""
        url = f"{self._imgur.base_url}/3/account/{self.name}/comments"
        resp = self._imgur.send_request(url)
        return [Comment(com, self._imgur) for com in resp]

    def get_favorites(self, limit=None):
        """Return the users favorited images."""
        url = f"{self._imgur.base_url}/3/account/{self.name}/favorites/{{}}"
        resp = self._imgur.send_request(url, limit=limit, needs_auth=True)
        return [Gallery_item.get_album_or_image(thing, self._imgur) for thing in resp]

    def get_gallery_favorites(self, sort=None, limit=None):
        """Get a list of the images in the gallery this user has favorited."""
        if sort not in (None, "oldest", "newest"):
            raise InvalidParameterError("sort must be None, 'oldest' or 'newest'")

        url = f"{self._imgur.base_url}/3/account/{self.name}/gallery_favorites/{{}}"

        if sort:
            url += f"/{sort}"

        resp = self._imgur.send_request(url, limit=limit)
        return [Image(img, self._imgur) for img in resp]

    def get_gallery_profile(self):
        """Return the users gallery profile."""
        url = f"{self._imgur.base_url}/3/account/{self.name}/gallery_profile"
        return self._imgur.send_request(url)

    def has_verified_email(self):
        """
        Has the user verified that the email he has given is legit?

        Verified e-mail is required to the gallery. Confirmation happens by
        sending an email to the user and the owner of the email user verifying
        that he is the same as the Imgur user.
        """
        url = f"{self._imgur.base_url}/3/account/{self.name}/verifyemail"
        return self._imgur.send_request(url, needs_auth=True)

    def get_images(self, limit=None):
        """Return all of the images associated with the user."""
        url = f"{self._imgur.base_url}/3/account/{self.name}/images/{{}}"
        resp = self._imgur.send_request(url, limit=limit)
        return [Image(img, self._imgur) for img in resp]

    def get_messages(self, new=True):
        """
        Return all messages sent to this user, formatted as a notification.

        :param new: False for all notifications, True for only non-viewed
            notifications.
        """
        url = f"{self._imgur.base_url}/3/account/{self.name}/notifications/messages"
        result = self._imgur.send_request(url, params={"new": new}, needs_auth=True)
        return [
            Notification(msg_dict, self._imgur, has_fetched=True) for msg_dict in result
        ]

    def get_notifications(self, new=True):
        """Return all the notifications for this user."""
        url = f"{self._imgur.base_url}/3/account/{self.name}/notifications"
        resp = self._imgur.send_request(url, params={"new": new}, needs_auth=True)
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
        url = f"{self._imgur.base_url}/3/account/{self.name}/notifications/replies"
        return self._imgur.send_request(url, params={"new": new}, needs_auth=True)

    def get_settings(self):
        """
        Returns current settings.

        Only accessible if authenticated as the user.
        """
        url = f"{self._imgur.base_url}/3/account/{self.name}/settings"
        return self._imgur.send_request(url)

    def get_statistics(self):
        """Return statistics about this user."""
        url = f"{self._imgur.base_url}/3/account/{self.name}/stats"
        return self._imgur.send_request(url, needs_auth=True)

    def get_submissions(self, limit=None):
        """Return a list of the images a user has submitted to the gallery."""
        url = f"{self._imgur.base_url}/3/account/{self.name}/submissions/{{}}"
        resp = self._imgur.send_request(url, limit=limit)
        return [Gallery_item.get_album_or_image(thing, self._imgur) for thing in resp]

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
        url = f"{self._imgur.base_url}/3/message"
        parent_id = reply_to.id if isinstance(reply_to, Message) else reply_to
        payload = {
            "recipient": self.name,
            "body": body,
            "subject": subject,
            "parent_id": parent_id,
        }
        self._imgur.send_request(url, params=payload, needs_auth=True, method="POST")

    def send_verification_email(self):
        """
        Send verification email to this users email address.

        Remember that the verification email may end up in the users spam
        folder.
        """
        url = f"{self._imgur.base_url}/3/account/{self.name}/verifyemail"
        self._imgur.send_request(url, needs_auth=True, method="POST")
