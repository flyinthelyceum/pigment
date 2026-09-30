# The case

What holds the head in a hand. Nothing here is designed yet; this is the research
the design should start from, three massing studies drawn around the real parts,
and the order to do the CAD and rendering in.

    .venv/bin/python -m spectra.cad.case                           # sizes and checks
    .venv/bin/python -m spectra.cad.viewer --cases --out export/cases.html

## What the market already settled

Every handheld contact colorimeter solves the same problem: a flat port pressed
square onto a sample, a light seal, a calibration standard that travels with it.
They make three different bets on form.

| Device | Form | Size | Geometry, sensor | Calibration | What to take from it |
|---|---|---|---|---|---|
| [Nix Mini 3][nix] | Cube-ish puck, metal | 40 × 40 × 25 mm | 31-channel sensor, 2 white LEDs, 13 mm samples | Separate tile | How small a puck can get when the head is small |
| [Nix Spectro 2][nix] | Puck, metal | 60 × 60 × 45 mm | 31 ch, 8 LEDs incl. violet and UV; 5 mm or 2 mm aperture | Ceramic tile | The closest size to this head. Aperture swaps by jig |
| [Datacolor ColorReader Spectro][dc] | Torch / pen | 30 dia × 105 mm | **8-channel, 45/0**, 6 mm aperture | Compact tile | The nearest thing on the market to this instrument. Held like a marker |
| [Variable Spectro 1][var] | Puck with a phone app | — | d/0, 8 mm aperture | Tile | Same port size as ours |
| [X-Rite ColorMunki][munki] | Palm body with a rotating dial | — | Spectro | **Tile built in**: turn the dial to a calibration position | Standards that cannot be left at home |
| [Konica Minolta CM-17d][km17] | Vertical grip, one hand | — | Lab spectro, camera viewfinder | **Cradle holds the zero box and the white cap** | A dock that is also the calibration ritual |

Two findings from that table carry weight here.

**The ColorReader Spectro is the reference, not the Nix.** It is an 8-channel
45/0 instrument with a small port, which is exactly Stage 1. It is a torch because
a 45/0 ring is round and axial, and everything else can line up behind it.

**The good devices carry their standards.** `OPTICAL_HEAD.md` rules dark, black
and white before every session. A case that parks on the PTFE tile when it is put
down, and has the light trap as its second station, makes that ritual the default
rather than a chore. The CM-17d cradle and the ColorMunki dial are two versions of
the same idea. This is the strongest single design idea in the research and it
applies to any of the three forms.

## Three massing studies

`spectra/cad/case.py` draws each as a hollow shell around the real head (44.5 mm
dia × 24 mm plus the lip), the real detector stack, and the ESP32-S3 DevKitC-1 and
SSD1306 from the components library. The shell is massing, not a part: no split
line, no fasteners, no bosses. Sizes are what the parts force.

| Concept | Overall, mm | Reference | Held |
|---|---|---|---|
| `puck` | 74.5 dia × 64.5 | Nix Spectro 2, 60 × 60 × 45 | Fingertip on top, load straight down the axis |
| `torch` | 51.3 dia × 103.6 | ColorReader, 30 dia × 105 | Like a fat marker |
| `palm` | 122.5 × 51.3 × 38.9 | i1Pro / ColorMunki | Palm on the body, broad foot coplanar with the port |

What the models show that a sketch would not:

- **The DevKitC-1, not the head, sets the puck.** It is 62.74 mm long, lies flat,
  and its diagonal makes the puck 74.5 mm across against the head's 44.5. A
  thumb-sized controller board would bring the puck down near the Nix Spectro 2.
  That is a board choice, not a CAD problem, and it is an order, so it waits for
  the lane.
- **The torch is the head's own diameter.** 51 mm is the head plus clearance and
  wall; both boards stand edge-on inside it. It cannot get thinner than the LED
  ring, so it is fatter than the ColorReader by the ring.
- **The palm is the only one with a foot.** Its whole underside is coplanar with
  the port face, so it resists rocking on a sample in a way the other two do not.
  It is also the only one with somewhere natural for a display.
- **There is a battery in every concept and none on the BOM.** The head as
  specified is tethered by USB. A handheld is a battery decision; the cell is an
  estimate (`CELL_L/W/T`) so the concepts are not flattered by leaving it out.

Rules each concept is checked against, in `case.check()` and `tests/test_cad.py`:
the port face is the stop, so no case geometry goes below z = 0; the case never
touches the head; every board fits inside its shell; the shell is one solid.

## The CAD and rendering order

1. **Massing, done here.** build123d plus the existing three.js viewer. Answers
   size, proportion and fit. Cheap to rerun whenever a part changes.
2. **Pick a form, then detail it.** Split line, how the head is held (above the
   LED plane, never at the port), fasteners with the heat-set inserts already in
   the components library, the USB-C opening, and the tile/trap dock. Chamfers by
   rotated box cutters, not kernel fillets, as in the head.
3. **Hold it before rendering it.** A draft print of the chosen shell in any
   filament answers grip and size better than any render. That is a print, so it
   waits for the lane to reopen.
4. **Photoreal renders, last.** `build123d.export_step` to Fusion or KeyShot,
   or `export_gltf` into Blender with a scripted Cycles scene
   (`blender -b -P render.py`) so a render is rebuilt from the model rather than
   posed by hand. Worth it for a finished form and for showing people; not worth
   it for choosing between forms, where the viewer is faster and honest about
   dimensions.

## Not decided

Which form. The controller board. The battery and whether there is one. Whether
the tile and trap become a dock. None of these is a CAD question first.

[nix]: https://www.nixsensor.com/color-sensor-comparison/
[dc]: https://www.datacolor.com/business-solutions/product/colorreader-spectro/
[var]: https://variableinc.com/product/spectro-1-professional-color-measurement/
[munki]: https://www.northlight-images.co.uk/x-rite-colormunki-photo-review/
[km17]: https://fineeng.eu/konica-minolta-to-launch-the-cm-17d-a-vertical-portable-spectrophotometer-for-high-accuracy-colour-measurement-in-any-situation/
