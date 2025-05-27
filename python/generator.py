import argparse
import cadquery as cq
import os
import time

def ensure_unique_filename(folder: str, base_name: str, extension: str) -> str:
    """Zwraca unikalną nazwę pliku w folderze."""
    counter = 0
    filename = f"{base_name}.{extension}"
    while os.path.exists(os.path.join(folder, filename)):
        counter += 1
        filename = f"{base_name}_{counter}.{extension}"
    return os.path.join(folder, filename)

def generate_cube(side_length: float, output_path: str):
    start_time = time.time()

    # Tworzenie modelu sześcianu
    cube = cq.Workplane("XY").box(side_length, side_length, side_length)

    # Zapis modelu
    ext = os.path.splitext(output_path)[1].lower()
    if ext == ".step" or ext == ".stp":
        cq.exporters.export(cube, output_path)
    elif ext == ".stl":
        cq.exporters.export(cube, output_path, exportType="STL")
    else:
        raise ValueError("Nieobsługiwany format pliku. Użyj .step, .stp lub .stl")

    elapsed = time.time() - start_time
    print(f"Model zapisany jako: {output_path}")
    print(f"Czas generowania: {elapsed:.3f} sekundy")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generuje sześcian o podanym boku i zapisuje jako plik STEP/STL.")
    parser.add_argument("side_length", type=float, help="Długość boku sześcianu")
    parser.add_argument("--output", "-o", default="cube.step", help="Nazwa bazowa pliku (np. cube.step, cube.stl)")

    args = parser.parse_args()

    # Przygotowanie ścieżki docelowej
    base_name, ext = os.path.splitext(os.path.basename(args.output))
    ext = ext.lstrip(".").lower()

    output_folder = "examples"
    os.makedirs(output_folder, exist_ok=True)

    output_file = ensure_unique_filename(output_folder, base_name, ext)
    generate_cube(args.side_length, output_file)

    
    