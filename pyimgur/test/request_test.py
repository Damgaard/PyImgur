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


import pyimgur


def test_to_imgur_list():
    assert None == pyimgur.request.to_imgur_list(None)
    assert "QK1fZ9L" == pyimgur.request.to_imgur_list(["QK1fZ9L"])
    assert "QK1fZ9L,NsuNI" == pyimgur.request.to_imgur_list(["QK1fZ9L",
                                                             "NsuNI"])
