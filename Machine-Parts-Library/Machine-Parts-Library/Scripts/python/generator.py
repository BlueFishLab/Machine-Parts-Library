import base64
import json
import xml.etree.ElementTree as ET
import tempfile
import os
import numpy as np
from cadquery import exporters
from models import Cube, Sphere, Cylinder, Cone
import cadquery as cq
import trimesh

class Generator:
    def __init__(self):
        self.models = {
            "cube": Cube,
            "sphere": Sphere,
            "cylinder": Cylinder,
            "cone": Cone
        }

    def get_supported_shapes(self):
        return [cls().get_info() for cls in self.models.values()]

    def generate_model(self, shape_name, **kwargs):
        cls = self.models.get(shape_name)
        if cls is None:
            raise ValueError(f"Nieznany kształt: {shape_name}")
        return cls(**kwargs).generate()

    def export_info(self, to_format="json"):
        shapes = self.get_supported_shapes()
        if to_format == "json":
            print(json.dumps({"shapes": shapes}, indent=4, ensure_ascii=False))
        elif to_format == "xml":
            root = ET.Element("shapes")
            for shape in shapes:
                el = ET.SubElement(root, "shape", name=shape["name"])
                for p in shape["parameters"]:
                    ET.SubElement(el, "parameter").text = p
            print(ET.tostring(root, encoding="unicode"))
        else:
            raise ValueError("Obsługiwane formaty: json, xml")

    def export_model_as_base64(self,model: cq.Workplane, format: str) -> str:
        with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as tmp_file:
            tmp_stl_path = tmp_file.name
            model.val().exportStl(tmp_stl_path)

        if format == "stl":
            with open(tmp_stl_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
            os.remove(tmp_stl_path)
            return encoded

        elif format == "glb":
            # Załaduj model STL i zapisz jako GLB
            mesh = trimesh.load(tmp_stl_path)
            tmp_glb_path = tmp_stl_path.replace(".stl", ".glb")
            mesh.export(tmp_glb_path, file_type='glb')

            with open(tmp_glb_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")

            os.remove(tmp_stl_path)
            os.remove(tmp_glb_path)
            return encoded

        else:
            raise ValueError(f"Nieobsługiwany format eksportu: {format}")
