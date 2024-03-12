from muscima.cropobject import CropObject
from typing import List, Tuple
from .sequential_model import Vector2, Situation, Intent, Action, Grapheme, GraphemeType, GraphemeAnchorType
import numpy as np


REST_GRAPHEME_MAP = {
    "whole_rest": GraphemeType.restWhole,
    "half_rest": GraphemeType.restHalf,
    "quarter_rest": GraphemeType.restQuarter,
    "8th_rest": GraphemeType.restEighth,
    "16th_rest": GraphemeType.rest16th,
    "32th_rest": GraphemeType.rest32nd,
}

CLEF_GRAPHEME_MAP = {
    "g-clef": GraphemeType.clefG,
    "f-clef": GraphemeType.clefF,
    "c-clef": GraphemeType.clefC
}

ACCIDENTAL_GRAPHEME_MAP = {
    "sharp": GraphemeType.sharp,
    "flat": GraphemeType.flat,
    "natural": GraphemeType.natural
}


def linearize_notehead(
    notehead: CropObject,
    universe: List[CropObject]
) -> List[Grapheme]:
    children: List[CropObject] = notehead.get_outlink_objects(universe)
    children.sort(key=lambda o: o.left)

    graphemes = []

    # "prefix" graphemes
    for c in children:
        if c.clsname in ["sharp", "flat", "natural"]:
            # TODO: "double_sharp", "double_flat"
            # TODO: proper anchor positions
            graphemes.append(Grapheme(
                co=c,
                grapheme_type=ACCIDENTAL_GRAPHEME_MAP[c.clsname],
                anchor_types=[GraphemeAnchorType.primary]
            ))

    for c in children:
        if c.clsname in ["ledger_line"]:
            # TODO: proper anchor positions
            graphemes.append(Grapheme(
                co=c,
                grapheme_type=GraphemeType.ledgerLine,
                anchor_types=[GraphemeAnchorType.primary]
            ))
    
    graphemes.append(Grapheme(
        co=notehead,
        grapheme_type=GraphemeType.noteheadEmpty if "empty" in notehead.clsname \
            else GraphemeType.noteheadEmpty,
        anchor_types=[GraphemeAnchorType.primary]
    ))

    # # "suffix" graphemes
    # for c in children:
    #     if c.clsname in ["stem", "duration-dot", "staccato-dot", "tenuto", \
    #             "accent", "trill", "fermata"]:
    #         graphemes.append(c)

    return graphemes


def linearize_key_signature(
    key_signature: CropObject,
    universe: List[CropObject]
) -> List[Grapheme]:
    children: List[CropObject] = key_signature.get_outlink_objects(universe)
    children.sort(key=lambda o: o.left)
    
    graphemes = []
    for c in children:
        if c.clsname == "sharp":
            # TODO: proper anchor positions
            graphemes.append(Grapheme(
                co=c,
                grapheme_type=GraphemeType.sharp,
                anchor_types=[GraphemeAnchorType.primary]
            ))
        elif c.clsname == "flat":
            # TODO: proper anchor positions
            graphemes.append(Grapheme(
                co=c,
                grapheme_type=GraphemeType.flat,
                anchor_types=[GraphemeAnchorType.primary]
            ))
    
    return graphemes


def linearize_staff(
    staff: CropObject,
    universe: List[CropObject]
) -> List[Grapheme]:
    children: List[CropObject] = staff.get_inlink_objects(universe)
    children.sort(key=lambda o: o.left)

    graphemes: List[Grapheme] = []
    for child in children:

        # handle noteheads
        if child.clsname in ["notehead-full", "notehead-empty", "grace-notehead-full", "grace-notehead-empty"]:
            graphemes += linearize_notehead(child, universe)

        # handle rests
        elif child.clsname.endswith("_rest"):
            # TODO: duration dots
            graphemes.append(Grapheme(
                co=child,
                grapheme_type=REST_GRAPHEME_MAP[child.clsname],
                anchor_types=[GraphemeAnchorType.primary]
            ))
        
        # handle clefs
        elif child.clsname.endswith("-clef"):
            # TODO: proper anchor positions
            graphemes.append(Grapheme(
                co=child,
                grapheme_type=CLEF_GRAPHEME_MAP[child.clsname],
                anchor_types=[GraphemeAnchorType.primary]
            ))

        # handle key signature
        elif child.clsname == "key_signature":
            graphemes += linearize_key_signature(child, universe)
        
        # elif tree.clsname == "time_signature":
        #     graphemes.append(tree)

        # handle barlines
        elif child.clsname in ["thin_barline", "thick_barline", \
                "measure_separator", "repeat", "repeat-dot", "dotted_barline"]:
            graphemes.append(Grapheme(
                co=child,
                grapheme_type=GraphemeType.barline,
                anchor_types=[GraphemeAnchorType.primary]
            ))
    
    return graphemes


def encode_staff(
    staff: CropObject,
    universe: List[CropObject]
) -> Tuple[List[Situation], List[Intent], List[Action], List[Grapheme]]:
    graphemes = linearize_staff(staff, universe)

    staff_origin = Vector2(staff.left, (staff.top + staff.bottom) / 2)
    staff_height = float(staff.bottom - staff.top)

    def to_staff_coords(v: Vector2) -> Vector2:
        return (v - staff_origin) * (1 / staff_height)

    def to_staff_size(s: float) -> float:
        return s / staff_height

    # situation before the first action
    situation = Situation(
        position_in_measure=Vector2(0.0, 0.0),
        position_from_last_notehead=None,
        this_grapheme=None,
        this_anchor_type=None,
        this_grapheme_width=0.0
    )

    situations = []
    intents = []
    actions = []

    for grapheme in graphemes:
        # TODO: for each grapheme anchor also

        # define the intent
        intent = Intent(
            grapheme=grapheme.grapheme_type,
            anchor_type=grapheme.anchor_types[0] # TODO: perform multiple jumps when many
        )
        target_position = to_staff_coords(
            Vector2(*reversed(grapheme.co.middle)) # TODO: specific anchor positions
            # TODO: store the position within the grapheme during its construction
        )
        
        # do the action
        action = Action(
            position_jump=target_position - situation.position_in_measure
        )

        # situation after the action
        next_situation = Situation(
            position_in_measure=target_position, # TODO: reset with each measure
            position_from_last_notehead=None, # TODO: use this
            this_grapheme=grapheme.grapheme_type,
            this_anchor_type=grapheme.anchor_types[0], # TODO: multiple options!
            this_grapheme_width=to_staff_size(float(grapheme.co.width))
        )

        # move next
        situations.append(situation)
        intents.append(intent)
        actions.append(action)
        situation = next_situation

    return situations, intents, actions, graphemes
