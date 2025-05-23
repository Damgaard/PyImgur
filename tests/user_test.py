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

import pytest

from . import USER_NOT_AUTHENTICATED, user


@pytest.mark.skipif(
    USER_NOT_AUTHENTICATED,
    reason="Cannot run live test without authentication variables.",
)
def test_change_settings():
    old_album_default = user.get_settings()["public_images"]
    user.change_settings(public_images=not old_album_default)
    found_new = user.get_settings()["album_privacy"]
    assert old_album_default != found_new


@pytest.mark.skipif(
    USER_NOT_AUTHENTICATED,
    reason="Cannot run live test without authentication variables.",
)
def test_get_favorites():
    # This test is flaky. It assumes the authenticated users has favourited at
    # least 1 gallery.
    assert len(user.get_favorites())


@pytest.mark.skipif(
    USER_NOT_AUTHENTICATED,
    reason="Cannot run live test without authentication variables.",
)
def test_get_settings():
    assert "messaging_enabled" in user.get_settings()


@pytest.mark.skipif(
    USER_NOT_AUTHENTICATED,
    reason="Cannot run live test without authentication variables.",
)
def test_get_notificationssettings():
    assert "messages" in user.get_notifications()
