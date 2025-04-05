"""Authorization by code example.

This example demonstrates how to authorize a user by code.

In particular, this file is for the backend portion of that example.
It shows the PyImgur code that is used to first generate an
authorization URL, redirect the user to it and then use the returned
code to get the access token.

The frontend portion of the example can be found in `index.html`.

"""

# Import errors are here because pylint runs based off the PyImgur
# package requirements.txt, not the special one for
# authorization_by_code.

from flask import (  # pylint: disable=import-error
    Flask,
    render_template,
    request,
    jsonify,
)
import pyimgur  # pylint: disable=import-error

app = Flask(__name__)

# Will be updated when user sets client_id and client_secret later.
INITIAL_CLIENT_ID = "TEMPORARY"
im = pyimgur.Imgur(INITIAL_CLIENT_ID)


@app.route("/")
def index():
    """Home page.

    Note that this page is both the default view you see when you start
    the app, but is also the page the user get's redirected to after
    authorizing the app. As such this path and function serves the dual
    purposes of getting a refresh_code if user is being redirected back to
    it, and the purpose of showing the user a form to generate the
    authorization URL.
    """
    code = request.args.get("code")
    state = request.args.get("state")

    if not code:
        return render_template("index.html")

    if im.client_id == INITIAL_CLIENT_ID:
        error_message = (
            "client_id wasn't properly set. It is updated on the backend, "
            "when you input the form to get the authoriation url. You should be able to fix "
            "this, by opening http://127.0.0.1:5000/ in a new tab. Setting client_id and "
            "client_secret. Submitting and then going back to this tab and refreshing."
        )
        return render_template(
            "index.html", code=code, state=state, error_message=error_message
        )

    try:
        im.exchange_code(code)
    except pyimgur.exceptions.ImgurIsDownException:
        error_message = "Imgur is currently down. Please try again in a bit."
        return render_template(
            "index.html", code=code, state=state, error_message=error_message
        )
    except Exception as e:  # pylint: disable=broad-exception-caught
        error_message = "Couldn't exchange code. Did you already use it?"

        print(f"Error: {str(e)}")
        return render_template(
            "index.html", code=code, state=state, error_message=error_message
        )

    user = im.get_user("me")

    return render_template("index.html", code=code, state=state, username=user.name)


@app.route("/api/authorize", methods=["POST"])
def authorize():
    """Authorize the app to make requests on behalf of the user.

    This function is called when the user submits the form in the frontend.
    First tt takes the client_id and client_secret from the form. client_id is used
    to make the authorization_url. Client_secret is not needed at this stage. It
    is requested to make the example easier to demo. We store it, so it is set on the
    Imgur objet and is available when the user is redirected back. At that point it
    is required for finalizing the authorization.

    Normally, you would set client_id and client_secret on initialization of your
    application and never change it.
    """
    data = request.get_json()

    # Strip whitespace from all input values
    data = {k: v.strip() if isinstance(v, str) else v for k, v in data.items()}

    try:
        im.change_authentication(data["client_id"], data["client_secret"])

        # Try to get an image to validate credentials
        im.get_image("5JTvLlM")

        # If successful, get the authorization URL
        auth_url = im.authorization_url("code")

        # Print to terminal as required
        print(f"Authorization URL: {auth_url}")

        return jsonify(
            {
                "message": f"Success: Please go to {auth_url} to verify authorization",
                "error": False,
            }
        )

    except pyimgur.exceptions.ImgurIsDownException:
        error_message = "Imgur is currently down. Please try again in a bit."
        return jsonify(
            {
                "message": error_message,
                "error": True,
            }
        )
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {str(e)}")
        return jsonify(
            {
                "message": "Problem when validating your client_id. Please verify it is correct",
                "error": True,
            }
        )


if __name__ == "__main__":
    app.run(debug=True)
