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
    Sits in that hole and on the disc. The LED's star board lies face down in
    its pocket, its back on the cap's ceiling, pressed against nothing but
    metal (later) or ASA (now).

**Prototype first, in plastic** (Jared, 2026-10-08: "let's prototype in an fdm
material even if it isn't going to hold up long term"). Every part prints:
the shared shell in PETG as the sensor's, and the three parts above in ASA,
because they touch the star. A printed emitter cannot shed full power; it
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

Dimensions of the LED, its star and the rod are from datasheets and
catalogue pages, marked DATASHEET or ESTIMATE where they are set. None of these
parts exists here yet; when they arrive, each one is measured into
``components`` and imported, as every other part is.
"""

from __future__ import annotations

import math

from build123d import Align, Box, Cylinder, Part, Pos, Rot

from components import heatset_insert_m2x4 as M2

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

STAR_D = 20.0  # lint: not-a-measurement
STAR_T = 1.6  # lint: not-a-measurement
"""ESTIMATE. The 20 mm aluminium star board the LZ7 is sold on (or reflowed
onto). 20 mm is the usual size; the thickness is the common 1.6 mm board."""

# ------------------------------------------------------------------- chosen --

ROD_CLEAR = 0.15
"""CHOSEN. Clearance across flats between the rod and its hexagonal bore. The
bore clocks the rod; nothing else holds it but a drop of black silicone."""

LEDGE_T = 0.8
"""CHOSEN. Two layers at 0.4. The rod stands on a ledge whose opening is the
hexagon's inscribed circle, so only its six corners rest on it. Below the
ledge the port is the sensor's 8 mm bore."""

ROD_GAP = 0.3
"""CHOSEN. Air between the rod's top and the LED's window. The rod never bears
on the LED; the ledge carries it."""

TUBE_WALL = 1.6
"""CHOSEN. The rod tube's wall, as the sensor head's collection tube."""

SHEET_T = 3.0
"""CHOSEN. Every layer above the head is a multiple of this: the plate is one
layer, the cap's pocket one more, so the metal version waterjets from one
sheet of 3 mm aluminium. It is also the sensor plate's thickness."""

CAP_ABOVE = 2.0
"""CHOSEN. Cap material above the star's back. It keeps the cap's top 0.3 under
the tray, which is the ceiling here."""

POCKET_CLEAR = 0.1
"""CHOSEN. Radial clearance between the star and its pocket. The pocket locates
the star; its own two screws only clamp it."""

CAP_R = 12.5
"""CHOSEN. The cap's body: the pocket plus a 2.4 mm wall."""

CAP_SPIGOT_T = 1.2
CAP_SPIGOT_CLEAR = 0.1
CAP_SPIGOT_H = 2.5
"""CHOSEN. A ring under the cap that drops into the plate's hole and centres
the cap on it, as the plate's own spigot centres the plate on the head."""

CAP_KEY_W = 3.0
CAP_KEY_ANGLE = 0.0
"""CHOSEN. A tab on the cap's spigot and a notch in the plate's hole, which
clock the cap so its wire slot meets the plate's. The screws never do."""

EAR_ANGLES = (60.0, 300.0)
EAR_R = 14.0
EAR_W = 7.0
"""CHOSEN. Two ears on the cap, each with an M2 insert in its underside, and
an M2 screw up through the plate into it. 60 and 300 degrees miss the head's
webs (0, 120, 240) that the screw heads hang among, and r=14 keeps the heads
inside the plate's spigot ring."""

M2_CLEAR_D = head.PLATE_SCREW_CLEAR_D

WIRE_SLOT_W = 5.0
WIRE_SLOT_ANGLE = 180.0
WIRE_SLOT_R = 17.0
"""CHOSEN. One slot from the pocket out through the cap's wall, below the
star's front face, and through the plate beside it, for the star's wires to
leave the pocket and rise to the boards. Seal it with black silicone once
wired."""

THERMISTOR_D = 2.2
THERMISTOR_ABOVE = 0.5
"""CHOSEN. A blind hole down into the cap for a bead thermistor, stopping
THERMISTOR_ABOVE short of the star's back: the reading is the star where it is
hottest, which is what the derating runs on."""

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
RTH_STAR = 0.5  # lint: not-a-measurement
"""DATASHEET for the junction limit and junction-to-case resistance; ESTIMATE
for star board plus thermal pad, case to plate."""

PLATE_LIMIT = 65.0
"""CHOSEN. Where firmware derates once there is aluminium: the PETG of the
shared shell touches the plate and softens near 80 C. The LED is not the limit
here; at this temperature and full power it is well under TJ_MAX."""

PRINTED_LIMIT = 85.0
"""CHOSEN. Where firmware derates in the all-printed prototype, read at the
star's back: the cap and plate are ASA, which holds its shape to about 95 C.
At full power this puts the junction just under TJ_MAX, so it is also the
LED's limit."""

AMBIENT = 25.0
AL_DENSITY = 2.70e-3  # g/mm^3
AL_CP = 0.90  # J/(g K)
AL_K = 0.20  # W/(mm K)
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
STAR_BACK_Z = PLATE_TOP + SHEET_T
STAR_FRONT_Z = STAR_BACK_Z - STAR_T
LED_FACE_Z = STAR_FRONT_Z - LZ7_H
ROD_SEAT_Z = LED_FACE_Z - ROD_GAP - ROD_L
"""DERIVED. The stack is set from the top: the plate, then one sheet of pocket
whose ceiling the star's back presses on, then the LED, an air gap, and the
rod, which lands where it lands above the port face."""
CAP_TOP_Z = STAR_BACK_Z + CAP_ABOVE
POCKET_R = STAR_D / 2 + POCKET_CLEAR
PLATE_HOLE_R = POCKET_R + CAP_SPIGOT_T + CAP_SPIGOT_CLEAR
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
    # The notch the cap's key drops into.
    part = part - _radial(CAP_KEY_ANGLE, PLATE_HOLE_R - 0.5, PLATE_HOLE_R + 1.3,
                          CAP_KEY_W + 2 * CAP_SPIGOT_CLEAR, -1.0, t + 1.0)
    # The wires' slot, inside the spigot ring underneath.
    part = part - _radial(WIRE_SLOT_ANGLE, PLATE_HOLE_R - 1.0, WIRE_SLOT_R,
                          WIRE_SLOT_W, -0.5, t + 1.0)
    for a in EAR_ANGLES:
        x, y = _polar(a, EAR_R)
        part = part - _cyl(M2_CLEAR_D / 2, -1.0, t + 1.0, x, y)
    # The posts' spigots and the head's M2 screws, as the detector plate.
    for x, y in K.post_positions():
        part = part - _cyl(K.POST_SPIGOT_D / 2 + K.SPIGOT_CLEAR, -1.0, t + 1.0, x, y)
    for x, y in head.plate_screw_positions():
        part = part - _cyl(head.PLATE_SCREW_CLEAR_D / 2, -1.0, t + 1.0, x, y)
    return part


def emitter_cap(ribs: bool = True) -> Part:
    """The star's housing, in puck coordinates: a body over the star, two ears
    with M2 inserts, and a keyed spigot down into the plate's hole. Flat on
    top, so it prints top down."""
    z0 = PLATE_TOP
    zs = z0 - CAP_SPIGOT_H
    part = _cyl(CAP_R, z0, CAP_TOP_Z)
    for a in EAR_ANGLES:
        part = part + _radial(a, CAP_R - 1.0, EAR_R + EAR_W / 2, EAR_W, z0, CAP_TOP_Z)
    part = part + _cyl(PLATE_HOLE_R - CAP_SPIGOT_CLEAR, zs, z0 + 0.5)
    part = part + _radial(CAP_KEY_ANGLE, POCKET_R + 0.5, PLATE_HOLE_R + 1.2,
                          CAP_KEY_W, zs, z0 + 0.5)
    part = part - _cyl(POCKET_R, zs - 1.0, STAR_BACK_Z)
    part = part - _radial(WIRE_SLOT_ANGLE, POCKET_R - 1.5, CAP_R + 1.0, WIRE_SLOT_W,
                          zs - 1.0, STAR_FRONT_Z)
    pilot_r = (M2.OD - head.INSERT_INTERFERENCE) / 2
    for a in EAR_ANGLES:
        x, y = _polar(a, EAR_R)
        part = part - _cyl(pilot_r, z0 - 1.0, z0 + M2.LENGTH + 0.5, x, y)
    tx = POCKET_R / 2
    part = part - _cyl(THERMISTOR_D / 2, STAR_BACK_Z + THERMISTOR_ABOVE, CAP_TOP_Z + 1.0, tx, tx)
    return part


def rod() -> Part:
    return _hex(ROD_AF, ROD_SEAT_Z, ROD_SEAT_Z + ROD_L)


def led_on_star() -> Part:
    """The LZ7 and its star, face down, as one envelope."""
    led = Pos(0, 0, LED_FACE_Z) * Box(LZ7_W, LZ7_W, LZ7_H + 0.01, align=_MIN)
    return led + _cyl(STAR_D / 2, STAR_FRONT_Z, STAR_BACK_Z)


PRINTED = ("emitter_base", "emitter_head", "emitter_plate", "emitter_cap",
           "puck_tray", "puck_lid")
MATERIAL = {"emitter_head": "ASA", "emitter_plate": "ASA", "emitter_cap": "ASA",
            "emitter_base": "PETG", "puck_tray": "PETG", "puck_lid": "PETG"}
"""The prototype. ASA where a part touches the star or the plate under it;
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
        "led": led_on_star(),
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
    between the star and the room.

    ``burst_s`` is full power from cold to the derating point; ``sustained_w``
    is what the puck sheds with the thermistor at that point; ``tj`` is the
    junction at the derating point under full power."""
    out_area, in_area = _areas()
    h = H_CONV + H_RAD
    ha = h * out_area
    g_air = 1 / (1 / (H_INSIDE * in_area) + 1 / ha)  # case air, then the wall
    star_cap = math.pi * (STAR_D / 2) ** 2 * STAR_T * AL_DENSITY * AL_CP
    if stage == "printed":
        limit = PRINTED_LIMIT
        g_cap = ASA_K * math.pi * POCKET_R ** 2 / CAP_ABOVE
        g = 1 / (1 / g_cap + 1 / g_air)
        burst = star_cap * (limit - AMBIENT) / FULL_POWER_W
        return dict(limit=limit, heat_cap=star_cap, g=g, burst_s=burst,
                    sustained_w=g * (limit - AMBIENT),
                    tj=limit + FULL_POWER_W * (RTH_JC + RTH_STAR))
    seat = math.pi * (CAP_R ** 2 - PLATE_HOLE_R ** 2) + len(EAR_ANGLES) * EAR_W * (EAR_W - 1.0)
    g_cap = JOINT_H * seat
    metal = (emitter_plate().volume + emitter_cap().volume) * AL_DENSITY * AL_CP
    if stage == "discs":
        limit = PLATE_LIMIT
        g = 1 / (1 / g_cap + 1 / g_air)
        burst = (metal + star_cap) * (limit - FULL_POWER_W / g_cap - AMBIENT) / FULL_POWER_W
        return dict(limit=limit, heat_cap=metal + star_cap, g=g, burst_s=burst,
                    sustained_w=g * (limit - AMBIENT),
                    tj=limit + FULL_POWER_W * (RTH_JC + RTH_STAR))
    if stage != "metal":
        raise ValueError(f"stage must be one of {STAGES}")
    heat_cap = metal + star_cap + K.base().volume * AL_DENSITY * AL_CP
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
                tj=PLATE_LIMIT + FULL_POWER_W * (RTH_JC + RTH_STAR))


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
    out.append(("the cap's key clocks it on the plate", turned > 1e-3,
                f"turned 1deg, the key strikes its notch ({turned:.3f} mm^3)"))
    moved = 1.5 * CAP_SPIGOT_CLEAR
    hit = min(_overlap(Pos(*_polar(a, moved), 0) * cap, ps["emitter_plate"]) for a in (90, 180))
    out.append(("the cap's spigot centres it in the plate", hit > 1e-4,
                f"moved {moved:g}, it strikes the hole (least {hit:.4f} mm^3)"))
    r_key = PLATE_HOLE_R + 0.4
    cap_play = math.hypot(CAP_SPIGOT_CLEAR, CAP_SPIGOT_CLEAR * EAR_R / r_key)
    m2_room = (M2_CLEAR_D - 2.0) / 2
    out.append(("no cap screw touches a hole wall", cap_play < m2_room,
                f"cap play at the screws {cap_play:.2f}; holes clear an M2 by {m2_room:.2f}"))

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
    out.append(("the rod never bears on the LED", ROD_GAP > 0,
                f"{ROD_GAP:g} mm of air at the rod's top"))
    v = _overlap(ps["led"], cap)
    out.append(("the star sits in its pocket", v < 1e-3, f"overlap {v:.3f} mm^3"))
    pushed = _overlap(Pos(0.15, 0, 0) * ps["led"], cap)
    out.append(("the pocket alone locates the star", pushed > 1e-3,
                f"moved 0.15, it strikes the pocket ({pushed:.3f} mm^3)"))
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
                f"{FULL_POWER_W / th['g_wall']:.1f} K from star to wall at {FULL_POWER_W:g} W"))
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
    print("\n  [est] LZ7_H, STAR_D, STAR_T, RTH_STAR, and every film and joint coefficient")
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
