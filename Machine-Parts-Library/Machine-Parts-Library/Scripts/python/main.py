import argparse
from generator import Generator

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generuje modele 3D i zwraca jako base64.")
    parser.add_argument("shape", nargs="?", choices=["cube", "sphere", "cylinder", "cone"])
    parser.add_argument("--size", type=float)
    parser.add_argument("--radius", type=float)
    parser.add_argument("--height", type=float)
    parser.add_argument("--export-info", action="store_true")
    parser.add_argument("--export-file", help="Plik XML/JSON")
    parser.add_argument("--as-base64", action="store_true")
    parser.add_argument("--format", choices=["glb", "stl"], default="glb")
    args = parser.parse_args()

    gen = Generator()

    if args.export_info:
        fmt = "json"
        if args.export_file:
            if args.export_file.endswith(".xml"):
                fmt = "xml"
            elif args.export_file.endswith(".json"):
                fmt = "json"
            else:
                raise ValueError("Obsługiwane formaty: .json, .xml")
        gen.export_info(fmt)
    else:
        if not args.shape:
            raise ValueError("Musisz podać kształt.")
        params = {
            "size": args.size,
            "radius": args.radius,
            "height": args.height
        }
        model = gen.generate_model(args.shape, **params)
        if args.as_base64:
            print(gen.export_model_as_base64(model, format=args.format))
        else:
            raise NotImplementedError("Użyj --as-base64.")
