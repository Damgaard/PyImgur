The simple way of using Imgur with Python.


# Imgur API Python Wrapper

With this library you can abstract away the convoluted ways of sending API requests, instead you'll have clear and readable function calls. Want to upload an image? It's simple.

```python
import imgur

API_KEY = 'you api key here'
image_path = 'and the path to the image'

imgur.upload_image(image_path, API_KEY)
```

You don't have to work with urllib, oauth or spend time trying to figure out Imgur's API. Instead you can focus on what's importment to you. Your application.

## Development

A closed beta of Imgur's API ver 3.0 has begun, the new version greatly expands on what can be done with the API. Current development of PyImgur is with the closed beta and will remain closed-source until Imgur's API ver 3.0 becomes publicly accesable.

## What can I do with Imgur?

You can do almost everything you can do through the web frontend.

 * Upload images by url. Anonymously and authenticated.
 * Upload images from the computer. Both anonymously and authenticated.
 * Delete images. By deletehash or any your authenticated account has uploaded.
 * Download images by image hash.
 * Find out what todays/this weeks/this months most popular images were. 
 * Find out all sorts of information about images or albums.
 * Get the oembed code for an image (json only at the moment).
 * Easily use oauth authentication to log in as a specific user.
 * Get information about the account.
 * Get all the images uploaded to the account.
 * Create and delete albums.
 * Edit the albums settings to make them private, display in grid and more.
 * Edit albums cover pictures.
 * Edit an image uploaded to an authenticated account. 
 * Add images to albums.
 * And more!

## What can't I do?

Some things aren't possible at all with the API, either due to limitations or bugs.

 * Find out user information.
 * See comments on images.
 * Change user settings like e-mail.
 * Re-order images in an album.
 * Remove images from an albums.
 * Empty albums can neither have their settings altered nor add images.

## Where can I find out more?

All functions have an updated docstring. For quick information about what a function does, use the builtin help function. Eg, `help(imgur.upload_image)` reveals information about how to use the upload_image function and what it does.

For more indepth information, go to our [wiki](google.com) on github for more informations. Here you'll find tutorials, references and everything else you'll need to get started. If you find a bug then this is also the place to file bug reports.

## Installation and dependencies

Install using pip

```  
pip install imgur
```

Alternatively, download the source from [Python Package Index](google.com), extract it and install using 

```
python setup.py install
```

Imgur works with Python 2.7 and 3.3. It has the dependencies x, y and z. Installing via pip automatically installs these dependencies. Installing via setup.py requires you to manually ensure that these modules are present.

## License

This library is licensed under GNU GPLv3. See COPYING for details.
