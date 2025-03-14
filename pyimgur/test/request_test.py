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


import responses

import pytest

from pyimgur import Imgur, Album
from pyimgur.request import send_request
from pyimgur.exceptions import (
    UnexpectedImgurException,
    InvalidParameterError,
    ImgurIsDownException,
)

MOCKED_UNAUTHED_IMGUR = Imgur("fake_client_id")
MOCKED_AUTHED_IMGUR = Imgur("fake_client_id", "fake_client_secret", "fake access token")


@responses.activate
def test_send_request():
    responses.get(
        "https://api.imgur.com/3/test",
        json={"data": {"title": "hello world"}},
    )
    content, _ = send_request("https://api.imgur.com/3/test")
    assert content == {"title": "hello world"}


@responses.activate
def test_send_request_handles_no_data_field():
    responses.get(
        "https://api.imgur.com/3/test",
        json={"status": "success"},
    )
    content, _ = send_request("https://api.imgur.com/3/test")
    assert content == {"status": "success"}


@responses.activate
def test_send_request_bad_method():
    with pytest.raises(InvalidParameterError):
        send_request("https://api.imgur.com/3/test", method="BAD")


@responses.activate
def test_send_request_unexpected_imgur_exception():
    responses.get(
        "https://api.imgur.com/3/test",
        json={"data": {"error": "Im a teapot", "request": "3/test", "method": "PUT"}},
        status=429,
    )

    with pytest.raises(UnexpectedImgurException):
        _, _ = send_request("https://api.imgur.com/3/test")


@responses.activate
def test_send_request_imgur_is_down():
    responses.get(
        "https://api.imgur.com/3/test",
        body="Varnish cache error",
        status=503,
    )

    with pytest.raises(ImgurIsDownException):
        _, _ = send_request("https://api.imgur.com/3/test")


@responses.activate
def test_send_request_adds_paramaters():
    responses.get(
        "https://api.imgur.com/3/test",
        json={"data": "hello world"},
        match=[responses.matchers.query_param_matcher({"bool_value": "true"})],
    )

    content, _ = send_request(
        "https://api.imgur.com/3/test",
        content_to_send={"params": {"bool_value": "true"}},
    )
    assert content == "hello world"


@responses.activate
def test_get_image_uses_right_url():
    image_id = "abc123"

    responses.add(
        responses.GET,
        f"https://api.imgur.com/3/image/{image_id}",
        json={"data": {"id": image_id, "title": "test"}},
        status=200,
    )

    im = Imgur("fake_client_id")
    im.get_image(image_id)

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == f"https://api.imgur.com/3/image/{image_id}"


@responses.activate
def test_get_album_uses_right_url():
    album_id = "xyz789"

    responses.add(
        responses.GET,
        f"https://api.imgur.com/3/album/{album_id}",
        json={"data": {"id": album_id, "title": "test"}},
        status=200,
    )

    im = Imgur("fake_client_id")
    im.get_album(album_id)

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == f"https://api.imgur.com/3/album/{album_id}"


@responses.activate
def test_get_message_uses_right_url():
    message_id = "msg123"

    responses.add(
        responses.GET,
        f"https://api.imgur.com/3/message/{message_id}",
        json={"data": {"id": message_id, "content": "test"}},
        status=200,
    )

    im = Imgur("fake_client_id")
    im.get_message(message_id)

    assert len(responses.calls) == 1
    assert (
        responses.calls[0].request.url
        == f"https://api.imgur.com/3/message/{message_id}"
    )


@responses.activate
def test_get_notification_uses_right_url():
    notification_id = "notif456"

    responses.add(
        responses.GET,
        f"https://api.imgur.com/3/notification/{notification_id}",
        json={"data": {"id": notification_id, "content": "test"}},
        status=200,
    )

    im = Imgur("fake_client_id")
    im.get_notification(notification_id)

    assert len(responses.calls) == 1
    assert (
        responses.calls[0].request.url
        == f"https://api.imgur.com/3/notification/{notification_id}"
    )


@responses.activate
def test_get_user_uses_right_url():
    username = "test_user"

    responses.add(
        responses.GET,
        f"https://api.imgur.com/3/account/{username}",
        json={"data": {"url": username, "id": 12345}},
        status=200,
    )

    im = Imgur("fake_client_id")
    im.get_user(username)

    assert len(responses.calls) == 1
    assert (
        responses.calls[0].request.url == f"https://api.imgur.com/3/account/{username}"
    )


@responses.activate
def test_album_delete_calls_right_url():
    album_id = "xyz789"

    responses.add(
        responses.DELETE,
        f"https://api.imgur.com/3/album/{album_id}",
        json={"data": True},
        status=200,
    )

    album = Album(
        {"id": album_id, "deletehash": "deletehash", "title": "test"},
        MOCKED_AUTHED_IMGUR,
        True,
    )
    album.delete()

    assert responses.calls[0].request.url == f"https://api.imgur.com/3/album/{album_id}"
    assert responses.calls[0].request.method == "DELETE"


@responses.activate
def test_album_delete_unauthed_imgur_uses_deletehash():
    deletehash = "deletehash"

    responses.add(
        responses.DELETE,
        f"https://api.imgur.com/3/album/{deletehash}",
        json={"data": True},
        status=200,
    )

    album = Album(
        {"id": "album_id", "deletehash": deletehash, "title": "test"},
        MOCKED_UNAUTHED_IMGUR,
        True,
    )
    album.delete()

    assert (
        responses.calls[0].request.url == f"https://api.imgur.com/3/album/{deletehash}"
    )
    assert responses.calls[0].request.method == "DELETE"


@responses.activate
def test_album_favorite_calls_right_url():
    album_id = "xyz789"

    responses.add(
        responses.POST,
        f"https://api.imgur.com/3/album/{album_id}/favorite",
        json={"data": {"id": album_id, "title": "test"}},
        status=200
    )

    album = Album(
        {"id": album_id, "deletehash": "deletehash", "title": "test"},
        MOCKED_AUTHED_IMGUR,
        True
    )
    album.favorite()

    assert responses.calls[0].request.url == f"https://api.imgur.com/3/album/{album_id}/favorite"
    assert responses.calls[0].request.method == "POST"
