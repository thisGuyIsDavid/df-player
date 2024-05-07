import random
import time
import serial


class DFPlayer:

    def __init__(self, queue):
        self.queue = queue
        self.serial = serial.Serial(port='/dev/ttyS0', baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=5)
        self.set_up()

    def set_up(self):
        self.stop_playback()
        return
        self.stop_playback()
        time.sleep(5)
        self.set_volume()

    @staticmethod
    def convert_dfplayer_response_to_hex(received_bytes):
        converted_string = received_bytes.hex()
        for i in range(int(len(converted_string) / 20)):
            single_message = converted_string[i*20: (i*20) + 20]
            single_message_array = []
            for x in range(20):
                two_characters = single_message[x*2:(x*2) + 2]
                if two_characters != '':
                    single_message_array.append(single_message[x*2:(x*2) + 2])
            print('convert_dfplayer_response_to_hex', single_message_array)
            return single_message_array

    @staticmethod
    def generate_command(command_one, parameter_1, parameter_2, feedback=False):
        out_bytes = bytearray(10)
        out_bytes[0]=126
        out_bytes[1]=255
        out_bytes[2]=6
        out_bytes[3]=command_one
        out_bytes[4]=0
        out_bytes[5]=parameter_1
        out_bytes[6]=parameter_2
        out_bytes[9]=239
        checksum = 0
        for i in range(1,7):
            checksum=checksum+out_bytes[i]
        out_bytes[7]=(checksum>>7)-1
        out_bytes[7]=~out_bytes[7]
        out_bytes[8]=checksum-1
        out_bytes[8]=~out_bytes[8]
        return out_bytes

    def send_command(self, command_type, parameter_one, parameter_two, return_feedback=False):
        generated_command = self.generate_command(command_type, parameter_one, parameter_two, return_feedback)
        print('Sending', generated_command)
        self.serial.write(generated_command)

    def send_query(self, command_type):
        self.send_command(command_type, 0x00, 0x00, True)
        for i in range(10):
            message = self.serial.read()
            print('Message', message)
            response = self.convert_dfplayer_response_to_hex(message)
            print('Response', response)
            time.sleep(0.1)

    def stop_playback(self):
        self.send_command(22, 0, 0)

    def set_module_to_normal(self):
        self.send_command(0x0b, 0x00, 0x00, return_feedback=True)

    def start_module(self):
        self.send_command(0x0D, 0x00, 0x00)



    def set_volume(self, volume_level=15):
        print('set volume', volume_level)
        self.send_command(0x06, 0x00, int(volume_level))

    def play_track(self, track_number):
        self.send_command(0x12, 0x00, int(track_number))

    def play_blank_space(self):
        pass

    def is_playing(self):
        result = self.send_command(0x42, 0x00, 0x00)

if __name__ == '__main__':
    serial_music_player = DFPlayer(queue=None)
    #   serial_music_player.play_track(str(1))
