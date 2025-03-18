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
import re
from urllib.parse import urlparse

from pyimgur import request
from pyimgur.conversion import clean_imgur_params, get_content_to_send
from pyimgur.exceptions import (
    AuthenticationError,
    InvalidParameterError,
    ResourceNotFoundError,
)
from pyimgur.image import Image
from pyimgur.objects import (
    Album,
    Notification,
    Comment,
    Message,
    Gallery_item,
    Gallery_album,
    Gallery_image,
    User,
)

__version__ = "0.7.1"

RAPIDAPI_BASE = "https://imgur-apiv3.p.rapidapi.com"
IMGUR_BASE = "https://api.imgur.com"

AUTHORIZE_URL = "{}/oauth2/authorize?client_id={}&response_type={}&state={}"
EXCHANGE_URL = "{}/oauth2/token"
REFRESH_URL = "{}/oauth2/token"


class Imgur:  # pylint: disable=too-many-instance-attributes,too-many-public-methods
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
        # Mashape KEY can no longer be used as Imgur has dropped support for it.
        # Keeping it here for a few releases to reduce number of releases with
        # breaking changes.
        mashape_key=None,
        rapidapi_key=None,
    ):  # pylint: disable=too-many-arguments,too-many-positional-arguments
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
        """
        self.is_authenticated = False
        self.access_token = access_token
        self.client_id = client_id
        self.client_secret = client_secret
        self.DEFAULT_LIMIT = 100  # pylint: disable=invalid-name
        self.ratelimit_clientlimit = None
        self.ratelimit_clientremaining = None
        self.ratelimit_userlimit = None
        self.ratelimit_userremaining = None
        self.ratelimit_userreset = None
        self.refresh_token = refresh_token
        self.mashape_key = mashape_key
        self.rapidapi_key = rapidapi_key
        self.base_url = RAPIDAPI_BASE if self.rapidapi_key else IMGUR_BASE

    def send_request(
        self, url, needs_auth=False, **kwargs
    ):  # pylint: disable=too-many-branches
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
        if self.access_token is None and needs_auth:
            raise AuthenticationError(
                "Authentication as a user is required to use this method."
            )

        if self.access_token is None:
            # Not authenticated as a user. Use anonymous access.
            authentication = {"Authorization": f"Client-ID {self.client_id}"}
        else:
            authentication = {"Authorization": f"Bearer {self.access_token}"}
        if self.mashape_key:
            authentication.update({"X-Mashape-Key": self.mashape_key})
        if self.rapidapi_key:
            authentication.update({"X-Mashape-Key": self.rapidapi_key})

        content = []
        is_paginated = False
        base_url = url

        if "limit" in kwargs:
            is_paginated = True

            limit = kwargs["limit"]
            if not limit or limit < 0:
                limit = self.DEFAULT_LIMIT

            del kwargs["limit"]
            page = 0
            url = url.format(page)

        kwargs["params"] = clean_imgur_params(kwargs.get("params", {}))
        content_to_send = get_content_to_send(**kwargs)

        while True:
            new_content, ratelimit_info = request.send_request(
                url,
                method=kwargs.get("method", "GET"),
                content_to_send=content_to_send,
                headers=authentication,
            )

            if (
                is_paginated
                and new_content
                and limit > (len(new_content) + len(content))
            ):
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
        return AUTHORIZE_URL.format(self.base_url, self.client_id, response, state)

    def change_authentication(
        self, client_id=None, client_secret=None, access_token=None, refresh_token=None
    ):
        """Change the current authentication."""
        if not (
            (client_id is None) == (client_secret is None)
        ):  # pylint: disable=superfluous-parens
            raise InvalidParameterError(
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
        url = self.base_url + "/3/album/"
        payload = {
            "ids": images,
            "title": title,
            "description": description,
            "cover": cover,
        }

        resp = self.send_request(
            url, params=payload, method="POST", as_json=True, use_form_data=True
        )
        return Album(resp, self, has_fetched=False)

    def exchange_code(self, code):
        """Exchange one-use code for an access_token and request_token."""
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code",
            "code": code,
        }
        result = self.send_request(
            EXCHANGE_URL.format(self.base_url),
            params=params,
            method="POST",
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
        result = self.send_request(
            EXCHANGE_URL.format(self.base_url),
            params=params,
            method="POST",
        )
        self.access_token = result["access_token"]
        self.refresh_token = result["refresh_token"]
        return self.access_token, self.refresh_token

    def get_album(self, album_id):
        """Return information about this album."""
        url = self.base_url + f"/3/album/{album_id}"
        json = self.send_request(url)
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

        def get_gallery_item(gallery_item_id):
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
                return self.get_gallery_image(gallery_item_id)
            except ResourceNotFoundError:
                return self.get_gallery_album(gallery_item_id)

        if not self.is_imgur_url(url):
            return None

        objects = {
            "album": {"regex": r"a/(?P<id>[\w.]*?)$", "method": self.get_album},
            "comment": {
                "regex": r"gallery/\w*/comment/(?P<id>[\w.]*?)$",
                "method": self.get_comment,
            },
            "gallery": {
                "regex": r"(gallery|r/\w*?)/(?P<id>[\w.]*?)$",
                "method": get_gallery_item,
            },
            # Valid image extensions: http://imgur.com/faq#types
            # All are between 3 and 4 chars long.
            "image": {
                "regex": r"(?P<id>[\w.]*?)(\\.\w{3,4})?$",
                "method": self.get_image,
            },
            "user": {"regex": r"user/(?P<id>[\w.]*?)$", "method": self.get_user},
        }
        parsed_url = urlparse(url)
        for obj_type, values in objects.items():
            regex_result = re.match("/" + values["regex"], parsed_url.path)
            if regex_result is not None:
                obj_id = regex_result.group("id")
                initial_object = values["method"](obj_id)

                # We cannot diffrentiate image from GalleryImage based on the url,
                # so first we assume it's an image. Then we try to fetch it as a
                # gallery image / subreddit image. If that fails, then we know it's
                # an image.
                if obj_type == "image":
                    try:
                        if getattr(initial_object, "section", None):
                            sub = initial_object.section
                            return self.get_subreddit_image(sub, obj_id)
                        return self.get_gallery_image(obj_id)
                    except ResourceNotFoundError:
                        pass
                return initial_object

    def get_comment(self, comment_id):
        """Return information about this comment."""
        url = self.base_url + f"/3/comment/{comment_id}"
        json = self.send_request(url)
        return Comment(json, self)

    def get_gallery(
        self, section="hot", sort="viral", window="day", show_viral=True, limit=None
    ):  # pylint: disable=too-many-arguments,too-many-positional-arguments
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
        url = (
            self.base_url
            + f"/3/gallery/{section}/{sort}/{window}/{{}}?showViral={show_viral}"
        )
        resp = self.send_request(url, limit=limit)
        return [Gallery_item.get_album_or_image(thing, self) for thing in resp]

    def get_gallery_album(self, gallery_album_id):
        """
        Return the gallery album.

        Note that an album's id is different from it's id as a gallery album.
        This makes it possible to remove an album from the gallery and setting
        it's privacy setting as secret, without compromising it's secrecy.
        """
        url = self.base_url + f"/3/gallery/album/{gallery_album_id}"
        resp = self.send_request(url)
        return Gallery_album(resp, self)

    def get_gallery_image(self, gallery_item_id):
        """
        Return the gallery image matching the id.

        Note that an image's id is different from it's id as a gallery image.
        This makes it possible to remove an image from the gallery and setting
        it's privacy setting as secret, without compromising it's secrecy.
        """
        url = self.base_url + f"/3/gallery/image/{gallery_item_id}"
        resp = self.send_request(url)
        return Gallery_image(resp, self)

    def get_image(self, image_id):
        """Return a Image object representing the image with the given id."""
        url = self.base_url + f"/3/image/{image_id}"
        resp = self.send_request(url)
        return Image(resp, self)

    def get_message(self, message_id):
        """
        Return a Message object for given id.

        :param id: The id of the message object to return.
        """
        url = self.base_url + f"/3/message/{message_id}"
        resp = self.send_request(url)
        return Message(resp, self)

    def get_notification(self, notification_id):
        """
        Return a Notification object.

        :param id: The id of the notification object to return.
        """
        url = self.base_url + f"/3/notification/{notification_id}"
        resp = self.send_request(url)
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
        url = self.base_url + f"/3/gallery/g/memes/{sort}/{window}/{'{}'}"
        resp = self.send_request(url, limit=limit)
        return [Gallery_item.get_album_or_image(thing, self) for thing in resp]

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
        url = f"{self.base_url}/3/gallery/r/{subreddit}/{sort}/{window}/{'{}'}"
        resp = self.send_request(url, limit=limit)
        return [Gallery_item.get_album_or_image(thing, self) for thing in resp]

    def get_subreddit_image(self, subreddit, image_id):
        """
        Return the Gallery_image with the id submitted to subreddit gallery

        :param subreddit: The subreddit the image has been submitted to.
        :param image_id: The id of the image we want.
        """
        url = self.base_url + f"/3/gallery/r/{subreddit}/{image_id}"
        resp = self.send_request(url)
        return Gallery_image(resp, self)

    def get_user(self, username):
        """
        Return a User object for this username.

        :param username: The name of the user we want more information about.
        """
        url = self.base_url + f"/3/account/{username}"
        json = self.send_request(url)
        return User(json, self)

    def is_imgur_url(self, url):
        """Is the given url a valid Imgur url?"""
        return re.match(r"(http://)?(www\.)?imgur\.com", url, re.I) is not None

    def refresh_access_token(self):
        """
        Refresh the access_token.

        The self.access_token attribute will be updated with the value of the
        new access_token which will also be returned.
        """
        if self.client_secret is None:
            raise AuthenticationError(
                "client_secret must be set to execute refresh_access_token."
            )
        if self.refresh_token is None:
            raise AuthenticationError(
                "refresh_token must be set to execute refresh_access_token."
            )
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
        }
        result = self.send_request(
            REFRESH_URL.format(self.base_url),
            params=params,
            method="POST",
        )
        self.access_token = result["access_token"]
        return self.access_token

    def search_gallery(self, q):
        """Search the gallery with the given query string."""
        url = self.base_url + f"/3/gallery/search?q={q}"
        resp = self.send_request(url)
        return [Gallery_item.get_album_or_image(thing, self) for thing in resp]

    def upload_image(
        self, path=None, url=None, title=None, description=None, album=None
    ):  # pylint: disable=too-many-arguments,too-many-positional-arguments
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
            raise InvalidParameterError("Either path or url must be given.")

        payload = {
            "album_id": album,
            "image_path": path,
            "image": url,
            "title": title,
            "description": description,
        }

        resp = self.send_request(
            self.base_url + "/3/image", params=payload, method="POST"
        )

        resp["title"] = title
        resp["description"] = description
        if album is not None:
            resp["album"] = (
                Album({"id": album}, self, False)
                if not isinstance(album, Album)
                else album
            )
        return Image(resp, self)
