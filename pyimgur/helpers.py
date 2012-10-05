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

"""
Helper functions for PyImgur

Main purpose is to provide a combined spot to send, parse and check requests to
imgur. Also converts lists to the format needed by imgur.
"""

import json
import urllib
from sys import version_info
if version_info < (3, 0):
    from urllib import urlencode
else:
    from urllib.parse import urlenocode

import requests

import pyimgur

def _request(url, payload={}, method="GET", force_client=False):
    if force_client or (pyimgur._client and
                        pyimgur._client.token is not None):
        payload = urlencode(payload)
        if method == 'GET':
            response, content = pyimgur._client.request(url + "?" + payload)
        else:
            response, content = pyimgur._client.request(url, body=payload,
                                                              method=method)
        _test_response(int(response['status']), response, content)
        if response['content-type'] == 'application/json':
            content = json.loads(content)
        else:
            content = dict(x.split('=') for x in content.split('&'))
    else:
        if method == 'GET':
            r = requests.get(url, params=payload)
        elif method == 'POST':
            r = requests.post(url, payload)
        elif method == 'DELETE':
            r = requests.delete(url)
        _test_response(r.status_code, r.headers, r.content)
        content = json.loads(r.content)

    return content

def _test_response(status_code, headers, content):
    """
    Test if everything is okay.

    If everything isn't okay, call the appropriate error code.
    """
    if status_code != 200:
        pyimgur.errors.raise_error(status_code)
    elif content == '':
        error_message = ("Malformed json returned from Imgur. "
                         "Status_code: %d" % status_code)
        raise pyimgur.errors.imgurapiError(error_message)

def _to_imgur_list(ids):
    """
    Transform an python list to an PyImgur api list.

    [1, 3, 6] becomes '(1,3,6)'.
    """
    if not ids:
        return ''
    return '(' + ",".join("''" if i == '' else i for i in ids) + ')'
