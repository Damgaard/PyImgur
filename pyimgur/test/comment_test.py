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

from pyimgur import Comment
from . import USER_NOT_AUTHENTICATED, im


@pytest.mark.skipif(
    USER_NOT_AUTHENTICATED,
    reason="Cannot run live test without authentication variables.",
)
def test_get_comment():
    comment = im.get_comment("49538390")
    assert isinstance(comment, Comment)


@pytest.mark.skipif(
    USER_NOT_AUTHENTICATED,
    reason="Cannot run live test without authentication variables.",
)
def test_get_comment_replies():
    comment = im.get_comment("49538390")
    child_comments = comment.get_replies()
    assert len(child_comments)
    assert isinstance(child_comments[0], Comment)
    assert child_comments[0].image.id == comment.image.id


@pytest.mark.skipif(
    USER_NOT_AUTHENTICATED,
    reason="Cannot run live test without authentication variables.",
)
def test_get_comments():
    gallery = im.get_gallery()
    gallery_item = gallery[0]
    comments = gallery_item.get_comments()
    assert isinstance(comments, list)
    assert isinstance(comments[0], Comment)
