PyImgur
=======

The simple way of using Imgur.

With PyImgur you won't have to deal with REST, but can instead use python-
idiomatic code. This will make your code easier to read, easier to understand
and faster to write.

A quick example
---------------

Lets start by doing an anonymous image upload, getting some information about
the uploaded image and then deleting it from Imgur::

    import imgur

    im = imgur.Imgur() # sigh... might as well just be a imgur.init()
    uploaded_image = im.upload_image(PATH_TO_LOCAL_FILE,
                                     title="Uploaded with PyImgur")
    print(uploaded_image.title)
    print(uploaded_image.date)
    print(uploaded_image.url)
    uploaded_image.delete()

For comparison, see ``how to implement this without PyImgur``.

What Can I do with PyImgur
--------------------------

You can upload images, download images, read comments, update your albums,
message people and more. In fact, you can do almost everything via PyImgur that
you can do via the webend. Only faster and automatically.

Using PyImgur - The Grand view
------------------------------

PyImgur is built on object oriented principles, with the information available
on Imgur accessible through classes representing them. The Imgur class that we
initialized at the beginning of the previous example contains the general
methods that have to do with Imgur itself such as the ``get_stats`` method that
return general statistical information. Things returned from Imgur are also
represented using classes such as Image. ``uploaded_image`` in the previous
example was an instance of Image.

Authentication
--------------

Just like when we access Imgur via the website, certain actions require us
to authenticate before they can be used. For instance we can't create an album
before we're authenticated as a user. This authentication happens via OAuth2,
where the user go to a page on Imgur and clicks a button that gives us us
access to their account. We gain a user secret and user key, which we use to
show Imgur that the user has allowed us to access Imgur via their account.
Important to note is that we don't get the users password and they can revoke
our access at any time.

Installation
------------

Use ``pip`` to download the latest version of PyImgur from PyPi.

    $ pip install pyimgur

Support
-------

If you have any questions or problems using PyImgur. Feel free to either shoot
me an e-mail or file an issue on the `project page at github <https://
github.com/Damgaard/PyImgur>`_.
