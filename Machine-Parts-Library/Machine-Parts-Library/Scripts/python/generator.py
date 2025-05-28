import argparse
import cadquery as cq
import os
import time
import json
import xml.etree.ElementTree as ET

SHAPE_DEFINITIONS = {
    "cube": ["size"],
    "sphere": ["size"],
    "cylinder": ["radius", "height"],
    "cone": ["radius", "height"]
}

def ensure_unique_filename(folder: str, base_name: str, extension: str) -> str:
    counter = 0
    filename = f"{base_name}.{extension}"
    while os.path.exists(os.path.join(folder, filename)):
        counter += 1
        filename = f"{base_name}_{counter}.{extension}"
    return os.path.join(folder, filename)

def generate_shape(shape: str, size: float, radius: float, height: float, output_path: str):
    start_time = time.time()

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

    ext = os.path.splitext(output_path)[1].lower()
    if ext in [".step", ".stp"]:
        cq.exporters.export(model, output_path)
    elif ext == ".stl":
        cq.exporters.export(model, output_path, exportType="STL")
    else:
        raise ValueError("Nieobsługiwany format pliku. Użyj .step, .stp lub .stl")

    elapsed = time.time() - start_time
    print(f"Model ({shape}) zapisany jako: {output_path}")
    print(f"Czas generowania: {elapsed:.3f} sekundy")

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
    parser = argparse.ArgumentParser(description="Generuje modele 3D i zapisuje jako STEP/STL.")
    parser.add_argument("shape", nargs="?", choices=list(SHAPE_DEFINITIONS.keys()), help="Kształt do wygenerowania")
    parser.add_argument("--size", type=float, help="Rozmiar (bok sześcianu, średnica kuli)")
    parser.add_argument("--radius", type=float, help="Promień (dla walca/stożka)")
    parser.add_argument("--height", type=float, help="Wysokość (dla walca/stożka)")
    parser.add_argument("--output", "-o", default="model.step", help="Nazwa pliku wyjściowego")

    parser.add_argument("--export-info", action="store_true", help="Wypisz informacje o dostępnych kształtach i parametrach (do stdout)")
    parser.add_argument("--export-file", help="Rozszerzenie .json lub .xml określa format (stdout)")

    args = parser.parse_args()

    if args.export_info:
        # Określenie formatu eksportu na podstawie rozszerzenia
        export_format = "json"
        if args.export_file:
            ext = os.path.splitext(args.export_file)[1].lower()
            if ext == ".xml":
                export_format = "xml"
            elif ext == ".json":
                export_format = "json"
            else:
                raise ValueError("Nieobsługiwany format — użyj .json lub .xml")
        export_info(export_format)
    else:
        if not args.shape:
            raise ValueError("Musisz podać kształt do wygenerowania, np. cube, sphere itd.")
        base_name, ext = os.path.splitext(os.path.basename(args.output))
        ext = ext.lstrip(".").lower()
        output_folder = "examples"
        os.makedirs(output_folder, exist_ok=True)
        output_file = ensure_unique_filename(output_folder, base_name, ext)

        generate_shape(
            shape=args.shape,
            size=args.size,
            radius=args.radius,
            height=args.height,
            output_path=output_file
        )
