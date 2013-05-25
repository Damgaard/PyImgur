Getting started with PyImgur
============================

PyImgur greatly simplifies accessing access to Imgurs API by wrapping it in a
OO layer that matches Python ideoms. This makes using imgur's API as normal as
using a regular python library.

Getting Authorized
------------------

Before we can start using PyImgur, we need to register our application with
Imgur. This way, Imgur can see what each application is doing on their site.
Go to https://api.imgur.com/oauth2/addclient to register your client. Note that
you can't use an application registration for the old v2 version of the imgur
API, which was depreciated in December 2012.

We can register out application as one of two types. Either anonymous or with
OAuth authentication. With the latter we can authenticate as a user and act on
their behalf, such as uploading images, adding images to their albums etc. We
can also do anything we can do with an anonymously registered app.

Baby Steps
----------

When we registered our application we got a ``client_id`` and ``client_secret``
irrespective of what type of application we registered as.

    >>> import pyimgur
    >>> im = pyimgur.Imgur(CLIENT_ID, CLIENT_SECRET)

Now we have an imgur object that knows who we are and can use that information
to request data from Imgur. ``client_id`` is sent every time we do an anonymous
authentication, refreshing a refresh_token or getting authorization from a new
user. It is therefore necessary that this value is given as an argument when
creating the Imgur object. The ``client_secret`` on the other hand is only
needed for the calls to refresh a refresh token or getting authorization from a
new user. These calls are only used in the non-anonymous user-authenticated
part of Imgur, so if we don't need that then we can leave it out.

Getting the first data
----------------------

Now that we've authenticated, we can use the methods in the ``Imgur`` object to
return data about Imgur, usually returned as objects. Continuing from the
previous example.

    >>> image = im.get_image('S1jmapR')
    >>> print(image.description)
    Cats
    >>> image.download()
    S1jmapR.pjpg

This short example prints the description of an image and then downloads it to
the current working directory.

Watch out. Lazy objects at work!
--------------------------------

To reduce the load on Imgur, PyImgur only requests the data it needs. This
meanSo each object has the attribute ``has_fetched`` which if True has fetched
all the data it can, if False it's a lazy object that can fetch more
information.

Whenever we request an attribute that hasn't been loaded the newest information
will be requested from imgur and the object will be updated with them. We can
also use the method ``refresh()`` to force a call to imgur, that will update
the object with the latest values even if it is not a lazily loaded object.

    >>> author = image.author
    >>> print(author.has_fetched)
    False # ie. it's a lazily loaded object
    >>> print(author.bio)
    This is one cool dude.
    >>> print(author.has_fetched)
    True

Introspection
-------------

Remember that as usual you can use the ``dir``, ``vars`` and ``help`` inbuilt
functions to introspect objects to learn more about objects and how they work.
