import serial
import time
from enum import Enum, unique, IntEnum
ser = serial.Serial('COM4', baudrate=19200, timeout=1)

@unique
class Input(Enum):
    # Buttons
    MINUS   = "MINUS"
    PLUS    = "PLUS"
    L_CLK   = "L_CLK"
    R_CLK   = "R_CLK"
    HOME    = "HOME"
    CAPTURE = "CAPTURE"
    SL      = "SL"
    SR      = "SR"
    Y       = "Y"
    B       = "B"
    A       = "A"
    X       = "X"
    L       = "L"
    R       = "R"
    ZL      = "ZL"
    ZR      = "ZR"

    # Dpad directions
    DPAD_CENTER = "DPAD_CENTER"
    DPAD_U      = "DPAD_U"
    DPAD_UR     = "DPAD_UR"
    DPAD_R      = "DPAD_R"
    DPAD_DR     = "DPAD_DR"
    DPAD_D      = "DPAD_D"
    DPAD_DL     = "DPAD_DL"
    DPAD_L      = "DPAD_L"
    DPAD_UL     = "DPAD_UL"


DPAD_VALUES = {
    "DPAD_CENTER": 0x08,
    "DPAD_U":      0x00,
    "DPAD_UR":     0x01,
    "DPAD_R":      0x02,
    "DPAD_DR":     0x03,
    "DPAD_D":      0x04,
    "DPAD_DL":     0x05,
    "DPAD_L":      0x06,
    "DPAD_UL":     0x07,
}

class Buttons(IntEnum):
    MINUS   = 1 << 0
    PLUS    = 1 << 1
    L_CLK   = 1 << 2
    R_CLK   = 1 << 3
    HOME    = 1 << 4
    CAPTURE = 1 << 5
    SL      = 1 << 6
    SR      = 1 << 7

    Y  = 1 << 8
    B  = 1 << 9
    A  = 1 << 10
    X  = 1 << 11
    L  = 1 << 12
    R  = 1 << 13
    ZL = 1 << 14
    ZR = 1 << 15

def crc8_ccitt_update(crc, data):
    data = crc ^ data
    for _ in range(8):
        if data & 0x80:
            data = (data << 1) ^ 0x07
        else:
            data <<= 1
        data &= 0xFF
    return data

def chocolate_handshake(ser):
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    time.sleep(0.1)

    ser.write(b'\xFF')
    time.sleep(0.05)
    resp = ser.read(1)
    if resp != b'\xFF':
        raise RuntimeError(f"Handshake failed at step 1, received: {resp.hex() if resp else 'None'}")

    ser.write(b'\x44')
    time.sleep(0.05)
    resp = ser.read(1)
    if resp != b'\xEE':
        raise RuntimeError(f"Handshake failed at step 2, received: {resp.hex() if resp else 'None'}")

    ser.write(b'\xEE')
    time.sleep(0.05)
    resp = ser.read(1)
    if len(resp) != 1:
        raise RuntimeError("Handshake failed at step 3 (no controller type received)")
    return True

def vanilla_handshake(ser):
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    time.sleep(0.1)

    ser.write(b'\xFF')
    time.sleep(0.05)
    resp = ser.read(1)
    if resp != b'\xFF':
        raise RuntimeError(f"Handshake failed at step 1, received: {resp.hex() if resp else 'None'}")

    ser.write(b'\x33')
    time.sleep(0.05)
    resp = ser.read(1)
    if resp != b'\xCC':
        raise RuntimeError(f"Handshake failed at step 2, received: {resp.hex() if resp else 'None'}")

    ser.write(b'\xCC')
    time.sleep(0.05)
    resp = ser.read(1)
    if resp != b'\x33':
        raise RuntimeError(f"Handshake failed at step 3, received: {resp.hex() if resp else 'None'}")

    return True

def send_input_packet(ser, *inputs,
                      lx=128, ly=128, rx=128, ry=128, vendor=0x00):
    buttons = 0
    dpad = DPAD_VALUES["DPAD_CENTER"]

    for inp in inputs:
        inp_value = inp.value.upper()
        if inp_value.startswith("DPAD_") and inp_value in DPAD_VALUES:
            dpad = DPAD_VALUES[inp_value]
        else:
            if hasattr(Buttons, inp_value):
                buttons |= getattr(Buttons, inp_value)
            else:
                raise ValueError(f"Unknown input name: {inp_value}")

    buttons_lsb = buttons & 0xFF
    buttons_msb = (buttons >> 8) & 0xFF

    packet = bytearray(9)
    packet[0] = buttons_lsb
    packet[1] = buttons_msb
    packet[2] = dpad
    packet[3] = lx
    packet[4] = ly
    packet[5] = rx
    packet[6] = ry
    packet[7] = vendor

    crc = 0
    for i in range(8):
        crc = crc8_ccitt_update(crc, packet[i])
    packet[8] = crc

    ack = ser.read(1)
    if ack != b'\x90':
        pass

    ser.write(packet)


def pressButton(*inputs, howLongPressed=0.3):
    send_input_packet(ser, *inputs)
    time.sleep(howLongPressed)
    send_input_packet(ser)


# def setup():
#     try:
#         try:
#             print("Trying Chocolate handshake...")
#             chocolate_handshake(ser)
#             print("Chocolate handshake succeeded.")
#         except Exception:
#             print("Chocolate handshake failed, trying Vanilla...")
#             vanilla_handshake(ser)
#             print("Vanilla handshake succeeded.")
#     except Exception as e:
#         print(f"Handshake failed: {e}")
#         ser.close()
#         exit(1)
#     time.sleep(12)


def writeToOled(ser, text=""):
    if not text:
        text = " "
    #Dont change the prefix 1-9, bytes will be > 9 now
    #And the oled writetext function will be triggered instead of detecting it
    #As controller inputs
    final_text = '123456789' + text
    ser.write(final_text.encode('ascii'))

def setup():
    while True:
        try:
            vanilla_handshake(ser)
            print("Vanilla handshake succeeded!")
            break  # exit loop on success
        except RuntimeError as e:
            print(f"Vanilla handshake failed: {e}, retrying...")
            time.sleep(0.5)  # small delay before retrying
    time.sleep(3)


def main():
    
    setup()

    # pressButton(Input.B)
    # time.sleep(1)
    # pressButton(Input.B)
    # time.sleep(1)
    # pressButton(Input.HOME)
    # time.sleep(1)
    # pressButton(Input.DPAD_R)
    # time.sleep(1)
    # pressButton(Input.DPAD_R)
    # time.sleep(1)
    # pressButton(Input.DPAD_D)
    writeToOled(ser,"hello")

    time.sleep(5)

    ser.close()

if __name__ == "__main__":
    main()
