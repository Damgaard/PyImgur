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

"""Handles sending and parsing requests to/from Imgur's REST API."""

# Note: The name should probably be changed to avoid confusion with the module
# requestS

from numbers import Integral

import requests

from pyimgur.exceptions import UnexpectedImgurException, InvalidParameterError

MAX_RETRIES = 3
RETRY_CODES = [500]


def convert_general(value):
    """Take a python object and convert it to the format Imgur expects."""
    if isinstance(value, bool):
        return "true" if value else "false"

    if isinstance(value, list):
        value = [convert_general(item) for item in value]
        value = convert_to_imgur_list(value)
    elif isinstance(value, Integral):
        return str(value)
    elif "pyimgur" in str(type(value)):
        return str(getattr(value, "id", value))

    return value


def convert_to_imgur_list(regular_list):
    """Turn a python list into the list format Imgur expects."""
    if regular_list is None:
        return None
    return ",".join(str(item) for item in regular_list)


def to_imgur_format(params: dict | None, use_form_data=False):
    """Convert the parameters to the format Imgur expects."""
    files = []
    if use_form_data:
        if params and "ids" in params:
            split_ids = convert_general(params["ids"]).split(",")
            for split_id in split_ids:
                files.append(("ids", (None, split_id)))

            del params["ids"]

    if params is None:
        return {}, files

    params = dict((k, convert_general(val)) for (k, val) in params.items())

    return params, files


def send_request(
    url,
    params=None,
    method="GET",
    authentication=None,
    verify=True,
    alternate=False,
    use_form_data=False,
):
    """Send a request to the Imgur API.

    Note that a lot is also handled in the send_request method inside the __init__.py file.

    Args:
        url: The API endpoint URL to send the request to.
        params: Optional dictionary of parameters to send with the request.
        method: HTTP method to use ('GET', 'POST', 'PUT'). Defaults to 'GET'.
        data_field: Field in response containing the data. Defaults to 'data'.
        authentication: Optional authentication headers.
        verify: Whether to verify SSL certificates. Defaults to True.
        alternate: Whether to use alternate request format. Defaults to False.
        use_form_data: Whether to send data as form data. Defaults to False.

    """
    # TODO: Looks like there isn't any protection to protect against
    # making calls without client_id / access_token. Not even on
    # endpoints that require it.

    # TODO figure out if there is a way to minimize this
    # TODO Add error checking
    params, files = to_imgur_format(params, alternate and use_form_data)

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

    if alternate:
        print("Being called with alternate")
        # headers["Content-Type"] = "application/json; charset=utf-8"
        # headers["Accept-Encoding"] = "gzip, deflate, br"

    print("Use form Data", use_form_data)
    print(f"Headers: {headers}")
    print(f"Url: {url}")
    print(f"Method: {method}")
    print(f"Params: {params}".replace("'", '"'))
    print(f"Headers: {headers}")

    is_succesful_request = False
    TIMEOUT_SECONDS = 30
    tries = 0
    while not is_succesful_request and tries <= MAX_RETRIES:
        if method == "GET":
            resp = requests.get(
                url,
                params=params,
                headers=headers,
                verify=verify,
                timeout=TIMEOUT_SECONDS,
            )
        elif method == "POST":
            if alternate:
                resp = requests.post(
                    url,
                    json=params,
                    files=files,
                    headers=headers,
                    verify=verify,
                    timeout=TIMEOUT_SECONDS,
                )
            else:
                resp = requests.post(
                    url, params, headers=headers, verify=verify, timeout=TIMEOUT_SECONDS
                )
        elif method == "PUT":
            if alternate:
                resp = requests.put(
                    url,
                    json=params,
                    headers=headers,
                    verify=verify,
                    timeout=TIMEOUT_SECONDS,
                )
            else:
                resp = requests.put(
                    url, params, headers=headers, verify=verify, timeout=TIMEOUT_SECONDS
                )
        elif method == "DELETE":
            resp = requests.delete(
                url, headers=headers, verify=verify, timeout=TIMEOUT_SECONDS
            )
        else:
            raise InvalidParameterError("Unsupported Method used")

        if resp.status_code in RETRY_CODES or resp.content == "":
            tries += 1
        else:
            is_succesful_request = True

    content = resp.json()
    if "data" in content.keys():
        content = content["data"]

    if not resp.ok:
        error_msg = f"Imgur ERROR message: {content.get('error', 'unknown Error')}"
        raise UnexpectedImgurException(error_msg)

    ratelimit_info = dict(
        (k, int(v)) for (k, v) in resp.headers.items() if k.startswith("x-ratelimit")
    )
    return content, ratelimit_info
