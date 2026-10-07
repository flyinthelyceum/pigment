# The emitter puck

The sensor puck's twin. The sensor puck reads a surface's colour. The emitter
puck gives that colour back as light, bright enough to throw onto a wall. It is
the second half of the pair in `INQUIRY.md`: the instrument that measures and
the light that answers it.

Drawn in `spectra/cad/emitter.py`, which checks everything below that geometry
can check. Nothing has been bought, machined or printed: the lane is HOLD for
hardware, and this is the drawing that a reopen would buy against.

## What Jared asked for (2026-10-07)

- **Bright.** Lux is the limit he keeps hitting, to the point of wanting to light
  rooms with lasers. The sensor puck's eight 5 mm LEDs cannot light a wall.
- **Efficient.** One emitter, one heat path and one supply. Separate drivers and
  heat sinks per colour were "laughably thoughtless".
- **No fan.**
- **The same form factor as the sensor puck.** "The symmetry between the two is
  super important."
- **Full power, or at least the ability to run it.** "Don't get conservative
  here. Let's push the limits."

## How the symmetry is kept

The emitter does not copy the sensor puck's shell. It imports it.
`puck.base()`, `puck.tray()` and `puck.lid()` are the same solids in both pucks,
and a test fails if they ever differ. Change the sensor's shell and the
emitter's changes with it. Both pucks are 79.4 mm across and 49.0 mm tall, with
the same seam, the same lid, the same four screws from the foot and the same
USB opening.

Two parts differ. Both sit inside, where the optics are:

- **The head.** It has the same outside, port land, lip, rim and inserts as the
  optical head, so it drops into the same collar. Inside, the LED bores are gone,
  and the collection tube becomes a holder for a glass mixing rod.
- **The plate.** It is aluminium instead of printed PETG, and a full disc instead
  of a plate with ears, because it is the heat spreader. The LED sits face down
  in a pocket in its underside.

The base is the same shape, turned from aluminium instead of printed. This is
the one place the twins differ in material, and it is the honest place for it:
the puck that makes light is the one that gets warm, and it is made of what
carries heat away. If Jared wants the materials to match as well, the sensor's
base can be turned from the same bar, since its shape is already identical.
The memory rule holds: anything in the emitter either fits the sensor's shape,
or both change together.

**Port to port.** Turn the emitter port-up and set the sensor on it port-down.
The two crushable lips meet and seal the joint against room light, and the
sensor reads the emitter's light directly. That is how the emitter is
calibrated: drive one die and read what arrives. It is also a small piece in
itself, an instrument reading its own echo. A section through the pair, lip to
lip, is in `/mnt/project-files/build/emitter/port-to-port-section.svg`. Nothing
centres the two pucks on each other yet; see "Not settled".

## The light

**LED Engin (ams OSRAM) LZ7-04M100.** Seven dies under one flat glass window,
each driven on its own: violet 395, blue 457, cyan 500, green 523, amber 595,
red 623 and a cool white. The package is 7 mm square, with all seven dies inside
3.8 mm. That set matches the sensor puck's channels except its 660, which is the
point. What the sensor separates, the emitter can put back. It runs up to about
20 W with every die on, around 0.85 A each.

- **End of life.** The family is marked not-for-new-designs, with an end-of-life
  notice dated August 2026. Buy spares when buying one.
- **It is a bare surface-mount part.** It comes on a 20 mm aluminium star board,
  or gets reflowed onto one. The star sits in the plate's pocket, located by the
  pocket and clamped by its own two screws into the plate.

**Mixing rod: Edmund Optics #17695.** A 4 mm hexagonal light pipe, 25 mm long,
in N-BK7 glass, about $130. Seven dies side by side make seven coloured blobs.
A hexagonal rod, through repeated internal bounces, turns them into one even
colour at its far end. That end sits 1.4 mm back from the port face, on a ledge
that catches only its six corners and masks 9.3% of the face. The rod never
touches the LED: there is 0.3 mm of air between them. 25 mm is the length that
fits under the plate. Edmund also sells 50 and 100 mm.

## Full power, no fan

The heat path runs from the LED, into the star, into the aluminium plate, and
into the base. It crosses to the base through the four posts and through a strip
of soft thermal gap pad wrapped round the plate's edge. The pad fills the 0.3 mm
gap to the wall. It is too soft to locate anything, so fasteners still only
fasten, and it carries most of the heat. From the base's wall the heat leaves
by air and by radiation; anodise the base black, which helps.

`python -m spectra.cad.emitter` computes this from the CAD's own volumes and
areas:

| | |
|---|---|
| Aluminium (base and plate) | 141 g, 127 J/K |
| Plate to wall | 8.6 W/K: gap pad 7.0, posts 1.6 |
| Full power (20 W) from cold | **4.9 minutes** to a 65 °C plate |
| After that, indefinitely | **7.1 W**, about a third of full power |
| LED junction at 65 °C plate, full power | 103 °C, against a 125 °C limit |

**65 °C is the printed parts' limit, not the LED's.** The head, tray and lid are
PETG, which softens near 80 °C, and they touch the aluminium. A thermistor
sits in a well in the plate above the star, and firmware derates when the plate
reaches 65 °C.

That makes the honest shape of "full power": every die flat out for about five
minutes from cold, then a third of that for as long as you like. Before the gap
pad went in, this came out at 3.4 minutes and 6.5 W. Both are estimates until a
thermistor log replaces them. The film coefficients and the joint conductances
are textbook figures, marked as estimates in the code.

**To push further, in order of cost:**

1. **A finned aluminium stand.** The puck sits in it, the stand carries the
   heat, and full power has no time limit. The stand is furniture, not part of
   the puck's form, so the symmetry holds.
2. **Head, tray and lid in a hotter plastic** (ASA or polycarbonate). The plate
   limit can then rise to 85 °C, where the LED's junction reaches 123 °C at full
   power, just under its 125 °C limit. That gives 8.6 minutes at full power and
   10.7 W sustained. Above 85 °C, the LED is the limit, not the plastic.
3. **An aluminium lid** adds the top face to the area that sheds heat. It is a
   change of material on a shared part, so it is asked of both pucks or of
   neither.

## Boards

Whatever drives the LED must fit the shell's two board envelopes: the DevKitC-1's
outline on the tray, and the TLC59711's outline under the lid. `check()` holds
everything clear of both.

There is one real problem, and it is power. Twenty watts does not come from a
5 V USB port. It needs USB-C Power Delivery at 20 V. The DevKitC-1's own
receptacle cannot ask a charger for 20 V, and the shell has exactly one opening,
lined up with that receptacle.

**Recommendation, not drawn:** one custom board on the DevKitC-1's outline and
height, so the tray, fences and opening do not change. Its USB-C receptacle sits
where the DevKitC-1's native port sits, and the board carries:

- the PD sink that asks for 20 V;
- an ESP32-S3 module;
- seven constant-current buck channels, about 1 A each.

The bay under the lid stays free, for the bucks if they do not all fit on the
one board. At about 90% efficiency the drivers add about 2 W of heat into the
case air. A 30 W PD charger (20 V at 1.5 A) covers the LED, the drivers and the
ESP32 with room to spare.

## Not settled

- **The board above.** Unrouted, and the largest piece of work left.
- **Centring the two pucks port to port.** Same diameter, so a thin printed
  sleeve or the dock could do it. Not drawn.
- **Light leaks.** The wire slot out of the pocket is sealed with black silicone
  once wired. Otherwise the pocket is closed metal.
- **Dimensions.** The LED, star and rod sizes come from catalogue pages, not
  calipers. The LED's height and the star's size are estimates. When the parts
  arrive, they are measured into `components` and imported, as every other part
  is.
- **The firmware**: thermistor reading and derating, and driving seven channels
  from a stored curve. None of it is written.
- **Machining.** The base's posts and collar were drawn to be printed. Turned
  and milled from bar they are possible but not cheap; a quote will say whether
  the base wants simplifying for metal.
