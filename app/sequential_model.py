from dataclasses import dataclass
from typing import Optional, List
from enum import Enum
from muscima.cropobject import CropObject


def vectorize_enum(TEnum, value: Optional[Enum]) -> List[float]:
    values = list(TEnum)
    vector = [0.0] * len(values)
    if value is not None:
        vector[values.index(value)] = 1.0
    return vector


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

    @staticmethod
    def vectorize_optional(v: Optional["Vector2"]) -> List[float]:
        if v is None:
            return [0.0, 0.0, 0.0]
        else:
            return [1.0, float(v.x), float(v.y)]
    
    def vectorize(self) -> List[float]:
        return [float(self.x), float(self.y)]
    
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




# 1) Where I am .......... Situation
# 2) What I want to do ... Intent
# 3) What I do ........... Action


class GraphemeType(str, Enum):
    # TODO: should be defined stricter for production
    ledgerLine = "ledgerLine"
    clefG = "clefG"
    clefF = "clefF"
    clefC = "clefC"
    noteheadFull = "noteheadFull"
    noteheadEmpty = "noteheadEmpty"
    stem = "stem"
    restWhole = "restWhole"
    restHalf = "restHalf"
    restQuarter = "restQuarter"
    restEighth = "restEighth"
    rest16th = "rest16th"
    rest32nd = "rest32nd"
    beam = "beam"
    dot = "dot"
    barline = "barline"
    sharp = "sharp"
    flat = "flat"
    natural = "natural"


class GraphemeAnchorType(str, Enum):
    """Grapheme may have more than one anchor point, this distiguishes them."""
    primary = "primary" # all graphemes have it; usually its geometric center
    secondary = "secondary" # slur end, barline end, etc...
    # add more if necessary


@dataclass
class Grapheme:
    """The smallest graphical unit"""
    co: CropObject
    grapheme_type: GraphemeType
    anchor_types: List[GraphemeAnchorType]


@dataclass
class Situation:
    """
    I am somewhere in the score, some graphemes have been already
    written. I've just finished placing an anchor point of some grapheme.
    What does the situation look like?
    
    All spatial distances have the same units, either:
    - pixels
    - staff spaces
    - staff heights
    """

    position_in_measure: Vector2
    """Position relative to the start of the measure (middle
    of the last barline or the middle of staff start)"""

    # TODO: there may be the next barline already present, it would be
    # smart to put the distance to it here as well as an optional value

    position_from_last_notehead: Optional[Vector2]
    """Position relative to the center of the last placed notehead.
    Resets to None with each new measure."""

    this_grapheme: Optional[GraphemeType]
    """What grapheme type have we just placed?"""

    this_anchor_type: Optional[GraphemeAnchorType]
    """What specific anchor have we placed for the just-placed grapheme?"""

    this_grapheme_width: float
    """We just placed a grapheme, what is its width? Useful for wide
    object adjustments."""

    def vectorize(self) -> List[float]:
        return [
            *self.position_in_measure.vectorize(),
            *Vector2.vectorize_optional(self.position_from_last_notehead),
            *vectorize_enum(GraphemeType, self.this_grapheme),
            *vectorize_enum(GraphemeAnchorType, self.this_anchor_type),
            float(self.this_grapheme_width)
        ]


@dataclass
class Intent:
    """
    I want to place the next grapheme (its anchor point), which one is it?
    """

    grapheme: GraphemeType
    """What grapheme are we placing?"""

    anchor_type: GraphemeAnchorType
    """Which anchor point of that grapheme are we placing?"""

    # TODO: note pitch? what about ledger lines?

    # TODO: voice change?

    # TODO: next note in chord or just another note?

    def vectorize(self) -> List[float]:
        return [
            *vectorize_enum(GraphemeType, self.grapheme),
            *vectorize_enum(GraphemeAnchorType, self.anchor_type)
        ]


@dataclass
class Action:
    """
    Given our situation and intent, what does our model predict we should do?
    """
    
    position_jump: Vector2
    """Where should we jump to place the next anchor point? Or rather,
    what is its position relative to our current position?"""

    def vectorize(self) -> List[float]:
        return [
            *self.position_jump.vectorize()
        ]
