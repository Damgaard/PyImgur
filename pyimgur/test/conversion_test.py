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


from pyimgur.conversion import (
    convert_to_imgur_list,
    to_imgur_format,
    clean_imgur_params,
    get_content_to_send,
)


def test_get_content_to_send_none():
    assert get_content_to_send(None) == {
        "files": [],
        "params": {},
        "data": None,
        "json": None,
    }


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


def test_clean_imgur_params_none():
    assert {} == clean_imgur_params(None)


def test_clean_imgur_params_empty_params():
    assert {} == clean_imgur_params({})


def test_clean_imgur_params_purges_self():
    assert {} == clean_imgur_params({"self": "BOB"})


def test_clean_imgur_params_purges_removes_none_keys():
    assert {} == clean_imgur_params({"number": None})


def test_clean_imgur_params_keeps_regular_values():
    assert {"number": 5} == clean_imgur_params({"number": 5})


def test_clean_imgur_params_doesnt_purge_false_keys():
    assert {"number": False} == clean_imgur_params({"number": False})
