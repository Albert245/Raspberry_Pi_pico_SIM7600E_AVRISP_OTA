from machine import UART, Pin, SPI
from mfrc522 import MFRC522
import time

phone_number = '0934413429'
text_message = 'Hello World!'
rxData = bytes()
rxData = b''
rxDataISP = bytes()
rxDataISP = b''
uart0 = UART(0, baudrate=115200, tx=Pin(16), rx=Pin(17))
uart1 = UART(1, baudrate=115200, tx=Pin(4), rx=Pin(5))
led = Pin(25, Pin.OUT)
true = Pin(15, Pin.OUT)
false = Pin(14, Pin.OUT)
outTrue = Pin(13, Pin.OUT)
sck = Pin(6, Pin.OUT)
mosi = Pin(7, Pin.OUT)
miso = Pin(4, Pin.OUT)
sda = Pin(5, Pin.OUT)
rst = Pin(22, Pin.OUT)
spi = SPI(0, baudrate=100000, polarity=0, phase=0, sck=sck, mosi=mosi, miso=miso)
poweron = Pin(2, Pin.OUT)
ServerIP = "123.20.57.30"
Port = '8080'
card1 = "0x608e981b"
card2 = "0x2063c1d2"
card3 = ""
card4 = ""
card5 = ""
card6 = ""

state = 0

#  FTP
ftp_user_name = 'user'
ftp_user_password = ''
ftp_server = ''
download_file_name = ''
upload_file_name = ''


#  TCP
APN = 'CMNET'
Message = 'Hello'



def send_at(command,back,timeout):
	rxData1 = bytes()
	uart0.write(command+'\r\n')
	time.sleep(timeout)
	print('checking')
	time.sleep(1)
	while uart0.any() > 0:
		rxData1 += uart0.read(1)
	print(rxData1.decode('utf-8'))
	if rxData1 != b'':
		if back not in rxData1.decode():
			print(command + ' ERROR')
			print(command + ' back:\t' + rxData1.decode('utf-8'))
			return 0
		else:
			print(rxData1.decode('utf-8'))
			return 1
	else:
		print('command: '+command+' is not ready')
		return 0



def SendShortMessage(phone_number,text_message):
	
	print("Setting SMS mode...")
	send_at("AT+CMGF=1",'',1)
	print("Sending Short Message")
	print("AT+CMGS=\""+phone_number+"\"")
	answer = send_at("AT+CMGS=\""+phone_number+"\"",">",2)
	if 1 == answer:
		uart0.write(text_message+'\r\n')
		uart0.write(b'\x1A')
		answer = send_at('','OK',20)
		if 1 == answer:
			print('send successfully')
		else:
			print('error')
	else:
		print('error%d'%answer)



def get_gps_position():
	send_at('AT+CGPSINFO','',1)



def configureFTP(server,u_name,u_password):
	send_at('AT+CFTPPORT=21','OK',1)
	send_at('AT+CFTPMODE=1','OK',1)
	send_at('AT+CFTPTYPE=A','OK',1)
	send_at('AT+CFTPSERV='+'\"'+server+'\"','OK',1)
	send_at('AT+CFTPUN='+'\"'+u_name+'\"','OK',1)
	send_at('AT+CFTPPW='+'\"'+u_password+'\"','OK',1)

def downloadFromFTP(file_name):
	print('Download file from FTP...')
	send_at('AT+CFTPGETFILE='+'\"'+file_name+'\",0','OK',1)

def uploadToFTP(file_name):
	print('Download file from FTP...')
	send_at('AT+CFTPGETFILE='+'\"'+file_name+'\",0','OK',1)



def TCP():
	send_at('AT+CSQ','OK',1)
	send_at('AT+CREG?','+CREG: 0,1',1)
	send_at('AT+CPSI?','OK',1)
	send_at('AT+CGREG?','+CGREG: 0,1',0.5)
	send_at('AT+CGSOCKCONT=1,\"IP\",\"'+APN+'\"','OK',1)
	send_at('AT+CSOCKSETPN=1', 'OK', 1)
	send_at('AT+CIPMODE=0', 'OK', 1)
	send_at('AT+NETOPEN', '+NETOPEN: 0',5)
	send_at('AT+IPADDR', '+IPADDR:', 1)
	send_at('AT+CIPOPEN=0,\"TCP\",\"'+ServerIP+'\",'+Port,'+CIPOPEN: 0,0', 5)
	send_at('AT+CIPSEND=0,', '>', 2)#If not sure the message number,write the command like this: AT+CIPSEND=0, (end with 1A(hex))
	ser.write(Message.encode())
	if 1 == send_at(b'\x1a'.decode(),'OK',5):
		print('send message successfully!')
	send_at('AT+CIPCLOSE=0','+CIPCLOSE: 0,0',15)
	send_at('AT+NETCLOSE', '+NETCLOSE: 0', 1)



def PhoneCall(phone_number):
	print('Start phonecall session')
	send_at('ATD'+phone_number+';','OK',5)
	time.sleep(10)
	send_at('AT+CHUP','',1)
	print('phonecall disconnected')



def power_on():
	print("Sim7600X is starting: ")
	poweron.value(1)
	time.sleep(2)
	poweron.value(0)
	print("turning on... ")
	time.sleep(20)
	print("Sim7600X is ready")



def power_down():
	print("Sim7600X is shuting down: ")
	poweron.value(1)
	time.sleep(3)
	poweron.value(0)
	time.sleep(18)
	print("Good bye")
	time.sleep(3)
def RFID_check():
    rdr = MFRC522(spi, sda, rst)
    (stat, tag_type) = rdr.request(rdr.REQIDL)
    if stat == rdr.OK:
        (stat, raw_uid) = rdr.anticoll()
        if stat == rdr.OK:
            uid = ("0x%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3]))
            print(uid)
            if uid == card1:
                print('Correct Card')
                true.value(1)
                outTrue.value(1)
                time.sleep(1)
                outTrue.value(0)
                time.sleep(1)
                true.value(0)
                return 1
            else:
                print('Wrong Card!!!')
                false.value(1)
                time.sleep(2)
                false.value(0)
                return 0
    return 0
true.value(0)
false.value(0)
outTrue.value(0)
print('RFID system block ready')

while True:
	led.value(1)
	time.sleep(0.06)
	led.value(0)
	check = 0
	RFID_check()
	





