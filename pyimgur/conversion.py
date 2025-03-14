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

"""Converts data to the format Imgur expects."""

from numbers import Integral


def get_content_to_send(
    params=None,
    method="GET",
    as_json=False,
    use_form_data=False,
):
    """Get the content to send to Imgur, in the format it expects.

    This means formatting stuff properly, removing None values and figuring out whether imgur wants
    stuff as data, json or form data.

    """

    params, files = to_imgur_format(params, as_json and use_form_data)

    content_to_send = {"files": files, "params": None, "data": None, "json": None}

    if method == "GET":
        content_to_send["params"] = params
    elif as_json:
        content_to_send["json"] = params
    else:
        content_to_send["data"] = params

    return content_to_send


def convert_to_imgur_list(regular_list):
    """Turn a python list into the list format Imgur expects."""
    if regular_list is None:
        return None
    return ",".join(str(item) for item in regular_list)


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


def to_imgur_format(params, use_form_data=False):
    """Convert the parameters t o the format Imgur expects."""
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


def clean_imgur_params(originals):
    """Clean the params before sending to Imgur.

    Remove keys set for internal purposes. Remove none
    values, that otherwise cause Imgur to throw errors.

    """
    if not originals:
        return {}

    params = {}
    for variable in originals.keys():
        if variable == "self":
            continue

        if originals[variable] is not None:
            params[variable] = originals[variable]

    return params
