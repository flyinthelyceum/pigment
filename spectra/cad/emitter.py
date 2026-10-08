"""The emitter puck: the sensor puck's twin, which gives light back instead of
reading it.

    python -m spectra.cad.emitter            # build, check, report

Jared, 2026-10-07: the sensor puck and the emitter puck "must share the same
form factor; the symmetry between the two is super important", and the emitter
must be able to run at full power, with no fan. `docs/EMITTER.md` says why it
is built this way. This module draws it and proves the claims that can be
proved from geometry.

The shell is the sensor puck's, imported, not copied. ``puck.base()``,
``puck.tray()`` and ``puck.lid()`` are the same solids in both pucks, so a
change to the sensor's shell is a change to the emitter's, and the two cannot
drift apart. Three parts differ, and all sit where the optics sit:

``emitter_head``
    In place of the optical head. The same outside, the same port land and lip,
    the same rim, inserts and cavity bore the plate's spigot locates in, so it
    drops into the same collar. Inside, the eight LED bores are gone and the
    collection tube becomes a holder for a glass mixing rod: a hexagonal light
    pipe that turns seven coloured dies into one even colour at the port.
``emitter_plate``
    In place of the detector plate: a full flat disc, the heat spreader, with a
    hole in the middle for the LED and the rod's top.
``emitter_cap``
    A shallow box on the disc. The LED's own board lies face down in its
    pocket, its back taped to the cap's ceiling, over the hole the LED hangs
    into. Two pegs locate it on the plate; the tray above captures it.

**Prototype first, in plastic** (Jared, 2026-10-08: "let's prototype in an fdm
material even if it isn't going to hold up long term"). Every part prints:
the shared shell in PETG as the sensor's, and the three parts above in ASA,
because they touch the LED's board. A printed emitter cannot shed full power; it
proves the optics, the colour mixing, the calibration port to port and the
form, at about a watt, with full power only in bursts. See ``thermal()``.

**Metal later, cut not milled.** The plate and cap are drawn as flat layers in
3 mm steps so the same shapes can be waterjet-cut from 3 mm aluminium sheet
(Jared has a waterjet): the plate is one disc, the cap is a ring and a disc.
The wall becomes stock aluminium tube cut on a cold saw. Neither is drawn yet;
the features a waterjet cannot cut (the plate's spigot ring, the cap's spigot
and ears) are what the metal version replaces with dowel pins.

The boards are the sensor puck's envelopes: whatever drives this LED must fit
the DevKitC-1's outline on the tray and the TLC59711's outline under the lid,
because those are the only places the shell has. See EMITTER.md, "Boards".

Dimensions of the LED, its board and the rod are from datasheets and
catalogue pages, marked DATASHEET or ESTIMATE where they are set. None of these
parts exists here yet; when they arrive, each one is measured into
``components`` and imported, as every other part is.
"""

from __future__ import annotations

import math

from build123d import Align, Box, Cylinder, Part, Pos, Rot

from . import head, params as P, plate, puck as K

_MIN = (Align.CENTER, Align.CENTER, Align.MIN)
_cyl, _ring = K._cyl, K._ring

# ---------------------------------------------------------------- the parts --
# Parts not yet bought, from their makers' pages: planning figures, not
# measurements, marked so for the components lint. Nothing here has been in a
# caliper. Each moves into `components` when the part is in hand, and is
# imported from there.

ROD_AF = 4.0  # lint: not-a-measurement
ROD_L = 25.0  # lint: not-a-measurement
"""DATASHEET. Edmund Optics #17695, 4 mm aperture, 25 mm long (+/-0.3), high-NA
hexagonal light pipe in N-BK7. The page does not say whether 4 mm is across
flats or across corners; it is taken as across flats, the larger rod, so the
bore is safe either way (a rod 4 mm across corners is loose in it, not stuck).
Edmund also sells 50 and 100 mm; 25 is the one that fits under the plate."""

LZ7_W = 7.0  # lint: not-a-measurement
LZ7_H = 1.6  # lint: not-a-measurement
"""DATASHEET for the 7.0 mm square package; ESTIMATE for its height through the
flat glass window. Only the rod's top gap depends on the height, and the rod
rests on its ledge, not on the LED, so a wrong height opens or closes the gap
and never loads the glass."""

EMIT_D = 3.8  # lint: not-a-measurement
"""DATASHEET. The width of the square the seven dies sit in, under the window."""

BOARD_L = 38.3  # lint: not-a-measurement
BOARD_W = 31.2  # lint: not-a-measurement
BOARD_T = 1.6  # lint: not-a-measurement
"""DATASHEET for the outline, ESTIMATE for the thickness. The LZ7 is not sold
on a 20 mm star: the mounted part is the LZ7-N4M100, the emitter on LED Engin's
own seven-channel copper board, 38.3 x 31.2 mm (+/-0.2), with a 10k NTC
thermistor already on it. The bare emitter has 14 pads, so it cannot be
reflowed onto a stock star either. (Found sourcing it, 2026-10-08.) The
datasheet's drawing gives no thickness, hole positions or pad positions; the
emitter is taken as centred on the board. All of it is measured into
``components`` when the board is in hand, before the cap is printed."""

PAD_EDGE = 1  # lint: not-a-measurement
"""ESTIMATE. Which long edge of the board carries its pad row (+1 or -1 in the
board's own frame). The drawing calls the layout "7x1", one row, but the text
does not say where. The cap's wire opening sits on this edge."""

# ------------------------------------------------------------------- chosen --

ROD_CLEAR = 0.15
"""CHOSEN. Clearance across flats between the rod and its hexagonal bore. The
bore clocks the rod; nothing else holds it but a drop of black silicone."""

LEDGE_T = 0.6
"""CHOSEN. Three layers at 0.2. The rod stands on a ledge whose opening is the
hexagon's inscribed circle, so only its six corners rest on it. Below the
ledge the port is the sensor's 8 mm bore."""

ROD_L_TOL = 0.3  # lint: not-a-measurement
"""DATASHEET. Edmund's length tolerance on the rod, +/-0.3."""

ROD_GAP = 0.6
"""CHOSEN. Air between a nominal rod's top and the LED's window: the rod's
length tolerance plus 0.3, so the longest rod Edmund will ship still clears the
LED. The ledge carries the rod; a dab of black silicone in the bore keeps it on
the ledge when the puck is turned port up. (Red team, 2026-10-08: at 0.3 a
long rod met the glass.)"""

TUBE_WALL = 1.6
"""CHOSEN. The rod tube's wall, as the sensor head's collection tube."""

SHEET_T = 3.0
"""CHOSEN. Every layer above the head is a multiple of this: the plate is one
layer, the cap's pocket one more, so the metal version waterjets from one
sheet of 3 mm aluminium. It is also the sensor plate's thickness."""

CAP_ABOVE = 1.6
"""CHOSEN. Cap material above the board's back: eight layers at 0.2. The tray's
rails pass over the cap, and this keeps them TRAY_AIR clear even with an ASA
print a little tall. (Red team, 2026-10-08: at 2.0 the gap was 0.3.)"""

TAPE_T = 0.25  # lint: not-a-measurement
"""ESTIMATE. Thermally conductive double-sided tape (3M 8810 class) between the
board's back and the pocket's ceiling. It is what holds the board up in the
prototype: face down, nothing else stops it dropping onto the rod. In the metal
stage the board screws to the aluminium through its own three M3 holes, as LED
Engin recommends, once those holes are measured."""

TRAY_AIR = 0.5
"""CHOSEN. Least air between the cap and the tray above it."""

POCKET_CLEAR = 0.1
"""CHOSEN. Clearance each side between the board and its pocket. The pocket
locates the board; the tape only holds it."""

CAP_WALL = 2.0
"""CHOSEN. The cap's wall round the pocket: five perimeters at 0.4."""

BOARD_ANGLE = 78.3
"""CHOSEN. The board's long axis, in degrees. The head's three plate screws sit
at r=22.6, closer than the board's corners (24.6), so the board is turned to
the angle that keeps it farthest from all three heads: about 3 mm from the
nearest, where the cap's wall is notched round each head. Found by a sweep;
78.3 and 146.8 tie, and 78.3 leaves the pad edge facing open plate."""

SCREW_HEAD_D = 3.8  # lint: not-a-measurement
SCREW_HEAD_K = 2.0  # lint: not-a-measurement
"""DATASHEET. An M2 socket head cap screw (ISO 4762): the head of each screw
that holds the plate to the head stands on the plate, under the cap's wall."""
SCREW_HEAD_AIR = 0.4
"""CHOSEN. Air round a screw head inside its notch in the cap."""

PEG_D = 2.4
PEG_H = 2.5
PEG_CLEAR = 0.1
"""CHOSEN. Two pegs under diagonally opposite corners of the cap drop into a
hole and a slot in the plate. The hole locates the cap; the slot, running
along the line between the pegs, only clocks it, so the pair never fights the
plate's own tolerance. Nothing screws the cap down: the tray above captures it,
and it cannot rise far enough to leave its pegs. In the metal version the pegs
are dowel pins."""

WIRE_OPEN_L = 30.0
"""CHOSEN. The opening in the cap's wall on the pad edge, from the plate up to
the board's face, for sixteen wires (fourteen LED, two thermistor) to leave
flat under the board's edge and turn up outside the cap. The board's face is
only BOARD_GAP above the plate, so the joints must be low: 30 AWG wire-wrap
wire, soldered flat."""

DISC_CLEAR = 0.3
"""CHOSEN. The disc stops this far inside the wall, as the sensor plate's ears
do, so the posts' spigots alone locate it. In the metal version the gap is
filled with a strip of soft thermal gap pad: too soft to locate anything, and
it carries most of the heat to the wall. See thermal()."""

# --------------------------------------------------------------- thermal ----
# Not measurements of anything here: material constants and the LED's own
# limits, used to say how long full power lasts. Every one is CHOSEN or
# DATASHEET; the result is an estimate until a thermistor log says otherwise.

FULL_POWER_W = 20.0  # lint: not-a-measurement
"""DATASHEET. The LZ7's maximum dissipation with every die on (about 0.85 A
each). This is the "full power" Jared asked for (2026-10-07: "don't get
conservative here")."""

TJ_MAX = 125.0  # lint: not-a-measurement
RTH_JC = 1.4  # lint: not-a-measurement
RTH_BOARD = 0.5  # lint: not-a-measurement
"""DATASHEET for the junction limit and junction-to-case resistance; ESTIMATE
for the board (0.1 by its datasheet) plus the tape under it."""

PLATE_LIMIT = 65.0
"""CHOSEN. Where firmware derates once there is aluminium: the PETG of the
shared shell touches the plate and softens near 80 C. The LED is not the limit
here; at this temperature and full power it is well under TJ_MAX."""

PRINTED_LIMIT = 85.0
"""CHOSEN. Where firmware derates in the all-printed prototype, read at the
board's back: the cap and plate are ASA, which holds its shape to about 95 C.
At full power this puts the junction just under TJ_MAX, so it is also the
LED's limit."""

AMBIENT = 25.0
AL_DENSITY = 2.70e-3  # g/mm^3
AL_CP = 0.90  # J/(g K)
AL_K = 0.20  # W/(mm K)
CU_DENSITY = 8.96e-3  # g/mm^3
CU_CP = 0.385  # J/(g K)
ASA_K = 0.17e-3  # W/(mm K)
H_CONV = 7.5e-6  # W/(mm^2 K), still air on a 50 mm vertical wall
H_RAD = 6.2e-6  # W/(mm^2 K), black anodised (emissivity 0.85) near 60 C
H_INSIDE = 3.0e-6  # W/(mm^2 K), still air shut inside the case
JOINT_G = 1.9
JOINT_H = 0.06  # W/(mm^2 K)
RIM_PAD_K = 3.0e-3  # W/(mm K)
"""Material constants; the gap pad round the disc's edge (a common 3 W/(m K)
silicone pad); thermal paste at 3 W/(m K) in a 0.05 mm film, per unit area
(JOINT_H) and over one post's seat (JOINT_G, W/K)."""

# ---------------------------------------------------------------- derived ---

TUBE_R = (ROD_AF + ROD_CLEAR) / math.sqrt(3) + TUBE_WALL
"""DERIVED. The rod tube's outer radius: the bore's corner radius plus a wall."""

PLATE_TOP = P.PLATE_Z + SHEET_T
CEILING_Z = PLATE_TOP + SHEET_T
BOARD_BACK_Z = CEILING_Z - TAPE_T
BOARD_FRONT_Z = BOARD_BACK_Z - BOARD_T
BOARD_GAP = BOARD_FRONT_Z - PLATE_TOP
LED_FACE_Z = BOARD_FRONT_Z - LZ7_H
ROD_SEAT_Z = LED_FACE_Z - ROD_GAP - ROD_L
"""DERIVED. The stack is set from the top: the plate, then one sheet of pocket
whose ceiling the board's back is taped to, then the LED, an air gap, and the
rod, which lands where it lands above the port face."""
CAP_TOP_Z = CEILING_Z + CAP_ABOVE
POCKET_L = BOARD_L + 2 * POCKET_CLEAR
POCKET_W = BOARD_W + 2 * POCKET_CLEAR
CAP_L = POCKET_L + 2 * CAP_WALL
CAP_W = POCKET_W + 2 * CAP_WALL
PLATE_HOLE_R = LZ7_W / math.sqrt(2) + 1.0
"""DERIVED. The hole the LED hangs into, its corners plus a millimetre."""
DISC_R = K.R_IN - DISC_CLEAR


def _hex(af: float, z0: float, z1: float) -> Part:
    """A hexagonal prism across flats ``af``, flats facing +/-Y, from z0 to z1.
    Three slabs at 60 degrees, intersected."""
    big = 2 * af
    slab = Pos(0, 0, z0) * Box(big, af, z1 - z0, align=_MIN)
    return slab & (Rot(0, 0, 60) * slab) & (Rot(0, 0, 120) * slab)


def _radial(angle: float, r0: float, r1: float, w: float, z0: float, z1: float) -> Part:
    """A box from radius r0 to r1, w wide, at ``angle`` degrees."""
    return Rot(0, 0, angle) * Pos((r0 + r1) / 2, 0, z0) * Box(r1 - r0, w, z1 - z0, align=_MIN)


def _polar(angle: float, r: float) -> tuple[float, float]:
    return r * math.cos(math.radians(angle)), r * math.sin(math.radians(angle))


def _on_board(u: float, v: float) -> tuple[float, float]:
    """A point in the board's frame (u along its length, v across) in the
    puck's."""
    a = math.radians(BOARD_ANGLE)
    return u * math.cos(a) - v * math.sin(a), u * math.sin(a) + v * math.cos(a)


def _rect(l: float, w: float, z0: float, z1: float, u: float = 0.0, v: float = 0.0) -> Part:
    """A box in the board's frame, centred at (u, v), from z0 to z1."""
    return Rot(0, 0, BOARD_ANGLE) * Pos(u, v, z0) * Box(l, w, z1 - z0, align=_MIN)


def peg_positions() -> list[tuple[float, float]]:
    """(located, clocked): under two diagonally opposite corners of the cap's
    wall, in the puck's frame."""
    u = (POCKET_L + CAP_WALL) / 2
    v = (POCKET_W + CAP_WALL) / 2
    return [_on_board(u, -v), _on_board(-u, v)]


def emitter_head() -> Part:
    """The sensor head's outside and rim, with a rod holder where the optics were."""
    part = _cyl(P.BODY_OD / 2, 0.0, P.BODY_H)
    part = part - _cyl(P.LED_RING_R, P.FLOOR_T, P.BODY_H + 1.0)
    # The rod tube stands on the floor, and the sensor's webs tie it to the wall.
    part = part + _cyl(TUBE_R, P.FLOOR_T - 0.5, P.PLATE_Z) + head._webs()
    # The sensor's port, only as deep as the ledge; then the ledge's opening,
    # the rod's inscribed circle; then the rod's bore.
    part = part - _cyl(P.PORT_D / 2, -1.0, ROD_SEAT_Z - LEDGE_T)
    part = part - _cyl(ROD_AF / 2, -1.0, ROD_SEAT_Z + 0.01)
    part = part - _hex(ROD_AF + ROD_CLEAR, ROD_SEAT_Z, P.PLATE_Z + 1.0)
    part = part - head._plate_insert_pilots()
    # The same crushable lip, overlapping the floor so it fuses (head.body()).
    overlap = 0.5
    lip = (_cyl(P.LIP_OD / 2, -P.LIP_PROUD, overlap)
           - _cyl(P.LIP_ID / 2, -P.LIP_PROUD - 1.0, overlap + 1.0))
    return part + lip


def emitter_plate() -> Part:
    """The heat spreader, in plate coordinates (z = 0 is its underside), so it
    places at PLATE_Z exactly as the detector plate does. Flat on top, so it
    prints top down; everything but the spigot ring underneath is a through
    cut, so the same outline waterjets."""
    t = SHEET_T
    part = _cyl(DISC_R, 0.0, t) + plate.spigot()
    part = part - _cyl(PLATE_HOLE_R, -1.0, t + 1.0)
    # The cap's pegs: a hole that locates it, and a slot along the diagonal
    # between them that only clocks it.
    (x0, y0), (x1, y1) = peg_positions()
    r = PEG_D / 2 + PEG_CLEAR
    part = part - _cyl(r, -1.0, t + 1.0, x0, y0)
    diag = math.atan2(y1 - y0, x1 - x0)
    run = 0.5  # the slot's give along the diagonal, each way
    dx, dy = run * math.cos(diag), run * math.sin(diag)
    part = part - (Pos(x1, y1, -1.0) * Rot(0, 0, math.degrees(diag))
                   * Box(2 * run, 2 * r, t + 2.0, align=_MIN))
    for k in (-1, 1):
        part = part - _cyl(r, -1.0, t + 1.0, x1 + k * dx, y1 + k * dy)
    # The posts' spigots and the head's M2 screws, as the detector plate.
    for x, y in K.post_positions():
        part = part - _cyl(K.POST_SPIGOT_D / 2 + K.SPIGOT_CLEAR, -1.0, t + 1.0, x, y)
    for x, y in head.plate_screw_positions():
        part = part - _cyl(head.PLATE_SCREW_CLEAR_D / 2, -1.0, t + 1.0, x, y)
    return part


def emitter_cap() -> Part:
    """The board's housing, in puck coordinates: a shallow box over the board,
    open underneath, two pegs into the plate, and notches round the plate's
    screw heads. Flat on top, so it prints top down."""
    z0 = PLATE_TOP
    part = _rect(CAP_L, CAP_W, z0, CAP_TOP_Z)
    part = part - _rect(POCKET_L, POCKET_W, z0 - 1.0, CEILING_Z)
    for x, y in head.plate_screw_positions():
        part = part - _cyl(SCREW_HEAD_D / 2 + SCREW_HEAD_AIR, z0 - 1.0,
                           z0 + SCREW_HEAD_K + SCREW_HEAD_AIR, x, y)
    # The wires leave flat under the pad edge.
    part = part - _rect(WIRE_OPEN_L, 2 * CAP_WALL, z0 - 1.0, BOARD_FRONT_Z,
                        v=PAD_EDGE * (POCKET_W + CAP_WALL) / 2)
    for x, y in peg_positions():
        part = part + _cyl(PEG_D / 2, z0 - PEG_H, z0 + 0.5, x, y)
    return part


def screw_heads() -> Part:
    """The heads of the three screws that hold the plate to the head, standing
    on the plate."""
    out = None
    for x, y in head.plate_screw_positions():
        h = _cyl(SCREW_HEAD_D / 2, PLATE_TOP, PLATE_TOP + SCREW_HEAD_K, x, y)
        out = h if out is None else out + h
    return out


def rod() -> Part:
    return _hex(ROD_AF, ROD_SEAT_Z, ROD_SEAT_Z + ROD_L)


def led_on_board() -> Part:
    """The LZ7 and its board, face down, as one envelope."""
    led = _rect(LZ7_W, LZ7_W, LED_FACE_Z, BOARD_FRONT_Z + 0.01)
    return led + _rect(BOARD_L, BOARD_W, BOARD_FRONT_Z, BOARD_BACK_Z)


PRINTED = ("emitter_base", "emitter_head", "emitter_plate", "emitter_cap",
           "puck_tray", "puck_lid")
MATERIAL = {"emitter_head": "ASA", "emitter_plate": "ASA", "emitter_cap": "ASA",
            "emitter_base": "PETG", "puck_tray": "PETG", "puck_lid": "PETG"}
"""The prototype. ASA where a part touches the board or the plate under it;
the shared shell in the sensor's black PETG."""
SHARED = {"emitter_base": "puck_base", "puck_tray": "puck_tray", "puck_lid": "puck_lid"}
"""Every emitter part that is the sensor puck's own solid, by the sensor's name."""


def parts() -> dict[str, Part]:
    return {
        "emitter_base": K.base(),
        "emitter_head": emitter_head(),
        "emitter_plate": Pos(0, 0, P.PLATE_Z) * emitter_plate(),
        "emitter_cap": emitter_cap(),
        "puck_tray": K.tray(),
        "puck_lid": K.lid(),
        "rod": rod(),
        "led": led_on_board(),
        "screw_heads": screw_heads(),
        "esp32_board": K.esp32(),
        "driver_board": K.driver(),
    }


# ----------------------------------------------------------------- thermal --

STAGES = ("printed", "discs", "metal")
"""What the puck is made of, in the order it will be built: all printed (the
prototype); waterjet aluminium plate and cap in the printed shell; and those
with an aluminium wall, which the base's volume stands in for until the tube
size is chosen."""


def _areas() -> tuple[float, float]:
    """(outside the wall and foot can shed from, inside surface the case air
    touches), from the shell's own dimensions."""
    wall = 2 * math.pi * K.R_OUT * (K.rim_top() - K.FOOT_RELIEF)
    foot = math.pi * (K.R_OUT ** 2 - (K.HEAD_R + K.HEAD_CLEAR) ** 2)
    inside = 2 * math.pi * K.R_IN * (K.lid_inner_top() - K.FLOOR_T) + 2 * math.pi * K.R_IN ** 2
    return wall + foot / 2, inside  # a foot facing down sheds about half as well


def thermal(stage: str = "metal") -> dict[str, float]:
    """How long full power lasts, and what the puck sheds for ever after, from
    the CAD's own volumes and areas. Each stage is one lump with fixed drops
    between the board and the room.

    ``burst_s`` is full power from cold to the derating point; ``sustained_w``
    is what the puck sheds with the thermistor at that point; ``tj`` is the
    junction at the derating point under full power."""
    out_area, in_area = _areas()
    h = H_CONV + H_RAD
    ha = h * out_area
    g_air = 1 / (1 / (H_INSIDE * in_area) + 1 / ha)  # case air, then the wall
    # The board is copper (MHE-301).
    board_cap = BOARD_L * BOARD_W * BOARD_T * CU_DENSITY * CU_CP
    if stage == "printed":
        limit = PRINTED_LIMIT
        g_cap = ASA_K * POCKET_L * POCKET_W / (CAP_ABOVE + TAPE_T)
        g = 1 / (1 / g_cap + 1 / g_air)
        burst = board_cap * (limit - AMBIENT) / FULL_POWER_W
        return dict(limit=limit, heat_cap=board_cap, g=g, burst_s=burst,
                    sustained_w=g * (limit - AMBIENT),
                    tj=limit + FULL_POWER_W * (RTH_JC + RTH_BOARD))
    # In metal the board screws flat to the plate itself, its back on paste.
    g_cap = JOINT_H * BOARD_L * BOARD_W
    metal = (emitter_plate().volume + emitter_cap().volume) * AL_DENSITY * AL_CP
    if stage == "discs":
        limit = PLATE_LIMIT
        g = 1 / (1 / g_cap + 1 / g_air)
        burst = (metal + board_cap) * (limit - FULL_POWER_W / g_cap - AMBIENT) / FULL_POWER_W
        return dict(limit=limit, heat_cap=metal + board_cap, g=g, burst_s=burst,
                    sustained_w=g * (limit - AMBIENT),
                    tj=limit + FULL_POWER_W * (RTH_JC + RTH_BOARD))
    if stage != "metal":
        raise ValueError(f"stage must be one of {STAGES}")
    heat_cap = metal + board_cap + K.base().volume * AL_DENSITY * AL_CP
    # Posts: aluminium columns, plate to floor, each in series with its joint.
    post_a = math.pi * (K.BOSS_R ** 2 - (K.M3_CLEAR_D / 2) ** 2)
    post_l = K.SEAT_Z - (K.FOOT_RELIEF + K.FLOOR_T)
    g_posts = K.POST_N / (1 / (AL_K * post_a / post_l) + 1 / JOINT_G)
    g_rim = RIM_PAD_K * 2 * math.pi * DISC_R * SHEET_T / DISC_CLEAR
    g_wall = 1 / (1 / g_cap + 1 / (g_posts + g_rim))  # thermistor to wall
    rise = PLATE_LIMIT - FULL_POWER_W / g_wall - AMBIENT
    frac = ha * rise / FULL_POWER_W
    burst = -heat_cap / ha * math.log(1 - frac) if frac < 1 else math.inf
    return dict(limit=PLATE_LIMIT, heat_cap=heat_cap, g=1 / (1 / g_wall + 1 / ha),
                g_wall=g_wall, g_rim=g_rim, g_posts=g_posts, g_cap=g_cap, burst_s=burst,
                sustained_w=ha * (PLATE_LIMIT - AMBIENT) / (1 + ha / g_wall),
                tj=PLATE_LIMIT + FULL_POWER_W * (RTH_JC + RTH_BOARD))


# ------------------------------------------------------------------ checks --

def _overlap(a: Part, b: Part) -> float:
    return K._overlap(a, b)


def check() -> list[tuple[str, bool, str]]:
    ps = parts()
    sensor = K.parts()
    out = []
    for name in PRINTED:
        n = len(ps[name].solids())
        out.append((f"{name} is one solid", n == 1, f"{n} solid(s)"))

    # The symmetry Jared asked for: the shell is the sensor's own.
    for mine, theirs in SHARED.items():
        a, b = ps[mine], sensor[theirs]
        ba, bb = a.bounding_box(), b.bounding_box()
        same = (math.isclose(a.volume, b.volume, rel_tol=1e-9)
                and all(math.isclose(getattr(p, c), getattr(q, c), abs_tol=1e-9)
                        for p, q in ((ba.min, bb.min), (ba.max, bb.max)) for c in "XYZ"))
        out.append((f"{mine} is the sensor's {theirs}", same, f"{a.volume / 1000:.2f} cm^3 each"))
    sensor_head = head.body()
    hb, sb = ps["emitter_head"].bounding_box(), sensor_head.bounding_box()
    same_out = all(math.isclose(getattr(hb.min, c), getattr(sb.min, c), abs_tol=1e-6)
                   and math.isclose(getattr(hb.max, c), getattr(sb.max, c), abs_tol=1e-6)
                   for c in "XYZ")
    out.append(("the emitter head has the sensor head's outside", same_out,
                f"{hb.size.X:.2f} x {hb.size.Y:.2f} x {hb.size.Z:.2f}, lip to rim"))

    # Every joint locates itself; the screws only clamp.
    turned = _overlap(Rot(0, 0, 1.0) * ps["emitter_plate"], ps["emitter_head"])
    out.append(("the plate's spigot clocks it on the emitter head", turned > 1e-3,
                f"turned 1deg, the key arc strikes a web ({turned:.3f} mm^3)"))
    cap = ps["emitter_cap"]
    turned = _overlap(Rot(0, 0, 1.0) * cap, ps["emitter_plate"])
    out.append(("the cap's pegs clock it on the plate", turned > 1e-3,
                f"turned 1deg, a peg strikes the slot ({turned:.3f} mm^3)"))
    moved = 1.5 * PEG_CLEAR
    hit = min(_overlap(Pos(*_polar(a, moved), 0) * cap, ps["emitter_plate"])
              for a in range(0, 360, 45))
    out.append(("the cap's pegs locate it on the plate", hit > 1e-4,
                f"moved {moved:g} any way, a peg strikes its hole (least {hit:.4f} mm^3)"))
    lift = PEG_H - 0.5
    caught = _overlap(Pos(0, 0, lift) * cap, ps["puck_tray"])
    out.append(("the tray captures the cap before it can leave its pegs", caught > 1e-3,
                f"raised {lift:g} of its {PEG_H:g} mm pegs, it meets the tray ({caught:.2f} mm^3)"))
    heads = ps["screw_heads"]
    near = min(_overlap(Pos(*_polar(a, 0.3), 0) * ps["led"], heads) for a in range(0, 360, 30))
    out.append(("the board clears the plate's screw heads", near < 1e-3,
                f"board moved 0.3 any way: overlap {near:.3f} mm^3"))

    # The optics.
    out.append(("the rod's output face is recessed in the port",
                ROD_SEAT_Z - LEDGE_T > 0,
                f"face {ROD_SEAT_Z:.2f} above the port face, ledge from {ROD_SEAT_Z - LEDGE_T:.2f}"))
    v = _overlap(ps["rod"], ps["emitter_head"])
    out.append(("the rod sits in its bore, on its ledge", v < 1e-3, f"overlap {v:.3f} mm^3"))
    lifted = _overlap(Pos(0, 0, -0.05) * ps["rod"], ps["emitter_head"])
    out.append(("the ledge carries the rod", lifted > 1e-4,
                f"dropped 0.05, its corners strike the ledge ({lifted:.4f} mm^3)"))
    hex_area = math.sqrt(3) / 2 * ROD_AF ** 2
    lost = 1 - math.pi * (ROD_AF / 2) ** 2 / hex_area
    out.append(("the ledge masks only the rod's corners", lost < 0.1,
                f"{lost:.1%} of the output face behind the ledge"))
    out.append(("even the longest rod never bears on the LED", ROD_GAP - ROD_L_TOL > 0,
                f"{ROD_GAP:g} mm of air at the rod's top, {ROD_GAP - ROD_L_TOL:.1f} at +{ROD_L_TOL:g}"))
    raised = _overlap(Pos(0, 0, TRAY_AIR) * ps["emitter_cap"], ps["puck_tray"])
    out.append(("the tray stays clear of the cap, with room for a tall print", raised < 1e-3,
                f"cap raised {TRAY_AIR:g}: overlap with the tray {raised:.3f} mm^3"))
    v = _overlap(ps["led"], cap)
    out.append(("the board sits in its pocket", v < 1e-3, f"overlap {v:.3f} mm^3"))
    pushed = min(_overlap(Pos(*_polar(a, 1.5 * POCKET_CLEAR), 0) * ps["led"], cap)
                 for a in (BOARD_ANGLE, BOARD_ANGLE + 90))
    out.append(("the pocket alone locates the board", pushed > 1e-3,
                f"moved {1.5 * POCKET_CLEAR:g} along or across, it strikes the pocket ({pushed:.3f} mm^3)"))
    out.append(("the wires have room under the board's edge", BOARD_GAP > 1.0,
                f"{BOARD_GAP:.2f} mm from the plate to the board's face"))
    out.append(("the LED's dies fall inside the rod's mouth", EMIT_D <= ROD_AF,
                f"emitting area {EMIT_D:g} mm across, rod {ROD_AF:g} mm across flats"))
    out.append(("the plate is one sheet thick, as the detector plate",
                math.isclose(SHEET_T, plate.PLATE_T), f"{SHEET_T:g} mm"))

    solids = {n: ps[n] for n in ps}
    solids["puck_lid"] = K.lid(ribs=False)  # its ribs reach into the tray on purpose
    names = list(solids)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if {a, b} == {"led", "rod"}:
                continue
            v = _overlap(solids[a], solids[b])
            out.append((f"{a} clear of {b}", v < 1e-3, f"overlap {v:.3f} mm^3"))

    # Full power, without a fan, at each stage of the build.
    for stage in STAGES:
        th = thermal(stage)
        out.append((f"{stage}: full power stays under the junction limit at the derating point",
                    th["tj"] < TJ_MAX,
                    f"Tj {th['tj']:.0f} C with the thermistor at {th['limit']:g} C; limit {TJ_MAX:g}"))
    th = thermal("metal")
    out.append(("metal: the plate hands full power to the wall without eating the margin",
                FULL_POWER_W / th["g_wall"] < (PLATE_LIMIT - AMBIENT) / 2,
                f"{FULL_POWER_W / th['g_wall']:.1f} K from board to wall at {FULL_POWER_W:g} W"))
    return out


def _duration(s: float) -> str:
    return f"{s:.0f} s" if s < 90 else f"{s / 60:.1f} min"


def report() -> int:
    fails = 0
    print(f"emitter puck: {2 * K.R_OUT:.1f} dia x {K.lid_top():.1f} tall, the sensor puck's shell")
    print(f"  rod {ROD_AF:g} mm hex x {ROD_L:g}, face {ROD_SEAT_Z:.2f} above the port; "
          f"LED face z={LED_FACE_Z:.2f}, cap top z={CAP_TOP_Z:.2f}")
    print(f"  full power is {FULL_POWER_W:g} W. From cold, until the thermistor derates:")
    labels = {"printed": "all printed (ASA)", "discs": "aluminium plate and cap",
              "metal": "and an aluminium wall"}
    for stage in STAGES:
        th = thermal(stage)
        print(f"    {labels[stage]:<26} {_duration(th['burst_s']):>8} at full power, "
              f"then {th['sustained_w']:.1f} W  ({th['heat_cap']:.0f} J/K, derate at {th['limit']:g} C)")
    print()
    for name, ok, detail in check():
        fails += not ok
        print(f"  [{'ok' if ok else 'FAIL'}] {name}  {detail}")
    print("\n  [est] LZ7_H, BOARD_T, PAD_EDGE, RTH_BOARD, and every film and joint coefficient")
    return fails


def print_ready() -> dict[str, Part]:
    """The parts this puck adds, turned to print and set on z = 0. The head
    prints rim down as the sensor head does; the plate and cap print top down,
    flat face on the bed. The base, tray and lid are the sensor puck's files."""
    flip = Rot(180, 0, 0)
    raw = {"emitter_head": flip * emitter_head(), "emitter_plate": flip * emitter_plate(),
           "emitter_cap": flip * emitter_cap()}
    return {name: Pos(0, 0, -p.bounding_box().min.Z) * p for name, p in raw.items()}


def export(out_dir) -> list:
    """STL for the slicer and STEP for Fusion, one pair per emitter part."""
    from pathlib import Path

    from build123d import export_step, export_stl

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    written = []
    for name, part in print_ready().items():
        for ext, fn in (("step", export_step), ("stl", export_stl)):
            path = out / f"{name}.{ext}"
            fn(part, str(path))
            written.append(path)
    return written


if __name__ == "__main__":
    import sys

    if "--export" in sys.argv:
        from pathlib import Path

        dest = Path(__file__).resolve().parents[2] / "export" / "emitter"
        for path in export(dest):
            print(f"wrote {path.relative_to(dest.parents[1])}")
    raise SystemExit(report())
