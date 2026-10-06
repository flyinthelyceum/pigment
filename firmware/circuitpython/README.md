# ESP32 firmware (CircuitPython)

The board end of Stage 1a. It drives the LEDs and reads the sensor when the computer
asks; the measurement itself is `spectra.capture` on the computer. Ruled 2026-10-06
in `docs/DECISIONS.md`.

## Wiring, with the board seen from the top

The GPIO numbers are printed beside each header pin on the DevKitC-1.

| ESP32 pin | To |
|---|---|
| 3V3 | AS7341 VIN |
| G | AS7341 GND |
| 8 | AS7341 SDA |
| 9 | AS7341 SCL |
| 5V | TLC59711 V+ (chip power and LED supply) |
| G | TLC59711 GND |
| 12 | TLC59711 CI (clock in) |
| 11 | TLC59711 DI (data in) |
| nothing | TLC59711 VCC |

The driver's VCC stays unconnected: Adafruit's wiring for 3.3 V logic is V+ at 4 to
17 V and VCC left open, so the chip runs from its own regulator and reads the ESP32's
3.3 V clock and data cleanly. The 5V pin is the USB supply when the board is powered
over USB; eight LEDs at 15 mA is 120 mA, well inside a USB port.

LEDs: long leg (anode) to the driver's V+, short leg (cathode) to a channel output.
No series resistors; the board fixes each channel at about 15 mA.

## Flashing, once

1. Read the module's variant off its label or the box (for example N8R8). Open the
   matching board page on circuitpython.org in Chrome, such as
   `circuitpython.org/board/espressif_esp32s3_devkitc_1_n8r8/`, and use **Open
   Installer**. Plug into the port marked **COM** for this step. If the installer
   cannot connect, hold BOOT, tap RST, release BOOT, and try again. Not sure of the
   variant: the `_n8` build runs on any 8 MB module.
2. Move the cable to the port marked **USB**. A drive called CIRCUITPY appears. This
   is the port the puck's opening is cut for.
3. Copy `boot.py` and `code.py` from this folder onto CIRCUITPY.
4. Install the two drivers: `pip install circup`, then
   `circup install adafruit_as7341 adafruit_tlc59711`.
5. Press RST. `boot.py` only takes effect after a reset.

## Checking it

On the computer, from this repo with `pip install -e '.[capture]'`:

```sh
python -c "from spectra.capture import serial_hw as s; S, L = s.connect('auto'); print(S.read())"
```

Ten counts printed means the cable, the firmware and the sensor all work. Then light
channel 0 only, to find which output that is before any LED goes in the head:

```sh
python -c "from spectra.capture import serial_hw as s; S, L = s.connect('auto'); L.set(0, 1.0); input('Enter for off '); L.off()"
```

If it says the hardware was not found, the serial console (the other port, at 115200)
prints the exact error from the board.

## What it does not do

No maths, no session files, no averaging, no saturation check: all of that is
`spectra.capture`, tested on the computer. The board's own RGB LED is switched off at
start; its red power LED is not switchable, so cover it with black tape before any
dark reading.
