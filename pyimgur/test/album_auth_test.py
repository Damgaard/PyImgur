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

"""Tests authenticated usage of the methods in the Album class."""

import sys
import time

import pytest

sys.path.insert(0, ".")

try:
    from authentication import client_id, client_secret, refresh_token
except ImportError:
    client_id = None
    client_secret = None
    refresh_token = None

import pyimgur

# Make im protected, so it's not run on initialization
# IDEA: To protect R and SR add a memorize class here, just like in the old
# version of PRAW, that returns a R / SR object. For the first time it will
# create the object, given an instance of PRAW, for the subsequent runs it will
# return the previously created object.

im = pyimgur.Imgur(
    client_id=client_id, client_secret=client_secret, refresh_token=refresh_token
)
if refresh_token:
    im.refresh_access_token()


IMAGE_IDS = ["4UoRzGc", "wHxiibZ", "w5pB7vT"]


@pytest.mark.skipif(
    refresh_token is None,
    reason="Cannot run live test without authentication variables.",
)
def test_add_images():
    new_album = im.create_album("New fancy album")
    time.sleep(2)
    assert not len(new_album.images)
    new_album.add_images(IMAGE_IDS)
    new_album.refresh()
    assert len(new_album.images) == len(IMAGE_IDS)
    new_album.delete()


@pytest.mark.skipif(
    refresh_token is None,
    reason="Cannot run live test without authentication variables.",
)
def test_remove_images():
    image_ids = IMAGE_IDS
    new_album = im.create_album("New fancy album", images=image_ids)
    assert len(new_album.images)
    time.sleep(1)
    new_album.remove_images(image_ids)
    time.sleep(1)
    new_album.refresh()
    assert not len(new_album.images)
    new_album.delete()


@pytest.mark.skipif(
    refresh_token is None,
    reason="Cannot run live test without authentication variables.",
)
def test_remove_images_non_existing():
    """Assert that no error is raised and that no change is made."""
    image_ids = IMAGE_IDS[0]
    new_album = im.create_album("New fancy album", images=image_ids)
    assert len(new_album.images) == 1
    time.sleep(2)
    new_album.remove_images(
        [
            IMAGE_IDS[-1],
        ]
    )
    new_album.refresh()
    assert len(new_album.images) == 1
    new_album.delete()


@pytest.mark.skipif(
    refresh_token is None,
    reason="Cannot run live test without authentication variables.",
)
@pytest.mark.skip(
    reason="Endpoint seem broken on Imgurs end. Skipping until it's fixed or a wrongaround can be found.",
)
def test_set_images():
    new_album = im.create_album("New fancy album", images=[IMAGE_IDS[0]])
    time.sleep(2)
    assert len(new_album.images)
    old_images = new_album.images
    new_album._set_images(IMAGE_IDS[1:])
    new_album.refresh()
    assert new_album.images != old_images
    new_album.delete()


@pytest.mark.skipif(
    refresh_token is None,
    reason="Cannot run live test without authentication variables.",
)
def test_create():
    new_album = im.create_album("New fancy album")
    time.sleep(2)
    # If it doesn't work then an exception will be raised.
    assert new_album.link is not None
    new_album.delete()


@pytest.mark.skipif(
    refresh_token is None,
    reason="Cannot run live test without authentication variables.",
)
def test_delete():
    new_album = im.create_album("New fancy album")
    time.sleep(2)
    new_album.delete()
    with pytest.raises(Exception):  # pylint: disable-msg=E1101
        im.get_album(new_album.id)


@pytest.mark.skipif(
    refresh_token is None,
    reason="Cannot run live test without authentication variables.",
)
def test_favorite():
    new_album = im.create_album("New fancy album")
    time.sleep(2)
    assert not new_album.is_favorited
    new_album.favorite()
    new_album.refresh()
    assert new_album.is_favorited


@pytest.mark.skipif(
    refresh_token is None,
    reason="Cannot run live test without authentication variables.",
)
def test_update():
    new_album = im.create_album(title="Ok album")
    time.sleep(2)
    old_title = new_album.title
    new_album.update(title="Great album")
    assert old_title != new_album.title
    new_album.delete()
