# Authentication by code

Example project demonstrating how to authenticate using code

# Install

Install required packages from requirements.txt

    pip install -r requirements.txt

# How To

First run the python application

    python .\app.py

It is now running on [localhost port 5000](http://127.0.0.1:5000/). 

If you haven't already. Register an [application with Imgur](https://api.imgur.com/oauth2/addclient).

For this to work, it is _important_ that callback is "http://127.0.0.1:5000/". If you created it with something else, then you can always go to [settings](https://imgur.com/account/settings/apps) and change it later.

Great. Now everything is setup.

Open [http://127.0.0.1:5000/](http://127.0.0.1:5000/). Enter you client_id and client_secret. Hit submit. If everything worked, you will get a message below and in the terminal listing the authorization url. If there was an error, it will also be listed here.

Go to the authorization url in a new tab. Then approve your own access. This will redirect you back to localhost. code and state will be set as GET parameters.

The BE uses the together with the credentials you set previously to exchange them for an access_token and refresh token. It is now authorized for your user and can make calls based on it.

The BE now figures out your username and shows it on the page.

Congratulations. You've not authenticated with code. 🚀