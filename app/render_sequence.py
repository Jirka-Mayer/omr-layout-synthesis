import cv2
from muscima.io import parse_cropobject_list
from muscima.cropobject import CropObject
from typing import List
import matplotlib.pyplot as plt
from .sequential_model import Transition, Vector2, Location


def draw_bbox(img, obj: CropObject, color: tuple, width=2):
    cv2.rectangle(
        img,
        (obj.left, obj.top),
        (obj.right, obj.bottom),
        color,
        2
    )


def draw_transitions(img, sequence: List[Transition], origin: Vector2):
    location = origin
    for transition in sequence:
        start = location
        location += transition.delta
        end = location
        cv2.line(
            img,
            (int(start.x), int(start.y)),
            (int(end.x), int(end.y)),
            (255, 0, 0),
            2
        )


def linearize_notehead(
    notehead: CropObject,
    cropobjects: List[CropObject],
    graphemes: List[CropObject]
):
    children: List[CropObject] = notehead.get_outlink_objects(cropobjects)
    children.sort(key=lambda o: o.left)

    # "prefix" graphemes
    for c in children:
        if c.clsname in ["sharp", "flat", "natural", "double_sharp", "double_flat"]:
            graphemes.append(c)

    for c in children:
        if c.clsname in ["ledger_line"]:
            graphemes.append(c)
    
    graphemes.append(notehead)

    # # "suffix" graphemes
    # for c in children:
    #     if c.clsname in ["stem", "duration-dot", "staccato-dot", "tenuto", \
    #             "accent", "trill", "fermata"]:
    #         graphemes.append(c)

def linearize_key_signature(
    key_signature: CropObject,
    cropobjects: List[CropObject],
    graphemes: List[CropObject]
):
    children: List[CropObject] = key_signature.get_outlink_objects(cropobjects)
    children.sort(key=lambda o: o.left)
    
    for c in children:
        if c.clsname != "staff":
            graphemes.append(c)

def linearize_staff(img, staff: CropObject, cropobjects: List[CropObject]):
    forest: List[CropObject] = staff.get_inlink_objects(cropobjects)
    forest.sort(key=lambda o: o.left)
    
    # forest to graphemes
    
    graphemes: List[CropObject] = []
    for tree in forest:
        if tree.clsname in ["notehead-full", "notehead-empty", "grace-notehead-full", "grace-notehead-empty"]:
            linearize_notehead(tree, cropobjects, graphemes)
        elif tree.clsname.endswith("_rest"):
            graphemes.append(tree)
        elif tree.clsname.endswith("-clef"):
            graphemes.append(tree)
        elif tree.clsname == "key_signature":
            linearize_key_signature(tree, cropobjects, graphemes)
        # elif tree.clsname == "time_signature":
        #     graphemes.append(tree)
        elif tree.clsname in ["thin_barline", "thick_barline", \
                "measure_separator", "repeat", "repeat-dot", "dotted_barline"]:
            graphemes.append(tree)

    # graphemes to transitions

    origin = Vector2(staff.left, (staff.top + staff.bottom) / 2)
    transitions: List[Transition] = []

    location = origin
    for g in graphemes:
        middle = Vector2(*reversed(g.middle))
        delta = middle - location
        location = middle
        transitions.append(Transition(delta))

        draw_bbox(img, g, (0, 255, 0))
    
    draw_transitions(img, transitions, origin)


### MAIN ###


img_path = "datasets/MUSCIMA-pp_v1.0/data/images/fulls/" + \
    "CVC-MUSCIMA_W-02_N-06_D-ideal.png"
cropobjects_path = "datasets/MUSCIMA-pp_v1.0/data/" + \
    "cropobjects_withstaff/CVC-MUSCIMA_W-02_N-06_D-ideal.xml"

cropobjects: List[CropObject] = parse_cropobject_list(cropobjects_path)
staves: List[CropObject] = [obj for obj in cropobjects if obj.clsname == "staff"]
staff = staves[0]

from .encode_staff import encode_staff
situations, intents, actions, graphemes = encode_staff(staff, cropobjects)

# render debug image
img = cv2.imread(img_path, cv2.IMREAD_COLOR)
# draw_bbox(img, staff, (255, 0, 0))

for g in graphemes:
    draw_bbox(img, g.co, (0, 255, 0))

position = situations[0].position_in_measure
for a in actions:
    start = position
    end = position + a.position_jump
    start = start * (staff.bottom - staff.top) + Vector2(staff.left, (staff.top + staff.bottom) / 2)
    end = end * (staff.bottom - staff.top) + Vector2(staff.left, (staff.top + staff.bottom) / 2)
    cv2.line(
        img,
        (int(start.x), int(start.y)),
        (int(end.x), int(end.y)),
        (255, 0, 0),
        2
    )
    position += a.position_jump

plt.imshow(img)
plt.show()
