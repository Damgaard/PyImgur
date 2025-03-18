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

from pyimgur import Imgur, Album, Image, User
from pyimgur.request import send_request
from pyimgur.exceptions import (
    UnexpectedImgurException,
    InvalidParameterError,
    ImgurIsDownException,
)

from pyimgur.test.data import (
    MOCKED_ALBUM_DATA,
    MOCKED_USER_DATA,
    MOCKED_GALLERY_ALBUM_DATA,
    MOCKED_GALLERY_IMAGE_DATA,
)

MOCKED_UNAUTHED_IMGUR = Imgur("fake_client_id")
MOCKED_AUTHED_IMGUR = Imgur(
    "fake_client_id",
    "fake_client_secret",
    refresh_token="fake refresh token",
    access_token="fake access token",
)
MOCKED_USER = User(MOCKED_USER_DATA, MOCKED_AUTHED_IMGUR)


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
def test_send_request_imgur_is_down_in_a_504_way():
    # I've not seen this happen. But we treat it as a 503, so
    # it should be tested for.
    responses.get(
        "https://api.imgur.com/3/test",
        body="Varnish cache error",
        status=504,
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
        status=200,
    )

    album = Album(
        {"id": album_id, "deletehash": "deletehash", "title": "test"},
        MOCKED_AUTHED_IMGUR,
        True,
    )
    album.favorite()

    assert (
        responses.calls[0].request.url
        == f"https://api.imgur.com/3/album/{album_id}/favorite"
    )
    assert responses.calls[0].request.method == "POST"


@responses.activate
def test_get_memes_gallery_calls_right_url():
    responses.add(
        responses.GET,
        "https://api.imgur.com/3/gallery/g/memes/viral/week/0",
        json={"data": [MOCKED_ALBUM_DATA] * 5},
        status=200,
    )

    im = Imgur("fake_client_id")
    im.get_memes_gallery(limit=3)

    assert len(responses.calls) == 1
    assert (
        responses.calls[0].request.url
        == "https://api.imgur.com/3/gallery/g/memes/viral/week/0"
    )


@responses.activate
def test_get_subreddit_gallery_fetches_from_right_url():
    subreddit = "pics"

    responses.add(
        responses.GET,
        f"https://api.imgur.com/3/gallery/r/{subreddit}/time/top/0",
        json={"data": [MOCKED_ALBUM_DATA] * 5},
        status=200,
    )

    im = Imgur("fake_client_id")
    im.get_subreddit_gallery(subreddit, limit=5)

    assert len(responses.calls) == 1
    assert (
        responses.calls[0].request.url
        == f"https://api.imgur.com/3/gallery/r/{subreddit}/time/top/0"
    )


@responses.activate
def test_pagination_fetches_multiple_pages():
    responses.add(
        responses.GET,
        "https://api.imgur.com/3/gallery/g/memes/viral/week/0",
        json={"data": [MOCKED_ALBUM_DATA] * 5},
        status=200,
    )
    responses.add(
        responses.GET,
        "https://api.imgur.com/3/gallery/g/memes/viral/week/1",
        json={"data": [MOCKED_ALBUM_DATA] * 5},
        status=200,
    )

    im = Imgur("fake_client_id")
    im.get_memes_gallery(limit=8)

    assert len(responses.calls) == 2


@responses.activate
def test_pagination_right_amount_of_content():
    responses.add(
        responses.GET,
        "https://api.imgur.com/3/gallery/g/memes/viral/week/0",
        json={"data": [MOCKED_ALBUM_DATA] * 5},
        status=200,
    )
    responses.add(
        responses.GET,
        "https://api.imgur.com/3/gallery/g/memes/viral/week/1",
        json={"data": [MOCKED_ALBUM_DATA] * 5},
        status=200,
    )

    im = Imgur("fake_client_id")
    result = im.get_memes_gallery(limit=8)

    assert len(result) == 8


@responses.activate
def test_pagination_does_not_fetch_more_data_than_needed():
    """Request #2 fulfils requirement. Another request would be redundant."""
    responses.add(
        responses.GET,
        "https://api.imgur.com/3/gallery/g/memes/viral/week/0",
        json={"data": [MOCKED_ALBUM_DATA] * 5},
        status=200,
    )
    responses.add(
        responses.GET,
        "https://api.imgur.com/3/gallery/g/memes/viral/week/1",
        json={"data": [MOCKED_ALBUM_DATA] * 5},
        status=200,
    )
    responses.add(
        responses.GET,
        "https://api.imgur.com/3/gallery/g/memes/viral/week/2",
        json={"data": [MOCKED_ALBUM_DATA] * 5},
        status=200,
    )

    im = Imgur("fake_client_id")
    result = im.get_memes_gallery(limit=8)

    assert len(responses.calls) == 2


@responses.activate
def test_pagination_handles_last_page_having_too_few_items():
    responses.add(
        responses.GET,
        "https://api.imgur.com/3/gallery/g/memes/viral/week/0",
        json={"data": [MOCKED_ALBUM_DATA] * 5},
        status=200,
    )
    responses.add(
        responses.GET,
        "https://api.imgur.com/3/gallery/g/memes/viral/week/1",
        json={"data": [MOCKED_ALBUM_DATA] * 2},
        status=200,
    )

    responses.add(
        responses.GET,
        "https://api.imgur.com/3/gallery/g/memes/viral/week/2",
        json={"data": []},
        status=200,
    )

    im = Imgur("fake_client_id")
    result = im.get_memes_gallery(limit=8)

    assert len(result) == 7


@responses.activate
def test_pagination_last_page_has_no_items_doesnt_break_system():
    responses.add(
        responses.GET,
        "https://api.imgur.com/3/gallery/g/memes/viral/week/0",
        json={"data": [MOCKED_ALBUM_DATA] * 5},
        status=200,
    )
    responses.add(
        responses.GET,
        "https://api.imgur.com/3/gallery/g/memes/viral/week/1",
        json={"data": []},
        status=200,
    )

    im = Imgur("fake_client_id")
    result = im.get_memes_gallery(limit=8)

    assert len(result) == 5


@responses.activate
def test_pagination_limit_argument_is_respected():
    responses.add(
        responses.GET,
        "https://api.imgur.com/3/gallery/g/memes/viral/week/0",
        json={"data": [MOCKED_ALBUM_DATA] * 5},
        status=200,
    )
    responses.add(
        responses.GET,
        "https://api.imgur.com/3/gallery/g/memes/viral/week/1",
        json={"data": [MOCKED_ALBUM_DATA] * 5},
        status=200,
    )
    responses.add(
        responses.GET,
        "https://api.imgur.com/3/gallery/g/memes/viral/week/2",
        json={"data": [MOCKED_ALBUM_DATA] * 5},
        status=200,
    )
    responses.add(
        responses.GET,
        "https://api.imgur.com/3/gallery/g/memes/viral/week/3",
        json={"data": []},
        status=200,
    )

    im = Imgur("fake_client_id")
    limited_result = im.get_memes_gallery(limit=8)
    limited_calls = len(responses.calls)

    no_limit_result = im.get_memes_gallery()
    no_limit_calls = len(responses.calls) - limited_calls

    assert len(limited_result) != len(no_limit_result)
    assert limited_calls != no_limit_calls


@responses.activate
def test_pagination_negative_limit_reverts_to_default_limit():
    responses.add(
        responses.GET,
        "https://api.imgur.com/3/gallery/g/memes/viral/week/0",
        json={"data": [MOCKED_ALBUM_DATA] * 75},
        status=200,
    )
    responses.add(
        responses.GET,
        "https://api.imgur.com/3/gallery/g/memes/viral/week/1",
        json={"data": [MOCKED_ALBUM_DATA] * 75},
        status=200,
    )
    responses.add(
        responses.GET,
        "https://api.imgur.com/3/gallery/g/memes/viral/week/2",
        json={"data": [MOCKED_ALBUM_DATA] * 75},
        status=200,
    )
    responses.add(
        responses.GET,
        "https://api.imgur.com/3/gallery/g/memes/viral/week/3",
        json={"data": []},
        status=200,
    )

    im = Imgur("fake_client_id")
    result = im.get_memes_gallery(limit=-1)

    assert len(result) == 100


@responses.activate
def test_rapidapi_support():
    responses.add(
        responses.GET,
        "https://imgur-apiv3.p.rapidapi.com/3/gallery/g/memes/viral/week/0",
        json={"data": [MOCKED_ALBUM_DATA] * 75},
        status=200,
    )

    im = Imgur("fake_client_id", rapidapi_key="fake_rapidapi_key")
    im.get_memes_gallery(limit=1)

    assert responses.calls[0].request.url.startswith(
        "https://imgur-apiv3.p.rapidapi.com/"
    )
    assert responses.calls[0].request.headers["X-Mashape-Key"] == "fake_rapidapi_key"


@responses.activate
def test_get_favorites_uses_pagination():
    responses.add(
        responses.GET,
        f"https://api.imgur.com/3/account/{MOCKED_USER.name}/favorites/0",
        json={"data": [MOCKED_GALLERY_ALBUM_DATA] * 25, "success": True, "status": 200},
    )

    responses.add(
        responses.GET,
        f"https://api.imgur.com/3/account/{MOCKED_USER.name}/favorites/1",
        json={"data": [MOCKED_GALLERY_ALBUM_DATA] * 25, "success": True, "status": 200},
    )

    result = MOCKED_USER.get_favorites(limit=40)

    assert len(responses.calls) == 2
    assert len(result) == 40


@responses.activate
def test_get_favorites_handles_mixed_types():
    responses.add(
        responses.GET,
        f"https://api.imgur.com/3/account/{MOCKED_USER.name}/favorites/0",
        json={
            "data": [
                MOCKED_GALLERY_ALBUM_DATA,
                MOCKED_GALLERY_IMAGE_DATA,
            ],
            "success": True,
            "status": 200,
        },
    )

    result = MOCKED_USER.get_favorites(limit=2)

    assert len(result) == 2
    assert isinstance(result[0], Album)
    assert isinstance(result[1], Image)


@responses.activate
def test_get_gallery_favorites_uses_pagination():
    responses.add(
        responses.GET,
        f"https://api.imgur.com/3/account/{MOCKED_USER.name}/gallery_favorites/0",
        json={"data": [MOCKED_GALLERY_ALBUM_DATA] * 25, "success": True, "status": 200},
    )

    responses.add(
        responses.GET,
        f"https://api.imgur.com/3/account/{MOCKED_USER.name}/gallery_favorites/1",
        json={"data": [MOCKED_GALLERY_ALBUM_DATA] * 25, "success": True, "status": 200},
    )

    result = MOCKED_USER.get_gallery_favorites(limit=40)

    assert len(responses.calls) == 2
    assert len(result) == 40


@responses.activate
def test_get_gallery_favorites_optional_sort_argument():
    responses.add(
        responses.GET,
        f"https://api.imgur.com/3/account/{MOCKED_USER.name}/gallery_favorites/0/oldest",
        json={"data": [MOCKED_GALLERY_ALBUM_DATA] * 25, "success": True, "status": 200},
    )
    result = MOCKED_USER.get_gallery_favorites(sort="oldest", limit=10)

    assert len(result) == 10
    assert (
        responses.calls[0].request.url
        == f"https://api.imgur.com/3/account/{MOCKED_USER.name}/gallery_favorites/0/oldest"
    )


@responses.activate
def test_get_gallery_favorites_invalid_sort_argument():
    with pytest.raises(InvalidParameterError):
        MOCKED_USER.get_gallery_favorites(sort="invalid")
