# PyImgur

![https://badge.fury.io/py/pyimgur](https://badge.fury.io/py/pyimgur.svg)

The simple way of using Imgur.

You can upload images, download images, read comments, update your albums,
message people and more. In fact, you can do almost everything via PyImgur that
you can via the webend.

>  PyImgur is a well-tested, user-friendly wrapper around the Imgur API that makes it easy to interact with Imgur's services through Python, with comprehensive documentation and clear examples. The codebase demonstrates good software engineering practices with extensive test coverage (particularly for API interactions), clear error handling, and a thoughtful pagination system. While some modernization could help (like the move to pyproject.toml), the project is actively maintained and provides a reliable, production-ready solution for developers needing to interact with Imgur programmatically.
>  
>  \- Claude 3.5 Sonnet

Prompt: Consicely evaluate this project for quality, userfriendliness and usefulness. Keep your answer to 3 sentences or less.

# Quick start

## Installation

The recommended way to install is via [pip](http://pypi.python.org/pypi/pip>).

    $ pip install pyimgur

## Let's get it running

Before we can start using PyImgur, you need to register your application with
Imgur. This way, Imgur can see what each application is doing on their site.
Go to https://api.imgur.com/oauth2/addclient to register your client.

Once you've registered. You can start using PyImgur.

    import pyimgur
    
    im = pyimgur.Imgur(client_id=YOUR_CLIENT_ID, client_secret=YOUR_CLIENT_SECRET)
    image = im.get_image('5JTvLlM')

    print(image.title) # Ssshhhh
    print(image.link) # https://i.imgur.com/5JTvLlM.gif

Great stuff. This was an un-authed request, since we made the request without
being authenticated as a user. Many endpoints are available in this way, however
stuff like commenting requires you to be authenticated as a user. This also
increases how many requests you can make before becoming ratelimited.

To act as an authenticated user, simply instantiate with a REFRESH_TOKEN for
that user.

    import pyimgur

    im = pyimgur.Imgur(client_id=YOUR_CLIENT_ID, client_secret=YOUR_CLIENT_SECRET, refresh_token=REFRESH_TOKEN)
    image = im.get_image('5JTvLlM')

    print(image.title) # Ssshhhh
    print(image.link) # https://i.imgur.com/5JTvLlM.gif

## Authorization

To get a users refresh token, you need the user to authorize your application. For development using pin authorization is easiest. It requires user to go the authorization_url and then giving you the pin they see there.

    import pyimgur

    im = pyimgur.Imgur(client_id=YOUR_CLIENT_ID, client_secret=YOUR_CLIENT_SECRET)

    auth_url = im.authorization_url("pin")

    print("Go to the following url to authenticate with your app")
    print(auth_url)

    pin = input("What is the pin? ")
    access_token, refresh_token = im.exchange_pin(pin)

Authorization by pin flow is also demonstrated in the refresh_token.py file, located at the
root of this repository. Which you can run to get a refresh token.

For applications running in production, it is preferable to use either code or token authorization as that requires manual inputs by the user. Demonstrating these use cases require running a web instance, so has a bit too much setup to be described in a README file.

The authorization_by_code folder inside the examples folder show a working example of a simple web application utilizing exchange by code. It has it's own README going into details on how it works.

## Examples

The examples folder contains programs demonstrating how to use PyImgur to achieve various tasks.

### Authorization By Code

Shows how to use the code based authorization. If you are running a service in production, with users accessing it through a website or app then this is superior to PIN based authorization. User is simply redirected to a url on Imgur's side, then just need to click a button to authorize. No need to copy or paste anything.

Example shows a full working example powered by a Flask web application.

## Delete empty albums

Cycles through all albums owned by the currently authorized user. Useful while experimentation, as this can build up a number of empty albums. Also useful generally as it shows a simple example of using PyImgur to access a users albums and make decisions based on their contents.

## Commercial Usage

Imgur supports commercial usage via RapidAPI. A paid subscription via them allows
for more monthly uploads and a higher ratelimit. To utilize it, requests must
be sent in a diffrent way. This is abstracted away by PyImgur. You simply need to
provide your RapidAPI key on initialization of the Imgur object::

    import pyimgur

    im = pyimgur.Imgur(CLIENT_ID, CLIENT_SECRET, rapidapi_key=RAPIDAPI_KEY)

**NOTE:** Development of PyImgur is focused on the public API. Endpoints specific to
the commercial API will not be developed and integration tests for RapidAPI are
not written. This is because I'm not paying 500$ a month for it. If you want extended
support of the RapidAPI I will be happy to accept a PR or do it as a paid service.

More information on RapidAPI can be found on the [RapidAPI
website](https://rapidapi.com/imgur/api/imgur-9>).

# Contribute

Want to contribute to the development of PyImgur? Great, let's go over the details
of how you ensure your code meets the quality standard and what practical details
you need to know to run the repository code locally.

## Required packages

PyImgur only requires the library `requests` to run as a package. To develop and test
however, it needs a few more. These are listed in `requirements.txt` and can be installed
with.

    pip install -r requirements.txt

## Quality. Black & Pylint

All code in PyImgur is quality checked by Pylint and formatted by Black. Github
actions are run on each commit to ensure they comply to this standard.

To check for correct linting please run

    pylint pyimgur
    pylint tests --disable missing-function-docstring,missing-module-docstring,protected-access

Some rules have been disabled in tests as they make less sense here.
Test functions should not as a rule require docstrings. If they do,
then they are badly written. The purpose of a test should be clear from
function name and if need be a glance at the code.

To check for correct code formatting

    black --check *.py pyimgur tests

## Testing

To run the tests, you can use the following command.

    pytest tests

On an unmodified download of this repository, it will run all unit tests.
These do not require an Imgur API key and include tests for API calls and
general functionality.

If you have configured a `authentication.py` file with your credentials,
then integration tests will also be run using these credentials. These
integration tests ensure that nothing has changed in the Imgur API, which
would break functionality.

## Upcoming breaking changes

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

# Deep dive

## Lazy objects

To reduce the load on Imgur, PyImgur only requests the data it needs. This
means each object has the attribute `_has_fetched` which if `True` has
fetched all the data it can, if `False` it can fetch more information.

Whenever we request an attribute that hasn't been loaded the newest information
will be requested from Imgur and all the object attributes will be updated to
the newest values. You can also use the method `refresh()` to force a call to
Imgur, that will update the object with the latest values.

    import pyimgur
    
    im = pyimgur.Imgur(client_id=CLIENT_ID)

    gallery_album =  im.get_gallery_album("W9Vouvn")
    author = gallery_album.author

    print(author._has_fetched) # False ie. it's a lazily loaded object
    print(author.reputation)
    print(author._has_fetched) # True ie. all values have now been retrieved.

## Introspection

Remember that as usual you can use the ``dir``, ``vars`` and ``help`` builtin
functions to introspect objects to learn more about them and how they work.

## Dynamic Object Generation

Attributes on objects in PyImgur are dynamically generated based on the response from Imgur. This mean that if Imgur for instance adds a new attribute to a User, then that attribute becomes instantly accessible to all versions of PyImgur. No need to upgrade is neccessary.

The value on these attributes are set to proper Python objects, like int, bool or string. So there is no need to do any excess work. Only exception would be if the new attribute is a reference to an object. Then PyImgurs object generation and lazy loading of referenced objects will not work out of the box. A new version of PyImgur that explicitly handles that case will need for the object to be accessed in the same manner as other objects.

## Ratelimits

There is currently no special handling of going over Imgurs API ratelimit and support of ratelimit handling is limited to exposing remaining queries via the Imgur object. Overall Imgur works on a more old-school generous model, where api credits are spread out. So as long as you don't keep usage high over a long time, then API limits are not hit. Being spikey in usage is  not a problem, the integration tests for instance never raise a ratelimit exception. Despite quickly making many calls and making images & albums.

For now, the decision is not to add extra complexity by adding more handling of the ratelimits.

Do note that Imgur is more aggressive on usage for non-authed usage. Ie. where you are just authenticated with client_id, so if you're doing that then I would recommend authenticating as a user by instantiating the Imgur object with a refresh_token.

# Related documents

## Changelog

The changelog can be found inside the CHANGES.rst file.

## Support

If you find an bug, have any questions about how to use PyImgur or have
suggestions for improvements then feel free to file an issue on the [Github
project page](https://github.com/Damgaard/PyImgur>).

## Documentation

PyImgur's full documentation is located on [ReadTheDocs](https://pyimgur.readthedocs.org>).

## License

All of the code contained here is licensed by [the GNU GPLv3](<http://www.gnu.org/licenses/gpl-3.0.html>).