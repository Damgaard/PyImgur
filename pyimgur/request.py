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


def send_request(
    url: str,
    content_to_send: dict | None = None,
    headers: dict | None = None,
    method: str = "GET",
):
    """Send a request to the Imgur API.

    Note that a lot is also handled in the send_request method inside the __init__.py file.

    Args:
        url: The API endpoint URL to send the request to.
        params: Optional dictionary of parameters to send with the request.
        method: HTTP method to use ('GET', 'POST', 'PUT'). Defaults to 'GET'.
        headers: Headers to send with the request.
        as_json: Whether to use data as json. Defaults to False.
        use_form_data: Whether to send data as form data. Defaults to False.

    """

    if content_to_send is None:
        content_to_send = {}

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
        (k, int(v))
        for (k, v) in response.headers.items()
        if k.startswith("x-ratelimit")
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
