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
from pyimgur.request import to_imgur_format, convert_to_imgur_list, send_request
from pyimgur.exceptions import UnexpectedImgurException


def test_to_imgur_list():
    assert convert_to_imgur_list(None) is None
    assert "QK1fZ9L" == convert_to_imgur_list(["QK1fZ9L"])
    assert "QK1fZ9L,NsuNI" == convert_to_imgur_list(["QK1fZ9L", "NsuNI"])


def test_to_imgur_format_called_with_none_dict():
    assert ({}, []) == to_imgur_format(None)


def test_to_imgur_format_called_with_empty_dict():
    assert ({}, []) == to_imgur_format({})


def test_to_imgur_format_string():
    params = {"title": "Hello world"}
    assert params, None == to_imgur_format(params)


def test_to_imgur_format_number():
    params = {"number": 5}
    assert {"number": "5"}, None == to_imgur_format(params)


def test_to_imgur_format_boolean_true():
    params = {"truthiness": True}
    assert {"truthiness": "true"}, None == to_imgur_format(params)


def test_to_imgur_format_boolean_false():
    params = {"truthiness": False}
    assert {"truthiness": "false"}, None == to_imgur_format(params)


def test_to_imgur_list_empty():
    params = {"ids": []}
    assert {"ids": ""}, [] == to_imgur_format(params)


def test_to_imgur_format_with_list_empty():
    assert ({"values": ""}, []) == to_imgur_format({"values": []})


def test_to_imgur_format_with_list():
    assert ({"values": "QK1fZ9L"}, []) == to_imgur_format({"values": "QK1fZ9L"})


def test_to_imgur_format_with_list_concats_on_string():
    assert ({"values": "QK1fZ9L,NsuNI"}, []) == to_imgur_format(
        {"values": ["QK1fZ9L", "NsuNI"]}
    )


def test_to_imgur_format_multiple_values():
    params = {"truthiness": False, "number": 5, "title": "Hello World"}
    result = {"truthiness": "false", "number": "5", "title": "Hello World"}
    assert (result, []) == to_imgur_format(params)


def test_to_imgur_format_files():
    assert ({}, []) == to_imgur_format({}, True)


def test_to_imgur_format_files_for_ids():
    assert (
        {},
        [
            ("ids", (None, "QK1fZ9L")),
        ],
    ) == to_imgur_format({"ids": "QK1fZ9L"}, True)


def test_to_imgur_format_files_for_ids_multiple():
    assert (
        {},
        [
            ("ids", (None, "QK1fZ9L")),
            ("ids", (None, "NsuNI")),
        ],
    ) == to_imgur_format({"ids": ["QK1fZ9L", "NsuNI"]}, True)


def test_to_imgur_format_files_for_ids_multiple_and_params():
    assert (
        {"number": "5"},
        [
            ("ids", (None, "QK1fZ9L")),
            ("ids", (None, "NsuNI")),
        ],
    ) == to_imgur_format({"ids": ["QK1fZ9L", "NsuNI"], "number": 5}, True)


@responses.activate
def test_send_request():
    responses.get(
        "https://api.imgur.com/3/test",
        json={"data": "hello world"},
    )
    content, _ = send_request("https://api.imgur.com/3/test")
    assert content == "hello world"


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
        "https://api.imgur.com/3/test", params={"bool_value": True}
    )
    assert content == "hello world"
