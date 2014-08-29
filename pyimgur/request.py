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

from __future__ import print_function

from numbers import Integral

import requests


MAX_RETRIES = 3
RETRY_CODES = [500]


def convert_general(value):
    """Take a python object and convert it to the format Imgur expects."""
    if isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, list):
        value = [convert_general(item) for item in value]
        value = convert_to_imgur_list(value)
    elif isinstance(value, Integral):
        return str(value)
    elif 'pyimgur' in str(type(value)):
        return str(getattr(value, 'id', value))
    return value


def convert_to_imgur_list(regular_list):
    """Turn a python list into the list format Imgur expects."""
    if regular_list is None:
        return None
    return ",".join(str(id) for id in regular_list)


def to_imgur_format(params):
    """Convert the parameters to the format Imgur expects."""
    if params is None:
        return None
    return dict((k, convert_general(val)) for (k, val) in params.items())


def send_request(url, params=None, method='GET', data_field='data',
                 authentication=None, verify=True):
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
    is_succesful_request = False
    tries = 0
    while not is_succesful_request and tries <= MAX_RETRIES:
        if method == 'GET':
            resp = requests.get(url, params=params, headers=headers,
                                verify=verify)
        elif method == 'POST':
            resp = requests.post(url, params, headers=headers, verify=verify)
        elif method == 'PUT':
            resp = requests.put(url, params, headers=headers, verify=verify)
        elif method == 'DELETE':
            resp = requests.delete(url, headers=headers, verify=verify)
        if resp.status_code in RETRY_CODES or resp.content == "":
            tries += 1
        else:
            is_succesful_request = True
    content = resp.json()
    if data_field is not None:
        content = content[data_field]
    if not resp.ok:
        try:
            error_msg = "Imgur ERROR message: {0}".format(content['error'])
            print(error_msg)
            print("-" * len(error_msg))
        except Exception:
            pass
        resp.raise_for_status()
    ratelimit_info = dict((k, int(v)) for (k, v) in resp.headers.items()
                          if k.startswith('x-ratelimit'))
    return content, ratelimit_info
