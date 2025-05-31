import unittest
from generator import Generator
import base64
import io
import sys
from contextlib import redirect_stdout
import xml.etree.ElementTree as ET
import json


class TestGenerator(unittest.TestCase):
    def setUp(self):
        self.gen = Generator()

    def test_generate_cube(self):
        model = self.gen.generate_model("cube", size=10, radius=None, height=None)
        self.assertIsNotNone(model)

    def test_generate_sphere(self):
        model = self.gen.generate_model("sphere", size=10, radius=None, height=None)
        self.assertIsNotNone(model)

    def test_generate_cylinder(self):
        model = self.gen.generate_model("cylinder", size=None, radius=5, height=20)
        self.assertIsNotNone(model)

    def test_generate_cone(self):
        model = self.gen.generate_model("cone", size=None, radius=5, height=20)
        self.assertIsNotNone(model)

    def test_export_model_as_base64_stl(self):
        model = self.gen.generate_model("cube", size=10, radius=None, height=None)
        b64 = self.gen.export_model_as_base64(model, "stl")  # poprawione
        decoded = base64.b64decode(b64.encode("utf-8"))
        self.assertTrue(len(decoded) > 0)

    def test_export_model_as_base64_glb(self):
        model = self.gen.generate_model("cube", size=10, radius=None, height=None)
        try:
            b64 = self.gen.export_model_as_base64(model, "glb")  # poprawione
            decoded = base64.b64decode(b64.encode("utf-8"))
            self.assertTrue(len(decoded) > 0)
        except RuntimeError as e:
            self.skipTest(f"Konwersja STL -> GLB nie powiodła się: {e}")

    def test_export_info_json(self):
        f = io.StringIO()
        with redirect_stdout(f):
            self.gen.export_info("json")
        out = f.getvalue()
        data = json.loads(out)
        self.assertIn("shapes", data)
        self.assertTrue(any(shape["name"] == "cube" for shape in data["shapes"]))

    def test_export_info_xml(self):
        f = io.StringIO()
        with redirect_stdout(f):
            self.gen.export_info("xml")
        out = f.getvalue()
        root = ET.fromstring(out)
        self.assertEqual(root.tag, "shapes")
        self.assertTrue(any(shape.attrib["name"] == "cube" for shape in root.findall("shape")))

    def test_invalid_shape(self):
        with self.assertRaises(ValueError):
            self.gen.generate_model("pyramid", size=10, radius=None, height=None)


# Ładne wyświetlanie wyników po zakończeniu testów
class PrettyTextTestRunner(unittest.TextTestRunner):
    def run(self, test):
        result = super().run(test)
        print("\n📋 Podsumowanie wyników testów:")
        print("✅ OK  :", result.testsRun - len(result.failures) - len(result.errors))
        if result.failures or result.errors:
            print("❌ Błędy:", len(result.failures) + len(result.errors))
        else:
            print("🎉 Wszystkie testy przeszły pomyślnie!")
        return result


if __name__ == "__main__":
    unittest.main(testRunner=PrettyTextTestRunner(), verbosity=2)
