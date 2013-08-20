Changelog
=========

This is the changelog for the released versions of PyImgur. These changes are
divided into four categories.

 * **[FEATURE]** Something new has been added.
 * **[BUGFIX]** Something was broken before, but is now fixed.
 * **[IMGUR]** A change caused by an upstream change from Imgur.
 * **[CHANGE]** Other changes affecting user programs, such as the renaming of
   a function.

PyImgur 0.5.2
-------------

 * **[BUGFIX]** Fixed an installation crash that happened if the `requests`
   dependency wasn't already installed.

PyImgur 0.5.1
-------------

 * **[BUGFIX]** Fix bug in :meth:`~pyimgur.__init__.Album.update` that caused
   it to crash when calling it with a list of image ids as the images argument.
   A bug also prevented the cover argument from being a Image object as is
   possible elsewhere, instead it could only be the id of an image.
 * **[BUGFIX]** If an album had no cover Image, then before it would create a
   lazy Image object for the cover with ``None`` as Id. Now the ``cover``
   attribute will correctly be ``None``.
 * **[BUGFIX]** Only albums instantiated with
   :meth:`~pyimgur.__init__.Imgur.get_album` starts with the ``images``
   attribute set. Now ``_has_fetched`` has been set to ``False`` for such
   albums. Meaning that a call to ``Album.images`` will refresh the object and
   it will then have the ``images`` attribute set.

PyImgur 0.5
-----------

 * **[FEATURE]** Add :meth:`~pyimgur.__init__.Imgur.get_at_url` that takes an
   url and returns an object matching what is located at the url.
 * **[FEATURE]** Add :meth:`~pyimgur.__init__.Imgur.get_memes_gallery` that
   return the gallery of memes as on `the webend <http://imgur.com/g/memes>`_.
 * **[FEATURE]** Add :meth:`~pyimgur.__init__.Imgur.get_subreddit_image` that
   can return a subreddit image.
 * **[IMGUR]** Imgur changed their API to return more data in the response,
   when uploading an image. But the variables that could be sent were always
   ``None`` in the response. See `the bug report to Imgur
   <https://groups.google.com/forum/#!topic/imgur/F3uVb55TMGo>`_
 * **[BUGFIX]** If :meth:`~pyimgur.__init__.Image.download` was used with an
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
