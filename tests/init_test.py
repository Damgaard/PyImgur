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

from pathlib import Path

import pytest

import pyimgur
from pyimgur import InvalidParameterError
from pyimgur.basic_objects import Basic_object

from . import USER_NOT_AUTHENTICATED, im, unauthed_im
from .data import (
    MOCKED_IMAGE_DATA,
    IMAGE_EXPECTED_DATA,
    MOCKED_ALBUM_DATA,
    ALBUM_EXPECTED_DATA,
    MOCKED_GALLERY_ALBUM_DATA,
    GALLERY_ALBUM_EXPECTED_DATA,
    MOCKED_GALLERY_IMAGE_DATA,
    GALLERY_IMAGE_EXPECTED_DATA,
    MOCKED_COMMENT_DATA,
    COMMENT_EXPECTED_DATA,
    MOCKED_USER_DATA,
    USER_EXPECTED_DATA,
)

TITLE = "Fancy title!"
DESCRIPTION = "Hello Description"

# Identify path to cat image. Needed as otherwise 2 tests might
# break depending on whether test suite is run from root or from
# the test folder.
current_file_path = Path(__file__).resolve()
current_directory = current_file_path.parent
CAT_IMAGE_PATH = current_directory / "cat.jpg"
COFFEE_MP4_PATH = current_directory / "coffee.mp4"


def test_accessing_bad_attribute():
    basic_object = Basic_object({}, None, True)
    with pytest.raises(AttributeError):
        basic_object.no_such_object  # pylint: disable=pointless-statement


def test_populate():
    info = {"score": 1, "hello": "world"}
    inst = Basic_object(info, None)
    assert "score" in vars(inst)
    assert "hello" in vars(inst)
    assert inst.score == 1


def test_populate_with_image():
    image = pyimgur.Image(MOCKED_IMAGE_DATA, im, True)
    result = vars(image)
    del result["_imgur"]
    assert result.keys() == IMAGE_EXPECTED_DATA.keys()
    assert result == IMAGE_EXPECTED_DATA


def test_populate_with_album():
    album = pyimgur.Album(MOCKED_ALBUM_DATA, im, True)
    result = vars(album)
    del result["_imgur"]
    del result["author"]
    del result["cover"]
    del result["images"]

    assert result.keys() == ALBUM_EXPECTED_DATA.keys()
    assert result == ALBUM_EXPECTED_DATA


def test_populate_with_gallery_album():
    gallery_album = pyimgur.Gallery_album(MOCKED_GALLERY_ALBUM_DATA, im, True)
    result = vars(gallery_album)
    del result["_imgur"]
    del result["author"]
    del result["cover"]
    del result["images"]

    assert result.keys() == GALLERY_ALBUM_EXPECTED_DATA.keys()
    assert result == GALLERY_ALBUM_EXPECTED_DATA


def test_populate_with_gallery_image():
    gallery_image = pyimgur.Gallery_image(MOCKED_GALLERY_IMAGE_DATA, im, True)
    result = vars(gallery_image)
    del result["_imgur"]
    del result["author"]

    assert result.keys() == GALLERY_IMAGE_EXPECTED_DATA.keys()
    assert result == GALLERY_IMAGE_EXPECTED_DATA


def test_populate_with_comment():
    comment = pyimgur.Comment(MOCKED_COMMENT_DATA, im, True)
    result = vars(comment)
    del result["author"]
    del result["_imgur"]
    del result["image"]

    assert result.keys() == COMMENT_EXPECTED_DATA.keys()
    assert result == COMMENT_EXPECTED_DATA


def test_populate_with_user():
    user = pyimgur.User(MOCKED_USER_DATA, im, True)
    result = vars(user)
    del result["_imgur"]

    assert result.keys() == USER_EXPECTED_DATA.keys()
    assert result == USER_EXPECTED_DATA


def test_is_imgur_url():
    assert im.is_imgur_url("http://imgur.com/gallery/46JTq")
    assert im.is_imgur_url("http://www.imgur.com/gallery/46JTq")
    assert im.is_imgur_url("www.imgur.com/gallery/46JTq")
    assert im.is_imgur_url("imgur.com/gallery/46JTq")
    assert im.is_imgur_url("imgUr.com/gallery/46JTq")
    assert not im.is_imgur_url("www.evil_domain/imgur.com/")


@pytest.mark.skipif(
    USER_NOT_AUTHENTICATED,
    reason="Cannot run live test without authentication variables.",
)
def test_get_image_i_didnt_upload():
    image = im.get_image("JPz2i")
    assert isinstance(image, pyimgur.Image)
    assert image.deletehash == ""


@pytest.mark.skipif(
    USER_NOT_AUTHENTICATED,
    reason="Cannot run live test without authentication variables.",
)
def test_get_image_i_uploaded():
    image = im.get_image("4UoRzGc")
    assert isinstance(image, pyimgur.Image)
    assert image.deletehash != ""


@pytest.mark.skipif(
    USER_NOT_AUTHENTICATED,
    reason="Cannot run live test without authentication variables.",
)
def test_upload_image():
    image = im.upload_image(path=CAT_IMAGE_PATH)
    assert isinstance(image, pyimgur.Image)
    assert image.title is None
    assert image.description is None
    assert image.deletehash is not None
    image.delete()


@pytest.mark.skipif(
    USER_NOT_AUTHENTICATED,
    reason="Cannot run live test without authentication variables.",
)
def test_upload_mp4():
    image = im.upload_image(path=COFFEE_MP4_PATH)
    assert isinstance(image, pyimgur.Image)
    image.delete()


@pytest.mark.skipif(
    USER_NOT_AUTHENTICATED,
    reason="Cannot run live test without authentication variables.",
)
def test_upload_image_with_args():
    image = im.upload_image(CAT_IMAGE_PATH, title=TITLE, description=DESCRIPTION)
    assert isinstance(image, pyimgur.Image)
    assert image.title == TITLE
    assert image.description == DESCRIPTION
    assert image.deletehash is not None
    image.delete()


@pytest.mark.skipif(
    USER_NOT_AUTHENTICATED,
    reason="Cannot run live test without authentication variables.",
)
def test_update_image():
    image = im.upload_image(CAT_IMAGE_PATH)
    assert image.title is None
    image.update(TITLE)
    assert image.title == TITLE
    image.delete()


@pytest.mark.skipif(
    USER_NOT_AUTHENTICATED,
    reason="Cannot run live test without authentication variables.",
)
def test_get_subreddit_image():
    image = im.get_subreddit_image("memes", "DqaPOFs")
    assert (
        image.title
        == "Maybe we got this whole ”Canada joining the US” thing backwards?"
    )
    assert image.datetime == 1741288211
    assert image.id == "DqaPOFs"
    assert image.link == "https://i.imgur.com/DqaPOFs.jpg"


@pytest.mark.skipif(
    USER_NOT_AUTHENTICATED,
    reason="Cannot run live test without authentication variables.",
)
def test_create_album_unauthed():
    album = unauthed_im.create_album()
    assert isinstance(album, pyimgur.Album)
    album.delete()


@pytest.mark.skipif(
    USER_NOT_AUTHENTICATED,
    reason="Cannot run live test without authentication variables.",
)
def test_update_album_unauthed():
    album = unauthed_im.create_album(TITLE)
    assert album.title == TITLE
    album.update("Different title")
    assert album.title == "Different title"
    album.delete()


@pytest.mark.skipif(
    USER_NOT_AUTHENTICATED,
    reason="Cannot run live test without authentication variables.",
)
def test_image_download():
    i = im.get_image("Hlddt")
    try:
        new_file = i.download()
        assert new_file.name == "Hlddt.jpeg"
    finally:
        Path(new_file).unlink(missing_ok=True)


@pytest.mark.skipif(
    USER_NOT_AUTHENTICATED,
    reason="Cannot run live test without authentication variables.",
)
def test_image_download_own_name():
    i = im.get_image("Hlddt")
    try:
        new_file = i.download(name="hello")
        assert new_file.name == "hello.jpeg"
    finally:
        Path(new_file).unlink(missing_ok=True)


@pytest.mark.skipif(
    USER_NOT_AUTHENTICATED,
    reason="Cannot run live test without authentication variables.",
)
def test_image_download_no_overwrite():
    i = im.get_image("Hlddt")
    new_file = None
    try:
        new_file = i.download()
        with pytest.raises(Exception):  # pylint: disable=E1101
            i.download()
    finally:
        if new_file:
            Path(new_file).unlink(missing_ok=True)


@pytest.mark.skipif(
    USER_NOT_AUTHENTICATED,
    reason="Cannot run live test without authentication variables.",
)
def test_image_download_small_square():
    i = im.get_image("Hlddt")
    try:
        new_file = i.download(size="small square")
        assert new_file.name == "Hlddts.jpeg"
    finally:
        Path(new_file).unlink(missing_ok=True)


@pytest.mark.skipif(
    USER_NOT_AUTHENTICATED,
    reason="Cannot run live test without authentication variables.",
)
def test_image_download_bad_size():
    i = im.get_image("Hlddt")
    with pytest.raises(InvalidParameterError):  # pylint: disable=E1101
        i.download(size="Invalid sized triangle")


@pytest.mark.skipif(
    USER_NOT_AUTHENTICATED,
    reason="Cannot run live test without authentication variables.",
)
def test_image_download_to_parent_folder():
    i = im.get_image("Hlddt")
    try:
        new_file = i.download(path="..")
        expected_path = Path("..") / "Hlddt.jpeg"
        assert new_file == expected_path
    finally:
        Path(new_file).unlink(missing_ok=True)


def test_can_change_authentication_cannot_just_update_id():
    client = pyimgur.Imgur(client_id="123", client_secret="455")
    with pytest.raises(Exception):
        client.change_authentication(client_id="888")


def test_change_authentication_client_resets_auth():
    client = pyimgur.Imgur(
        client_id="123",
        client_secret="455",
        access_token="Hello",
        refresh_token="Refresh",
    )

    client.change_authentication(
        client_id="test test", client_secret="Something diffrent"
    )
    assert client.access_token is None
    assert client.refresh_token is None


def test_change_authentication_client_can_swithc_refresh_auth():
    client = pyimgur.Imgur(
        client_id="123",
        client_secret="455",
        access_token="Hello",
        refresh_token="Refresh",
    )

    client.change_authentication(refresh_token="New refresh token")
    assert client.access_token is None
    assert client.refresh_token is not None
    assert client.client_id is not None
    assert client.client_secret is not None


@pytest.mark.skipif(
    USER_NOT_AUTHENTICATED,
    reason="Cannot run live test without authentication variables.",
)
def test_lazy_loading_can_be_triggered_by_refresh():
    album = im.get_album("PaUermF")
    author = album.author
    assert not author._has_fetched
    author.refresh()
    assert author._has_fetched


@pytest.mark.skipif(
    USER_NOT_AUTHENTICATED,
    reason="Cannot run live test without authentication variables.",
)
def test_lazy_loading_can_be_triggered_attribute_access():
    album = im.get_album("PaUermF")
    author = album.author
    assert not author._has_fetched
    print(author.reputation)
    assert author._has_fetched


@pytest.mark.skipif(
    USER_NOT_AUTHENTICATED,
    reason="Cannot run live test without authentication variables.",
)
def test_lazy_loading_attributes_are_not_visible_until_fetched():
    album = im.get_album("PaUermF")
    author = album.author
    assert "reputation" not in vars(author).keys()
    author.refresh()
    assert "reputation" in vars(author).keys()


@pytest.mark.skipif(
    USER_NOT_AUTHENTICATED,
    reason="Cannot run live test without authentication variables.",
)
def test_ratelimit_values_are_updated():
    im.get_image("JPz2i")
    clientlimit = im.ratelimit_clientlimit
    clientremaining = im.ratelimit_clientremaining
    userlimit = im.ratelimit_userlimit
    userremaining = im.ratelimit_userremaining
    userreset = im.ratelimit_userreset
    im.get_image("wHxiibZ")
    assert im.ratelimit_clientlimit == clientlimit
    assert im.ratelimit_clientremaining == clientremaining - 1
    assert im.ratelimit_userlimit == userlimit
    assert im.ratelimit_userremaining == userremaining - 1

    # In rare cases, the second request will happen after the clock ticks over to a new second.
    # That means the time until reset of ratelimits has decreased by one second. Otherwise
    # the value would not have changed.
    assert im.ratelimit_userreset >= userreset - 1
