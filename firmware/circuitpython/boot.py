"""Runs once at power-up, before code.py. Copy to the CIRCUITPY drive.

Turns on CircuitPython's second USB serial channel. The first is the REPL
console, which prints tracebacks and status lines at any moment; the commands
from `spectra.capture` and their replies need a channel nothing else writes to,
or one stray status line corrupts a reading. The host finds the data channel by
asking each port for `ID`, so it does not care which number the OS gives it.

Changes here take effect only after a hard reset (the RST button), not a save.
"""

import usb_cdc

usb_cdc.enable(console=True, data=True)
