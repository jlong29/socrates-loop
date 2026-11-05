import os
import unittest


class ExampleTests(unittest.TestCase):
    def test_configured_value(self):
        self.assertEqual(os.environ.get("EXAMPLE_VALUE"), "42")
