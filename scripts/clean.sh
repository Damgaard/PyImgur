echo "Removes downloaded images"
mv cats.png TEST_IMAGE
rm *.jpg 2> /dev/null
rm *.jpeg 2> /dev/null
rm *.png 2> /dev/null
rm *.gif 2> /dev/null
mv TEST_IMAGE cats.png
