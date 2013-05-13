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


import requests
import sys
import time

import pytest

sys.path.insert(0, ".")

import pyimgur

# Make im protected, so it's not run on initialization
im = pyimgur.Imgur()


# TODO: Currently some tests do more than one thing. This is to limit the
# calls to Imgur and thus the requests consumed and to prevent getting
# ratelimited. They need to be split into more tests when a local fake
# imitation of Imgur has been set up.

TITLE = "Fancy title!"
DESCRIPTION = "Hello Description"


class Empty(pyimgur.Basic_object):
    pass


def test_populate():
    info = {'score': 1, 'hello': 'world'}
    inst = Empty(info, None)
    assert 'score' in vars(inst)
    assert 'hello' in vars(inst)
    assert inst.score == 1


def test_is_imgur_url():
    assert im.is_imgur_url("http://imgur.com/gallery/46JTq")
    assert im.is_imgur_url("http://www.imgur.com/gallery/46JTq")
    assert im.is_imgur_url("www.imgur.com/gallery/46JTq")
    assert im.is_imgur_url("imgur.com/gallery/46JTq")
    assert im.is_imgur_url("imgUr.com/gallery/46JTq")
    assert not im.is_imgur_url("www.evil_domain/imgur.com/")


def test_get_image():
    image = im.get_image('JPz2i')
    assert isinstance(image, pyimgur.Image)
    assert image.deletehash is None
    assert image.height == 78


def test_upload_image():
    image = im.upload_image('paradox.png')
    assert isinstance(image, pyimgur.Image)
    assert image.title is None
    assert image.description is None
    assert image.deletehash is not None
    image.delete()


def test_upload_image_with_args():
    image = im.upload_image('paradox.png', TITLE, DESCRIPTION)
    assert isinstance(image, pyimgur.Image)
    assert image.title == TITLE
    assert image.description == DESCRIPTION
    assert image.deletehash is not None
    image.delete()


def test_update_image():
    image = im.upload_image('paradox.png')
    assert image.title is None
    image.update(TITLE)
    assert image.title == TITLE
    image.delete()


def test_to_imgur_list():
    assert None == pyimgur.request.to_imgur_list(None)
    assert "QK1fZ9L" == pyimgur.request.to_imgur_list(["QK1fZ9L"])
    assert "QK1fZ9L,NsuNI" == pyimgur.request.to_imgur_list(["QK1fZ9L",
                                                             "NsuNI"])


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


def test_get_comments_count_error():
    gallery = im.get_gallery()
    gallery_item = gallery[0]
    with pytest.raises(NotImplementedError):  # pylint: disable-msg=E1101
        gallery_item.get_comment_count()


def test_get_comments_ids_error():
    gallery = im.get_gallery()
    gallery_item = gallery[0]
    with pytest.raises(NotImplementedError):  # pylint: disable-msg=E1101
        gallery_item.get_comment_ids()


def test_get_comments():
    gallery = im.get_gallery()
    gallery_item = gallery[0]
    comments = gallery_item.get_comments()
    assert isinstance(comments, list)
    assert isinstance(comments[0], pyimgur.Comment)
