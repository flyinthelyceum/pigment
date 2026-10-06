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

Plug into the port marked **COM** and run, from the repo root:

```sh
firmware/circuitpython/flash.sh
```

It reads the chip's flash and PSRAM with esptool and picks the matching
CircuitPython build. It flashes the board and tells you to move the cable to the
port marked **USB** (the port the puck's opening is cut for). Then it copies
`boot.py` and `code.py` onto the CIRCUITPY drive, installs `adafruit_as7341` and
`adafruit_tlc59711` with circup, and asks for one press of RST, because `boot.py`
only takes effect after a reset. It ends by asking the board for `ID` and one `READ`.
`--no-flash` redoes only the files and drivers. Its tools live in `~/.venvs/esp`.

If esptool cannot reach the chip, close anything holding the port (a browser tab
counts). If it still can't, hold BOOT, tap RST, release BOOT, and run it again.

**The console is on the port marked COM.** The
ESP32-S3 runs out of USB endpoints with two serial channels and the drive at once.
CircuitPython 10.3 then boots into safe mode, even with MIDI and HID off. So
`boot.py` turns the USB console off, and the REPL and tracebacks are on the port
marked **COM**, at 115200.

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

If it says the hardware was not found, the console on the port marked COM, at
115200, prints the exact error from the board.

## What it does not do

No maths, no session files, no averaging, no saturation check: all of that is
`spectra.capture`, tested on the computer. The board's own RGB LED is switched off at
start; its red power LED is not switchable, so cover it with black tape before any
dark reading.
