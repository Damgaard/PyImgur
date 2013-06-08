.. _authorization:

Authorization
=============

Before we can do stuff on behalf of a user, such as uploading images to one of
his albums. We need to authenticate as that user using a three step approach.

Step One - Ask for authorization
--------------------------------

We cannot authenticate as a user, without first getting permission. So first we
need to send the user to an Imgur url, where they can authorize our application
to act on their behalf::

  import webbrowser

  import pyimgur

  CLIENT_ID = "Your applications client_id"
  CLIENT_SECRET = "Your applications client_secret"   # Needed for step 2 and 3

  im = pyimgur.Imgur(CLIENT_ID, CLIENT_SECRET)
  auth_url = im.authorization_url('pin')
  webbrowser.open(auth_url)
  pin = input("What is the pin? ") # Python 3x
  #pin = raw_input("What is the pin? ") # Python 2x

The response argument in :meth:`.authorization_url` can be either 'pin' or
'code'. If it's code then the user will be redirected to your redirect url
with the code as a get parameter after authorizing your application. If it's
pin then after authorizing your application, the user will instead be shown a
pin on Imgurs website.

Step Two - Exchange pin/code for access_token and refresh_token
---------------------------------------------------------------

Both pin and code are one-use token that we send to Imgur in exchange for a
pair of access_token and refresh_token. These are used to authenticate as an
user.  Since we got a pin in the previous example, we'll use
:meth:`.exchange_pin` to exchange it for an access_token and request_token. If
we had gotten a code in the previous step, then we would have used
:meth:`.exchange_code` instead::

    im.exchange_pin(pin)

This returns an access_token and request_token and also updates ``im``'s
access_token and request_token attributes to the latest values. All requests
to Imgur will now use this new authentication.

Now we can use our new authorization to do cool stuff, so let's create a new
album for this user::

    im.create_album("An authorized album", "Cool stuff!")

This line is exactly the same as how to create anonymous resources. But since
we are now authenticated, it will create an album belonging to that user.

Step Three - Refreshing the access_token
----------------------------------------

access_tokens only last for 60 minutes, so every hour we'll need to update
the access_token using the refresh_token. The refresh_token lasts forever and
refreshing the access_token is easy::

    im.refresh_access_token()

