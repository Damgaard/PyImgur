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

"""
Test suite for PyImgur.

Running the test suite takes about 75 seconds.
"""

import filecmp
import os
import unittest
import uuid

from . import *
import test_auth as auth

LOCAL_FILE = "local.jpg"
WEB_IMG = 'http://www.paradoxplaza.com/sites/all/themes/paradoxplaza/logo.png'


class AnonymousTest(unittest.TestCase):
    def test_delete_image_with_del_hash(self):
        image_info = upload_image(LOCAL_FILE, api_key=auth.API_KEY)
        deletehash = image_info['image']['deletehash']
        result = delete_image(deletehash)
        self.assertEqual(result['message'], 'Success')

    def test_upload_local(self):
        image_info = upload_image(LOCAL_FILE, api_key=auth.API_KEY)
        self.assertTrue("image" in image_info.keys())
        deletehash = image_info['image']['deletehash']
        delete_image(deletehash)

    def test_upload_local_and_web_given(self):
        self.assertRaises(LookupError, upload_image, LOCAL_FILE, url=WEB_IMG,
                          api_key=auth.API_KEY)

    def test_upload_from_the_web(self):
        image_info = upload_image(url=WEB_IMG, api_key=auth.API_KEY)
        deletehash = image_info['image']['deletehash']
        result = delete_image(deletehash)
        self.assertEqual(result['message'], 'Success')

    def test_upload_with_arguments(self):
        image_info = upload_image(LOCAL_FILE, title='title',
                                  caption = 'caption', api_key=auth.API_KEY)
        self.assertTrue(image_info['image']['title'], 'title')
        self.assertTrue(image_info['image']['caption'], 'caption')
        deletehash = image_info['image']['deletehash']
        result = delete_image(deletehash)

    def test_upload_without_api_key(self):
        self.assertRaises(errors.Code401, upload_image, LOCAL_FILE)


class AuthenticatedTest(unittest.TestCase):
    def setUp(self):
        oauth_set_credentials(auth.CONSUMER_KEY, auth.CONSUMER_SECRET,
                              auth.TOKEN_KEY, auth.TOKEN_SECRET)

    def test_account_images(self):
        start_images = account_images()
        self.assertTrue(isinstance(start_images, list))

    def test_account_images_noalbum(self):
        all_images = account_images()
        noalbumimages = account_images(noalbum=True)
        self.assertTrue(all_images != noalbumimages)

    def test_count_albums(self):
        albums = count_albums()
        self.assertTrue(albums > 0)

    def test_count_albums(self):
        images = count_images()
        self.assertTrue(images > 0)

    def test_count_images(self):
        initial_count = count_images()
        image_info = upload_image(LOCAL_FILE)
        second_count = count_images()
        self.assertEqual(second_count, initial_count + 1)

    def test_create_album_defaults(self):
        my_defaults = create_album()
        imgur_defaults = create_album(title='', description='', privacy='',
                                      layout='')
        self.assertEqual(my_defaults['title'], imgur_defaults['title'])
        self.assertEqual(my_defaults['description'],
                         imgur_defaults['description'])
        self.assertEqual(my_defaults['privacy'], imgur_defaults['privacy'])
        self.assertEqual(my_defaults['layout'], imgur_defaults['layout'])
        result = delete_album(my_defaults['id'])['message']
        result = delete_album(imgur_defaults['id'])['message']

    def test_create_and_delete_album(self):
        album = create_album()
        album_id = album['id']
        result = delete_album(album_id)['message']
        self.assertEqual(result, 'Success')

    def test_delete_album_nonexisting(self):
        self.assertRaises(errors.Code404, delete_album, 'invalid')

    def test_delete_image_with_img_hash(self):
        image_info = upload_image(LOCAL_FILE)
        imagehash = image_info['image']['hash']
        result = delete_image(imagehash)['message']
        self.assertEqual(result, 'Success')

    def test_edit_album_parameters(self):
        # Privacy cannot be tested, as it is not exposed via info_album
        album_id = 'kEdJc'
        old_settings = info_album(album_id)
        new_title = 'Title: %s' % uuid.uuid4()
        new_des = 'Des: %s' % uuid.uuid4()
        layout = 'grid' if old_settings['layout'] == 'grid' else 'blog'
        change_to = edit_album(album_id, title=new_title, description=new_des,
                               layout=layout)
        new_settings = info_album(album_id)
        self.assertEqual(new_settings['title'], new_title)
        self.assertEqual(new_settings['description'], new_des)
        self.assertEqual(new_settings['layout'], layout)

    def test_edit_album_add_images(self):
        unittest.skip("Currently doesn't work in testing. Works in production")

    def test_edit_images(self):
        image_info = upload_image(LOCAL_FILE, api_key=auth.API_KEY)['image']
        edit_image(image_info['hash'], title='new_title', caption="new_cap")
        info = info_image(image_info['hash'])['image']
        self.assertEqual(info['title'], 'new_title')
        self.assertEqual(info['caption'], 'new_cap')

    def test_info_account(self):
        info = info_account()
        self.assertTrue('is_pro' in info.keys())

    def test_info_account(self):
        info = info_albums()
        albums = count_albums()
        self.assertEqual(len(info), albums)

    def test_order_albums(self):
        unittest.skip('Upstream bug.')

    def test_order_album_images(self):
        unittest.skip('Upstream bug.')

    def test_upload_to_account_web(self):
        oauth_set_credentials(auth.CONSUMER_KEY, auth.CONSUMER_SECRET,
                              auth.TOKEN_KEY, auth.TOKEN_SECRET)
        image_info = upload_image(url=WEB_IMG)
        deletehash = image_info['image']['deletehash']
        result = delete_image(deletehash)
        self.assertEqual(result['message'], 'Success')


class DownloadImageTest(unittest.TestCase):
    def test_download(self):
        image_hash = 'yvRHP'
        dl_file = download_image(image_hash)
        self.assertTrue(os.path.exists(dl_file))
        os.remove(dl_file)

    def test_download_non_existing_image(self):
        self.assertRaises(errors.Code404, download_image, 'ABCDEF')

    def test_download_other_size(self):
        image_hash = 'yvRHP'
        original_size = download_image(image_hash)
        os.rename(original_size, 'original.jpg')
        small_square = download_image(image_hash, 'small_square')
        self.assertFalse(filecmp.cmp('original.jpg', small_square))
        os.remove('original.jpg')
        os.remove(small_square)


class HelperTests(unittest.TestCase):
    def test_imgur_lists_empty(self):
        self.assertEqual('', helpers._to_imgur_list([]))

    def test_imgur_lists_non_empty(self):
        python_list = ['6sYjs', 'dTTqa', 'gsE8z']
        imgur_list = '(6sYjs,dTTqa,gsE8z)'
        self.assertEqual(imgur_list, helpers._to_imgur_list(python_list))


class NoAutentication(unittest.TestCase):
    def test_credits(self):
        imgur_credits = credits()
        self.assertTrue('limit' in imgur_credits.keys())

    def test_info_image(self):
        image_hash = 'yvRHP'
        returned = info_image(image_hash)
        self.assertEqual(image_hash, returned['image']['hash'])

    def test_info_album(self):
        album_hash = 'p30mf'
        correct_title = 'Kurt Cobain Rare Pictures'
        returned = info_album('p30mf')
        self.assertEqual(correct_title, returned['title'])

    def test_non_existing_image(self):
        non_existing_hash = "qqqqqq"
        self.assertRaises(errors.ImgurError, info_image, non_existing_hash)

    def test_oembed(self):
        result = oembed('i.imgur.com/yvRHP.jpg')
        self.assertTrue('provider_url' in result.keys())

    def test_stats(self):
        imgur_stats = stats()
        self.assertTrue('most_popular_images' in imgur_stats.keys())

    def test_stats_today_not_equal_month(self):
        month = stats('month')
        today = stats('today')
        self.assertNotEqual(month, today)

    def test_sideload(self):
        base_api_url = "http://api.imgur.com/2/upload.json"
        url = sideload(WEB_IMG)
        self.assertEqual(url, base_api_url + "?url=%s" % WEB_IMG)

    def test_sideload_with_edit(self):
        base_api_url = "http://api.imgur.com/2/upload.json"
        url = sideload(WEB_IMG, edit=True)
        self.assertEqual(url, base_api_url + "?edit&url=%s" % WEB_IMG)


class OAuthTest(unittest.TestCase):
    def test_oauth_access_token(self):
        unittest.skip('This cannot be tested without user input.')

    def test_oauth_pin_without_consumer_token(self):
        oauth_set_credentials(consumer_key=auth.CONSUMER_KEY,
                              consumer_secret=auth.CONSUMER_SECRET,
                              token_key=auth.TOKEN_KEY,
                              token_secret=auth.TOKEN_SECRET)
        self.assertTrue(isinstance(oauth_pin(), str))

    def test_oauth_set_credentials(self):
        self.assertRaises(LookupError, oauth_set_credentials)
        # Ensure none of these create errors
        oauth_set_credentials(consumer_key=auth.CONSUMER_KEY,
                              consumer_secret=auth.CONSUMER_SECRET)
        oauth_set_credentials(token_key=auth.TOKEN_KEY,
                              token_secret=auth.TOKEN_SECRET)
        oauth_set_credentials(consumer_key=auth.CONSUMER_KEY,
                              consumer_secret=auth.CONSUMER_SECRET,
                              token_key=auth.TOKEN_KEY,
                              token_secret=auth.TOKEN_SECRET)
