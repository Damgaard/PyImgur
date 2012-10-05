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

'''
Custom errors in PyImgur.

LookupError is used to indicate a function was called with an invalid
argument and thus avoid API calls with undefined behavior. Read the official
imgur documentation on error handling for more information.
http://api.imgur.com/error_handling
'''

class AccessDeniedError(Exception):
    """We don't have the authorization to do that."""

class ImgurError(Exception):
    """Our request returned with an error."""

class Code400(ImgurError):
    pass

class Code401(ImgurError):
    pass

class Code403(ImgurError):
    pass

class Code404(ImgurError):
    pass

class Code500(ImgurError):
    pass


def raise_error(status_code):
    if status_code == 400:
        raise Code400(
            "A parameter has a value that is out of bounds or otherwise "
            "incorrect. This status code is also returned when image uploads "
            "fail due to images that are corrupt or do not meet the format "
            "requirements.")
    elif status_code == 401:
        raise Code401(
            "The request requires user authentication. Either you were not "
            "logged in or the authentication you sent were invalid.")
    elif status_code == 403:
        raise Code403(
            "Forbidden. You don't have access to this action. If you're getting"
            " this error, check that you haven't run out of API credits and "
            "make sure you have valid tokens/secrets.")
    elif status_code == 404:
        raise Code404(
            "Action not supported. This indicates you have requested a resource"
            " that does not exist. For example, requesting page 100 from a list"
            " of 5 images will result in a 404.")
    elif status_code == 500:
        raise Code500(
            "Unexpected internal error. What it says. We'll strive NOT to "
            "return these but your app should be prepared to see it. It "
            "basically means that something is broken with the Imgur service.")
