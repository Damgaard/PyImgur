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


import responses

import pytest
from pyimgur.request import send_request
from pyimgur.exceptions import UnexpectedImgurException, InvalidParameterError


@responses.activate
def test_send_request():
    responses.get(
        "https://api.imgur.com/3/test",
        json={"data": {"title": "hello world"}},
    )
    content, _ = send_request("https://api.imgur.com/3/test")
    assert content == {"title": "hello world"}


@responses.activate
def test_send_request_handles_no_data_field():
    responses.get(
        "https://api.imgur.com/3/test",
        json={"status": "success"},
    )
    content, _ = send_request("https://api.imgur.com/3/test")
    assert content == {"status": "success"}


@responses.activate
def test_send_request_bad_method():
    with pytest.raises(InvalidParameterError):
        send_request("https://api.imgur.com/3/test", method="BAD")


@responses.activate
def test_send_request_unexpected_imgur_exception():
    responses.get(
        "https://api.imgur.com/3/test",
        json={"data": {"error": "Im a teapot", "request": "3/test", "method": "PUT"}},
        status=429,
    )

    with pytest.raises(UnexpectedImgurException):
        _, _ = send_request("https://api.imgur.com/3/test")


@responses.activate
def test_send_request_adds_paramaters():
    responses.get(
        "https://api.imgur.com/3/test",
        json={"data": "hello world"},
        match=[responses.matchers.query_param_matcher({"bool_value": "true"})],
    )

    content, _ = send_request(
        "https://api.imgur.com/3/test",
        content_to_send={"params": {"bool_value": "true"}},
    )
    assert content == "hello world"
