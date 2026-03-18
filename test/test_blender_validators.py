# -*- coding: utf-8 -*-

import unittest

from blender_agent.validators import validate_action


class BlenderValidatorTest(unittest.TestCase):
    def test_create_primitive_requires_supported_primitive(self):
        ok, error = validate_action(
            {"action": "create_primitive", "params": {"primitive": "cube"}}
        )
        self.assertTrue(ok)
        self.assertEqual(error, "")

    def test_apply_material_requires_target_and_color(self):
        ok, error = validate_action(
            {"action": "apply_material", "params": {"target": "Cube"}}
        )
        self.assertFalse(ok)
        self.assertIn("color", error)


if __name__ == "__main__":
    unittest.main()
