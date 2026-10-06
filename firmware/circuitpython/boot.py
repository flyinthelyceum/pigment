"""Runs once at power-up, before code.py. Copy to the CIRCUITPY drive.

Turns on CircuitPython's second USB serial channel. The first is the REPL
console, which prints tracebacks and status lines at any moment; the commands
from `spectra.capture` and their replies need a channel nothing else writes to,
or one stray status line corrupts a reading. The host finds the data channel by
asking each port for `ID`, so it does not care which number the OS gives it.

The ESP32-S3 has too few USB endpoints for two serial channels and the
CIRCUITPY drive at once: with both channels on, CircuitPython 10.3 boots into safe
mode ("USB devices need more endpoints than are available"), even with MIDI and
HID off. So the USB port carries the data channel and the drive only, and the
console (REPL and tracebacks) moves to the port marked COM, at 115200.

Changes here take effect only after a hard reset (the RST button), not a save.
"""

import usb_cdc
import usb_hid
import usb_midi

usb_midi.disable()
usb_hid.disable()
usb_cdc.enable(console=False, data=True)
