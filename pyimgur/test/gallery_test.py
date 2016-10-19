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

import sys

sys.path.insert(0, ".")

from authentication import client_id
import pyimgur

# Make im protected, so it's not run on initialization
im = pyimgur.Imgur(client_id)


def test_get_subreddit():
    response = im.get_subreddit_gallery("pic", limit=5)
    assert isinstance(response[0], pyimgur.Image) or isinstance(response[0], pyimgur.Album)


def test_get_subreddit_gallery_low_limit():
    requested_limit = 5
    response = im.get_subreddit_gallery("pic", limit=requested_limit)
    assert len(response) == requested_limit

