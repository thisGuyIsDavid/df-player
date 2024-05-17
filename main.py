import random
import time
import serial
from gpiozero import LED, Button

class DFPlayerPico():
    UART_BAUD_RATE=9600
    UART_BITS=8
    UART_PARITY=None
    UART_STOP=1

    START_BYTE = 0x7E
    VERSION_BYTE = 0xFF
    COMMAND_LENGTH = 0x06

    ACKNOWLEDGE = 0x01
    END_BYTE = 0xEF
    COMMAND_LATENCY =   500

    def __init__(self):
        self.playerBusy = Button(23)
        self.uart = serial.Serial(port='/dev/ttyS0', baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=5)

    def split(self, num):
        return num >> 8, num & 0xFF

    def send_cmd(self, command, parameter1, parameter2):
        checksum = -(self.VERSION_BYTE + self.COMMAND_LENGTH + command + self.ACKNOWLEDGE + parameter1 + parameter2)
        highByte, lowByte = self.split(checksum)
        toSend = bytes([b & 0xFF for b in [self.START_BYTE, self.VERSION_BYTE, self.COMMAND_LENGTH, command, self.ACKNOWLEDGE,parameter1, parameter2, highByte, lowByte, self.END_BYTE]])
        self.uart.write(toSend)
        time.sleep(self.COMMAND_LATENCY)
        return self.uart.read()

    def send_query(self, command, parameter_1 = 0x00, parameter_2 = 0x00):
        response = self.send_cmd(command, parameter_1, parameter_2)
        return self.convert_dfplayer_response_to_hex(response)

    @staticmethod
    def convert_dfplayer_response_to_hex(received_bytes):
        if received_bytes is None:
            return
        converted_string = received_bytes.hex()
        for i in range(int(len(converted_string) / 20)):
            single_message = converted_string[i*20: (i*20) + 20]
            single_message_array = []
            for x in range(20):
                two_characters = single_message[x*2:(x*2) + 2]
                if two_characters != '':
                    single_message_array.append(single_message[x*2:(x*2) + 2])
            return single_message_array

    def is_busy(self):
        return True
        return not self.playerBusy.value()

    #Common DFPlayer control commands
    def next_track(self):
        self.send_cmd(0x01, 0x00, 0x00)

    def prev_track(self):
        self.send_cmd(0x02, 0x00, 0x00)

    def set_volume(self, volume):
        #Volume can be between 0-30
        self.send_cmd(0x06, 0x00, volume)

    def get_volume_level(self):
        converted_response = self.send_query(0x43, 0x00, 0x00)
        if converted_response is not None:
            return converted_response[6]


    def set_eq(self, eq):
        self.send_cmd(0x07, 0x00, eq)

    def set_playback_mode(self, mode):
        #Mode can be 0-3
        #0=Repeat
        #1=Folder Repeat
        #2=Single Repeat
        #3=Random
        self.send_cmd(0x08, 0x00, mode)

    def set_playback_source(self, source):
        self.send_cmd(0x09, 0x00, source)

    def standby(self):
        self.send_cmd(0x0A, 0x00, 0x00)

    def set_normal_working(self):
        self.send_cmd(0x0B, 0x00, 0x00)

    def reset(self):
        self.send_cmd(0x0C, 0x00, 0x00)

    def resume(self):
        self.send_cmd(0x0D, 0x00, 0x00)

    def pause(self):
        self.send_cmd(0x0E, 0x00, 0x00)

    def play_track(self, folder, file):
        self.send_cmd(0x0F, folder, file)

    def play_mp3(self, filenum):
        a = (filenum >> 8) & 0xff
        b = filenum & 0xff
        return self.send_cmd(0x12, a, b)

    #Query System Parameters
    def init(self, params):
        self.send_cmd(0x3F, 0x00, params)





if __name__ == '__main__':
    serial_music_player = DFPlayerPico()
    #   serial_music_player.play_track(str(1))
