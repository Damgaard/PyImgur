"""Test basic reuqests.

For each public function on the objects, it runs the basic no argument test.
This ensures any unexpected changes in the url being called are caught.

Any testing of extra arguments or how the tests behaves under special conditions
should be done in different file. This allows this file to be simple and easily
proveable, whether all expected methods are covered or not.

When Python 3.9 is deprecated and PyImgur is updated to require 3.10, then
this function will also be updated to verify that the returned data matches
what is expected.

"""

import responses

from pyimgur import Album, Image, User, Gallery_image, Gallery_album

from tests import MOCKED_AUTHED_IMGUR
from .data import (
    MOCKED_ALBUM_DATA,
    MOCKED_USER_DATA,
    MOCKED_GALLERY_ALBUM_DATA,
    MOCKED_GALLERY_IMAGE_DATA,
    MOCKED_COMMENT_DATA,
    MOCKED_IMAGE_DATA,
)


class TestBasicUrlsAlbum:
    MOCKED_ALBUM = Album(MOCKED_ALBUM_DATA, MOCKED_AUTHED_IMGUR)

    @responses.activate
    def test_album_favorite_calls_right_url(self):
        responses.add(
            responses.POST,
            f"https://api.imgur.com/3/album/{self.MOCKED_ALBUM.id}/favorite",
            json={"data": {"id": self.MOCKED_ALBUM.id, "title": "test"}},
            status=200,
        )

        self.MOCKED_ALBUM.favorite()

        assert (
            responses.calls[0].request.url
            == f"https://api.imgur.com/3/album/{self.MOCKED_ALBUM.id}/favorite"
        )

    @responses.activate
    def test_album_add_images_calls_right_url(self):
        images = ["image1", "image2"]

        responses.add(
            responses.POST,
            f"https://api.imgur.com/3/album/{self.MOCKED_ALBUM.id}/add",
            json={"data": {"id": self.MOCKED_ALBUM.id, "title": "test"}},
            status=200,
        )

        self.MOCKED_ALBUM.add_images(images)

        assert (
            responses.calls[0].request.url
            == f"https://api.imgur.com/3/album/{self.MOCKED_ALBUM.id}/add"
        )

    @responses.activate
    def test_album_delete_calls_right_url(self):
        responses.add(
            responses.DELETE,
            f"https://api.imgur.com/3/album/{self.MOCKED_ALBUM.id}",
            json={"data": {"id": self.MOCKED_ALBUM.id, "title": "test"}},
            status=200,
        )

        self.MOCKED_ALBUM.delete()

        assert (
            responses.calls[0].request.url
            == f"https://api.imgur.com/3/album/{self.MOCKED_ALBUM.id}"
        )

    @responses.activate
    def test_album_remove_images_calls_right_url(self):
        images = ["image1", "image2"]

        responses.add(
            responses.POST,
            f"https://api.imgur.com/3/album/{self.MOCKED_ALBUM.id}/remove_images",
            json={"data": {"id": self.MOCKED_ALBUM.id, "title": "test"}},
            status=200,
        )

        self.MOCKED_ALBUM.remove_images(images)

        assert (
            responses.calls[0].request.url
            == f"https://api.imgur.com/3/album/{self.MOCKED_ALBUM.id}/remove_images"
        )

    @responses.activate
    def test_album_submit_to_gallery_calls_right_url(self):
        title = "Test Gallery"

        responses.add(
            responses.POST,
            f"https://api.imgur.com/3/gallery/{self.MOCKED_ALBUM.id}",
            json={"data": {"id": self.MOCKED_ALBUM.id, "title": "test"}},
            status=200,
        )

        # Currently the mocked gallery album is not a gallery version of the mocekd album.
        # Meaning if we simply return the mocked_gallery_album it will give issues with id.
        # So update it for now. Maybe in future it should be the same object returned.
        return_data = MOCKED_GALLERY_ALBUM_DATA
        return_data["id"] = self.MOCKED_ALBUM.id

        responses.add(
            responses.GET,
            f"https://api.imgur.com/3/gallery/album/{self.MOCKED_ALBUM.id}",
            json={"data": return_data},
            status=200,
        )

        self.MOCKED_ALBUM.submit_to_gallery(title)

        assert (
            responses.calls[0].request.url
            == f"https://api.imgur.com/3/gallery/{self.MOCKED_ALBUM.id}"
        )

    @responses.activate
    def test_album_update_calls_right_url(self):
        title = "Updated Title"
        description = "Updated Description"

        responses.add(
            responses.PUT,
            f"https://api.imgur.com/3/album/{self.MOCKED_ALBUM.id}",
            json={"data": {"id": self.MOCKED_ALBUM.id, "title": "test"}},
            status=200,
        )

        self.MOCKED_ALBUM.update(title=title, description=description)

        assert (
            responses.calls[0].request.url
            == f"https://api.imgur.com/3/album/{self.MOCKED_ALBUM.id}"
        )


class TestBasicUrlsGalleryAlbum:
    MOCKED_GALLERY_ALBUM = Gallery_album(MOCKED_GALLERY_ALBUM_DATA, MOCKED_AUTHED_IMGUR)

    @responses.activate
    def test_gallery_album_comment_calls_right_url(self):
        text = "Test comment"

        responses.add(
            responses.POST,
            "https://api.imgur.com/3/comment",
            json={"data": {"id": "123", "comment": text}},
            status=200,
        )

        self.MOCKED_GALLERY_ALBUM.comment(text)

        assert responses.calls[0].request.url == "https://api.imgur.com/3/comment"

    @responses.activate
    def test_gallery_album_downvote_calls_right_url(self):
        responses.add(
            responses.POST,
            f"https://api.imgur.com/3/gallery/{self.MOCKED_GALLERY_ALBUM.id}/vote/down",
            json={"data": {"id": self.MOCKED_GALLERY_ALBUM.id}},
            status=200,
        )

        self.MOCKED_GALLERY_ALBUM.downvote()

        assert (
            responses.calls[0].request.url
            == f"https://api.imgur.com/3/gallery/{self.MOCKED_GALLERY_ALBUM.id}/vote/down"
        )

    @responses.activate
    def test_gallery_album_get_comments_calls_right_url(self):
        responses.add(
            responses.GET,
            f"https://api.imgur.com/3/gallery/{self.MOCKED_GALLERY_ALBUM.id}/comments",
            json={"data": [MOCKED_COMMENT_DATA] * 50},
            status=200,
        )

        self.MOCKED_GALLERY_ALBUM.get_comments(limit=10)

        assert (
            responses.calls[0].request.url
            == f"https://api.imgur.com/3/gallery/{self.MOCKED_GALLERY_ALBUM.id}/comments"
        )

    @responses.activate
    def test_gallery_album_get_votes_calls_right_url(self):
        responses.add(
            responses.GET,
            f"https://api.imgur.com/3/gallery/{self.MOCKED_GALLERY_ALBUM.id}/votes",
            json={"data": {"ups": 100, "downs": 10}},
            status=200,
        )

        self.MOCKED_GALLERY_ALBUM.get_votes()

        assert (
            responses.calls[0].request.url
            == f"https://api.imgur.com/3/gallery/{self.MOCKED_GALLERY_ALBUM.id}/votes"
        )

    @responses.activate
    def test_gallery_album_upvote_calls_right_url(self):
        responses.add(
            responses.POST,
            f"https://api.imgur.com/3/gallery/{self.MOCKED_GALLERY_ALBUM.id}/vote/up",
            json={"data": {"id": self.MOCKED_GALLERY_ALBUM.id}},
            status=200,
        )

        self.MOCKED_GALLERY_ALBUM.upvote()

        assert (
            responses.calls[0].request.url
            == f"https://api.imgur.com/3/gallery/{self.MOCKED_GALLERY_ALBUM.id}/vote/up"
        )

    @responses.activate
    def test_gallery_album_remove_from_gallery_calls_right_url(self):
        return_data = MOCKED_GALLERY_ALBUM_DATA
        return_data["id"] = self.MOCKED_GALLERY_ALBUM.id

        responses.add(
            responses.DELETE,
            f"https://api.imgur.com/3/gallery/{self.MOCKED_GALLERY_ALBUM.id}",
            json={"data": {"id": self.MOCKED_GALLERY_ALBUM.id}},
            status=200,
        )

        responses.add(
            responses.GET,
            f"https://api.imgur.com/3/album/{self.MOCKED_GALLERY_ALBUM.id}",
            json={"data": return_data},
            status=200,
        )

        self.MOCKED_GALLERY_ALBUM.remove_from_gallery()

        assert (
            responses.calls[0].request.url
            == f"https://api.imgur.com/3/gallery/{self.MOCKED_GALLERY_ALBUM.id}"
        )


class TestBasicUrlsUser:
    MOCKED_USER = User(MOCKED_USER_DATA, MOCKED_AUTHED_IMGUR)

    @responses.activate
    def test_user_change_settings_calls_right_url(self):
        bio = "Updated bio"
        public_images = True
        messaging_enabled = True
        album_privacy = "public"
        accepted_gallery_terms = True

        responses.add(
            responses.POST,
            f"https://api.imgur.com/3/account/{self.MOCKED_USER.name}/settings",
            json={"data": {"bio": bio}},
            status=200,
        )

        self.MOCKED_USER.change_settings(
            bio=bio,
            public_images=public_images,
            messaging_enabled=messaging_enabled,
            album_privacy=album_privacy,
            accepted_gallery_terms=accepted_gallery_terms,
        )

        assert (
            responses.calls[0].request.url
            == f"https://api.imgur.com/3/account/{self.MOCKED_USER.name}/settings"
        )

    @responses.activate
    def test_user_delete_calls_right_url(self):
        responses.add(
            responses.DELETE,
            f"https://api.imgur.com/3/account/{self.MOCKED_USER.name}",
            json={"data": {"id": self.MOCKED_USER.id}},
            status=200,
        )

        self.MOCKED_USER.delete()

        assert (
            responses.calls[0].request.url
            == f"https://api.imgur.com/3/account/{self.MOCKED_USER.name}"
        )

    @responses.activate
    def test_user_get_albums_calls_right_url(self):
        responses.add(
            responses.GET,
            f"https://api.imgur.com/3/account/{self.MOCKED_USER.name}/albums/0",
            json={"data": [MOCKED_ALBUM_DATA] * 50},
            status=200,
        )

        self.MOCKED_USER.get_albums(limit=10)

        assert (
            responses.calls[0].request.url
            == f"https://api.imgur.com/3/account/{self.MOCKED_USER.name}/albums/0"
        )

    @responses.activate
    def test_user_get_comments_calls_right_url(self):
        responses.add(
            responses.GET,
            f"https://api.imgur.com/3/account/{self.MOCKED_USER.name}/comments",
            json={"data": [MOCKED_COMMENT_DATA] * 50},
            status=200,
        )

        self.MOCKED_USER.get_comments()

        assert (
            responses.calls[0].request.url
            == f"https://api.imgur.com/3/account/{self.MOCKED_USER.name}/comments"
        )

    @responses.activate
    def test_user_get_favorites_calls_right_url(self):
        responses.add(
            responses.GET,
            f"https://api.imgur.com/3/account/{self.MOCKED_USER.name}/favorites/0",
            json={"data": [MOCKED_GALLERY_IMAGE_DATA] * 50},
            status=200,
        )

        self.MOCKED_USER.get_favorites(limit=10)

        assert (
            responses.calls[0].request.url
            == f"https://api.imgur.com/3/account/{self.MOCKED_USER.name}/favorites/0"
        )

    @responses.activate
    def test_user_get_gallery_favorites_calls_right_url(self):
        responses.add(
            responses.GET,
            f"https://api.imgur.com/3/account/{self.MOCKED_USER.name}/gallery_favorites/0",
            json={"data": [MOCKED_IMAGE_DATA] * 50},
            status=200,
        )

        self.MOCKED_USER.get_gallery_favorites(limit=10)

        assert (
            responses.calls[0].request.url
            == f"https://api.imgur.com/3/account/{self.MOCKED_USER.name}/gallery_favorites/0"
        )

    @responses.activate
    def test_user_get_gallery_profile_calls_right_url(self):
        responses.add(
            responses.GET,
            f"https://api.imgur.com/3/account/{self.MOCKED_USER.name}/gallery_profile",
            json={"data": {"bio": "Test bio"}},
            status=200,
        )

        self.MOCKED_USER.get_gallery_profile()

        assert (
            responses.calls[0].request.url
            == f"https://api.imgur.com/3/account/{self.MOCKED_USER.name}/gallery_profile"
        )

    @responses.activate
    def test_user_has_verified_email_calls_right_url(self):
        responses.add(
            responses.GET,
            f"https://api.imgur.com/3/account/{self.MOCKED_USER.name}/verifyemail",
            json={"data": {"verified": True}},
            status=200,
        )

        self.MOCKED_USER.has_verified_email()

        assert (
            responses.calls[0].request.url
            == f"https://api.imgur.com/3/account/{self.MOCKED_USER.name}/verifyemail"
        )

    @responses.activate
    def test_user_get_images_calls_right_url(self):
        responses.add(
            responses.GET,
            f"https://api.imgur.com/3/account/{self.MOCKED_USER.name}/images/0",
            json={"data": [MOCKED_IMAGE_DATA] * 50},
            status=200,
        )

        self.MOCKED_USER.get_images(limit=10)

        assert (
            responses.calls[0].request.url
            == f"https://api.imgur.com/3/account/{self.MOCKED_USER.name}/images/0"
        )

    @responses.activate
    def test_user_get_settings_calls_right_url(self):
        responses.add(
            responses.GET,
            f"https://api.imgur.com/3/account/{self.MOCKED_USER.name}/settings",
            json={"data": {"bio": "Test bio"}},
            status=200,
        )

        self.MOCKED_USER.get_settings()

        assert (
            responses.calls[0].request.url
            == f"https://api.imgur.com/3/account/{self.MOCKED_USER.name}/settings"
        )

    @responses.activate
    def test_user_get_statistics_calls_right_url(self):
        responses.add(
            responses.GET,
            f"https://api.imgur.com/3/account/{self.MOCKED_USER.name}/stats",
            json={"data": {"reputation": 100}},
            status=200,
        )

        self.MOCKED_USER.get_statistics()

        assert (
            responses.calls[0].request.url
            == f"https://api.imgur.com/3/account/{self.MOCKED_USER.name}/stats"
        )

    @responses.activate
    def test_user_get_submissions_calls_right_url(self):
        responses.add(
            responses.GET,
            f"https://api.imgur.com/3/account/{self.MOCKED_USER.name}/submissions/0",
            json={"data": [MOCKED_GALLERY_IMAGE_DATA] * 50},
            status=200,
        )

        self.MOCKED_USER.get_submissions(limit=10)

        assert (
            responses.calls[0].request.url
            == f"https://api.imgur.com/3/account/{self.MOCKED_USER.name}/submissions/0"
        )

    @responses.activate
    def test_user_send_message_calls_right_url(self):
        body = "Test message"
        subject = "Test subject"
        reply_to = "123"

        responses.add(
            responses.POST,
            "https://api.imgur.com/3/message",
            json={"data": {"id": "123"}},
            status=200,
        )

        self.MOCKED_USER.send_message(body=body, subject=subject, reply_to=reply_to)

        assert responses.calls[0].request.url == "https://api.imgur.com/3/message"

    @responses.activate
    def test_user_send_verification_email_calls_right_url(self):
        responses.add(
            responses.POST,
            f"https://api.imgur.com/3/account/{self.MOCKED_USER.name}/verifyemail",
            json={"data": {"success": True}},
            status=200,
        )

        self.MOCKED_USER.send_verification_email()

        assert (
            responses.calls[0].request.url
            == f"https://api.imgur.com/3/account/{self.MOCKED_USER.name}/verifyemail"
        )


class TestBasicUrlsImage:
    MOCKED_IMAGE = Image(MOCKED_IMAGE_DATA, MOCKED_AUTHED_IMGUR)

    @responses.activate
    def test_image_delete_calls_right_url(self):
        responses.add(
            responses.DELETE,
            f"https://api.imgur.com/3/image/{self.MOCKED_IMAGE.id}",
            json={"data": {"id": self.MOCKED_IMAGE.id}},
            status=200,
        )

        self.MOCKED_IMAGE.delete()

        assert (
            responses.calls[0].request.url
            == f"https://api.imgur.com/3/image/{self.MOCKED_IMAGE.id}"
        )

    @responses.activate
    def test_image_favorite_calls_right_url(self):
        responses.add(
            responses.POST,
            f"https://api.imgur.com/3/image/{self.MOCKED_IMAGE.id}/favorite",
            json={"data": {"id": self.MOCKED_IMAGE.id}},
            status=200,
        )

        self.MOCKED_IMAGE.favorite()

        assert (
            responses.calls[0].request.url
            == f"https://api.imgur.com/3/image/{self.MOCKED_IMAGE.id}/favorite"
        )

    @responses.activate
    def test_image_update_calls_right_url(self):
        title = "Updated Title"
        description = "Updated Description"

        responses.add(
            responses.POST,
            f"https://api.imgur.com/3/image/{self.MOCKED_IMAGE.id}",
            json={"data": {"id": self.MOCKED_IMAGE.id}},
            status=200,
        )

        self.MOCKED_IMAGE.update(title=title, description=description)

        assert (
            responses.calls[0].request.url
            == f"https://api.imgur.com/3/image/{self.MOCKED_IMAGE.id}"
        )

    @responses.activate
    def test_image_submit_to_gallery_calls_right_url(self):
        return_data = MOCKED_GALLERY_IMAGE_DATA
        return_data["id"] = self.MOCKED_IMAGE.id

        title = "Test Gallery"

        responses.add(
            responses.POST,
            f"https://api.imgur.com/3/gallery/{self.MOCKED_IMAGE.id}",
            json={"data": {"id": self.MOCKED_IMAGE.id}},
            status=200,
        )

        responses.add(
            responses.GET,
            f"https://api.imgur.com/3/gallery/image/{self.MOCKED_IMAGE.id}",
            json={"data": return_data},
            status=200,
        )

        self.MOCKED_IMAGE.submit_to_gallery(title)

        assert (
            responses.calls[0].request.url
            == f"https://api.imgur.com/3/gallery/{self.MOCKED_IMAGE.id}"
        )


class TestBasicUrlsGalleryImage:
    MOCKED_GALLERY_IMAGE = Gallery_image(MOCKED_GALLERY_IMAGE_DATA, MOCKED_AUTHED_IMGUR)

    @responses.activate
    def test_gallery_image_comment_calls_right_url(self):
        text = "Test comment"

        responses.add(
            responses.POST,
            "https://api.imgur.com/3/comment",
            json={"data": {"id": "123", "comment": text}},
            status=200,
        )

        self.MOCKED_GALLERY_IMAGE.comment(text)

        assert responses.calls[0].request.url == "https://api.imgur.com/3/comment"

    @responses.activate
    def test_gallery_image_downvote_calls_right_url(self):
        responses.add(
            responses.POST,
            f"https://api.imgur.com/3/gallery/{self.MOCKED_GALLERY_IMAGE.id}/vote/down",
            json={"data": {"id": self.MOCKED_GALLERY_IMAGE.id}},
            status=200,
        )

        self.MOCKED_GALLERY_IMAGE.downvote()

        assert (
            responses.calls[0].request.url
            == f"https://api.imgur.com/3/gallery/{self.MOCKED_GALLERY_IMAGE.id}/vote/down"
        )

    @responses.activate
    def test_gallery_image_get_comments_calls_right_url(self):
        responses.add(
            responses.GET,
            f"https://api.imgur.com/3/gallery/{self.MOCKED_GALLERY_IMAGE.id}/comments",
            json={"data": [MOCKED_COMMENT_DATA] * 50},
            status=200,
        )

        self.MOCKED_GALLERY_IMAGE.get_comments(limit=10)

        assert (
            responses.calls[0].request.url
            == f"https://api.imgur.com/3/gallery/{self.MOCKED_GALLERY_IMAGE.id}/comments"
        )

    @responses.activate
    def test_gallery_image_get_votes_calls_right_url(self):
        responses.add(
            responses.GET,
            f"https://api.imgur.com/3/gallery/{self.MOCKED_GALLERY_IMAGE.id}/votes",
            json={"data": {"ups": 100, "downs": 10}},
            status=200,
        )

        self.MOCKED_GALLERY_IMAGE.get_votes()

        assert (
            responses.calls[0].request.url
            == f"https://api.imgur.com/3/gallery/{self.MOCKED_GALLERY_IMAGE.id}/votes"
        )

    @responses.activate
    def test_gallery_image_upvote_calls_right_url(self):
        responses.add(
            responses.POST,
            f"https://api.imgur.com/3/gallery/{self.MOCKED_GALLERY_IMAGE.id}/vote/up",
            json={"data": {"id": self.MOCKED_GALLERY_IMAGE.id}},
            status=200,
        )

        self.MOCKED_GALLERY_IMAGE.upvote()

        assert (
            responses.calls[0].request.url
            == f"https://api.imgur.com/3/gallery/{self.MOCKED_GALLERY_IMAGE.id}/vote/up"
        )

    @responses.activate
    def test_gallery_image_remove_from_gallery_calls_right_url(self):
        return_data = MOCKED_IMAGE_DATA
        return_data["id"] = self.MOCKED_GALLERY_IMAGE.id

        responses.add(
            responses.DELETE,
            f"https://api.imgur.com/3/gallery/{self.MOCKED_GALLERY_IMAGE.id}",
            json={"data": {"id": self.MOCKED_GALLERY_IMAGE.id}},
            status=200,
        )

        responses.add(
            responses.GET,
            f"https://api.imgur.com/3/image/{self.MOCKED_GALLERY_IMAGE.id}",
            json={"data": return_data},
            status=200,
        )

        self.MOCKED_GALLERY_IMAGE.remove_from_gallery()

        assert (
            responses.calls[0].request.url
            == f"https://api.imgur.com/3/gallery/{self.MOCKED_GALLERY_IMAGE.id}"
        )
