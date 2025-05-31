import cadquery as cq

class BaseModel:
    name = "base"
    parameters = []

    def __init__(self, **kwargs):
        self.params = kwargs

    def generate(self):
        raise NotImplementedError()

    def get_info(self):
        return {"name": self.name, "parameters": self.parameters}


class Cube(BaseModel):
    name = "cube"
    parameters = ["size"]

    def generate(self):
        size = self.params.get("size")
        if size is None:
            raise ValueError("Dla sześcianu należy podać --size")
        return cq.Workplane("XY").box(size, size, size)


class Sphere(BaseModel):
    name = "sphere"
    parameters = ["size"]

    def generate(self):
        size = self.params.get("size")
        if size is None:
            raise ValueError("Dla kuli należy podać --size")
        return cq.Workplane("XY").sphere(size / 2)


class Cylinder(BaseModel):
    name = "cylinder"
    parameters = ["radius", "height"]

    def generate(self):
        radius = self.params.get("radius")
        height = self.params.get("height")
        if radius is None or height is None:
            raise ValueError("Dla walca należy podać --radius i --height")
        return cq.Workplane("XY").cylinder(height=height, radius=radius)


class Cone(BaseModel):
    name = "cone"
    parameters = ["radius", "height"]

    def generate(self):
        radius = self.params.get("radius")
        height = self.params.get("height")
        if radius is None or height is None:
            raise ValueError("Dla stożka należy podać --radius i --height")
        return (
            cq.Workplane("XZ")
            .moveTo(0, 0)
            .lineTo(0, height)
            .lineTo(radius, 0)
            .close()
            .revolve()
        )
