import pytest

import pyimgur

from pyimgur.basic_objects import Basic_object

from . import im, USER_NOT_AUTHENTICATED
from .data import (
    MOCKED_IMAGE_DATA,
    MOCKED_ALBUM_DATA,
    MOCKED_GALLERY_ALBUM_DATA,
    MOCKED_GALLERY_IMAGE_DATA,
    MOCKED_COMMENT_DATA,
    MOCKED_USER_DATA,
    IMAGE_EXPECTED_DATA,
    ALBUM_EXPECTED_DATA,
    GALLERY_ALBUM_EXPECTED_DATA,
    GALLERY_IMAGE_EXPECTED_DATA,
    COMMENT_EXPECTED_DATA,
    USER_EXPECTED_DATA,
)


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
