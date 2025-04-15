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

"""Tests of the Imgur class."""

from pathlib import Path

import pytest

import pyimgur
from pyimgur import Album, Image, InvalidParameterError, ResourceNotFoundError

from . import USER_NOT_AUTHENTICATED, im, unauthed_im

TITLE = "Fancy title!"
DESCRIPTION = "Hello Description"

# Identify path to cat image. Needed as otherwise 2 tests might
# break depending on whether test suite is run from root or from
# the test folder.
current_file_path = Path(__file__).resolve()
current_directory = current_file_path.parent
CAT_IMAGE_PATH = current_directory / "cat.jpg"
COFFEE_MP4_PATH = current_directory / "coffee.mp4"


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
    new_filename = "NotExistingFile.jpg"
    try:
        new_filename = i.download(name="Hlddt").name
    except Exception:  # pylint: disable=broad-exception-caught
        Path(new_filename).unlink(missing_ok=True)

    assert new_filename == "Hlddt.jpeg"

    # Assert file exists and not just in name only
    assert Path(new_filename).exists()
    filesize = Path(new_filename).stat().st_size
    Path(new_filename).unlink(missing_ok=True)
    assert filesize > 0


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


def test_get_subreddit_invalid_sort():
    with pytest.raises(InvalidParameterError):
        im.get_subreddit_gallery("pic", sort="invalid")


@pytest.mark.skipif(
    USER_NOT_AUTHENTICATED,
    reason="Cannot run live test without authentication variables.",
)
def test_get_subreddit():
    response = im.get_subreddit_gallery("pic", limit=5)
    assert isinstance(response[0], (Image, Album))


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
def test_get_subreddit_gallery_low_limit():
    requested_limit = 5
    response = im.get_subreddit_gallery("pic", limit=requested_limit)
    assert len(response) == requested_limit


@pytest.mark.skipif(
    USER_NOT_AUTHENTICATED,
    reason="Cannot run live test without authentication variables.",
)
def test_get_gallery_album():
    album = im.get_gallery_album("vDtsSUW")
    assert album.title == "Baby elephant asks for water from a man in Nepal"


@pytest.mark.skipif(
    USER_NOT_AUTHENTICATED,
    reason="Cannot run live test without authentication variables.",
)
def test_get_gallery_album_does_not_exist():
    with pytest.raises(ResourceNotFoundError):
        im.get_gallery_album("NotExist")


class GetAtUrlTests:
    def test_retrieve_non_imgur_url(self):
        url = "http://github.com"
        result = im.get_at_url(url)
        assert result is None

    @pytest.mark.skipif(
        im.refresh_token is None,
        reason="Cannot run live test without authentication variables.",
    )
    def test_retrieve_comment(self):
        url = "http://imgur.com/gallery/CleiK2V/comment/87511312"
        comment = im.get_at_url(url)
        assert isinstance(comment, pyimgur.Comment)

    @pytest.mark.skipif(
        im.refresh_token is None,
        reason="Cannot run live test without authentication variables.",
    )
    def test_retrieve_album(self):
        album = im.get_at_url("http://imgur.com/a/SPlYO")
        assert isinstance(album, pyimgur.Album)

    @pytest.mark.skipif(
        im.refresh_token is None,
        reason="Cannot run live test without authentication variables.",
    )
    def test_retrieve_album_with_fragment(self):
        album = im.get_at_url("http://imgur.com/a/SPlYO#0")
        assert isinstance(album, pyimgur.Album)

    @pytest.mark.skipif(
        im.refresh_token is None,
        reason="Cannot run live test without authentication variables.",
    )
    def test_retrieve_album_with_params(self):
        album = im.get_at_url("http://imgur.com/a/SPlYO?sort=hot")
        assert isinstance(album, pyimgur.Album)

    @pytest.mark.skipif(
        im.refresh_token is None,
        reason="Cannot run live test without authentication variables.",
    )
    def test_retrieve_image(self):
        image = im.get_at_url("http://imgur.com/c79sp")
        assert isinstance(image, pyimgur.Image)
        assert image.title is not None

    @pytest.mark.skipif(
        im.refresh_token is None,
        reason="Cannot run live test without authentication variables.",
    )
    def test_retrieve_user(self):
        user = im.get_at_url("http://imgur.com/user/sarah")
        assert isinstance(user, pyimgur.User)
        assert user.name is not None

    @pytest.mark.skipif(
        im.refresh_token is None,
        reason="Cannot run live test without authentication variables.",
    )
    def test_retrieve_gallery_image(self):
        gallery_image = im.get_at_url("http://imgur.com/gallery/CleiK2V")
        assert isinstance(gallery_image, pyimgur.Gallery_image)
        assert gallery_image.title is not None

    @pytest.mark.skipif(
        im.refresh_token is None,
        reason="Cannot run live test without authentication variables.",
    )
    def test_retrieve_subreddit_image(self):
        gallery_image = im.get_at_url("http://imgur.com/gallery/RSwYGcc")
        assert isinstance(gallery_image, pyimgur.Gallery_image)
        assert gallery_image.title is not None

    @pytest.mark.skipif(
        im.refresh_token is None,
        reason="Cannot run live test without authentication variables.",
    )
    def test_retrieve_gallery_album(self):
        gallery_album = im.get_at_url("http://imgur.com/gallery/mpVzS")
        assert isinstance(gallery_album, pyimgur.Gallery_album)
        assert gallery_album.title is not None

    def test_retrive_non_existing_url_format(self):
        bad_result = im.get_at_url("http://imgur.com/bad/mpVzS")
        assert bad_result is None
