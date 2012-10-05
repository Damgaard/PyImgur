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

'''
Main file and main functions for PyImgur.
'''

from base64 import b64encode
import os

import requests
import oauth2 as oauth

from . import decorators
from . import errors

from pyimgur.helpers import _request, _test_response, _to_imgur_list

_BASE_URL = "http://api.imgur.com/"
_API_PATH = {'info_album': _BASE_URL + "2/album/%s.json",
             'info_image': _BASE_URL + '2/image/%s.json',
             'credits' : _BASE_URL + '2/credits.json',
             'stats' : _BASE_URL + '2/stats.json',
             'upload' : _BASE_URL + '2/upload.json',
             'sideload' : _BASE_URL + '2/upload.json',
             'delete_image' : _BASE_URL + '2/delete/%s.json',
             'oembed' : _BASE_URL + 'oembed?url=%s',
             'request_token' : _BASE_URL + 'oauth/request_token',
             'authorize' : _BASE_URL + 'oauth/authorize',
             'access_token' : _BASE_URL + 'oauth/access_token',
             'account' : _BASE_URL + '2/account.json',
             'acct_albums' : _BASE_URL + '2/account/albums.json',
             'acct_albums_edit' : _BASE_URL + '2/account/albums/%s.json',
             'albums_count' : _BASE_URL + '2/account/albums_count.json',
             'images_count' : _BASE_URL + '2/account/images_count.json',
             'albums_order' : _BASE_URL + '2/account/albums_order.json',
             'albums_img_order' : _BASE_URL + '2/account/albums_order/%s.json',
             'acct_images' : _BASE_URL + '2/account/images.json',
             'owned_image' : _BASE_URL + '2/account/images/%s.json'
            }

# Maybe some loading of stored access from an ini file
_client = None

########################
# Functions not requirering or related to any authentication
########################

def credits():
    """Returns information about our API credits."""
    return _request(_API_PATH['credits'], locals())['credits']

def delete_image(img_hash):
    """
    Delete an image from imgur

    You can use this either by supplying the deletehash or the hash belonging
    to an image belonging to an account that you're authenticated as.
    """
    # This is unflexible as number of chars may be changed.
    if len(img_hash) < 8:
        # With image hash. Only for authenticated
        return _request(_API_PATH['owned_image'] % img_hash, locals(),
                        method='DELETE')['images']
    else:
        # With deletehash
        return _request(_API_PATH['delete_image'] % img_hash, locals())['delete']

def download_image(img_hash, size='original'):
    """
    Download the image.

    The first that exists of title, caption or hash on imgur will be used as
    the new local name of the image. Overwrites any existing file of the same
    name.
    """
    if size not in ['original', 'small_square', 'large_thumbnail']:
        raise LookupError('Size must be original, small_square or '
                          'large_thumbnail')
    info = info_image(img_hash)
    path = info['links'][size]
    _, file_extension = os.path.splitext(path)
    name = (info['image']['title'] or info['image']['caption'] or
            info['image']['hash'])
    full_name = name + file_extension
    with open(full_name, 'wb') as local_file:
        local_file.write(requests.get(path).content)
    return full_name

def info_album(album_id):
    """
    Return information about an album.

    Note that privacy setting is not exposed via this command.
    """
    return _request(_API_PATH['info_album'] % album_id, locals())['album']

def info_image(img_hash):
    """Return information about an image."""
    return _request(_API_PATH['info_image'] % img_hash, locals())['image']

def oembed(url, maxheight=None, maxwidth=None):
    """Return embed code as well as additional information."""
    format = 'json'
    return _request(_API_PATH['oembed'], locals())

def sideload(url, edit=False):
    """Return an url that sideloads the image at url."""
    if not url.startswith('http'):
        raise LookupError('Url must start with http')
    if edit:
        return _API_PATH['sideload'] + '?edit&url=%s' % url
    return _API_PATH['sideload'] + '?url=%s' % url

def stats(view='month'):
    """Return imgur-wide statistics."""
    if view not in ('', 'today', 'week', 'month'):
       raise LookupError('View must be today, week or month')
    return _request(_API_PATH['stats'], locals())['stats']

######################,
# Anonymous Application
########################

def upload_image(image_path=None, url=None, title=None, caption=None,
                 api_key=None):
    if bool(image_path) == bool(url):
        raise LookupError('Precisely one of image_path or url must be given')

    if image_path:
        with open(image_path, 'rb') as f:
            binary_data = f.read()
        image = b64encode(binary_data)
    else:
        image = url

    payload = {'key' : api_key, 'image': image,
               'title': title, 'caption': caption}

    if api_key is not None:
        # Anonymous upload
        return _request(_API_PATH['upload'], payload, method="POST")['upload']
    else:
        # Authenticated upload
        return (_request(_API_PATH['acct_images'], payload, method="POST")
                                                                   ['images'])

########################
# Oauthentication
########################

def oauth_set_credentials(consumer_key=None, consumer_secret=None,
                          token_key=None, token_secret=None):
    """Set Oauthentication credentials."""
    global _client
    changed_something = False
    if consumer_key and consumer_secret:
        consumer = oauth.Consumer(consumer_key, consumer_secret)
        _client = oauth.Client(consumer)
        changed_something = True
    if token_key and token_secret:
        if _client is not None:
            _client.token = oauth.Token(token_key, token_secret)
            changed_something = True
        else:
            raise errors.AccessDenied('No consumer info set!')
    if not changed_something:
        raise LookupError('oauth_set_credentials must be called with a pair '
                          'of either consumer_secret and consumer_key or '
                          'token_key and token_secret.')

@decorators._client_has_consumer
def oauth_pin(callback_url=''):
    """
    Get a url where the user can go to authorize our application.

    If a callback_url is provided, then this is the site where the user will be
    sent afterwards. The access token and secret pin will be provided as GET
    parameters. If no callback_url is provided, the user will be sent to a
    imgur site after authorisation where the pin will be displayed.
    """
    global _client
    if not (callback_url == '' or callback_url.startswith('http')):
        raise LookupError('Callback_url must start with http')
    _client.token = None
    request_token = _request(_API_PATH['request_token'], force_client = True)
    _client.token = oauth.Token(request_token['oauth_token'],
                                request_token['oauth_token_secret'])
    return "%s?oauth_token=%s&oauth_callback=%s" % (_API_PATH['authorize'],
                                  request_token['oauth_token'], callback_url)

@decorators.require_authentication
def oauth_access_token(verification_code):
    """
    Exchange the pin and access token for a permanent access token.

    Sets token to this user and returns (token, secret) for later use.
    """
    global _client
    _client.token.set_verifier(verification_code)
    access_token = _request(_API_PATH['access_token'], method='POST')
    _client.token = oauth.Token(access_token['oauth_token'],
                                access_token['oauth_token_secret'])
    return access_token['oauth_token'], access_token['oauth_token_secret']

########################
# Authenticated Application
########################

@decorators.require_authentication
def account_images(noalbum=False):
    """
    Return a list of images uploaded to this account.

    If noalbum is True, only return images that doesn't belong to any album.
    """
    kwargs = locals()
    if not noalbum:
        del kwargs['noalbum']
    return _request(_API_PATH['acct_images'], kwargs)['images']


@decorators.require_authentication
def count_albums():
    """
    Returns the number of albums.

    Note, this returns an integer. Not a dict.
    """
    return (_request(_API_PATH['albums_count'], locals())['albums_count']
                                                         ['count'])

@decorators.require_authentication
def count_images():
    """
    Returns the number of images belonging to the account.

    Note, this returns an integer. Not a dict.
    """
    return (_request(_API_PATH['images_count'], locals())
                                                ['images_count']['count'])

@decorators.require_authentication
def create_album(title='', description='', privacy='public', layout = 'blog'):
    """Create a new album for the authenticated account."""
    if layout not in ('', 'blog', 'horizontal', 'vertical', 'grid'):
        raise LookupError('Layout must be blog, horizontal, vertical or grid')
    elif privacy not in ('', 'public', 'hidden', 'secret'):
        raise LookupError('Privacy must be public, hidden or secret')
    return (_request(_API_PATH['acct_albums'], locals(), method='POST')
                                                        ['albums'])

@decorators.require_authentication
def delete_album(album_id):
    """Delete the album."""
    return _request(_API_PATH['acct_albums_edit'] % album_id, locals(),
            method='DELETE')['albums']

# BUG. Doesn't work with images or del_images
# It doesn't come with an error message. Nothing just happens
# Appears to be upstream bug, as add_images can be made to work with a hack.
@decorators.require_authentication
def edit_album(album_id, title='', description='', cover='', privacy='',
               layout='', images=[], add_images=[], del_images=[]):
    """Edit the variables for the album."""
    add_images = [''] + add_images
    images     = _to_imgur_list(images)
    add_images = _to_imgur_list(add_images)
    del_images = _to_imgur_list(del_images)
    if layout not in ('', 'blog', 'horizontal', 'vertical', 'grid'):
        raise LookupError('Layout must be blog, horizontal, vertical or grid')
    elif privacy not in ('', 'public', 'hidden', 'secret'):
        raise LookupError('Privacy must be public, hidden or secret')
    return _request(_API_PATH['acct_albums_edit'] % album_id, locals(),
                                                    method='POST')['albums']

@decorators.require_authentication
def edit_image(img_hash, title='', caption=''):
    """Edit an image belonging to an authenticated account."""
    return _request(_API_PATH['owned_image'] % img_hash, locals(),
                                               method='POST')['images']

@decorators.require_authentication
def info_account():
    """Return information about the account."""
    return _request(_API_PATH['account'], locals())['account']

@decorators.require_authentication
def info_albums(count=30, page=1):
    """List information about albums."""
    return _request(_API_PATH['acct_albums'], locals())['albums']

@decorators.require_authentication
def order_albums(ids):
    """
    Re-order albums.

    Note any misspelling will cause a silent falling. Upstream bug cause it to
    deadlock after enough changes and prevent any further online change.
    Making a single manuel change restes this and allow further api reordering.
    """
    ids = _to_imgur_list(ids)
    return (_request(_API_PATH['albums_order'], locals(), method='POST')
                                                          ['albums_order'])

# BUG. it cannot find the album with json
# Can find the album, but won't update if I just go with xml
# The following is how it should be if everything worked upstream
'''
@decorators.require_authentication
def order_album_images(album_id, hashes):
    """Reorder the images within an album."""
    hashes = _to_imgur_list(hashes)
    return _request(_API_PATH['albums_img_order'] % album_id, locals(),
                                                              method='POST')
'''
