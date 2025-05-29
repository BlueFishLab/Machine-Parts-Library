import unittest
from generator import generate_shape, export_model_as_base64, export_info, SHAPE_DEFINITIONS
import base64
import io
import sys
from contextlib import redirect_stdout
import xml.etree.ElementTree as ET
import json

class TestGenerator(unittest.TestCase):

    def test_generate_cube(self):
        model = generate_shape("cube", size=10, radius=None, height=None)
        self.assertIsNotNone(model)

    def test_generate_sphere(self):
        model = generate_shape("sphere", size=10, radius=None, height=None)
        self.assertIsNotNone(model)

    def test_generate_cylinder(self):
        model = generate_shape("cylinder", size=None, radius=5, height=20)
        self.assertIsNotNone(model)

    def test_generate_cone(self):
        model = generate_shape("cone", size=None, radius=5, height=20)
        self.assertIsNotNone(model)

    def test_export_model_as_base64(self):
        model = generate_shape("cube", size=10, radius=None, height=None)
        b64 = export_model_as_base64(model)
        decoded = base64.b64decode(b64.encode("utf-8"))
        self.assertTrue(len(decoded) > 0)

    def test_export_info_json(self):
        f = io.StringIO()
        with redirect_stdout(f):
            export_info("json")
        out = f.getvalue()
        data = json.loads(out)
        self.assertIn("shapes", data)
        self.assertTrue(any(shape["name"] == "cube" for shape in data["shapes"]))

    def test_export_info_xml(self):
        f = io.StringIO()
        with redirect_stdout(f):
            export_info("xml")
        out = f.getvalue()
        root = ET.fromstring(out)
        self.assertEqual(root.tag, "shapes")
        self.assertTrue(any(shape.attrib["name"] == "cube" for shape in root.findall("shape")))

    def test_invalid_shape(self):
        with self.assertRaises(ValueError):
            generate_shape("pyramid", size=10, radius=None, height=None)

if __name__ == "__main__":
    unittest.main()
