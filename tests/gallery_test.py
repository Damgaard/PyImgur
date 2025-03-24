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

import pytest

from pyimgur import Album, Image, ResourceNotFoundError
from . import USER_NOT_AUTHENTICATED, im


@pytest.mark.skipif(
    USER_NOT_AUTHENTICATED,
    reason="Cannot run live test without authentication variables.",
)
def test_get_subreddit():
    response = im.get_subreddit_gallery("pic", limit=5)
    assert isinstance(response[0], (Image, Album))


@pytest.mark.skipif(
    USER_NOT_AUTHENTICATED,
    reason="Cannot run live test without authentication variables.",
)
def test_get_subreddit_gallery_low_limit():
    requested_limit = 5
    response = im.get_subreddit_gallery("pic", limit=requested_limit)
    assert len(response) == requested_limit


@pytest.mark.skipif(
    USER_NOT_AUTHENTICATED,
    reason="Cannot run live test without authentication variables.",
)
def test_get_gallery_album():
    album = im.get_gallery_album("vDtsSUW")
    assert album.title == "Baby elephant asks for water from a man in Nepal"


@pytest.mark.skipif(
    USER_NOT_AUTHENTICATED,
    reason="Cannot run live test without authentication variables.",
)
def test_get_gallery_album_does_not_exist():
    with pytest.raises(ResourceNotFoundError):
        im.get_gallery_album("NotExist")
