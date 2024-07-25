import serial
import time


def send_sms(serial_port, baudrate, phone_number, message):
    ser = serial.Serial(serial_port, baudrate=baudrate, timeout=1)
    ser.write(b'AT\r')
    time.sleep(1)
    ser.write(b'AT+CMGF=1\r')  # 문자 메시지 모드 설정
    time.sleep(1)
    ser.write(f'AT+CMGS="{phone_number}"\r'.encode())
    time.sleep(1)
    ser.write(message.encode() + b'\r')
    time.sleep(1)
    ser.write(bytes([26]))  # Ctrl+Z 문자 (문자 전송 완료를 의미)
    time.sleep(3)
    print("Message sent")

