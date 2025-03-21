.. begin_intro

PyImgur
=======

.. image:: https://badge.fury.io/py/pyimgur.svg
    :target: https://badge.fury.io/py/pyimgur

The simple way of using Imgur.

You can upload images, download images, read comments, update your albums,
message people and more. In fact, you can do almost everything via PyImgur that
you can via the webend.

  PyImgur is a well-tested, user-friendly wrapper around the Imgur API that makes it easy to interact with Imgur's services through Python, with comprehensive documentation and clear examples. The codebase demonstrates good software engineering practices with extensive test coverage (particularly for API interactions), clear error handling, and a thoughtful pagination system. While some modernization could help (like the move to pyproject.toml), the project is actively maintained and provides a reliable, production-ready solution for developers needing to interact with Imgur programmatically.
  
  \- Claude 3.5 Sonnet

Prompt: Consicely evaluate this project for quality, userfriendliness and usefulness. Keep your answer to 3 sentences or less.

.. end_intro

.. begin_installation

Installation
------------

The recommended way to install is via `pip <http://pypi.python.org/pypi/pip>`_.

.. code-block:: bash

   $ pip install pyimgur


.. end_installation

.. begin_getting_started

Getting Started
---------------

Before we can start using PyImgur, we need to register our application with
Imgur. This way, Imgur can see what each application is doing on their site.
Go to https://api.imgur.com/oauth2/addclient to register your client.

When we registered our application we got a ``client_id`` and a
``client_secret``. The ``client_secret`` is used for authenticating as a user,
if we just need access to public or anonymous resources, then we can leave it
out. For our first example we're going to get some information about an image
already uploaded to image::

    import pyimgur
    CLIENT_ID = "Your_applications_client_id"
    im = pyimgur.Imgur(CLIENT_ID)
    image = im.get_image('S1jmapR')
    print(image.title) # Cat Ying & Yang
    print(image.link) # http://imgur.com/S1jmapR.jpg

The ``Imgur`` object keeps the authentication information, changes
authentication and is the common way to get objects from Imgur.

Uploading an Image
------------------

Let's use another example to show how to upload an image::

    import pyimgur

    CLIENT_ID = "Your_applications_client_id"
    PATH = "A Filepath to an image on your computer"

    im = pyimgur.Imgur(CLIENT_ID)
    uploaded_image = im.upload_image(PATH, title="Uploaded with PyImgur")
    print(uploaded_image.title)
    print(uploaded_image.link)
    print(uploaded_image.size)
    print(uploaded_image.type)


Some methods here one or more arguments with the default value ``None``. For
methods modifying existing objects, this mean to keep the already existing
value. For methods not modifying existing objects, this mean to use the Imgur
default.

Testing
-------

To run the tests, you can use the following command.

.. code-block:: bash

    pytest

On an unmodified download of this repository, it will run all unit tests.
These do not require an Imgur API key and include tests for API calls and
general functionality.

If you have configured a ´authentication.py´ file with your credentials,
then integration tests will also be run. Ensuring that nothing has changed
in the Imgur API, which would break functionality.

Lazy objects
------------

To reduce the load on Imgur, PyImgur only requests the data it needs. This
means each object has the attribute ``_has_fetched`` which if ``True``` has
fetched all the data it can, if ``False`` it can fetch more information.

Whenever we request an attribute that hasn't been loaded the newest information
will be requested from Imgur and all the object attributes will be updated to
the newest values. We can also use the method ``refresh()`` to force a call to
Imgur, that will update the object with the latest values::

    import pyimgur
    CLIENT_ID = "Your_applications_client_id"
    im = pyimgur.Imgur(CLIENT_ID)
    gallery_image = im.get_gallery_image('JiAaT')
    author = gallery_image.author
    print(author._has_fetched) # False ie. it's a lazily loaded object
    print(author.reputation)
    print(author._has_fetched) # True ie. all values have now been retrieved.

Introspection
-------------

Remember that as usual you can use the ``dir``, ``vars`` and ``help`` builtin
functions to introspect objects to learn more about them and how they work.

Mashape API
-----------

Imgur supports commercial use via Mashape, which uses a different endpoint and
some additional authentication. You can enable this easily by providing your
Mashape key on initialization of the Imgur object::

    import pyimgur
    CLIENT_ID = "Your_applications_client_id"
    MASHAPE_KEY = "Your_mashape_api_key"
    im = pyimgur.Imgur(CLIENT_ID, mashape_key=MASHAPE_KEY)

More information on Mashape's API and Pricing can be found on the `Mashape
website <https://market.mashape.com/imgur/imgur-9>`_.

Support
-------

If you find an bug, have any questions about how to use PyImgur or have
suggestions for improvements then feel free to file an issue on the `Github
project page <https://github.com/Damgaard/PyImgur>`_.

Documentation
-------------

PyImgur's full documentation is located on `ReadTheDocs
<https://pyimgur.readthedocs.org>`_.

License
-------

All of the code contained here is licensed by
`the GNU GPLv3 <http://www.gnu.org/licenses/gpl-3.0.html>`_.

Upcoming breaking changes
-------------------------

To avoid multiple releases with breaking changes, I will try to bulk
release breaking changes in a single release. This won't prevent future
releases with breaking changes, but will reduce the number of them.
Which will make it easier to upgrade.

- Remove Mashape key argument from Imgur object. It currently does nothing.
  As Mashape is no longer used by Imgur, instead RapidAPI is used. Which
  is also supported by the Imgur object.
- Fix some classes like Gallery_album not being in following PascalCase.
- Rename / remove DEFAULT_LIMIT from Imgur. Also not following conventions.
  Should maybe be set via an environment variable or other config instead.
- Change to a more permissive license.

.. end_getting_started
