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
easier and less frustrating by automatically handle a lot of stuff for you. For
instance you'll only need to use your client_id when you instantiate the Imgur
object and when changing authentication. For the REST API this value needs to
be sent with every request, but PyImgur handles this automatically for you.

Before using PyImgur, or the Imgur REST API in general, you'll first need to
register your application here: https://api.imgur.com/oauth2/addclient

For more information on usage visit https://github.com/Damgaard/PyImgur
"""


from base64 import b64encode
from decorator import decorator
import os.path
import re

import requests

import request

# Note: Maybe base_object.imgur should instead be base_object._imgur ?
# eg. private since it not for public consumption


def _get_album_or_image(json, imgur):
    """Return a gallery image/album depending on what the json represent."""
    if json['is_album']:
        return Gallery_album(json, imgur)
    return Gallery_image(json, imgur)


@decorator
def _require_auth(func, obj, *args, **kwargs):
    """This method requires that we've successfully authenticated as a user."""
    imgur = obj if isinstance(obj, Imgur) else obj.imgur
    if not imgur.is_authenticated:
        raise Exception("Login required to use this method.")


class Basic_object(object):
    """Contains the basic functionality shared by a lot of PyImgurs classes."""
    def __init__(self, json_dict, imgur, has_fetched=True):
        self._has_fetched = has_fetched
        self.imgur = imgur
        self._populate(json_dict)

    def __getattr__(self, attribute):
        if not self._has_fetched:
            self.refresh()
            self._has_fetched = True
            return getattr(self, attribute)
        raise AttributeError("%s instance has no attribute '%s'" %
                             (type(self).__name__, attribute))

    def __repr__(self):
        return "<%s %s>" % (type(self).__name__, self.id)

    def _populate(self, json_dict):
        for key, value in json_dict.iteritems():
            setattr(self, key, value)
        # TODO: ups will need to be likes, because that's what the webinterface
        # is. But we also have "voted" which is the current users vote on it.
        # Update certain attributes for certain objects, to be link to lazily
        # created objects rather than a string of ID or similar.
        if isinstance(self, Album) or isinstance(self, Image):
            if "favorite" in vars(self):
                self.has_favorited = self.favorite
                del self.favorite
            if "nsfw" in vars(self):
                self.is_nsfw = self.nsfw
                del self.nsfw
        if isinstance(self, Album):
            if "account_url" in vars(self):
                self.author = User({'url': self.account_url}, self.imgur,
                                   has_fetched=False)
                del self.account_url
            if "cover" in vars(self):
                self.cover = Image({'id': self.cover}, self.imgur,
                                   has_fetched=False)
            if "images" in vars(self):
                self.images = [Image(img, self.imgur, has_fetched=False) for
                               img in self.images]
        elif isinstance(self, Comment):
            if "author" in vars(self):
                self.author = User({'url': self.author}, self.imgur,
                                   has_fetched=False)
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
                self.replies = [Comment(com, self.imgur) for com in
                                self.children]
                del self.children
            if "image_id" in vars(self):
                self.permalink = ("http://imgur.com/gallery/%s/comment/%d" %
                                 (self.image_id, self.id))
                self.image = Image({'id': self.image_id}, self.imgur,
                                   has_fetched=False)
                del self.image_id
            if "parent_id" in vars(self):
                self.parent_comment = Comment({'id': self.parent_id},
                                              self.imgur, has_fetched=False)
                del self.parent_id
        elif isinstance(self, Gallery_image):
            if "account_url" in vars(self):
                self.author = User({'url': self.account_url}, self.imgur,
                                   has_fetched=False)
                del self.account_url
        elif isinstance(self, Image):
            if "animated" in vars(self):
                self.is_animated = self.animated
                del self.animated
            if "link" in vars(self):
                base, sep, ext = self.link.rpartition('.')
                self.link_small_square = base + "s" + sep + ext
                self.link_big_square = base + "b" + sep + ext
                self.link_small_thumbnail = base + "t" + sep + ext
                self.link_medium_thumbnail = base + "m" + sep + ext
                self.link_large_thumbnail = base + "l" + sep + ext
                self.link_huge_thumbnail = base + "h" + sep + ext
        elif isinstance(self, User) and 'url' in vars(self):
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
        Refresh this object with the newest values.

        For instance, a User reputation may have changed in the time since the
        creating the object. Calling this function would update the reputation
        to the newest correct value.

        If the variables weren't loaded, due to lazy loading, then this call
        will force a call to imgur and update the object with all the
        attributes.
        """
        resp = self.imgur._send_request(self._INFO_URL)
        self._populate(resp)


class Album(Basic_object):
    """
    An album is a collection of images.

    :ivar author: The user that authored the album. None if anonymous.
    :ivar cover: The albums cover image.
    :ivar datetime: Time inserted into the gallery, epoch time
    :ivar deletehash: For anonymous uploads, this is used to delete the album.
    :ivar description: A short description of the album.
    :ivar has_favorited: Has the logged in user favorited this album?
    :ivar id: The ID for the album.
    :ivar images: A list of the images in this album.
    :ivar images_count: The total number of images in the album.
    :ivar is_nsfw: Is the album Not Safe For Work (contains gore/porn)?
    :ivar layout: The view layout of the album.
    :ivar link: The URL link to the album
    :ivar public: The privacy level of the album, you can only view public if
                  not logged in as album owner
    :ivar section: No info in Imgur documentation.
    :ivar title: The Albums title
    :ivar views: Total number of views the album has received.
    """
    def __init__(self, json_dict, imgur, has_fetched=True):
        self._INFO_URL = ("https://api.imgur.com/3/album/%s" % json_dict['id'])
        self.deletehash = None
        super(Album, self).__init__(json_dict, imgur, has_fetched)

    @_require_auth
    def add_images(self, ids):
        """
        Add images to the album.

        :param ids: A list of the image id we want to add to the album.
        """
        pass

    def delete(self):
        """Delete this album."""
        url = "https://api.imgur.com/3/album/%s" % self.deletehash
        return self.imgur._send_request(url, method="DELETE")

    @_require_auth
    def favorite(self):
        """Favorite the album."""
        pass

    @_require_auth
    def remove_images(self, ids):
        """
        Remove images from the album.

        :param ids: A list of the image id we want to remove from the album.
        """
        pass

    @_require_auth
    def set_images(self, ids):
        """
        Set the images in this album.

        :param ids: The list of images the album will now consists of.
        """
        pass

    @_require_auth
    def submit_to_gallery():
        """
        Add this to the gallery.

        Requires that we have verified our email address and accepted the
        Gallery terms of services.
        """
        pass

    def update(self, title=None, description=None, ids=None, cover=None,
               layout=None, privacy=None):
        """
        Update the albums information.

        Arguments with the value None will retain their old values.

        :param title: The title of the album.
        :param description: A description of the album.
        :param privacy: The albums privacy level, can be public, hidden or
            secret.
        :param cover: The id of the cover image.
        :param layout: The way the album is displayed, can be blog, grid,
            horizontal or vertical.
        """
        url = "https://api.imgur.com/3/album/%s" % self.deletehash
        payload = {'title': title, 'description': description,
                   'ids': ids, 'cover': cover,
                   'layout': layout, 'privacy': privacy}
        is_updated = self.imgur._send_request(url, params=payload, method='POST')
        if is_updated:
            self.title = title or self.title
            self.description = description or self.description
            self.layout = layout or self.layout
            self.privacy = privacy or self.privacy
            if cover is not None:
                self.cover = Image(cover)
            if ids:
                self.images = [Image(img, self.imgur) for img in ids]
        return is_updated


class Comment(Basic_object):
    """
    A Comment a user has made.

    Users can commit on Gallery album, Gallery image or other Comment.

    :ivar album_cover: The ID of the album cover image, this is what should be displayed for album comment
    :ivar author: The user that created the comment.
    :ivar comment: The comment text.
    :ivar datetime: Time inserted into the gallery, epoch time
    :ivar deletehash: For anonymous uploads, this is used to delete the image.
    :ivar downs: The total number of dislikes (downvotes) the comment has received.
    :ivar image: The image the comment belongs to.
    :ivar on_album: Is the image part of a album.
    :ivar parent_comment: The comment this one has replied to.
    :ivar permalink: A permanent link to the comment.
    :ivar points: ups - downs
    :ivar replies: A list of comment replies to this comment.
    :ivar ups: The total number of likes (upvotes) the comment has received.
    :ivar vote: The currently logged in users vote on the comment
    """
    # NOTE: I think parent_comment in a comment is 0 when it is a root level
    # comment and so has no parents. It should probably be None instead.
    def __init__(self, json_dict, imgur, has_fetched=True):
        self.deletehash = None
        self._INFO_URL = ("https://api.imgur.com/3/comment/%s" %
                          json_dict['id'])
        super(Comment, self).__init__(json_dict, imgur, has_fetched)

    @_require_auth
    def delete(self):
        """Delete the comment."""
        pass

    @_require_auth
    def downvote(self):
        """Downvote this comment."""
        pass

    def get_replies(self):
        """Create a reply for the given comment."""
        url = "https://api.imgur.com/3/comment/%s/replies" % self.id
        json = self.imgur._send_request(url)
        child_comments = json['children']
        return [Comment(com, self.imgur) for com in child_comments]

    # Question. Can you only reply to images? If you can comment on other
    # comments, then how do you do that? Use comment_id instead of image_id?
    # It's clearly possible to reply to a comment.
    # http://imgur.com/gallery/LA2RQqp/comment/49538390
    # If it is image_only, then this should probably be moved to Image
    def reply(self, image_id, text):
        """Create a reply for the given comment."""
        pass

    @_require_auth
    def report(self):
        """Reply comment for being inappropriate."""
        pass

    @_require_auth
    def upvote(self):
        """Upvote this comment."""
        pass


class Gallery_item(object):
    """Functionality shared by Gallery_image and Gallery_album."""
    @_require_auth
    def comment(self, comment):
        """
        Make a top-level comment to this.

        :param text: The comment text.
        """
        pass

    @_require_auth
    def downvote(self):
        """Dislike this."""
        pass

    def get_comment_count(self):
        # So far I've decided not to implement this and get_comment_ids. Their
        # functionality seems covered by get_comments on the assumption that
        # there is no limit to the number of comments returned.
        raise NotImplementedError("Use len(get_comments) instead")

    def get_comment_ids(self):
        raise NotImplementedError("Use get_comments instead to return the "
                                  "Comment objects and retrieve the ids from "
                                  "that call")

    def get_comments(self):
        """Get a list of the top-level comments."""
        url = "https://api.imgur.com/3/gallery/%s/comments" % self.id
        resp = self.imgur._send_request(url)
        return [Comment(com, self.imgur) for com in resp]

    @_require_auth
    def upvote(self):
        """Like this."""
        pass


class Image(Basic_object):
    """
    A image uploaded to imgur.

    :ivar bandwidth: Bandwidth consumed by the image in bytes
    :ivar datetime: Time inserted into the gallery, epoch time
    :ivar deletehash: For anonymous uploads, this is used to delete the image.
    :ivar description: A short description of the image.
    :ivar has_favorited: Has the logged in user favorited this album?
    :ivar height: The height of the image in pixels
    :ivar id: The ID for the image.
    :ivar is_animated: is the image animated?
    :ivar is_nsfw: Is the image Not Safe For Work (contains gore/porn)?
    :ivar link: The URL link to the image
    :ivar link_big_square: The URL to a big square thumbnail of the image.
    :ivar link_huge_thumbnail: The URL to a huge thumbnail of the image.
    :ivar link_large_square: The URL to a large square thumbnail of the image.
    :ivar link_large_thumbnail: The URL to a large thumbnail of the image.
    :ivar link_medium_thumbnail: The URL to a medium thumbnail of the image.
    :ivar link_small_square: The URL to a small square thumbnail of the image.
    :ivar section: ???
    :ivar size: The size of the image in bytes
    :ivar title: The Albums title
    :ivar views: Total number of views the album has received.
    :ivar width: The width of the image in bytes
    """
    def __init__(self, json_dict, imgur, has_fetched=True):
        self._INFO_URL = ("https://api.imgur.com/3/image/%s" % json_dict['id'])
        self.deletehash = None
        super(Image, self).__init__(json_dict, imgur, has_fetched)

    def delete(self):
        """Delete the image."""
        return self.imgur._send_request("https://api.imgur.com/3/image/%s" %
                                        self.deletehash, method='DELETE')

    def download(self, path='', name=None, overwrite=False, size=None):
        """
        Download the image.

        :param path: The image will be downloaded to the folder specified at
            path, if path is None (default) then the current working directory
            will be used.
        :param name: The name the image will be stored as (not including file
            extensions). If it's None, then the name of the Image will be used
            as Name. If it doesn't have a title, it's id will be used instead.
        :param overwrite: If True already existing file with the same name as
            what we want to store the file as will be overwritten.  will be
            overwritten when we download a new image with the same name.
        :param size: Instead of downloading the image in it's original size, we
            may choose to instead download a thumbnail of it. Options are
            'small_square', 'big_square', 'small_thumbnail',
            'medium_thumbnail', 'large_thumbnail' or 'huge_thumbnail'.

        :returns: Name of the new file.
        """
        valid_sizes = {'small_square': 's', 'big_square': 'b',
                       'small_thumbnail': 't', 'medium_thumbnail': 'm',
                       'large_thumbnail': 'l', 'huge_thumbnail': 'h'}
        if size is not None:
            size = size.lower().replace(' ', '_')
            if size not in valid_sizes:
                raise LookupError('Invalid size. Valid options are: %s' % ", "
                                  .join(valid_sizes.keys()))
        suffix = valid_sizes.get(size, '')
        base, sep, ext = self.link.rpartition('.')
        resp = requests.get(base + suffix + sep + ext)
        filename = (name or self.title or self.id) + suffix + sep + ext
        local_path = os.path.join(path, filename)
        if os.path.exists(local_path) and not overwrite:
            raise Exception("Trying to save as %s, but file already exists." %
                            local_path)
        with open(local_path, 'wb') as out_file:
            out_file.write(resp.content)
        return local_path

    @_require_auth
    def favorite(self):
        """Favorite the image."""
        pass

    @_require_auth
    def remove_from_gallery():
        """Remove this image from the gallery."""
        # TODO. Text implies this is image only and won't work with albums.
        # Confirm
        pass

    @_require_auth
    def submit_to_gallery():
        """Add this to the gallery."""
        pass

    def update(self, title=None, description=None):
        """Update the image with a new title and/or description."""
        payload = {'title': title, 'description': description}
        url = "https://api.imgur.com/3/image/%s" % self.deletehash
        is_updated = self.imgur._send_request(url, params=payload,
                                              method='POST')
        if is_updated:
            self.title = title or self.title
            self.description = description or self.description
        return is_updated


class Imgur:
    """
    The base class containing general functionality for Imgur.

    You should create an Imgur object at the start of your code and use it to
    interact with imgur. You shouldn't directly initialize any other classes,
    but instead use the methods in this class to get them.
    """
    def __init__(self, client_id, client_secret=None, access_token=None,
                 refresh_token=None):
        """
        Initialize the Imgur object.

        Before using PyImgur, or the imgur api in general, you need to register
        your application with Imgur. This can be done at
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
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.ratelimit_clientlimit = None
        self.ratelimit_clientremaining = None
        self.ratelimit_userlimit = None
        self.ratelimit_userremaining = None
        self.ratelimit_userreset = None
        self.DEFAULT_LIMIT = 100

    def _send_request(self, url, *args, **kwargs):
        """Handles sending requests to Imgur and updates ratelimit info."""
        if self.access_token is None:
            # Not authenticated as a user. Use anonymous access.
            auth = {'Authorization': 'Client-ID %s' % self.client_id}
        else:
            auth = {'Authorization': 'Bearer %s' % self.access_token}
        content = []
        is_paginated = False
        if 'limit' in kwargs:
            is_paginated = True
            limit = kwargs['limit'] or self.DEFAULT_LIMIT
            del kwargs['limit']
            page = 0
            base_url = url
            url %= page
        kwargs['authentication'] = auth
        while True:
            result = request.send_request(url, *args, **kwargs)
            new_content, ratelimit_info = result
            if is_paginated and new_content and limit > len(new_content):
                content += new_content
                page += 1
                url = base_url % page
            else:
                if is_paginated:
                    content = (content + new_content)[:limit]
                else:
                    content = new_content
                break
        # Disable ratelimit info as it seems it stopped being included in the
        # returned information from 9-05-2013
        # self.ratelimit_clientlimit = ratelimit_info['x-ratelimit-clientlimit']
        # self.ratelimit_clientremaining = ratelimit_info['x-ratelimit-'
        #                                                 'clientremaining']
        # self.ratelimit_userlimit = ratelimit_info['x-ratelimit-userlimit']
        # self.ratelimit_userremaining = ratelimit_info['x-ratelimit-'
        #                                               'userremaining']
        # self.ratelimit_userreset = ratelimit_info['x-ratelimit-userreset']
        # Note: When the cache is implemented, it's important that the
        # ratelimit info doesn't get updated with the ratelimit info in the
        # cache since that's likely incorrect.
        return content

    def change_authentication(self, client_id=None, client_secret=None,
                              access_token=None, refresh_token=None):
        """Change the current authentication."""
        self.client_id = client_id or self.client_id
        self.client_secret = client_secret or self.client_secret
        self.access_token = access_token or self.access_token
        self.refresh_token = refresh_token or self.refresh_token

    def create_album(self, title=None, description=None, ids=None, cover=None):
        """
        Create a new Album.

        :param title: The title of the album.
        :param description: The albums describtion.
        :param ids: A list of image ids that will be added to the image after
            it's been created.
        :param cover: The id of the image you want as the albums cover image.
        :returns: The newly created album.
        """
        url = "https://api.imgur.com/3/album/"
        payload = {'ids': ids, 'title': title,
                   'description': description, 'cover': cover}
        resp = self._send_request(url, params=payload, method='POST')
        return Album(resp, self, has_fetched=False)

    @_require_auth
    def create_user(self, username):
        """Create this user on Imgur."""
        pass

#    def get_at_url(self, url):
#        """Return whatever is at the imgur url as an object."""
#        pass

    def get_album(self, id):
        """Return information about this album."""
        json = self._send_request("https://api.imgur.com/3/album/%s" % id)
        return Album(json, self)

    def get_comment(self, id):
        """Return information about this comment."""
        url = "https://api.imgur.com/3/comment/%s" % id
        json = self._send_request(url)
        return Comment(json, self)

    def get_gallery(self, section='hot', sort='viral', window='day',
                    show_viral=True, limit=None):
        """
        Return the albums and and images in the gallery.

        :param section: hot | top | user - defaults to hot
        :param sort: viral | time - defaults to viral
        :param window: Change the date range of the request if the section is
            "top", day | week | month | year | all, defaults to day
        :param show_viral: true | false - Show or hide viral images from the
            'user' section. Defaults to true
        """
        url = ("https://api.imgur.com/3/gallery/%s/%s/%s/%s?showViral=%s" %
               (section, sort, window, '%d', show_viral))
        resp = self._send_request(url, limit=limit)
        return [_get_album_or_image(thing, self) for thing in resp]

    def get_gallery_album(self, id):
        """
        Return the gallery album matching the id.

        Note that an albums id is different from it's id as a gallery album.
        This makes it possible to remove an album from the gallery and setting
        it as secret, without compromising it's secrecy.
        """
        url = "https://api.imgur.com/3/gallery/album/%s" % id
        resp = self._send_request(url)
        return Gallery_album(resp, self)

    def get_gallery_image(self, id):
        """
        Return the gallery image matching the id.

        Note that an images id is different from it's id as a gallery image.
        This makes it possible to remove an imaeg from the gallery and setting
        it as secret, without compromising it's secrecy.
        """
        url = "https://api.imgur.com/3/gallery/image/%s" % id
        resp = self._send_request(url)
        return Gallery_image(resp, self)

    def get_image(self, id):
        """Return a Image object representing the image with id."""
        resp = self._send_request("https://api.imgur.com/3/image/%s" % id)
        return Image(resp, self)

    def get_subreddit_gallery(self, subreddit, sort='time', window='top',
                              limit=None):
        """View gallery images for a subreddit."""
        url = ("https://api.imgur.com/3/gallery/r/%s/%s}/%s/%s" %
               (subreddit, sort, window, '%d'))
        resp = self._send_request(url, limit=limit)
        return [_get_album_or_image(thing, self) for thing in resp]

    def get_subreddit_image(self):
        """View a single image in the subreddit."""
        # I think this duplicates get_gallery_image. So there should be no
        # reason to implement it.
        pass

    def get_user(self, username):
        """
        Return information about this user.

        :param username: The name of the user we want more information about.
        """
        url = "https://api.imgur.com/3/account/%s" % username
        json = self._send_request(url)
        return User(json, self)

    def is_imgur_url(self, url):
        """Is the given url a valid imgur url?"""
        return re.match("(http://)?(www\.)?imgur\.com", url, re.I) is not None

    def search_gallery(self, q):
        """Search the gallery with the given query string."""
        url = "https://api.imgur.com/3/gallery/search?q=%s" % q
        resp = self._send_request(url)
        return [_get_album_or_image(thing, self) for thing in resp]

    def upload_image(self, path, title=None, description=None, album_id=None):
        """Upload the image at path and return it."""
        with open(path, 'rb') as image_file:
            binary_data = image_file.read()
            image = b64encode(binary_data)

        payload = {'album_id': album_id, 'image': image,
                   'title': title, 'description': description}

        resp = self._send_request("https://api.imgur.com/3/image",
                                  params=payload, method='POST')
        return Image(resp, self, False)


class Message(object):
    """This corresponds to the messages users can send each other."""
    # Requires login to test
    def __init__(self, json_dict, imgur):
        # Is never gotten lazily, so _has_fetched is always True
        super(Message, self).__init__(json_dict, imgur, True)


class Notification(object):
    """
    This corresponds to the notifications a user may receive.

    A notification can come for several reasons. For instance, one may be
    received if someone replies to one of your comments.
    """
    # Requires login to test
    def __init__(self, json_dict, imgur):
        # Is never gotten lazily, so _has_fetched is always True
        super(Notification, self).__init__(json_dict, imgur, True)


class User(Basic_object):
    """
    A User on Imgur.

    :ivar bio: A basic description the user has filled out.
    :ivar created: The epoch time of user account creation
    :ivar id: The user id.
    :ivar name: The user name
    :ivar reputation: The reputation for the user, in it's numerical format.
    """
    def __init__(self, json_dict, imgur, has_fetched=True):
        self._INFO_URL = ("https://api.imgur.com/3/account/%s" %
                          json_dict['url'])
        super(User, self).__init__(json_dict, imgur, has_fetched)

    # Overrides __repr__ method in Basic_object
    def __repr__(self):
        return "<%s %s>" % (type(self).__name__, self.name)

    @_require_auth
    def change_settings(self, bio=None, public_images=None,
                        messaging_enabled=None, album_privacy=None,
                        accepted_gallery_terms=None):
        """
        Update the settings for the user.

        If the argument is None, then current value is retained.

        :param bio: The biography of the user, is displayed in the gallery
            profile page.
        :param public_images: Set the users images to private or public by
            default
        :param messaging_enabled: Set to True to enable messaging.
        :param album_privacy: The default privacy level of albums created by
            the user.
        :param accepted_gallery_terms: The user has agreed to the Imgur Gallery
            terms. This is necessary before the user can submit to the gallery.
        """

        # NOTE: album_privacy should maybe be renamed to default_privacy
        pass

    @_require_auth
    def delete(self):
        """Delete this user."""
        pass

    def get_album_count(self):
        """Get the Number of albums this user has."""
        # See get_comment_count for comment on non-implementation
        raise NotImplementedError("Use len(get_albums) instead.")

    def get_album_ids(self):
        """Get a list of the users albums ids."""
        # See get_comment_ids for comment on non-implementation
        raise NotImplementedError("Use get_albums instead to return the "
                                  "Album objects and retrieve the ids from "
                                  "that call")

    def get_albums(self, limit=None):
        """
        Return the users albums.

        Secret and hidden albums are only returned if this is the logged-in
        user.
        """
        url = "https://api.imgur.com/3/account/%s/albums/%s" % (self.name,
                                                                '%d')
        resp = self.imgur._send_request(url, limit=limit)
        return [Album(alb, self.imgur) for alb in resp]

    def get_comments(self):
        """Return the comments made by the user."""
        url = "https://api.imgur.com/3/account/%s/comments" % self.name
        resp = self.imgur._send_request(url)
        return [Comment(com, self.imgur) for com in resp]

    def get_comment_count(self):
        """Get the number of comments this user has made."""
        # See the other get_comment_count for non-implementing reasoning
        raise NotImplementedError("Use len(get_comments) instead")

    def get_comment_ids(self):
        """Get a list of the users comments ids."""
        # See the other get_comment_ids for non-implementing reasoning
        raise NotImplementedError("Use get_comments instead to return the "
                                  "Comment objects and retrieve the ids from "
                                  "that call")

    @_require_auth
    def get_favorites(self):
        """Return the users favorited images."""
        pass

    def get_gallery_favorites(self):
        """Get a list of the images in the gallery this user has favorited."""
        url = ("https://api.imgur.com/3/account/%s/gallery_favorites" %
               self.name)
        resp = self.imgur._send_request(url)
        return [Image(img, self.imgur) for img in resp]

    def get_gallery_profile(self):
        """Return the users gallery profule."""
        url = "https://api.imgur.com/3/account/%s/gallery_profile" % self.name
        return self.imgur._send_request(url)

    @_require_auth
    def has_verified_email(self):
        """
        Has the user verified that the email he has given is legit?

        A user with verified e-mail may post to the gallery. Confirmation
        happens by sending an email to the user and the owner of the email
        user verifying that he is the same as the imgur user.
        """
        pass

    def get_images(self, limit=None):
        """Return all of the images associated with the user."""
        url = "https://api.imgur.com/3/account/%s/images/%s" % (self.name,
                                                                '%d')
        resp = self.imgur._send_request(url, limit=limit)
        return [Image(img, self.imgur) for img in resp]

    def get_image_count(self):
        """Get the number of images this user has on imgur."""
        # See the other get_comment_count for non-implementing reasoning
        raise NotImplementedError("Use len(get_images) instead")

    def get_images_ids(self):
        """Get a list of image ids this user has on imgur."""
        # See the other get_comment_ids for non-implementing reasoning
        raise NotImplementedError("Use get_images instead to return the "
                                  "Image objects and retrieve the ids from "
                                  "that call")

    @_require_auth
    def get_messages(new=True):
        """
        Return all messages sent to this user.

        :param new: False for all notifications, True for only non-viewed
            notification.
        """
        pass

    @_require_auth
    def get_notifications(new=True):
        """Return all the notifications for this user."""
        pass

    @_require_auth
    def get_replies():
        """Return all reply notifications for the user."""
        pass

    def get_submissions(self, limit=None):
        """Return the images a user has submitted to the gallery."""
        url = "https://api.imgur.com/3/account/%s/submissions/%s" % (self.name,
                                                                     '%d')
        resp = self.imgur._send_request(url, limit=limit)
        return [_get_album_or_image(thing, self.imgur) for thing in resp]

    @_require_auth
    def get_statistics(self):
        """Return the statistics about the user."""
        url = "https://api.imgur.com/3/account/%s/stats" % self.name
        return self.imgur._send_request(url)

    def send_message(body, subject=None, parent_id=None):
        """Send a message to this user from the logged in user."""
        pass

    @_require_auth
    def send_verification_email(self):
        """Send verification email to this users email address."""
        pass


# Gallery_album and Gallery_image are placed at the end as they need to inherit
# from Gallery_item, Album and Image. It's thus impossible to place them
# alphabetically without errors.
class Gallery_album(Album, Gallery_item):
    """Gallery Albums are albums submitted to the gallery."""
    def __init__(self, json_dict, imgur):
        self._INFO_URL = ("https://api.imgur.com/3/gallery/album/%s" %
                          json_dict['id'])
        super(Gallery_album, self).__init__(json_dict, imgur)


class Gallery_image(Image, Gallery_item):
    """Gallery images are images submitted to the gallery."""
    def __init__(self, json_dict, imgur):
        self._INFO_URL = ("http://api.imgur.com/3/gallery/image/%s" %
                          json_dict['id'])
        super(Gallery_image, self).__init__(json_dict, imgur)
