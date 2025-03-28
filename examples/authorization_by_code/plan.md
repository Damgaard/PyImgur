# Authentication by code

This plan outlines the project, how it should be structured and what rules it should follow. The instructions are for Cursor, and are left in the project to help in future maintenance.

If you are human I would recommend reading the README. It is written by a human, by hand for human reading ✍️

## Goals

The goals of this project is to create a small simple web application that demonstrates how to use PyImgur to authenticate by code with Imgur.

## Technologies

The web application needs to be built with flask.
All requests to Imgur must be done with the latest version of PyImgur.
The returned HTML should all be in one page. The CSS, may or may not, use bootstap. It should not use any other frameworks.

## The Web page

The webpage should be in a modern, clean look. It should have a header, which says "PyImgur: Authenticate by code example". In the main content of the page there should be a form with the following fields. client_id, client_secret and state. State is an optional field. The others are required. Below there should be a single clear call to action button. On click, the contents of the form is sent in json format to /api/authorize with a POST request.

All errors and success responses should be listed below the form. They should persist in being shown. There should be a visual difference in errors and success messsages. Newest responses should be listed at the top.

Above the form should be the text listed in the "Usage explanation" section. You may format it to make it more beautiful. You may fix any typos you see. You may add newlines to increase readability.

If the get parameter "code" is set. Show a success section above the form with the header saying "You did it rockstar". If BE also sends "error_message". Add text saying. "But it wasn't perfect, we couldn't get the user. Instead we got this error: {error_message}". If BE sends "username", write text saying. "You are now authorized as {username} 🥳". If "state" is returned. Add text on it's own line. "Returned state was: {state}".

### Usage explanation

Use this form to test creating a code using PyImgur. Input your credentials in the form below and hit submit. You will get a url to go to, here you can go authorize. Normally in your app, you would directly redirect the user. In this example, I'm asking you to do that step manually as it makes it easier to understand the process if you run the authorization in a seperate tab while this remain visible.

State isn't used by PyImgur or Imgur. Instead Imgur simply passes it back. It can be used to differentiate the user experience depending on the state or other things. That's up to you :)

## The Web Application

The web application should be built using Python. It should have the following endpoints

 - / Returns the web page described above
 - /api/authorize outputs perform the actions listed in the "API authorize" section

### API authorize

Set the credentials of the im object using the client_id and client_secret sent by the FE. Then call im.get_image('5JTvLlM'). If this throws an error of any sort, then eturn an error message to the frontend, with the error text "Problem when validating your client_id. Please verify it is correct". Otherwise call im.authorization_url("code"), the result of that call is then authorization url. It should be outputted both to the terminal and returned to the frontend with the text "Success: Please go to {authorization_url} to verify authorization"

Before doing anything with any data received from the frontend, strip any preceeding and trailing whitespace from it.

