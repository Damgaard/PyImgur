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

from authentication import client_id
import pyimgur

# Make im protected, so it's not run on initialization
im = pyimgur.Imgur(client_id)


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
    i = im.get_image('Hlddt')
    new_file = i.download()
    assert new_file == 'Hlddt.jpg'
    os.remove(new_file)


def test_image_download_own_name():
    i = im.get_image('Hlddt')
    new_file = i.download(name="hello")
    assert new_file == 'hello.jpg'
    os.remove(new_file)


def test_image_download_no_overwrite():
    i = im.get_image('Hlddt')
    new_file = i.download()
    with pytest.raises(Exception):  # pylint: disable-msg=E1101
        i.download()
    os.remove(new_file)


def test_image_download_small_square():
    i = im.get_image('Hlddt')
    new_file = i.download(size='small square')
    assert new_file == 'Hlddts.jpg'
    os.remove(new_file)


def test_image_download_bad_size():
    i = im.get_image('Hlddt')
    with pytest.raises(LookupError):  # pylint: disable-msg=E1101
        i.download(size='Invalid sized triangle')


def test_image_download_to_parent_folder():
    i = im.get_image('Hlddt')
    new_file = i.download(path="..")
    assert new_file == "..\Hlddt.jpg"
    os.remove(new_file)
