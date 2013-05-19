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

import pytest

from authentication import client_id
import pyimgur

# Make im protected, so it's not run on initialization
im = pyimgur.Imgur(client_id)


def test_get_comment():
    comment = im.get_comment("49538390")
    assert isinstance(comment, pyimgur.Comment)


def test_get_comment_replies():
    comment = im.get_comment("49538390")
    child_comments = comment.get_replies()
    assert len(child_comments)
    assert isinstance(child_comments[0], pyimgur.Comment)
    assert child_comments[0].image.id == comment.image.id


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
