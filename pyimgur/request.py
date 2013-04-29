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

"""Handles sending and parsing the requests to an Imgur API endpoint."""

import json
import requests

from authentication import headers


def send_request(url, params=None, authentication=None, method='GET'):
    # TODO figure out if there is a way to minimize this
    # TODO Add error checking
    if method == 'GET':
        resp = requests.get(url, params=params, verify=False, headers=headers)
    elif method == 'POST':
        resp = requests.post(url, params, verify=False, headers=headers)
    elif method == 'PUT':
        resp = requests.put(url, params, verify=False, headers=headers)
    elif method == 'DELETE':
        resp = requests.delete(url, verify=False, headers=headers)
    if not resp.ok:
        resp.raise_for_status()
    result = json.loads(resp.content)['data']
    return result
