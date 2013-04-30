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

import pyimgur

# Make im protected, so it's not run on initialization
im = pyimgur.Imgur()


def test_get_comment():
    comment = im.get_comment("49538390")
    assert isinstance(comment, pyimgur.Comment)


def test_get_comment_replies():
    comment = im.get_comment("49538390")
    child_comments = comment.get_replies()
    assert len(child_comments)
    assert isinstance(child_comments[0], pyimgur.Comment)
    assert child_comments[0].image_id == comment.image_id