Changelog
=========

This is the changelog for the released versions of PyImgur. These changes are
divided into four categories.

 * **[FEATURE]** Something new has been added.
 * **[BUGFIX]** Something was broken before, but is now fixed.
 * **[IMGUR]** A change caused by an upstream change from Imgur.
 * **[CHANGE]** Other changes affecting user programs, such as the renaming of
   a function.

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
