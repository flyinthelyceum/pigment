# First build

The order to put the first unit together in, from parts on the shelf to the first
Stage 1a number. Written 2026-10-04, the day Jared reported every part in hand.
Each step says why it comes where it does; the order is the point.

The short version: print the bore coupon, bring the electronics up on the Pi with
no head at all, print the head once the coupon has picked its bore, then run the
dark test, the white and the ten-read repeat. The puck and the dock come after the
head has produced a number, not before.

## Where the pieces are

Nothing below is on `main` yet. Each lives on an open PR, and only Jared merges.

| PR | Carries | State for this build |
|---|---|---|
| #6 | The 2026-09-22 rulings: 5 mm LEDs, `LED_Z` 18, `LED_SEAT_D` 5.3, ColorChecker patch 19 as the 1a white, the Pi | Needed. Every LED on the shelf is 5 mm; the head on `main` has 3 mm bores. |
| #8 | `spectra.capture`: the Pi reads the AS7341 and drives the TLC59711 | Needed. Runs against fakes today (`--fake`); the real path has not touched hardware yet. |
| #7 | Stage 0 colour maths | Not needed for the first number. Needed for ΔE00. |
| #9 | The puck, and the head and detector plate to print | Carries the 5 mm rulings since 6f37bf2, all puck checks pass. **The head and plate for step 3 come from here.** |
| #10 | The dock, and the light trap | Being brought up to #9. |
| this PR | The bore coupon, this file | Print the coupon first. |

Suggested merge order: #6, then #8 (it will need #6's test fix; see #8's body),
then this one. #7 whenever.

## 1. Print the bore coupon

`python -m spectra.cad.coupon coupon.stl`, or the STL in the project files. Black
PETG, bed face down, same settings the head will use. Five 45 degree bores, 5.2 to
5.6 mm, a notch at the 5.2 end.

Press a 5 mm LED into each from the top. The right bore is the smallest one the LED
goes fully into by hand and stays in when the coupon is turned over and tapped. Set
`LED_SEAT_D` in `spectra/cad/params.py` to that bore's nominal size.

**Done 2026-10-05: 5.2 mm grips.** Jared printed the coupon and the 5.2 bore held.
5.2 is the smallest bore on the coupon, so nothing tighter was tried; it grips, so
it is the value. The case thread set `LED_SEAT_D` to 5.2 on #9 and regenerated
`head.stl` and `puck_plate.stl`. The light trap (`light-trap.stl`, a 14 x 14 x 30 mm
column) was printed alongside it and is ready for step 4.

Why first: the head is the long print and its eight bores are the one feature that
cannot be fixed after. A loose bore lets an LED tilt off 45 degrees; a tight one
cracks the wall.

## 2. Bring the electronics up on the Pi, with no head

The head is not needed to prove the wiring, and finding a bad solder joint is
easier with everything on the bench in the open.

Pin by pin, Pi header numbers. This supersedes the wiring lines in #8's README in
one place: **the driver's VCC pin stays unconnected.** Adafruit's own wiring guide
for 3.3 V logic is "keep VCC disconnected and connect V+ to 4-17V"; the chip then
runs from its on-chip 3.3 V regulator, and the Pi's 3.3 V clock and data are full
logic levels to it. #8 says VCC to 5 V, which is Adafruit's option for 5 V logic,
not for a Pi.

| From (Pi) | Pin | To |
|---|---|---|
| 3.3 V | 1 | AS7341 VIN |
| GPIO2 SDA | 3 | AS7341 SDA |
| GPIO3 SCL | 5 | AS7341 SCL |
| GND | 9 | AS7341 GND |
| 5 V | 2 | TLC59711 V+ (chip power and LED supply; eight LEDs at 15 mA is 120 mA) |
| GND | 6 | TLC59711 GND |
| GPIO11 SCLK | 23 | TLC59711 CI (clock in) |
| GPIO10 MOSI | 19 | TLC59711 DI (data in) |
| nothing | | TLC59711 VCC |

The AS7341 also takes a STEMMA QT cable, which carries the first four rows. Enable
I2C and SPI in `raspi-config` first.

Before any LED goes near the head, prove which output is channel 0, because the
white must sit in the bore that channel lights and the board's silkscreen groups
outputs as R/G/B triples rather than numbering them:

```sh
python - <<'PY'
import board, busio, adafruit_tlc59711
d = adafruit_tlc59711.TLC59711(busio.SPI(board.SCK, MOSI=board.MOSI))
d.set_channel(0, 65535); d.show()     # only channel 0 lights
input("Enter to switch off "); d.set_channel(0, 0); d.show()
PY
```

Three more things:

- **The TLC59711 sinks.** LED anodes go to the board's V+, cathodes to the channel
  outputs. The Adafruit 1455 sets every channel to about 15 mA with an on-board
  3.3 kΩ resistor, so **no series resistors**. 5 V on V+ covers every LED in the
  set, including the 400 nm and 460 nm parts.
- **Sleeve every LED's back in black heat-shrink before it goes in the head**, not
  only the white. Ruled in `OPTICAL_HEAD.md`: the bores open into the case, and an
  unsealed LED back is a path for room light into the head.
- **The AS7341 breakout has its own LEDs**: a power LED, and a bright white one
  the chip can switch. Cover the power LED (or cut its jumper) and leave the
  white one off before any dark reading. Red team round two found the same thing
  on the ESP32.

Then, on the Pi:

```sh
i2cdetect -y 1                      # expect 39
python -m spectra.capture --fake session new /tmp/s   # the CLI works at all
python -m spectra.capture session new ~/spectra-sessions/2026-10-xx-bench
```

The real `session new` will take a dark and ask for the white. With no head, hold
the white patch near the sensor under the white LED just to see counts move and to
find a gain that does not trip the saturation stop. Nothing from this step is kept.

## 3. Print the head, plate and trap

From **#9**, not #6 or `main`. #9 carries the 5 mm rulings (since 6f37bf2) and is
the head and plate the puck uses, so they are printed once: `head.stl` and
`puck_plate.stl` in the project files' `case-concepts/puck-v1/`. **Do not print the
detector plate from #6 or `main`**: theirs is a solid disc over all eight bore
mouths, with no notches for the LED leads. The light trap is the standalone
`trap.light_trap()` on this branch (`light-trap.stl` in the project files' `build/`),
until the dock, which has a trap cup of its own, is printed.

Those STLs are drawn at `LED_SEAT_D` 5.3. If the coupon picks another bore, the
case thread regenerates the head at that value before it is sliced. Port face on the bed, black
PETG. Check `python -m spectra.cad.head` says one solid before slicing.

Seat the LEDs, white in the position channel 0 is wired to. Mount the AS7341 on the
plate and screw the plate down with the M2s into the head's inserts. Black tape
round that joint until the case exists.

## 4. The dark test, which is also the torch test

Head on the light trap, every LED off. Three dark readings: room lights off, room
lights on, then a torch held at each opening in turn (the plate joint, the LED
backs, the leads). If the counts move beyond their own read-to-read noise, there is
a leak, and it gets found now with the head in the open rather than later inside a
case. Red team round two asked for exactly this before any fix is modelled.

## 5. The white

`session new` for real: dark on the trap, then ColorChecker patch 19 on the port as
the white (ruled 2026-09-22; the PTFE tile is a 1d item). Lower the gain until the
saturation stop stays quiet. Note the gain and the settle time used; the session
records both.

## 6. The first number

Print a few flat matte black PLA chips (ruled 2026-09-22 as the first samples).
Then:

```sh
python -m spectra.capture repeat SESSION black-pla-1 --count 10
```

lifting and replacing the head between reads. That table is the Stage 1a
repeatability row, minus the ΔE00, which waits on #7 and the eight-channel fitter.

## 7. Write it down

One entry in `process/BENCH_LOG.md`: commit, gain, settle time, what the torch did,
the worst channel's spread. The next session reads nothing else about the bench.

## Not in this build

- **The puck shell and the dock.** The shell waits for the bare-board caliper
  numbers and the native USB side.
- **The ESP32.** The 2026-09-22 ruling put Stage 1a on the Pi, and nothing in this
  repo talks to the ESP32 yet. The puck is drawn around a DevKitC-1, so firmware
  that speaks the same `Sensor` and `Lamp` protocols over USB is owed before the
  puck is a working instrument. Not started.
- **The seven colour LEDs.** Wire them to channels 1 to 7 now if convenient; they
  are Stage 1b.
