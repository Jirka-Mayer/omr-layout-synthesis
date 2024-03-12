from dataclasses import dataclass
from typing import Optional
from enum import Enum


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


class GraphemeAnchorType(str, Enum):
    """Grapheme may have more than one anchor point, this distiguishes them."""
    primary = "primary" # all graphemes have it; usually its geometric center
    secondary = "secondary" # slur end, barline end, etc...
    # add more if necessary


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


@dataclass
class Action:
    """
    Given our situation and intent, what does our model predict we should do?
    """
    
    position_jump: Vector2
    """Where should we jump to place the next anchor point? Or rather,
    what is its position relative to our current position?"""
