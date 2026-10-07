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
drift apart. Two parts differ, and both sit where the optics sit:

``emitter_head``
    In place of the optical head. The same outside, the same port land and lip,
    the same rim, inserts and cavity bore the plate's spigot locates in, so it
    drops into the same collar. Inside, the eight LED bores are gone and the
    collection tube becomes a holder for a glass mixing rod: a hexagonal light
    pipe that turns seven coloured dies into one even colour at the port.
``emitter_plate``
    In place of the detector plate. Aluminium, not printed, and a full disc
    rather than a plate with ears: it is the heat spreader. The LED sits face
    down in a pocket in its underside, on a star board, pressed against the
    rod's top end. Heat goes from the star into the plate, through the posts
    into the base, and out through the base's wall.

The base is the sensor's base, turned from aluminium instead of printed. That
is the one place the twins differ in material, and it is the honest one: the
puck that makes light is the puck that gets warm, and it is made of the thing
that carries heat. If Jared wants the material to match too, the sensor's base
can be turned from the same bar; its shape is already identical.

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

ROD_SEAT_Z = 1.4
"""CHOSEN. Height of the rod's output face above the port face. The rod stands
on a ledge whose opening is the hexagon's inscribed circle, so only the six
corners rest on it, and its face is recessed where nothing touches the glass."""

LEDGE_T = 0.8
"""CHOSEN. Two layers at 0.4. Below it the port is the sensor's 8 mm bore."""

ROD_GAP = 0.3
"""CHOSEN. Air between the rod's top and the LED's window. The rod never bears
on the LED; the ledge carries it."""

TUBE_WALL = 1.6
"""CHOSEN. The rod tube's wall, as the sensor head's collection tube."""

POCKET_CLEAR = 0.1
"""CHOSEN. Radial clearance between the star and its pocket. The pocket locates
the star; its two screws only clamp it to the plate."""

CAP_T = 2.0
"""CHOSEN. Aluminium above the star's back, so the pocket is closed and the star
presses on solid metal."""

WIRE_SLOT_W = 5.0
WIRE_SLOT_ANGLE = 0.0
"""CHOSEN. One slot from the pocket out through the boss and the disc, at +X,
for the star's wires to leave the pocket and rise to the boards. Seal it with
black silicone once wired; the pocket is otherwise light-tight."""

THERMISTOR_D = 2.2
THERMISTOR_ABOVE = 0.5
"""CHOSEN. A blind hole down into the cap for a bead thermistor, stopping
THERMISTOR_ABOVE short of the star's back: the reading is the plate where it is
hottest, which is what the derating runs on."""

DISC_CLEAR = 0.3
"""CHOSEN. The disc stops this far inside the wall, as the sensor plate's ears
do, so the posts' spigots alone locate it. The gap is filled with a strip of
soft thermal gap pad wrapped round the disc's edge: too soft to locate
anything, and it carries most of the heat to the wall. See thermal()."""

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
"""CHOSEN. The plate temperature at which firmware derates. Set by the printed
parts that touch aluminium (PETG softens near 80 C), not by the LED, which at
this plate temperature and full power is still well under TJ_MAX."""

AMBIENT = 25.0
AL_DENSITY = 2.70e-3  # g/mm^3
AL_CP = 0.90  # J/(g K)
AL_K = 0.20  # W/(mm K)
H_CONV = 7.5e-6  # W/(mm^2 K), still air on a 50 mm vertical wall
H_RAD = 6.2e-6  # W/(mm^2 K), black anodised (emissivity 0.85) near 60 C
JOINT_G = 1.9
RIM_PAD_K = 3.0e-3  # W/(mm K)
"""Material constants, the gap pad round the disc's edge (a common 3 W/(m K)
silicone pad), and the conductance of one post-to-plate joint with
thermal paste (W/K), from paste at 3 W/(m K) in a 0.05 mm film over the ring
the plate sits on."""

# ---------------------------------------------------------------- derived ---

TUBE_R = (ROD_AF + ROD_CLEAR) / math.sqrt(3) + TUBE_WALL
"""DERIVED. The rod tube's outer radius: the bore's corner radius plus a wall."""

LED_FACE_Z = ROD_SEAT_Z + ROD_L + ROD_GAP
STAR_FRONT_Z = LED_FACE_Z + LZ7_H
STAR_BACK_Z = STAR_FRONT_Z + STAR_T
BOSS_TOP_Z = STAR_BACK_Z + CAP_T
POCKET_R = STAR_D / 2 + POCKET_CLEAR
BOSS_R = POCKET_R + 2.4
DISC_R = K.R_IN - DISC_CLEAR


def _hex(af: float, z0: float, z1: float) -> Part:
    """A hexagonal prism across flats ``af``, flats facing +/-Y, from z0 to z1.
    Three slabs at 60 degrees, intersected."""
    big = 2 * af
    slab = Pos(0, 0, z0) * Box(big, af, z1 - z0, align=_MIN)
    return slab & (Rot(0, 0, 60) * slab) & (Rot(0, 0, 120) * slab)


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
    places at PLATE_Z exactly as the detector plate does."""
    t = plate.PLATE_T
    z = P.PLATE_Z
    part = _cyl(DISC_R, 0.0, t) + plate.spigot()
    part = part + _cyl(BOSS_R, t - 0.5, BOSS_TOP_Z - z)
    # The star's pocket, up from the underside to the star's back.
    part = part - _cyl(POCKET_R, -1.0, STAR_BACK_Z - z)
    # The wires' slot, from the pocket out past the boss, below the star's
    # front face only, so the star's back keeps its whole seat.
    r0, r1 = POCKET_R - 1.5, BOSS_R + 4.0
    slot = Rot(0, 0, WIRE_SLOT_ANGLE) * Pos((r0 + r1) / 2, 0, -1.0) * Box(
        r1 - r0, WIRE_SLOT_W, STAR_FRONT_Z - z + 1.0, align=_MIN)
    part = part - slot
    # The thermistor's well, down into the cap beside the axis.
    tx = POCKET_R / 2
    part = part - _cyl(THERMISTOR_D / 2, STAR_BACK_Z - z + THERMISTOR_ABOVE,
                       BOSS_TOP_Z - z + 1.0, tx, tx)
    # The posts' spigots and the head's M2 screws, as the detector plate.
    for x, y in K.post_positions():
        part = part - _cyl(K.POST_SPIGOT_D / 2 + K.SPIGOT_CLEAR, -1.0, t + 1.0, x, y)
    for x, y in head.plate_screw_positions():
        part = part - _cyl(head.PLATE_SCREW_CLEAR_D / 2, -1.0, t + 1.0, x, y)
    return part


def rod() -> Part:
    return _hex(ROD_AF, ROD_SEAT_Z, ROD_SEAT_Z + ROD_L)


def led_on_star() -> Part:
    """The LZ7 and its star, face down, as one envelope."""
    led = Pos(0, 0, LED_FACE_Z) * Box(LZ7_W, LZ7_W, LZ7_H + 0.01, align=_MIN)
    return led + _cyl(STAR_D / 2, STAR_FRONT_Z, STAR_BACK_Z)


PRINTED = ("emitter_head", "puck_tray", "puck_lid")
MACHINED = ("emitter_base", "emitter_plate")
SHARED = {"emitter_base": "puck_base", "puck_tray": "puck_tray", "puck_lid": "puck_lid"}
"""Every emitter part that is the sensor puck's own solid, by the sensor's name."""


def parts() -> dict[str, Part]:
    return {
        "emitter_base": K.base(),
        "emitter_head": emitter_head(),
        "emitter_plate": Pos(0, 0, P.PLATE_Z) * emitter_plate(),
        "puck_tray": K.tray(),
        "puck_lid": K.lid(),
        "rod": rod(),
        "led": led_on_star(),
        "esp32_board": K.esp32(),
        "driver_board": K.driver(),
    }


# ----------------------------------------------------------------- thermal --

def thermal() -> dict[str, float]:
    """What the aluminium can hold and shed, from the CAD's own volumes and areas.

    One lump for the base and plate, with the posts and the rim's gap pad
    between them as a fixed drop. Full power runs until the plate reaches PLATE_LIMIT; after that the
    puck can shed what its wall loses at that temperature, and no more without
    a stand to sink into."""
    base, plate_ = K.base(), emitter_plate()
    mass = (base.volume + plate_.volume) * AL_DENSITY
    heat_cap = mass * AL_CP
    # The wall's outside and the foot shed heat; the lid is PETG and is left out.
    wall = 2 * math.pi * K.R_OUT * (K.rim_top() - K.FOOT_RELIEF)
    foot = math.pi * (K.R_OUT ** 2 - (K.HEAD_R + K.HEAD_CLEAR) ** 2)
    h = H_CONV + H_RAD
    ha = h * (wall + foot / 2)  # a foot facing down sheds about half as well
    # Posts: aluminium columns, plate to floor, in parallel with their joints.
    post_a = math.pi * (K.BOSS_R ** 2 - (K.M3_CLEAR_D / 2) ** 2)
    post_l = K.SEAT_Z - (K.FOOT_RELIEF + K.FLOOR_T)
    g_post = AL_K * post_a / post_l
    g_posts = K.POST_N / (1 / g_post + 1 / JOINT_G)
    # The gap pad round the disc's edge, in parallel with the posts.
    g_rim = RIM_PAD_K * 2 * math.pi * DISC_R * plate.PLATE_T / DISC_CLEAR
    g = g_posts + g_rim
    # Plate at the limit means the base is behind it by the posts' drop.
    body_limit = PLATE_LIMIT - FULL_POWER_W / g
    rise = body_limit - AMBIENT
    frac = ha * rise / FULL_POWER_W
    full_s = -heat_cap / ha * math.log(1 - frac) if frac < 1 else math.inf
    sustained = ha * (PLATE_LIMIT - AMBIENT) / (1 + ha / g)
    tj = PLATE_LIMIT + FULL_POWER_W * (RTH_JC + RTH_STAR)
    return dict(mass_g=mass, heat_cap=heat_cap, area_mm2=wall + foot, ha=ha, g=g,
                g_posts=g_posts, g_rim=g_rim, full_s=full_s, sustained_w=sustained, tj_at_limit=tj)


# ------------------------------------------------------------------ checks --

def _overlap(a: Part, b: Part) -> float:
    return K._overlap(a, b)


def check() -> list[tuple[str, bool, str]]:
    ps = parts()
    sensor = K.parts()
    out = []
    for name in PRINTED + MACHINED:
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
    turned = _overlap(Rot(0, 0, 1.0) * ps["emitter_plate"], ps["emitter_head"])
    out.append(("the plate's spigot clocks it on the emitter head", turned > 1e-3,
                f"turned 1deg, the key arc strikes a web ({turned:.3f} mm^3)"))

    # The optics.
    out.append(("the rod's output face is recessed in the port", ROD_SEAT_Z > 0,
                f"{ROD_SEAT_Z:g} mm above the port face, behind the lip"))
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
    v = _overlap(ps["led"], ps["emitter_plate"])
    out.append(("the star sits in its pocket", v < 1e-3, f"overlap {v:.3f} mm^3"))
    pushed = _overlap(Pos(0.15, 0, 0) * ps["led"], ps["emitter_plate"])
    out.append(("the pocket alone locates the star", pushed > 1e-3,
                f"moved 0.15, it strikes the pocket ({pushed:.3f} mm^3)"))
    out.append(("the LED's dies fall inside the rod's mouth", EMIT_D <= ROD_AF,
                f"emitting area {EMIT_D:g} mm across, rod {ROD_AF:g} mm across flats"))

    # Room in the shell.
    room = K.esp_z() - BOSS_TOP_Z
    out.append(("the boss clears the board above it", room >= K.STACK_GAP,
                f"{room:.2f} mm under the ESP32, wiring needs {K.STACK_GAP:g}"))
    out.append(("the boss clears the plate's screws",
                BOSS_R < head.PLATE_SCREW_R - head.PLATE_SCREW_CLEAR_D / 2 - 1.0,
                f"boss r={BOSS_R:.2f}, M2 screws at r={head.PLATE_SCREW_R:.2f}"))

    solids = {n: ps[n] for n in ps}
    solids["puck_lid"] = K.lid(ribs=False)  # its ribs reach into the tray on purpose
    names = list(solids)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if {a, b} == {"led", "rod"}:
                continue
            v = _overlap(solids[a], solids[b])
            out.append((f"{a} clear of {b}", v < 1e-3, f"overlap {v:.3f} mm^3"))

    # Full power, without a fan.
    th = thermal()
    out.append(("full power keeps the LED under its junction limit at the derating point",
                th["tj_at_limit"] < TJ_MAX,
                f"Tj {th['tj_at_limit']:.0f} C with the plate at {PLATE_LIMIT:g} C; limit {TJ_MAX:g}"))
    out.append(("the plate hands full power to the wall without eating the margin",
                FULL_POWER_W / th["g"] < (PLATE_LIMIT - AMBIENT) / 2,
                f"{FULL_POWER_W / th['g']:.1f} K from plate to wall at {FULL_POWER_W:g} W"))
    return out


def report() -> int:
    fails = 0
    th = thermal()
    print(f"emitter puck: {2 * K.R_OUT:.1f} dia x {K.lid_top():.1f} tall, the sensor puck's shell")
    print(f"  rod {ROD_AF:g} mm hex x {ROD_L:g}, face {ROD_SEAT_Z:g} above the port; "
          f"LED face z={LED_FACE_Z:.2f}, boss top z={BOSS_TOP_Z:.2f}")
    print(f"  aluminium {th['mass_g']:.0f} g (base and plate), {th['heat_cap']:.0f} J/K; "
          f"sheds {th['ha']:.3f} W/K from {th['area_mm2'] / 100:.0f} cm^2; "
          f"plate to wall {th['g']:.2f} W/K "
          f"(gap pad {th['g_rim']:.2f}, posts {th['g_posts']:.2f})")
    print(f"  full power ({FULL_POWER_W:g} W) from cold: {th['full_s'] / 60:.1f} min to a "
          f"{PLATE_LIMIT:g} C plate; then {th['sustained_w']:.1f} W for as long as you like\n")
    for name, ok, detail in check():
        fails += not ok
        print(f"  [{'ok' if ok else 'FAIL'}] {name}  {detail}")
    print("\n  [est] LZ7_H, STAR_D, STAR_T, RTH_STAR, H_CONV, H_RAD, JOINT_G, RIM_PAD_K")
    return fails


def print_ready() -> dict[str, Part]:
    """The parts this puck adds, in their make orientation. The head prints rim
    down as the sensor head does; the plate and base are machined, given here
    as modelled. The tray and lid are the sensor puck's files."""
    flip = Rot(180, 0, 0)
    raw = {"emitter_head": flip * emitter_head(), "emitter_plate": flip * emitter_plate(),
           "emitter_base": K.base()}
    return {name: Pos(0, 0, -p.bounding_box().min.Z) * p for name, p in raw.items()}


if __name__ == "__main__":
    raise SystemExit(report())
