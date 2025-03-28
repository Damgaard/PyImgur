from flask import Flask, render_template, request, jsonify
import pyimgur

app = Flask(__name__)

# Will be updated when user sets client_id and client_secret later.
INITIAL_CLIENT_ID = "TEMPORARY"
im = pyimgur.Imgur(INITIAL_CLIENT_ID)


@app.route("/")
def index():
    code = request.args.get("code")
    state = request.args.get("state")

    if not code:
        return render_template("index.html")

    if im.client_id == INITIAL_CLIENT_ID:
        error_message = "client_id wasn't properly set. It is updated on the backend, when you input the form to get the authoriation url. You should be able to fix this, by opening http://127.0.0.1:5000/ in a new tab. Setting client_id and client_secret. Submitting and then going back to this tab and refreshing."
        return render_template(
            "index.html", code=code, state=state, error_message=error_message
        )

    try:
        im.exchange_code(code)
    except Exception as e:
        error_message = "Couldn't exchange code. Did you already use it?"

        print(f"Error: {str(e)}")
        return render_template(
            "index.html", code=code, state=state, error_message=error_message
        )

    user = im.get_user("me")

    return render_template("index.html", code=code, state=state, username=user.name)


@app.route("/api/authorize", methods=["POST"])
def authorize():
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

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify(
            {
                "message": "Problem when validating your client_id. Please verify it is correct",
                "error": True,
            }
        )


if __name__ == "__main__":
    app.run(debug=True)
