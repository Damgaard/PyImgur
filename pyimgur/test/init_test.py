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

import os
import sys

import pytest

sys.path.insert(0, ".")

from authentication import client_id, client_secret, refresh_token
import pyimgur

# Make im protected, so it's not run on initialization
im = pyimgur.Imgur(client_id, client_secret=client_secret, refresh_token=refresh_token)
im.refresh_access_token()


# TODO: Currently some tests do more than one thing. This is to limit the
# calls to Imgur and thus the requests consumed and to prevent getting
# ratelimited. They need to be split into more tests when a local fake
# imitation of Imgur has been set up.

TITLE = "Fancy title!"
DESCRIPTION = "Hello Description"

# Identify path to cat image. Needed as otherwise 2 tests might
# break depending on whether test suite is run from root or from
# the test folder.
current_file_path = os.path.abspath(__file__)
current_directory = os.path.dirname(current_file_path)
CAT_IMAGE_PATH = os.path.join(current_directory, "cat.jpg")


class Empty(pyimgur.Basic_object):
    pass


def test_accessing_bad_attribute():
    basic_object = pyimgur.Basic_object({}, None, True)
    with pytest.raises(AttributeError):
        basic_object.no_such_object  # pylint: disable=pointless-statement


def test_can_change_authentication():
    im = pyimgur.Imgur(client_id="123", client_secret="455")
    im.change_authentication(client_id="888")
    assert im.client_id == "888"


def test_populate():
    info = {"score": 1, "hello": "world"}
    inst = Empty(info, None)
    assert "score" in vars(inst)
    assert "hello" in vars(inst)
    assert inst.score == 1


def test_is_imgur_url():
    assert im.is_imgur_url("http://imgur.com/gallery/46JTq")
    assert im.is_imgur_url("http://www.imgur.com/gallery/46JTq")
    assert im.is_imgur_url("www.imgur.com/gallery/46JTq")
    assert im.is_imgur_url("imgur.com/gallery/46JTq")
    assert im.is_imgur_url("imgUr.com/gallery/46JTq")
    assert not im.is_imgur_url("www.evil_domain/imgur.com/")


def test_get_image_i_didnt_upload():
    image = im.get_image("JPz2i")
    assert isinstance(image, pyimgur.Image)
    assert image.deletehash is ""


def test_get_image_i_uploaded():
    image = im.get_image("4UoRzGc")
    assert isinstance(image, pyimgur.Image)
    assert image.deletehash is not ""


def test_upload_image():
    image = im.upload_image(path=CAT_IMAGE_PATH)
    assert isinstance(image, pyimgur.Image)
    assert image.title is None
    assert image.description is None
    assert image.deletehash is not None
    image.delete()


def test_upload_image_with_args():
    image = im.upload_image(CAT_IMAGE_PATH, title=TITLE, description=DESCRIPTION)
    assert isinstance(image, pyimgur.Image)
    assert image.title == TITLE
    assert image.description == DESCRIPTION
    assert image.deletehash is not None
    image.delete()


def test_update_image():
    image = im.upload_image(CAT_IMAGE_PATH)
    assert image.title is None
    image.update(TITLE)
    assert image.title == TITLE
    image.delete()


def test_create_album():
    album = im.create_album()
    assert isinstance(album, pyimgur.Album)
    album.delete()


def test_update_album():
    album = im.create_album(TITLE)
    assert album.title == TITLE
    album.update("Different title")
    assert album.title == "Different title"
    album.delete()


def test_image_download():
    i = im.get_image("Hlddt")
    new_file = i.download()
    assert new_file == "Hlddt.jpeg"
    os.remove(new_file)


def test_image_download_own_name():
    i = im.get_image("Hlddt")
    new_file = i.download(name="hello")
    assert new_file == "hello.jpeg"
    os.remove(new_file)


def test_image_download_no_overwrite():
    i = im.get_image("Hlddt")
    new_file = i.download()
    with pytest.raises(Exception):  # pylint: disable=E1101
        i.download()
    os.remove(new_file)


def test_image_download_small_square():
    i = im.get_image("Hlddt")
    new_file = i.download(size="small square")
    assert new_file == "Hlddts.jpeg"
    os.remove(new_file)


def test_image_download_bad_size():
    i = im.get_image("Hlddt")
    with pytest.raises(LookupError):  # pylint: disable=E1101
        i.download(size="Invalid sized triangle")


def test_image_download_to_parent_folder():
    i = im.get_image("Hlddt")
    new_file = i.download(path="..")
    expected_path = os.path.join("..", "Hlddt.jpeg")
    assert new_file == expected_path
    os.remove(new_file)
