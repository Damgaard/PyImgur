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

from base64 import b64encode
import re

from cache import Default_cache
import request


# Needs to be moved into another file or to be standard behaviour in a clas
# this function inherits from.

def populate(self, json_dict):
    for key, value in json_dict.iteritems():
        setattr(self, key, value)


def to_imgur_list(regular_list):
    """Turn a python list into the format imgur expects."""
    if regular_list is None:
        return None
    return ",".join(str(id) for id in regular_list)


class Imgur:
    DEFAULT_LONG_URL = "imgur.com"
    # Put these urls into a configuration object that retrieves the values from
    # settings file.

    def __init__(self, long_url=None, short_url=None, cache=None):
        self.long_url = long_url or self.DEFAULT_LONG_URL
        self.cache = cache or Default_cache()

    def is_imgur_url(self, url):
        """Is the given url a valid imgur url?"""
        return re.match("(http://)?(www\.)?imgur\.com", url, re.I) is not None

    def create_album(self, title=None, description=None, ids=None, cover=None):
        url = "https://api.imgur.com/3/album/"
        payload = {'ids': to_imgur_list(ids), 'title': title,
                   'description': description, 'cover': cover}
        new_album = request.send_request(url, params=payload, method='POST')
        album = self.get_album(new_album['id'])
        album.deletehash = new_album['deletehash']
        return album

    def get_at_url(self, url):
        """Return whatever is at the imgur url as an object."""
        pass

    def get_album(self, id):
        """Return information about this album."""
        json = request.send_request("https://api.imgur.com/3/album/%s" % id)
        return Album(json, self)

    def get_comment(self, id):
        """Return information about this comment."""
        json = request.send_request("https://api.imgur.com/3/comment/%s" % id)
        return Comment(json, self)

    def get_image(self, id):
        """Return a Image object representing the image with id."""
        resp = request.send_request("https://api.imgur.com/3/image/%s" % id)
        return Image(resp, self)

    def upload_image(self, path, title=None, description=None, album_id=None):
        """Upload the image at path and return it."""
        with open(path, 'rb') as image_file:
            binary_data = image_file.read()
            image = b64encode(binary_data)

        payload = {'album_id': album_id, 'image': image,
                   'title': title, 'description': description}

        img = request.send_request("https://api.imgur.com/3/image",
                                   params=payload, method='POST')
        # The information returned when we upload the image is only a subset
        # of the information about an image. When it was uploaded (datetime)
        # for instance isn't returned. We have to re-request the image to get
        # everything.
        # Sole exception is deletehash. But this might only be present for
        # anonymous images?
        return_image = self.get_image(img['id'])
        return_image.deletehash = img['deletehash']
        return return_image


class Album:
    def __init__(self, json_dict, imgur):
        self.deletehash = None
        self.images = []
        self.imgur = imgur
        populate(self, json_dict)

    def __repr__(self):
        return "<Album %s>" % self.id

    def add_images(self, ids):
        """Add images to the album."""
        pass

    def delete(self):
        url = "https://api.imgur.com/3/album/%s" % self.deletehash
        return request.send_request(url, method="DELETE")

    def favorite(self):
        """Favorite the album."""
        pass

    # TODO: Doing it like this seem to obfuscate the API. Since we change
    # the state of the album without the user taking a direct action.
    def get_images(self):
        images = request.send_request("https://api.imgur.com/3/album/%s/images"
                                      % self.id)
        self.images = [Image(img, self.imgur) for img in images]
        return self.images

    def remove_images(self, ids):
        """Remove images from the album."""
        pass

    def set_images(self, ids):
        """Set the images in this album."""
        pass

    def update(self, title=None, description=None, ids=None, cover=None,
               layout=None, privacy=None):
        """Update the albums information."""
        url = "https://api.imgur.com/3/album/%s" % self.deletehash
        ids = to_imgur_list(ids)
        payload = {'title': title, 'description': description,
                   'ids': ids, 'cover': cover,
                   'layout': layout, 'privacy': privacy}
        is_updated = request.send_request(url, params=payload, method='POST')
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


class Comment:
    def __init__(self, json_dict, imgur):
        self.deletehash = None
        self.imgur = imgur
        populate(self, json_dict)
        # Possible via webend, not exposed via json
        # self.permalink == ?!??!

    def __repr__(self):
        return "<Comment %s>" % self.id

    def delete(self):
        """Delete the comment."""
        pass

    def downvote(self):
        """Downvote this comment."""
        pass

    def get_replies(self):
        """Create a reply for the given comment."""
        json = request.send_request("https://api.imgur.com/3/comment/"
                                    "%s/replies" % self.id)
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

    def report(self):
        """Reply comment for being inappropriate."""

    def upvote(self):
        """Upvote this comment."""
        pass


class Image:
    def __init__(self, json_dict, imgur):
        self.deletehash = None
        self.imgur = imgur
        populate(self, json_dict)

    def __repr__(self):
        return "<Image %s>" % self.id

    def delete(self):
        """Delete the image."""
        return request.send_request("https://api.imgur.com/3/image/%s" %
                                    self.deletehash, method='DELETE')

    def favorite(self):
        """Favorite the image."""
        pass

    def update(self, title=None, description=None):
        """Update the image with a new title and/or description."""
        payload = {'title': title, 'description': description}
        is_updated = request.send_request("https://api.imgur.com/3/image/%s" %
                                          self.deletehash, params=payload,
                                          method='POST')
        if is_updated:
            self.title = title or self.title
            self.description = description or self.description
        return is_updated
