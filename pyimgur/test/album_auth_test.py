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
import time
from uuid import uuid4

import pytest

sys.path.insert(0, ".")

from authentication import client_id, client_secret, refresh_token
import pyimgur

"""Tests authenticated usage of the methods in the Album class."""

# Make im protected, so it's not run on initialization
# IDEA: To protect R and SR add a memorize class here, just like in the old
# version of PRAW, that returns a R / SR object. For the first time it will
# create the object, given an instance of PRAW, for the subsequent runs it will
# return the previously created object.

im = pyimgur.Imgur(client_id=client_id, client_secret=client_secret,
                   refresh_token=refresh_token)
im.refresh_access_token()


IMAGE_IDS = ["7skLpQo", "JCVvSVY", "S1jmapR"]


def test_add_images():
    new_album = im.create_album("New fancy album")
    assert not len(new_album.images)
    new_album.add_images(IMAGE_IDS)
    new_album.refresh()
    assert len(new_album.images) == len(IMAGE_IDS)
    new_album.delete()


def test_remove_images():
    image_ids = ["7skLpQo"]
    new_album = im.create_album("New fancy album", ids=image_ids)
    assert len(new_album.images)
    time.sleep(1)
    new_album.remove_images(image_ids)
    time.sleep(1)
    new_album.refresh()
    assert not len(new_album.images)
    new_album.delete()


def test_remove_images_non_existing():
    image_ids = ["7skLpQo"]
    new_album = im.create_album("New fancy album", ids=image_ids)
    assert len(new_album.images)
    time.sleep(1)
    new_album.remove_images(["NonExisting"])
    time.sleep(1)
    new_album.refresh()
    assert not len(new_album.images)
    new_album.delete()


def test_set_images():
    new_album = im.create_album("New fancy album", ids=[IMAGE_IDS[0]])
    assert len(new_album.images)
    old_images = new_album.images
    new_album.set_images(IMAGE_IDS[1:])
    new_album.refresh()
    assert new_album.images != old_images
    new_album.delete()


def test_create():
    new_album = im.create_album("New fancy album")
    # If it doesn't work then an exception will be raised.
    assert new_album.link is not None
    new_album.delete()


def test_delete():
    new_album = im.create_album("New fancy album")
    time.sleep(1)
    new_album.delete()
    with pytest.raises(Exception):  # pylint: disable-msg=E1101
        im.get_album(new_album.id)


def test_favorite():
    new_album = im.create_album("New fancy album")
    assert not new_album.has_favorited
    new_album.favorite()
    new_album.refresh()
    assert new_album.has_favorited


def test_update():
    new_album = im.create_album(uuid4())
    old_title = new_album.title
    new_album.update(title=uuid4())
    assert old_title != new_album.title
    new_album.delete()
