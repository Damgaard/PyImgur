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

    def get_at_url(self, url):
        """Return whatever is at the imgur url as an object."""
        pass

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


class Image:
    def __init__(self, json_dict, imgur):
        self.deletehash = None
        self.imgur = imgur
        populate(self, json_dict)

    def __repr__(self):
        return "<Comment %s>" % self.id

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
        result = request.send_request("https://api.imgur.com/3/image/%s" %
                                      self.deletehash, params=payload,
                                      method='POST')
        if result:
            self.title = title or self.title
            self.description = description or self.description
        return result
