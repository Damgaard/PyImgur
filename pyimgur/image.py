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

"""Image object"""

from pathlib import Path

import requests

from pyimgur.basic_objects import Basic_object, _change_object
from pyimgur.exceptions import (
    InvalidParameterError,
    FileOverwriteError,
    UnexpectedImgurException,
)


class Image(Basic_object):  # pylint: disable=too-many-instance-attributes
    """
    An image uploaded to Imgur.

    :ivar bandwidth: Bandwidth consumed by the image in bytes.
    :ivar datetime: Time inserted into the gallery, epoch time.
    :ivar deletehash: For anonymous uploads, this is used to delete the image.
    :ivar description: A short description of the image.
    :ivar height: The height of the image in pixels.
    :ivar id: The ID for the image.
    :ivar is_animated: is the image animated?
    :ivar is_favorited: Has the logged in user favorited this album?
    :ivar is_nsfw: Is the image Not Safe For Work (contains gore/porn)?
    :ivar link: The URL link to the image.
    :ivar link_big_square: The URL to a big square thumbnail of the image.
    :ivar link_huge_thumbnail: The URL to a huge thumbnail of the image.
    :ivar link_large_square: The URL to a large square thumbnail of the image.
    :ivar link_large_thumbnail: The URL to a large thumbnail of the image.
    :ivar link_medium_thumbnail: The URL to a medium thumbnail of the image.
    :ivar link_small_square: The URL to a small square thumbnail of the image.
    :ivar section: ??? - No info in Imgur documentation.
    :ivar size: The size of the image in bytes.
    :ivar title: The albums title.
    :ivar views: Total number of views the album has received.
    :ivar width: The width of the image in bytes.

    """

    def __init__(self, json_dict, imgur, has_fetched=True):
        self._info_url = imgur.base_url + f"/3/image/{json_dict['id']}"
        self.deletehash = None
        super().__init__(json_dict, imgur, has_fetched)

    def _populate(self, json_dict):
        super()._populate(json_dict)
        if "link" in vars(self):
            base, sep, ext = self.link.rpartition(".")
            self.link_small_square = base + "s" + sep + ext
            self.link_big_square = base + "b" + sep + ext
            self.link_small_thumbnail = base + "t" + sep + ext
            self.link_medium_thumbnail = base + "m" + sep + ext
            self.link_large_thumbnail = base + "l" + sep + ext
            self.link_huge_thumbnail = base + "h" + sep + ext

    def delete(self):
        """Delete the image."""
        url = self._imgur.base_url + f"/3/image/{self._delete_or_id_hash}"
        return self._imgur.send_request(url, method="DELETE")

    def download(self, path="", name=None, overwrite=False, size=None):
        """
        Download the image.

        :param path: The image will be downloaded to the folder specified at
            path, if path is None (default) then the current working directory
            will be used.
        :param name: The name the image will be stored as (not including file
            extension). If name is None, then the title of the image will be
            used. If the image doesn't have a title, it's id will be used. Note
            that if the name given by name or title is an invalid filename,
            then the hash will be used as the name instead.
        :param overwrite: If True overwrite already existing file with the same
            name as what we want to save the file as.
        :param size: Instead of downloading the image in it's original size, we
            can choose to instead download a thumbnail of it. Options are
            'small_square', 'big_square', 'small_thumbnail',
            'medium_thumbnail', 'large_thumbnail' or 'huge_thumbnail'.

        :returns: Name of the new file.
        :raises FileExistsError: If the file already exists and overwrite is False
        """

        def save_as(filename):
            local_path = Path(path) / filename
            if local_path.exists() and not overwrite:
                raise FileOverwriteError(
                    f"Trying to save as {local_path}, but file already exists."
                )
            with open(local_path, "wb") as out_file:
                out_file.write(resp.content)
            return local_path

        valid_sizes = {
            "small_square": "s",
            "big_square": "b",
            "small_thumbnail": "t",
            "medium_thumbnail": "m",
            "large_thumbnail": "l",
            "huge_thumbnail": "h",
        }

        if size is not None:
            size = size.lower().replace(" ", "_")
            if size not in valid_sizes:
                raise InvalidParameterError(
                    f"Invalid size. Valid options are: {', '.join(valid_sizes.keys())}"
                )

        suffix = valid_sizes.get(size, "")
        _, sep, ext = self.link.rpartition(".")

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "referer": "https://imgur.com/gallery/cat-synth-AgnksJY",
        }

        url = f"https://imgur.com/download/{self.id}/undefined"
        # Should be a way to reuse existing functionality without making things too complicated
        resp = requests.get(url, headers=headers, stream=True, timeout=60)

        if resp.status_code != 200:
            raise UnexpectedImgurException(
                f"Failed to download image: {resp.status_code} {resp.text}"
            )

        if name:
            return save_as(name + suffix + sep + ext)

        return save_as(self.id + suffix + sep + ext)

    def favorite(self):
        """
        Favorite the image.

        Favoriting an already favorited image will unfavorite it.
        """
        url = self._imgur.base_url + f"/3/image/{self.id}/favorite"
        return self._imgur.send_request(url, needs_auth=True, method="POST")

    def submit_to_gallery(self, title, bypass_terms=False):
        """
        Add this to the gallery.

        Require that the authenticated user has accepted gallery terms and
        verified their email.

        :param title: The title of the new gallery item.
        :param bypass_terms: If the user has not accepted Imgur's terms yet,
            this method will return an error. Set this to True to by-pass the
            terms.
        """
        url = self._imgur.base_url + f"/3/gallery/{self.id}"
        payload = {"title": title, "terms": "1" if bypass_terms else "0"}
        self._imgur.send_request(url, needs_auth=True, params=payload, method="POST")
        item = self._imgur.get_gallery_image(self.id)
        _change_object(self, item)
        return self

    def update(self, title=None, description=None):
        """Update the image with a new title and/or description."""
        url = self._imgur.base_url + f"/3/image/{self._delete_or_id_hash}"

        if not title and not description:
            raise InvalidParameterError(
                "At least one of title or description must be provided."
            )

        is_updated = self._imgur.send_request(
            url, params=locals(), method="POST", as_json=True
        )
        if is_updated:
            self.title = title or self.title
            self.description = description or self.description

        return is_updated
