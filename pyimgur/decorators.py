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
Decorators. Used to ensure proper authentication before use.
'''

from decorator import decorator

# I would love to do from . import errors, _client. But sadly this gives
# problems as _client is not defined at the runtime.

import pyimgur

@decorator
def require_authentication(function, *args, **kwargs):
    """This function requires oauth_authentication to be executed."""
    if pyimgur._client is None or pyimgur._client.token is None:
        raise pyimgur.errors.AccessDeniedError('You need to be authenticated '
                                               'to do that')
    return function(*args, **kwargs)
