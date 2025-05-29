import argparse
import cadquery as cq
import io
import base64
import json
import xml.etree.ElementTree as ET
import sys

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
        model = cq.Workplane("XY").cone(height=height, radius1=radius, radius2=0)
    else:
        raise ValueError(f"Nieznany kształt: {shape}")
    return model

def export_model_as_base64(model) -> str:
    buf = io.BytesIO()
    cq.exporters.export(model, buf, exportType="STL")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")

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
            b64 = export_model_as_base64(model)
            print(b64)
        else:
            raise NotImplementedError("Obsługa zapisu do pliku została usunięta. Użyj --as-base64.")
