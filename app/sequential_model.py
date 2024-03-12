class Vector2:
    def __init__(self, x: float, y: float):
        self._x = x
        self._y = y
    
    @property
    def x(self) -> float:
        return self._x
    
    @property
    def y(self) -> float:
        return self._y
    
    def __repr__(self):
        return f"Vector2({self.x}, {self.y})"
    
    def __add__(self, other):
        if isinstance(other, Vector2):
            return Vector2(
                self.x + other.x,
                self.y + other.y
            )
        else:
            return Vector2(
                self.x + float(other),
                self.y + float(other)
            )
    
    def __sub__(self, other):
        if isinstance(other, Vector2):
            return Vector2(
                self.x - other.x,
                self.y - other.y
            )
        else:
            return Vector2(
                self.x - float(other),
                self.y - float(other)
            )
    
    def __mul__(self, other):
        return Vector2(
            self.x * float(other),
            self.y * float(other)
        )
    
    def __div__(self, other):
        return Vector2(
            self.x / float(other),
            self.y / float(other)
        )
    
    def __iter__(self):
        yield self.x
        yield self.y


# input is a sequence of graphemes (nope, grapheme anchors - "locations")

# output is a sequence of steps (edges between grapheme anchors - "transitions")


class Location:
    def __init__(self):
        self.staff_position = Vector2() # in staff space units
        self.measure_position: float = 0


class Transition:
    def __init__(self, delta: Vector2):
        self.delta = delta
