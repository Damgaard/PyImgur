# Testing

This document outlines you you, cursor, should write and update tests.

# General

These rules are the general base rules. There may be rules for specific files or tests that overrides these instructions.

 - Have at most 2 assertions pr. test
 - Do not add docstrings to a test. The name should be clear enough.

# Specifc Files

## Basic_url_tests

These instructions are only for the file tests/basic_url_tests.py. Only apply them here and no where else.

For each of the following objects: Album, Image, User, Gallery_album, Gallery_image

Tests for Gallery_album should not include tests of method inherited from the Album class.
Tests for Gallery_image should not include tests of method inherited from the Image class.

Create a test class called TestBasicUrls{object_name} where the part in paranthesis is replaced with the name of the object. The class should create a mocked instance of the object, see example in TestBasicUrlsAlbum

Within the class, for each public method on the class create a new test. It should be called 
test_{method_name}_uses_right_url where the part in brackets is replaced by the name of the method. When the method is called, it should be called with no arguments. Except if it has a limit parameter. In which case it should be called with limit=10.

New test methods should follow the format of the test test_album_favorite_calls_right_url.