# The emitter puck

The sensor puck's twin. The sensor puck reads a surface's colour. The emitter
puck gives that colour back as light, bright enough to throw onto a wall. It is
the second half of the pair in `INQUIRY.md`: the instrument that measures and
the light that answers it.

Drawn in `spectra/cad/emitter.py`, which checks everything below that geometry
can check. Parts were ordered on 2026-10-08; nothing has been printed yet. The prototype's print files
are in `/mnt/project-files/build/emitter/prototype/`.

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

Three parts differ, and all of them sit inside, where the optics are:

- **The head.** It has the same outside, port land, lip, rim and inserts as the
  optical head, so it drops into the same collar. Inside, the LED bores are gone,
  and the collection tube becomes a holder for a glass mixing rod.
- **The plate.** A full flat disc instead of a plate with ears, because it is
  the heat spreader, with a hole in the middle for the LED and the rod's top.
- **The cap.** A shallow box on the plate. The LED's own board lies face down
  in its pocket, over a hole the LED hangs into, held to the cap's ceiling by
  thermally conductive double-sided tape. Two pegs under opposite corners drop
  into a hole and a slot in the plate, which locate and clock it. Nothing
  screws it down: the tray above captures it, and it cannot rise far enough
  to leave its pegs.

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
- **Buy it on its own board: LZ7-N4M100-0000.** The bare emitter has 14 pads,
  so it cannot be reflowed onto a stock 20 mm star, and no star version
  exists. LED Engin's seven-channel board is copper, 38.3 x 31.2 mm, and
  carries a 10k NTC thermistor, so the puck needs no thermistor of its own.
  The datasheet gives no thickness, hole or pad positions, and the emitter is
  taken as centred. The board is measured when it arrives, before the cap
  and plate are printed.
- **It only just fits.** The head's three plate screws sit at 22.6 mm from the
  centre, nearer than the board's corners at 24.6. The board is turned 78.3
  degrees, the angle that keeps it farthest from all three screw heads, about
  1 mm clear of the nearest. The cap's wall is notched round them.

**Mixing rod: Edmund Optics #17695.** A 4 mm hexagonal light pipe, 25 mm long,
in N-BK7 glass, about $130. Seven dies side by side make seven coloured blobs.
A hexagonal rod, through repeated internal bounces, turns them into one even
colour at its far end. That end sits about 1 mm back from the port face, on a ledge
that catches only its six corners and masks 9.3% of the face. The rod never
touches the LED: there is 0.6 mm of air between them, so even a rod at the top
of Edmund's ±0.3 mm length tolerance clears the glass. A dab of black silicone
in the bore keeps the rod on its ledge when the puck is turned port up. 25 mm is the length that
fits under the cap. Edmund also sells 50 and 100 mm.

## Building it: printed first, metal later

Jared, 2026-10-08: "let's prototype in an fdm material even if it isn't going to
hold up long term. we have petg and asa if we need higher heat resistance." And
for later: he has a waterjet for flat discs and a cold-cut saw for tube.

**Stage 1, all printed.** The shared shell (base, tray, lid) prints in the
sensor's black PETG, from the sensor puck's own files. The head, plate and cap
print in ASA, because the cap and plate touch the LED's board, and ASA holds its shape
to about 95 °C, where PETG gives up near 80 °C. All three print flat face down
with no supports: the head rim down as the sensor head does, and the plate and
cap top down. Files: `emitter_head`, `emitter_plate` and `emitter_cap`, as STL
and STEP.

The plastic cannot carry heat away, so this stage tests everything except
power: the colour mixing in the rod, what the light looks like on a wall in a
dark room, calibrating port to port, the wiring, and the form in the hand.

**Stage 2, waterjet the plate and cap.** The plate is already one flat 3 mm
layer, and the cap is two: a 3 mm frame round the board and a thinner sheet
over it (1.6 mm in the print, so the nearest sheet, 1.5 or 2 mm). Cut them from
aluminium sheet. What a waterjet cannot cut, it gives up for dowel pins: the
plate's spigot ring (which locates it on the head), and the cap's pegs. In
metal the board screws to the cap through its own three M3 holes, as LED Engin
recommends. That drawing is not done yet.

**Stage 3, the aluminium wall.** Stock round tube, cut to length on the cold
saw, with the base's floor and posts still printed inside it. This is where the
puck's diameter has to meet a stock tube size. Both pucks change together, so
the sensor keeps the same outside. Not drawn: it waits on choosing the tube.

## Driving the prototype

The printed prototype needs no new driver. The TLC59711 board Jared already has
sits in the bay under the lid in both pucks, and it sinks up to about 60 mA per
channel from the 5 V USB rail. Wire all seven anodes to V+ and each die's
cathode to its own channel. Seven channels at 60 mA come to about 1.3 W, which
is close to what the printed puck can shed (about 1 W), so the firmware should
hold the total a little under full scale until the thermistor is read. The
CircuitPython firmware in #11 already sets TLC59711 channels over USB serial.

At 60 mA each die runs at about a fourteenth of its rated current, so this is a
dim, even, true-coloured light: the right brightness for the printed stage, and
the 20 V board waits for the metal.

## The board, 2026-10-08

Sourcing the LED turned up that it is not sold on a 20 mm star, which the first
cap was drawn for. The cap and plate were redrawn for LED Engin's own
38.3 x 31.2 mm board. What changed:

- **The cap is a shallow box, not a round cup**, turned to clear the plate's
  screw heads, and notched round two of them.
- **No cap screws.** Pegs locate it and the tray captures it, which drops two
  screws and two inserts.
- **No separate thermistor.** The board has one.
- **More time at full power.** The copper board holds about five times the
  heat of a star, so the printed puck runs full power for about 20 seconds
  rather than 4, and sheds about 2 W rather than 1.
- **The wires are tight.** The board's face is 1.15 mm above the plate, so its
  sixteen wires (fourteen LED, two thermistor) leave flat under one long edge
  through an opening in the cap's wall: 30 AWG wire-wrap wire, soldered flat.
  Which edge carries the pads is a guess until the board arrives.

## Red team, 2026-10-08

Asked to red-team the printed design before the first print, Claude found and
fixed:

- **The star had nothing holding it up.** (The star has since become a
  board; the same tape holds it.) Face down in its pocket, it would
  have dropped onto the rod. It is now held by thermal tape to the ceiling, and
  the stack allows for the tape's thickness.
- **A long rod could touch the LED.** The 0.3 mm gap equalled Edmund's length
  tolerance. It is now 0.6 mm.
- **The thermistor read plastic, not the star.** Its well stopped 0.5 mm short.
  It went through to the star's back; the board now carries its own.
- **The tray's rails cleared the cap by 0.3 mm.** A slightly tall ASA print
  would have had the tray bearing on the cap. The ceiling is thinner and the
  gap is now 0.7 mm, checked with the cap raised half a millimetre.
- **Fourteen wires through a 5 mm slot.** It is now 6 mm.

Not fixed, and why:

- **The board's thickness, pads and holes are unverified.** The cap and plate
  wait for the board to arrive and be measured.
- **The gap between rod and LED loses light.** Some of the LED's light escapes
  sideways through the 0.6 mm gap before the rod catches it. That is the cost
  of never loading the glass; it is worth measuring port to port, not guessing.
- **The two pucks are not yet centred port to port.** The lips meet, but
  nothing aligns them. Hold them by hand for the first calibration.

## Full power, no fan

`python -m spectra.cad.emitter` works out each stage from the CAD's own volumes
and areas. Full power is 20 W, all seven dies on. The thermistor on the LED's
board tells the firmware when to turn the power down.

| Stage | Full power from cold | Then, indefinitely | Turns down at |
|---|---|---|---|
| All printed | **20 seconds** | **1.9 W** | 85 °C (ASA) |
| Aluminium plate and cap | **about 90 seconds** | **1.7 W** | 65 °C (PETG shell) |
| Plus an aluminium wall | **5.3 minutes** | **7 W** | 65 °C (PETG shell) |

At every stage the LED's junction stays under its 125 °C limit at the
turn-down point. The printed prototype is the tightest, at 123 °C, so 85 °C is
the LED's limit there as much as the plastic's.

So the prototype gives about two watts continuously and full power for a
count of twenty. Two watts from this LED is a soft glow on a wall in a dark
room, not a beam. The discs alone buy time rather than watts: they last longer
at full power, but the PETG shell makes them turn down cooler than the
all-ASA prototype does. The wall gives minutes plus a third of full power for
good. All of these
are estimates until a thermistor log replaces them. The film coefficients and
joint conductances are textbook figures, marked as estimates in the code.

In the metal stages, the heat runs from the board into the cap, the plate, and
the wall. It crosses to the wall through the four posts and through a strip of
soft thermal gap pad wrapped round the plate's edge, filling the 0.3 mm gap. The
pad is too soft to locate anything, so fasteners still only fasten.

**To push further, once the wall is metal:**

1. **A finned aluminium stand.** The puck sits in it, the stand carries the
   heat, and full power has no time limit. The stand is furniture, not part of
   the puck's form, so the symmetry holds.
2. **The shared shell in ASA as well.** The turn-down point can then rise to
   85 °C, which nearly doubles the minutes at full power.
3. **An aluminium lid** adds the top face to the area that sheds heat. It is a
   change of material on a shared part, so it is asked of both pucks or of
   neither.

## Tools and stock

From Jared's own repositories, read 2026-10-08:

- `fabrication/lib/house.py` lists the printers: a Flashforge Adventurer 5M and
  a Bambu P1S/X1C. Every emitter part fits the AD5M's 220 mm bed.
- The `components` library has a Shapeoko 5 Pro, which could mill the cap's
  pocket in aluminium if dowel pins turn out fiddly.
- Neither repository records the waterjet, the cold-cut saw, or any aluminium
  sheet or tube stock yet. When the metal stages start, those go in
  `fabrication/equipment/` and `components` respectively, so the drawing can
  read the real sheet thickness and tube size.

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
  once wired. Otherwise the pocket is closed.
- **Dimensions.** The LED, board and rod sizes come from catalogue pages, not
  calipers. The LED's height, the board's thickness and which edge carries
  its pads are estimates. When the parts
  arrive, they are measured into `components` and imported, as every other part
  is.
- **The firmware**: thermistor reading and derating, and driving seven channels
  from a stored curve. None of it is written.
- **The metal stages' drawings.** The dowel-pinned waterjet plate and cap, and
  the tube wall, are described above and not drawn.
