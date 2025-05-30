import argparse
import cadquery as cq
import io
import base64
import json
import xml.etree.ElementTree as ET
import sys
import tempfile
import os
import subprocess
import trimesh

SHAPE_DEFINITIONS = {
    "cube": ["size"],
    "sphere": ["size"],
    "cylinder": ["radius", "height"],
    "cone": ["radius", "height"]
}

def generate_shape(shape: str, size: float, radius: float, height: float):
    if shape == "cube":
        if size is None:
            raise ValueError("Dla sześcianu należy podać --size")
        model = cq.Workplane("XY").box(size, size, size)
    elif shape == "sphere":
        if size is None:
            raise ValueError("Dla kuli należy podać --size")
        model = cq.Workplane("XY").sphere(size / 2)
    elif shape == "cylinder":
        if radius is None or height is None:
            raise ValueError("Dla walca należy podać --radius i --height")
        model = cq.Workplane("XY").cylinder(height=height, radius=radius)
    elif shape == "cone":
        if radius is None or height is None:
            raise ValueError("Dla stożka należy podać --radius i --height")
        model = (
            cq.Workplane("XZ")
            .moveTo(0, 0)
            .lineTo(0, height)
            .lineTo(radius, 0)
            .close()
            .revolve()
        )
    else:
        raise ValueError(f"Nieznany kształt: {shape}")
    return model

def export_model_as_base64(model, format="stl"):
    """
    Eksportuje model CadQuery do base64 w wybranym formacie.
    Format musi być np. "stl" lub "step".
    GLB wymaga konwersji przez trimesh - patrz niżej.
    """
    format = format.lower()
    if format == "glb":
        # Konwersja przez trimesh (potrzebna instalacja trimesh)
        import trimesh
        # Konwersja CadQuery -> trimesh
        # Załóżmy, że model to CadQuery solid
        # Pobieramy mesh CadQuery i tworzymy trimesh.Trimesh
        # To wymaga zbudowania mesh z CadQuery:
        cq_mesh = model.val().mesh()  # mesh CadQuery w formie (vertices, faces)
        vertices = cq_mesh.vertices
        faces = cq_mesh.faces
        # Trimesh wymaga numpy array
        import numpy as np
        vertices_np = np.array(vertices)
        faces_np = np.array(faces)
        trimesh_mesh = trimesh.Trimesh(vertices=vertices_np, faces=faces_np)
        
        glb_data = trimesh_mesh.export(file_type="glb")
        return base64.b64encode(glb_data).decode("utf-8")
    else:
        # Dla STL, STEP, etc podajemy exportType jawnie
        ext_map = {
            "stl": "STL",
            "step": "STEP",
            "brep": "BREP",
            "iges": "IGES",
        }
        export_type = ext_map.get(format)
        if export_type is None:
            raise ValueError(f"Nieobsługiwany format: {format}")

        with tempfile.NamedTemporaryFile(suffix=f".{format}", delete=False) as tmp_file:
            model.export(tmp_file.name, exportType=export_type)
            tmp_file.close()
            with open(tmp_file.name, "rb") as f:
                data = f.read()
            os.unlink(tmp_file.name)  # usuń tymczasowy plik

        return base64.b64encode(data).decode("utf-8")

def export_info(to_format="json"):
    if to_format == "json":
        data = {"shapes": [{"name": name, "parameters": params} for name, params in SHAPE_DEFINITIONS.items()]}
        print(json.dumps(data, indent=4, ensure_ascii=False))
    elif to_format == "xml":
        root = ET.Element("shapes")
        for name, params in SHAPE_DEFINITIONS.items():
            shape_el = ET.SubElement(root, "shape", name=name)
            for param in params:
                ET.SubElement(shape_el, "parameter").text = param
        tree_str = ET.tostring(root, encoding="unicode")
        print(tree_str)
    else:
        raise ValueError("Obsługiwane formaty: json, xml")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generuje modele 3D i zwraca jako base64 lub plik.")
    parser.add_argument("shape", nargs="?", choices=list(SHAPE_DEFINITIONS.keys()), help="Kształt do wygenerowania")
    parser.add_argument("--size", type=float, help="Rozmiar (bok sześcianu, średnica kuli)")
    parser.add_argument("--radius", type=float, help="Promień (dla walca/stożka)")
    parser.add_argument("--height", type=float, help="Wysokość (dla walca/stożka)")
    parser.add_argument("--export-info", action="store_true", help="Wypisz dostępne kształty i parametry")
    parser.add_argument("--export-file", help="Nazwa pliku .json lub .xml do wypisania definicji")
    parser.add_argument("--as-base64", action="store_true", help="Zamiast zapisu do pliku zwróć model jako base64")
    parser.add_argument("--format", choices=["stl", "glb"], default="glb", help="Format eksportu: glb (domyślny) lub stl")

    args = parser.parse_args()

    if args.export_info:
        export_format = "json"
        if args.export_file:
            ext = args.export_file.lower()
            if ext.endswith(".xml"):
                export_format = "xml"
            elif ext.endswith(".json"):
                export_format = "json"
            else:
                raise ValueError("Obsługiwane tylko: .json, .xml")
        export_info(export_format)
    else:
        if not args.shape:
            raise ValueError("Musisz podać kształt, np. cube, sphere itd.")

        model = generate_shape(
            shape=args.shape,
            size=args.size,
            radius=args.radius,
            height=args.height
        )

        if args.as_base64:
            b64 = export_model_as_base64(model, export_format=args.format)
            print(b64)
        else:
            raise NotImplementedError("Obsługa zapisu do pliku została usunięta. Użyj --as-base64.")