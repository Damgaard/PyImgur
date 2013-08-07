Changelog
=========

This is the changelog for the released versions of PyImgur. These changes are
divided into four categories.

 * **[FEATURE]** Something new has been added.
 * **[BUGFIX]** Something was broken before, but is now fixed.
 * **[IMGUR]** A change caused by an upstream change from Imgur.
 * **[CHANGE]** Other changes affecting user programs, such as the renaming of
   a function.

Unreleased Development version
------------------------------

 * **[FEATURE]** Add :meth:`~pyimgur.__init__.Imgur.get_memes_gallery` that
   return the gallery of memes as on `the webend <http://imgur.com/g/memes>`_.
 * **[FEATURE]** Add :meth:`~pyimgur.__init__.Imgur.get_subreddit_image` that
   can return a subreddit image.
 * **[Bugfix]** If :meth:`~pyimgur.__init__.Image.download` was used with an
   invalid filename given as the ``name`` argument or an invalid filename was
   gotten via the title, then the download would fail with an IOError. It now
   defaults to saving it with the hash as the name if the primary choice is an
   invalid filename.
 * **[BUGFIX]** Manually calling :meth:`~pyimgur.__init__.Basic_object.refresh`
   didn't update the value of ``_has_fetched``.

PyImgur 0.4.2
-------------

 * **[FEATURE]** :meth:`~pyimgur.__init__.Imgur.upload_image` can now upload
   images given with a url as well as being able to upload images given with a
   path. Either a path or a url to an image must be given when calling
   :meth:`~pyimgur.__init__.Imgur.upload_image`.

PyImgur 0.4.1
-------------

 * **[FEATURE]** Instead of returning an error, PyImgur will now resend
   requests to Imgur if it's expected that the second request will be
   successful.  This is for the cases where Imgur has an internal error or the
   returned data is malformed.
 * **[BUGFIX]** Fixed that User.get_images() unnecessarily required
   authentication as a user.

PyImgur 0.4.0
-------------

 * **[CHANGE]** This version was a complete overhaul of PyImgur. It updated the
   version of Imgurs API PyImgur used to version 3.0 and implemented almost all
   functionality exposed. Additionally PyImgur changed from functional code to
   object oriented code.
