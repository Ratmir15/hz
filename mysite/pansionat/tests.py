"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import re

from django.test import TestCase


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

    def retest(self):
        res = re.compile("\{\{\{(A-Za-z)*\}\}\}")
        list = res.findall('{{{aaa}}}')
        self.assertTrue(len(list)>0)
