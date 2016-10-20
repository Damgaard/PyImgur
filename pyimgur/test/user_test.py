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

import pytest

sys.path.insert(0, ".")


try:
    from authentication import client_id, client_secret, refresh_token
except ImportError:
    client_id = None
    client_secret = None
    refresh_token = None

import pyimgur

"""Tests authenticated usage of the methods in the Album class."""

# Make im protected, so it's not run on initialization
# IDEA: To protect R and SR add a memorize class here, just like in the old
# version of PRAW, that returns a R / SR object. For the first time it will
# create the object, given an instance of PRAW, for the subsequent runs it will
# return the previously created object.

im = pyimgur.Imgur(client_id=client_id, client_secret=client_secret,
                   refresh_token=refresh_token)
if refresh_token:
    im.refresh_access_token()
    user = im.get_user('me')


@pytest.mark.skipif(refresh_token is None, reason="Cannot run live test without "
                                                   "authentication variables.")
def test_change_settings():
    old_album_default = user.get_settings()['public_images']
    new_setting = False if old_album_default else True
    user.change_settings(public_images=new_setting)
    found_new = user.get_settings()['album_privacy']
    assert old_album_default != found_new


@pytest.mark.skipif(refresh_token is None, reason="Cannot run live test without "
                                                  "authentication variables.")
def test_get_favorites():
    assert len(user.get_favorites())


@pytest.mark.skipif(refresh_token is None, reason="Cannot run live test without "
                                                  "authentication variables.")
def test_get_settings():
    assert 'messaging_enabled' in user.get_settings()


@pytest.mark.skipif(refresh_token is None, reason="Cannot run live test without "
                                                  "authentication variables.")
def test_get_notificationssettings():
    assert "messages" in user.get_notifications()
