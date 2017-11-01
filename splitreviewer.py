#!/usr/bin/env python
#
# Copyright (C) 2014 Mozilla Corporation
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, If not, see
# http://www.gnu.org/licenses/.


# Split out reviewers from a description. Run this file directly for
# unit tests, or import this file and call split_reviewer().

import re

# This function takes a description as an argument. It returns a list
# where the first element is the description with the reviewers
# stripped, and the second element is a list of reviewers found, if
# any. If no reviewers were found, the description will just be the
# one passed in.

reviewer_pattern = re.compile("^(.+)\s+\(?r=([a-zA-Z0-9.,\-]+[a-zA-Z0-9])\)?\.?\s*$")

def split_reviewer(description):
    m = re.match(reviewer_pattern, description)
    if not m:
        return [description, []]
    return [str.rstrip(m.group(1), ' ,;'), str.split(m.group(2), ',')]

def get_split_reviewer_tests():
    tests = []

    # Match failures.
    tests.append(['some stuff.', ['some stuff.', []]]) # no reviewer
    tests.append(['whatever r=m*e', ['whatever r=m*e', []]]) # invalid character
    tests.append(['some stuff. r=', ['some stuff. r=', []]]) # r=, but no reviewer. Ideally, remove the r=

    # Match successes.
    tests.append(['Bug 1234 - whatever r=me', ['Bug 1234 - whatever', ['me']]]) # simple case
    tests.append(['Bug 1234 - whatever. r=me', ['Bug 1234 - whatever.', ['me']]]) # simple case, preceeded by period
    tests.append(['Bug 1234 - whatever.   r=me', ['Bug 1234 - whatever.', ['me']]]) # simple case, multispace, preceeded by period
    tests.append(['Bug 1234 - whatever, r=me', ['Bug 1234 - whatever', ['me']]]) # simple case, preceeded by comma.
    tests.append(['Bug 1234 - whatever; r=me', ['Bug 1234 - whatever', ['me']]]) # simple case, preceeded by semicolon.
    tests.append(['Bug 1234 - whatever. r=me.', ['Bug 1234 - whatever.', ['me']]]) # period before and after
    tests.append(['Bug 1234 - whatever, r=me.', ['Bug 1234 - whatever', ['me']]]) # comma before, period after
    tests.append(['Bug 1234 - whatever. r=mccr8', ['Bug 1234 - whatever.', ['mccr8']]]) # numbers
    tests.append(['Bug 1234 - whatever. r=MeMe', ['Bug 1234 - whatever.', ['MeMe']]]) # upper case
    tests.append(['Bug 1234 - whatever. r=foo.bar', ['Bug 1234 - whatever.', ['foo.bar']]]) # periods in the user name
    tests.append(['Bug 1234 - whatever. (r=foo)   ', ['Bug 1234 - whatever.', ['foo']]]) # parentheses, trailing space
    tests.append(['Bug 1234 - whatever,   (r=foo) ', ['Bug 1234 - whatever', ['foo']]]) # parentheses, preceeded by comma.
    tests.append(['Bug 1234 - whatever. r=foo,bar,baz', ['Bug 1234 - whatever.', ['foo','bar','baz']]]) # multiple reviewers
    tests.append(['Bug 1234 - whatever; r=build-peer', ['Bug 1234 - whatever', ['build-peer']]]) # dash in reviewer name

    return tests

def run_split_reviewer_tests():
    tests = get_split_reviewer_tests()

    # Run the tests
    num_passed = 0
    num_failed = 0

    for [t, correct] in tests:
        res = split_reviewer(t)
        if res == correct:
            num_passed += 1
            print 'OK.'
        else:
            num_failed += 1
            print 'FAIL on', t, 'EXPECTED', correct, 'GOT', res

    # Print the results.
    print
    if num_failed == 0:
       print 'All', num_passed, 'tests passed.'
    else:
      print num_failed, 'tests failed and', num_passed, 'passed.'

if __name__ == "__main__":
    run_split_reviewer_tests()
