#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import unittest

__author__ = u'Jonas Gröger <jonas.groeger@gmail.com>'


class LearningCase(unittest.TestCase):
    def test_starting_out(self):
        self.assertEqual(1, 1)


def main():
    unittest.main()


if __name__ == "__main__":
    main()
