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

"""Custom exceptions for PyImgur."""


class PyImgurError(Exception):
    """Base exception class for all PyImgur exceptions."""


class FileOverwriteError(PyImgurError):
    """Raised when attempting to save a file that already exists and overwrite is False."""


class UnexpectedImgurException(PyImgurError):
    """Imgur behaved in a unexpected way unhandled by this library.

    This could be a temporary issue with their service, a bug on their end
    or something else unexpected.
    """

    def __init__(self, message, response=None):
        super().__init__(message)
        self.response = response


class ImgurIsDownException(PyImgurError):
    """Imgur's API is not available."""


class AuthenticationError(PyImgurError):
    """Raised when authentication fails or is missing required credentials."""


class ResourceNotFoundError(PyImgurError):
    """Raised when requested Imgur resource (image, album, comment etc) is not found."""


class InvalidParameterError(PyImgurError):
    """Raised when invalid parameters are provided to an API call."""
