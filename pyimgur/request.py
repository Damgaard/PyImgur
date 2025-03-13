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


import os
from numbers import Integral

import requests

from pyimgur.exceptions import (
    UnexpectedImgurException,
    InvalidParameterError,
    ResourceNotFoundError,
)

MAX_RETRIES = 3
RETRY_CODES = [500]

VERIFY_SSL = os.getenv("PYIMGUR_VERIFY_SSL", "True").lower() == "true"
TIMEOUT_SECONDS = int(os.getenv("PYIMGUR_TIMEOUT", "30"))


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
    url: str,
    params: dict | None = None,
    method: str = "GET",
    authentication: dict | None = None,
    as_json: bool = False,
    use_form_data: bool = False,
):
    """Send a request to the Imgur API.

    Note that a lot is also handled in the send_request method inside the __init__.py file.

    Args:
        url: The API endpoint URL to send the request to.
        params: Optional dictionary of parameters to send with the request.
        method: HTTP method to use ('GET', 'POST', 'PUT'). Defaults to 'GET'.
        authentication: Optional authentication headers.
        as_json: Whether to use data as json. Defaults to False.
        use_form_data: Whether to send data as form data. Defaults to False.

    """
    # TODO Add error checking
    params, files = to_imgur_format(params, as_json and use_form_data)

    # We may need to add more elements to the header later. For now, it seems
    # the only thing in the header is the authentication
    headers = authentication

    print("As json", as_json)
    print("Use form Data", use_form_data)
    print(f"Headers: {headers}")
    print(f"Url: {url}")
    print(f"Method: {method}")
    print(f"Params: {params}".replace("'", '"'))
    print(f"Headers: {headers}")

    content_to_send = {"files": files, "params": None, "data": None, "json": None}

    if method == "GET":
        content_to_send["params"] = params
    elif as_json:
        content_to_send["json"] = params
    else:
        content_to_send["data"] = params

    response = perform_request(url, method, content_to_send, headers)

    if response.status_code == 404:
        raise ResourceNotFoundError(f"Resource not found: {url}")

    content = response.json()
    if "data" in content.keys():
        content = content["data"]

    if not response.ok:
        error_msg = f"Imgur ERROR message: {content.get('error', 'unknown Error')}"
        raise UnexpectedImgurException(error_msg)

    ratelimit_info = dict(
        (k, int(v)) for (k, v) in response.headers.items() if k.startswith("x-ratelimit")
    )
    return content, ratelimit_info


def perform_request(url, method, content_to_send, headers):
    """Perform the actual request to the Imgur API with retries."""
    if method not in ["GET", "POST", "PUT", "DELETE"]:
        raise InvalidParameterError("Unsupported Method used")

    tries = 0
    while tries <= MAX_RETRIES:
        response = requests.request(
            method,
            url,
            params=content_to_send.get("params", None),
            data=content_to_send.get("data", None),
            json=content_to_send.get("json", None),
            files=content_to_send.get("files", None),
            headers=headers,
            verify=VERIFY_SSL,
            timeout=TIMEOUT_SECONDS,
        )

        if response.status_code in RETRY_CODES or response.content == "":
            tries += 1
        else:
            break

    return response
