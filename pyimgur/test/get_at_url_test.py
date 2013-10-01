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

from authentication import client_id, client_secret, refresh_token
import pyimgur

"""Testing of the get_at_url method."""

im = pyimgur.Imgur(client_id=client_id, client_secret=client_secret,
                   refresh_token=refresh_token)
im.refresh_access_token()


def test_retrieve_non_imgur_url():
    url = "http://github.com"
    result = im.get_at_url(url)
    assert result is None


def test_retrieve_comment():
    url = 'http://imgur.com/gallery/CleiK2V/comment/87511312'
    comment = im.get_at_url(url)
    assert isinstance(comment, pyimgur.Comment)


def test_retrieve_album():
    album = im.get_at_url('http://imgur.com/a/SPlYO')
    assert isinstance(album, pyimgur.Album)


def test_retrieve_album_with_fragment():
    album = im.get_at_url('http://imgur.com/a/SPlYO#0')
    assert isinstance(album, pyimgur.Album)


def test_retrieve_album_with_GET_params():
    album = im.get_at_url('http://imgur.com/a/SPlYO?sort=hot')
    assert isinstance(album, pyimgur.Album)


def test_retrieve_image():
    image = im.get_at_url('http://imgur.com/c79sp')
    assert isinstance(image, pyimgur.Image)
    assert image.title is not None


def test_retrieve_user():
    user = im.get_at_url('http://imgur.com/user/AwildNikkiappears')
    assert isinstance(user, pyimgur.User)
    assert user.name is not None


def test_retrieve_gallery_image():
    gallery_image = im.get_at_url('http://imgur.com/gallery/CleiK2V')
    assert isinstance(gallery_image, pyimgur.Gallery_image)
    assert gallery_image.title is not None


def test_retrieve_gallery_album():
    gallery_album = im.get_at_url('http://imgur.com/gallery/mpVzS')
    assert isinstance(gallery_album, pyimgur.Gallery_album)
    assert gallery_album.title is not None

def test_retrive_non_existing_url_format():
    bad_result = im.get_at_url('http://imgur.com/bad/mpVzS')
    assert bad_result is None
