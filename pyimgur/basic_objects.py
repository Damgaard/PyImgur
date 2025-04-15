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

"""Basic object, which all subsequent objects inherit from."""


def _change_object(from_object, to_object):
    from_object.__class__ = to_object.__class__
    from_object.__dict__ = to_object.__dict__
    from_object.__repr__ = to_object.__repr__


class Basic_object:  # pylint: disable=invalid-name
    """Contains basic functionality shared by a lot of PyImgur's classes."""

    def __init__(self, json_dict, imgur, has_fetched=True):
        self._has_fetched = has_fetched
        self._imgur = imgur
        self._populate(json_dict)

    def _populate(self, json_dict):
        for key, value in json_dict.items():
            setattr(self, key, value)

        rename_attrs = {
            "favorite": {
                "forObjects": ("Album", "Image", "Gallery_album", "Gallery_image"),
                "to": "is_favorited",
            },
            "nsfw": {
                "forObjects": ("Album", "Image", "Gallery_album", "Gallery_image"),
                "to": "is_nsfw",
            },
            "animated": {"forObjects": ("Image", "Gallery_image"), "to": "is_animated"},
            "comment": {"forObjects": ("Comment",), "to": "text"},
            "deleted": {"forObjects": ("Comment",), "to": "is_deleted"},
            "viewed": {"forObjects": ("Notification",), "to": "is_viewed"},
            "url": {"forObjects": ("User",), "to": "name"},
        }

        for change_key, change_value in rename_attrs.items():
            if any(
                self.__class__.__name__ == class_name
                for class_name in change_value["forObjects"]
            ) and change_key in vars(self):
                value = self.__dict__[change_key]
                self.__dict__[change_value["to"]] = value
                del self.__dict__[change_key]

        # author_id should be gotten with .author.id instead
        dropped_attrs = [
            "author_id",
        ]

        for attr in dropped_attrs:
            if attr in vars(self):
                del self.__dict__[attr]

    def __repr__(self):
        return f"<{type(self).__name__} {self.id}>"

    def __getattr__(self, attribute):
        if not self._has_fetched:
            self.refresh()
            return getattr(self, attribute)
        raise AttributeError(
            f"{type(self).__name__} instance has no attribute '{attribute}'"
        )

    @property
    def _delete_or_id_hash(self):
        if self._imgur.access_token:
            return self.id

        return self.deletehash

    def refresh(self):
        """
        Refresh this objects attributes to the newest values.

        Attributes that weren't added to the object before, due to lazy
        loading, will be added by calling refresh.
        """
        resp = self._imgur.send_request(self._info_url)
        self._populate(resp)
        self._has_fetched = True


def _change_object(from_object, to_object):
    from_object.__class__ = to_object.__class__
    from_object.__dict__ = to_object.__dict__
    from_object.__repr__ = to_object.__repr__
    # NOTE: What if the object has been deleted in the meantime? That might
    # give a pretty cryptic error.
