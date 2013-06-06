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

"""Handles sending and parsing requests to/from Imgur REST API."""

# Note: The name should probably be changed to avoid confusion with the module
# requestS

import json

import requests


def to_imgur_list(regular_list):
    """Turn a python list into the format Imgur expects."""
    if regular_list is None:
        return None
    return ",".join(str(id) for id in regular_list)


def to_imgur_format(params):
    """Convert normal Python types into the format Imgur expects."""
    if params is None:
        return None
    parsed = {}
    for key, value in params.iteritems():
        if isinstance(value, list):
            value = to_imgur_list(value)
        elif isinstance(value, bool):
            value = "true" if value else "false"
        parsed[key] = value
    return parsed


def send_request(url, params=None, method='GET', authentication=None):
    # TODO figure out if there is a way to minimize this
    # TODO Add error checking
    params = to_imgur_format(params)
    # We may need to add more elements to the header later. For now, it seems
    # the only thing in the header is the authentication
    headers = authentication
    # NOTE I could also convert the returned output to the correct object here.
    # The reason I don't is that some queries just want the json, so they can
    # update an existing object. This we do with lazy evaluation. Here we
    # wouldn't know that, although obviously we could have a "raw" parameter
    # that just returned the json. Dunno. Having parsing of the returned output
    # be done here could make the code simpler at the highest level. Just
    # request an url with some parameters and voila you get the object back you
    # wanted.
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
    # Some times we get a 200 return, but no content. Either an exception
    # should be raised or ideally, the request attempted again up to 3 times.
    content = json.loads(resp.content)['data']
    ratelimit_info = {key: int(value) for (key, value) in resp.headers.items()
                      if key.startswith('x-ratelimit')}
    return content, ratelimit_info
