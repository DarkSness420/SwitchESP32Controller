# SwitchESP32Controller

This project is a controller for the Nintendo Switch based on the ESP32 platform.

## Description

This repository is based on work from [UARTSwitchCon](https://github.com/nullstalgia/UARTSwitchCon), [BlueCubeMod](https://github.com/NathanReeves/BlueCubeMod) by Nathan Reeves, and [OpenSwitchPad](https://github.com/agustincampeny/OpenSwitchPad) by Agustin Campeny, and has been altered to allow writing text to an OLED screen and to send controller inputs using just Python functions.

The OLED screen functionality uses the [esp-idf-ssd1306](https://github.com/nopnop2002/esp-idf-ssd1306) library by nopnop2002.

**Note:** In the UARTSwitchCon `protocol.md`, the MSB and LSB byte ordenering are swapped and should be reversed.

## Example Usage

```python
# Press buttons with default press duration (0.3 seconds)
pressButton(Input.B)
time.sleep(1)
pressButton(Input.B)
time.sleep(1)
pressButton(Input.HOME)
time.sleep(1)
pressButton(Input.DPAD_R)
time.sleep(1)
pressButton(Input.DPAD_R)
time.sleep(1)
pressButton(Input.DPAD_D)

# Press a button with a custom press duration of 1 second
pressButton(Input.B, howLongPressed=1.0)

# Write text to OLED screen
writeToOled(ser, "hello")
