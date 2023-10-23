# (c) Copyright IBM Corp. 2023
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)
import os
import filecmp


def assert_duplicates(*files):
    file_absolute_paths = [os.getcwd() + path for path in files]
    first = file_absolute_paths[0]
    rest = file_absolute_paths[1:]
    for next in rest:
        if (not filecmp.cmp(first, next)):
            raise BaseException(f"{first} and {rest} must be identical, but were not")
