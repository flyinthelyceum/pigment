"""The puck, version one: the case the concepts were choosing between, detailed.

    python -m spectra.cad.puck                         # build, check, report
    SPECTRA_CASE=puck-v1 python -m spectra.cad.viewer  # see it

Chosen over the palm on 2026-09-30, for the reasons in `docs/CASE.md`: a press
on the top goes straight down the optical axis, it works on anything the lip
covers, and a round body parks on a round dock.

Four printed parts and one set of screws:

``puck_base``
    Printed foot down. A floor ring, a short collar that locates the head
    radially, an outer wall, and four posts carrying M3 heat-set inserts.
``puck_plate``
    The detector plate from `plate.py` with four ears added. The ears sit on the
    posts. Three M2 screws hold the plate down on the head's rim, so the head
    hangs from the plate and the plate hangs from the posts.
``puck_tray``
    Carries the ESP32-S3 DevKitC-1 by its pin headers: the header plastic rests
    on the tray and the pins pass through slots. The board has no mounting
    holes, so the headers are the only thing it can be held by. Standoff tubes
    under the tray land on the plate's ears.
``puck_lid``
    Printed top down. Bosses come down onto the tray. The USB-C opening is in
    its wall.

One M3 screw per post runs down through the lid boss, the tray standoff and
the plate ear into the post's insert, clamping the whole stack. Four screws
hold the entire instrument together.

**The load path is the point of the design.** A finger on the lid pushes down
the bosses, the standoffs, the ears and the plate onto the head's rim, and the
head onto the sample through its port land. The base hangs from the ears and
touches nothing below: its foot stands ``FOOT_RELIEF`` above the port face, so
the port land is the only stop when the puck is square, and the foot catches
it before it can tilt out of the ruled +/-2 degrees.

Powered by USB, as the BOM specifies. There is no battery; see `CASE.md`.
"""

from __future__ import annotations

import math
import os

from build123d import Align, Box, Cylinder, Part, Pos, Rot

from components import esp32_s3_devkitc1 as E
from components import heatset_insert_m3x6 as M3

from . import head, params as P, plate

_MIN = (Align.CENTER, Align.CENTER, Align.MIN)

# ------------------------------------------------------------------ chosen --

WALL = 2.4
"""CHOSEN. Six perimeters, as the head. Opaque, and stiff under a fingertip."""

FLOOR_T = 2.4
"""CHOSEN. The base's floor ring."""

FOOT_RELIEF = 0.4
"""CHOSEN, and the number that makes the foot safe to have. A foot coplanar with
the port face would share the stop with the port land, and a print that came
out a tenth proud would lift the port off the sample. Standing the foot 0.4 mm
above the port face makes the port land the only stop when the puck is square;
the foot only touches down once the puck has tilted, which caps the tilt. See
check()."""

HEAD_CLEAR = 0.3
"""CHOSEN. Radial clearance between the collar and the head. The collar guides;
the plate and its screws locate. Two things locating one part fight."""

COLLAR_TOP = 10.0
"""CHOSEN. Height of the collar that guides the head. It must stop well below
where the LED bores break out of the head's wall, or it closes in on the LED
leads. See check()."""

LEAD_ROOM = head.LEAD_ROOM
LEAD_R = head.LEAD_R

CASE_CLEAR = 1.0
"""CHOSEN. Air between a board and the case wall."""

STACK_GAP = 2.0
"""CHOSEN. Air between the detector's STEMMA QT socket and the ESP32 above it."""

WIRE_ROOM = 3.0
"""CHOSEN. Air between the tips of the ESP32's header pins and the plate, for
the wires soldered to them."""

BOSS_WALL = 2.0
"""CHOSEN. Wall around an M3 insert. Five perimeters at 0.4 mm."""

M3_CLEAR_D = 3.4
"""CHOSEN. Clearance hole for M3."""

M3_HEAD_D = 6.0
M3_HEAD_H = 3.4
"""CHOSEN. Counterbore for an ISO 4762 M3 socket head (5.5 mm across, 3 mm tall)
with print clearance."""

INSERT_INTERFERENCE = head.INSERT_INTERFERENCE
"""The same 0.4 mm the head's M2 inserts use; see head.py."""

POST_N = 4
"""CHOSEN. Four posts, not three. The board lies along X and fills a band across
the middle of the puck, and the only places midway between two LEDs that are
also outside that band come in fours."""

SEAM = 0.2
"""CHOSEN. Axial gap where the lid meets the base. The screws set the lid's
height through the stack, so the walls must not also try to."""

LAP_H = 3.0
LAP_CLEAR = 0.15
"""CHOSEN. The lid and base overlap in a half-wall lap, so the seam is not a
straight line of sight into the case."""

TRAY_T = 2.0
TRAY_BAR_W = 6.0
TRAY_SLOT_W = 1.4
"""CHOSEN. Tray thickness, the width of the bars under each header row, and the
slot the 0.64 mm pins drop through."""

HEADER_PITCH = 2.54
"""The 0.1 inch pin header standard. Width of a header's plastic strip."""

USB_PLUG_W = 12.5
USB_PLUG_H = 7.5
"""CHOSEN. Opening for a USB-C plug's overmould, around each of the board's two
USB-C receptacles. Sized for common cables; a fat one will not fit."""

USB_REACH = 6.5
"""CHOSEN. How far behind the outside of the wall a USB-C receptacle's mouth may
sit and still take a plug. About the plug's insertion depth."""

# ---------------------------------------------------------------- estimates --

ESP_BELOW = 8.5
"""ESTIMATE. How far the DevKitC-1's pin headers stand below its PCB. The
components library has the bare PCB. Owed: a caliper reading."""

HEADER_PLASTIC_H = 2.5
"""ESTIMATE. Height of the header's plastic strip, which is what rests on the
tray. Owed with ESP_BELOW."""

ESP_ABOVE = 3.5
"""ESTIMATE. Height of the module can and buttons above the PCB. Owed."""

USB_Z = 1.6
"""ESTIMATE. Height of a USB-C receptacle's centre above the PCB. Owed."""

# ----------------------------------------------------------------- derived --

HEAD_R = P.BODY_OD / 2
BOSS_R = (M3.OD - INSERT_INTERFERENCE) / 2 + BOSS_WALL
SPLIT_Z = P.PLATE_Z
"""DERIVED. The base ends where the plate sits: the plate's ears are the joint."""

PLATE_TOP = P.PLATE_Z + plate.PLATE_T


def led_breakout_z() -> float:
    """Lowest height at which an LED bore breaks out of the head's outer wall."""
    run = HEAD_R - P.LED_RING_R
    axis_z = P.LED_Z + run * math.tan(math.radians(P.ILLUM_ANGLE))
    return axis_z - (P.LED_SEAT_D / 2) / math.cos(math.radians(P.ILLUM_ANGLE))


def board_layout() -> tuple[float, float]:
    """(inner radius the board forces, x of the board's USB edge).

    The DevKitC-1 lies along X with its USB edge towards -X, as near the wall as
    it will go so a cable reaches it. The antenna overhangs the far edge, so the
    board plus antenna is not a rectangle and not centred: the smallest circle
    that holds it is found by searching over where the USB edge sits.
    """
    half_w = E.PCB_W / 2
    ant_half = E.ANTENNA_W / 2

    def need(x_usb: float) -> float:
        far = x_usb + E.LENGTH_WITH_ANTENNA
        pcb_far = x_usb + E.PCB_L
        return max(
            math.hypot(x_usb, half_w),
            math.hypot(pcb_far, half_w),
            math.hypot(far, ant_half),
        ) + CASE_CLEAR

    lo, hi = -E.LENGTH_WITH_ANTENNA, 0.0
    for _ in range(200):  # golden-section on a convex function
        a = hi - (hi - lo) / 1.618
        b = lo + (hi - lo) / 1.618
        if need(a) < need(b):
            hi = b
        else:
            lo = a
    x_usb = (lo + hi) / 2
    return need(x_usb), x_usb


def inner_r() -> float:
    """The case's inner radius: the largest of what the board, the LED leads and
    the posts each demand."""
    board_r, _ = board_layout()
    lead_r = HEAD_R + LEAD_ROOM * math.cos(math.radians(P.ILLUM_ANGLE)) + LEAD_R
    return max(board_r, lead_r)


R_IN = inner_r()
R_OUT = R_IN + WALL
POST_R = R_IN - BOSS_R + 0.5
"""DERIVED. The posts stand half a millimetre into the wall, so they fuse with it
into one solid rather than touching it along a line."""


def post_angles() -> list[float]:
    """Four angles midway between LEDs and clear of the board's band."""
    step = 360.0 / P.LED_N
    band = E.PCB_W / 2 + CASE_CLEAR + BOSS_R
    ok = [
        step * (k + 0.5)
        for k in range(P.LED_N)
        if abs(POST_R * math.sin(math.radians(step * (k + 0.5)))) > band
    ]
    if len(ok) < POST_N:
        raise ValueError(f"only {len(ok)} post positions clear the board; need {POST_N}")
    return ok[:POST_N]


def post_positions() -> list[tuple[float, float]]:
    return [(POST_R * math.cos(math.radians(a)), POST_R * math.sin(math.radians(a)))
            for a in post_angles()]


def esp_z() -> float:
    """Underside of the DevKitC-1's PCB. Whichever is higher: clear of the
    detector's socket, or high enough that the pins clear the plate."""
    from .case import detector_top

    return max(detector_top() + STACK_GAP, PLATE_TOP + ESP_BELOW + WIRE_ROOM)


def tray_top() -> float:
    return esp_z() - HEADER_PLASTIC_H


def lid_inner_top() -> float:
    return esp_z() + E.THICKNESS + ESP_ABOVE + STACK_GAP


def lid_top() -> float:
    return lid_inner_top() + WALL


def board_x0() -> float:
    return board_layout()[1]


# ------------------------------------------------------------------- parts --

def _cyl(r: float, z0: float, z1: float, x: float = 0.0, y: float = 0.0) -> Part:
    return Pos(x, y, z0) * Cylinder(r, z1 - z0, align=_MIN)


def _ring(r_in: float, r_out: float, z0: float, z1: float) -> Part:
    return _cyl(r_out, z0, z1) - _cyl(r_in, z0 - 1.0, z1 + 1.0)


def base() -> Part:
    """Floor ring, collar, wall with its half of the lap, and the posts."""
    z0 = FOOT_RELIEF
    bore = HEAD_R + HEAD_CLEAR
    floor = _ring(bore, R_OUT, z0, z0 + FLOOR_T)
    collar = _ring(bore, bore + WALL, z0 + FLOOR_T - 0.5, COLLAR_TOP)
    wall = _ring(R_IN, R_OUT, z0 + FLOOR_T - 0.5, SPLIT_Z)
    lap = _ring(R_IN + WALL / 2, R_OUT, SPLIT_Z - 0.5, SPLIT_Z + LAP_H)
    part = floor + collar + wall + lap

    pilot_r = (M3.OD - INSERT_INTERFERENCE) / 2
    for x, y in post_positions():
        part = part + _cyl(BOSS_R, z0 + FLOOR_T - 0.5, SPLIT_Z, x, y)
        part = part - _cyl(pilot_r, SPLIT_Z - M3.LENGTH - 0.5, SPLIT_Z + 1.0, x, y)
    return part


def puck_plate() -> Part:
    """The detector plate with an ear out to each post."""
    part = plate.detector_plate()
    reach = R_IN - 0.3
    for a in post_angles():
        ear = Rot(0, 0, a) * Pos((HEAD_R - 1.0 + reach) / 2, 0, 0) * Box(
            reach - HEAD_R + 1.0, 2 * BOSS_R, plate.PLATE_T, align=_MIN
        )
        part = part + ear
    # Trim the ear ends to the inside of the wall.
    part = part & Cylinder(reach, plate.PLATE_T, align=_MIN)
    for x, y in post_positions():
        part = part - Pos(x, y, -1.0) * Cylinder(M3_CLEAR_D / 2, plate.PLATE_T + 2.0, align=_MIN)
    return part


def tray() -> Part:
    """Two slotted bars under the header rows, tied to four standoff tubes."""
    z0, z1 = tray_top() - TRAY_T, tray_top()
    x0 = board_x0()
    xc = x0 + E.PCB_L / 2
    row = E.HEADER_ROW_SPACING / 2
    bar_len = E.PCB_L + 4.0
    part = None
    for sy in (-1, 1):
        bar = Pos(xc, sy * row, z0) * Box(bar_len, TRAY_BAR_W, TRAY_T, align=_MIN)
        part = bar if part is None else part + bar
    # A tie across the USB end joins the two halves. At that end, not the
    # antenna end (an antenna wants no material near it) and not the middle,
    # which is where the detector's cable and the LED wires come up.
    part = part + Pos(x0 + 2.0, 0, z0) * Box(6.0, 2 * row + TRAY_BAR_W, TRAY_T, align=_MIN)
    for x, y in post_positions():
        # A link from the post straight across to the nearer bar, then the tube.
        y_bar = math.copysign(row, y)
        link_len = abs(y - y_bar) + TRAY_BAR_W / 2
        part = part + Pos(x, (y + y_bar) / 2, z0) * Box(TRAY_BAR_W, link_len, TRAY_T, align=_MIN)
        part = part + _cyl(BOSS_R, PLATE_TOP, z1, x, y)
    part = part & _cyl(R_IN - 0.3, z0 - 50.0, z1 + 1.0)
    for sy in (-1, 1):
        part = part - Pos(xc, sy * row, z0 - 1.0) * Box(E.PCB_L - 2.0, TRAY_SLOT_W, TRAY_T + 2.0,
                                                        align=_MIN)
    for x, y in post_positions():
        part = part - _cyl(M3_CLEAR_D / 2, PLATE_TOP - 1.0, z1 + 1.0, x, y)
    return part


def lid() -> Part:
    """Wall with its half of the lap, the top, the bosses, and the USB opening."""
    z_lap = SPLIT_Z + SEAM
    top_in, top = lid_inner_top(), lid_top()
    outer = _cyl(R_OUT, SPLIT_Z + LAP_H + SEAM, top)
    lap = _ring(R_IN, R_IN + WALL / 2 - LAP_CLEAR, z_lap, SPLIT_Z + LAP_H + SEAM + 0.5)
    part = outer - _cyl(R_IN, z_lap - 1.0, top_in) + lap

    for x, y in post_positions():
        part = part + _cyl(BOSS_R, tray_top(), top_in + 0.5, x, y)
        part = part - _cyl(M3_CLEAR_D / 2, tray_top() - 1.0, top + 1.0, x, y)
        part = part - _cyl(M3_HEAD_D / 2, top - M3_HEAD_H, top + 1.0, x, y)

    # USB-C: one opening spanning both receptacles, through the wall at -X.
    z_usb = esp_z() + E.THICKNESS + USB_Z
    width = E.USB_C_CENTRES_APART + USB_PLUG_W
    # Long enough in X to get through the wall where it curves in at the
    # opening's edges, not only on the axis.
    depth = R_OUT - math.sqrt(R_IN ** 2 - (width / 2) ** 2) + 2.0
    part = part - Pos(-R_OUT - 1.0 + depth / 2, 0, z_usb) * Box(
        depth + 2.0, width, USB_PLUG_H, align=(Align.CENTER, Align.CENTER, Align.CENTER)
    )
    return part


def esp32() -> Part:
    """The DevKitC-1 as an envelope: PCB and antenna from the components library,
    headers and module height from the estimates above."""
    x0, z = board_x0(), esp_z()
    xc = x0 + E.PCB_L / 2
    pcb = Pos(xc, 0, z) * Box(E.PCB_L, E.PCB_W, E.THICKNESS, align=_MIN)
    ant = Pos(x0 + E.PCB_L + E.ANTENNA_OVERHANG / 2, 0, z) * Box(
        E.ANTENNA_OVERHANG + 0.5, E.ANTENNA_W, E.THICKNESS, align=_MIN)
    module = Pos(xc, 0, z + E.THICKNESS - 0.2) * Box(E.PCB_L - 6.0, E.PCB_W - 6.0,
                                                    ESP_ABOVE + 0.2, align=_MIN)
    part = pcb + ant + module
    row = E.HEADER_ROW_SPACING / 2
    for sy in (-1, 1):
        plastic = Pos(xc, sy * row, z - HEADER_PLASTIC_H) * Box(
            E.PCB_L - 4.0, HEADER_PITCH, HEADER_PLASTIC_H + 0.2, align=_MIN)
        pins = Pos(xc, sy * row, z - ESP_BELOW) * Box(
            E.PCB_L - 4.0, 0.64, ESP_BELOW - HEADER_PLASTIC_H + 0.2, align=_MIN)
        part = part + plastic + pins
    return part


def lead_keepouts() -> Part:
    return head.lead_keepouts()


PRINTED = ("puck_base", "puck_plate", "puck_tray", "puck_lid")
FAMILIES = PRINTED + ("esp32_board",)


def _explode() -> float:
    return float(os.environ.get("SPECTRA_EXPLODE", "0") or 0)


def parts() -> dict[str, Part]:
    return {
        "puck_base": base(),
        "puck_plate": Pos(0, 0, P.PLATE_Z) * puck_plate(),
        "puck_tray": tray(),
        "puck_lid": lid(),
        "esp32_board": esp32(),
    }


def placed() -> list[tuple[str, Part]]:
    """The puck's own solids, placed, exploded along Z if SPECTRA_EXPLODE is set.

    The head, its board and the sample are placed by assembly.py as always; the
    base drops away below them and everything above lifts, so the stack reads
    in the order it is screwed together.
    """
    e = _explode()
    shift = {"puck_base": -e, "puck_plate": 0.0, "puck_tray": e,
             "esp32_board": 2 * e, "puck_lid": 3 * e}
    return [(name, Pos(0, 0, shift[name]) * solid) for name, solid in parts().items()]


# ------------------------------------------------------------------ checks --

def _overlap(a: Part, b: Part) -> float:
    hit = a & b
    return 0.0 if hit is None else sum(s.volume for s in hit.solids())


def check() -> list[tuple[str, bool, str]]:
    ps = parts()
    body = head.body()
    out = []
    for name in PRINTED:
        n = len(ps[name].solids())
        out.append((f"{name} is one solid", n == 1, f"{n} solid(s)"))

    low = min(ps[n].bounding_box().min.Z for n in PRINTED)
    out.append(("the port land is the only stop", low > 0.0,
                f"lowest case point z={low:.2f}, port face z=0"))

    lever = R_OUT - P.PORT_LAND_OD / 2
    tilt = math.degrees(math.atan2(FOOT_RELIEF, lever))
    out.append(("the foot catches a tilt inside the ruled tolerance",
                tilt < P.ILLUM_ANGLE_TOL,
                f"foot touches down at {tilt:.2f}deg; ruled +/-{P.ILLUM_ANGLE_TOL:g}deg"))

    out.append(("collar stops below the LED breakout",
                COLLAR_TOP < led_breakout_z(),
                f"collar top z={COLLAR_TOP:g}, LED bores break out from z={led_breakout_z():.2f}"))

    keep = lead_keepouts()
    for name in PRINTED:
        v = _overlap(ps[name], keep)
        out.append((f"{name} leaves the LED leads room", v < 1e-6, f"overlap {v:.3f} mm^3"))

    solids = {**{n: ps[n] for n in PRINTED}, "head": body, "esp32": ps["esp32_board"]}
    if plate.available():
        from build123d import Pos as _P

        solids["as7341"] = _P(0, 0, PLATE_TOP) * plate.as7341_board()
    names = list(solids)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            v = _overlap(solids[a], solids[b])
            out.append((f"{a} clear of {b}", v < 1e-3, f"overlap {v:.3f} mm^3"))

    _, x_usb = board_layout()
    reach = R_OUT - abs(x_usb)
    out.append(("a USB-C plug reaches the board", reach <= USB_REACH,
                f"receptacle mouth {reach:.2f} behind the outer wall; plug reaches {USB_REACH:g}"))
    return out


def screw_length() -> tuple[float, float]:
    """Shortest and longest M3 that clamps the stack without bottoming out."""
    grip = (lid_top() - M3_HEAD_H) - P.PLATE_Z
    return grip + 3.0, grip + M3.LENGTH - 0.5


def print_ready() -> dict[str, Part]:
    """Every part to print, turned to its print orientation and set on z = 0.

    The base and the head print foot down, as modelled. The tray and the lid
    print upside down: the tray on its flat top with the standoffs standing up,
    the lid on its top face with the bosses standing up, so neither needs
    support and the counterbores are on the bed.
    """
    flip = Rot(180, 0, 0)
    raw = {
        "head": head.body(),
        "puck_base": base(),
        "puck_plate": puck_plate(),
        "puck_tray": flip * tray(),
        "puck_lid": flip * lid(),
    }
    return {name: Pos(0, 0, -p.bounding_box().min.Z) * p for name, p in raw.items()}


def export(out_dir) -> list:
    """STEP for Fusion and STL for the slicer, one pair per printed part."""
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


def report() -> int:
    fails = 0
    print(f"puck v1: {2 * R_OUT:.1f} dia x {lid_top():.1f} tall above the port face "
          f"(plus the {P.LIP_PROUD:g} lip)")
    print(f"  inner radius {R_IN:.2f}, posts at r={POST_R:.2f}, angles "
          f"{', '.join(f'{a:g}' for a in post_angles())}")
    lo, hi = screw_length()
    print(f"  4 x M3 socket head, {lo:.1f} to {hi:.1f} mm long; "
          f"4 x M3x6 inserts in the posts, 3 x M2x4 in the head rim\n")
    for name, ok, detail in check():
        fails += not ok
        print(f"  [{'ok' if ok else 'FAIL'}] {name}  {detail}")
    print("\n  [est] ESP_BELOW, HEADER_PLASTIC_H, ESP_ABOVE, USB_Z — caliper the populated DevKitC-1")
    return fails


if __name__ == "__main__":
    import sys

    if "--export" in sys.argv:
        from pathlib import Path

        dest = Path(__file__).resolve().parents[2] / "export" / "puck"
        for path in export(dest):
            print(f"wrote {path.relative_to(dest.parents[1])}")
    raise SystemExit(report())
