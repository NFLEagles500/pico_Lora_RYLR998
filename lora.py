#GT-U7 GPS Module guide: https://microcontrollerslab.com/neo-6m-gps-module-raspberry-pi-pico-micropython/
#About Device:  https://reyax.com/products/RYLR998
#AT Commands for Device:  https://reyax.com//upload/products_download/download_file/LoRa_AT_Command_RYLR998_RYLR498_EN.pdf
#This script was updated for the RYLR998, with a Raspberry Pico, using
#the original post and script for the RYLR896 provided by the poster below:
    # More details can be found in TechToTinker.blogspot.com 
    # George Bantique | tech.to.tinker@gmail.com

from machine import Pin, UART
from time import sleep_ms, sleep
import secrets

#You'll need to set a unique client address for each lora device you run this on.  Set it below
clientAddr = 

led = Pin(25, Pin.OUT)

baud = 115200
class RYLR998:
    def __init__(self, port_num=0, tx_pin='', rx_pin=''):
        if tx_pin=='' and rx_pin=='':
            self._uart = UART(port_num, baudrate=baud)
            print(self._uart)
        else:
            uart0tx = [0,12,16]
            if tx_pin in uart0tx:
                self._uart = UART(0, baudrate=baud, tx=Pin(tx_pin), rx=Pin(rx_pin))
            else:
                self._uart = UART(1, baudrate=baud, tx=Pin(tx_pin), rx=Pin(rx_pin))
                
    def cmd(self, lora_cmd, retrn=False):
        print(f"retrn value is {retrn}")
        self._uart.write('{}\r\n'.format(lora_cmd))
        sleep(2)
        while(self._uart.any()==0):
            pass
        reply = self._uart.read()
        sleep(0.5)
        print(reply.decode().strip('\r\n'))
        if retrn:
            return reply.decode().strip('\r\n')
            
    def test(self):
        self._uart.write('AT\r\n') #was 'ATrn'
        while(self._uart.any()==0):
            pass
        reply = self._uart.readline()
        print(reply.decode())#.strip('rn'))

    def set_addr(self, addr):
        self._uart.write('AT+ADDRESS={}\r\n'.format(addr))
        while(self._uart.any()==0):
            pass
        reply = self._uart.readline()
        print('Address set to: {}'.format(addr))
        
    def set_pswd(self, cpin):
        self._uart.write('AT+CPIN={}\r\n'.format(cpin))
        while(self._uart.any()==0):
            pass
        reply = self._uart.readline()
        print(reply.decode("utf-8"))

    def set_networkid(self, netId):
        self._uart.write('AT+NETWORKID={}\r\n'.format(netId))
        while(self._uart.any()==0):
            pass
        reply = self._uart.readline()
        print(reply.decode())

    def send_msg(self, addr, msg): #max message size: 240 bytes
        self._uart.write('AT+SEND={},{},{}\r\n'.format(addr,len(msg),msg))
        #while(self._uart.any()==0):
        #    pass
        #reply = self._uart.readline()
        #print(f"send_msg: {reply.decode().strip('\r\n')}")

    def reset(self):
        self._uart.write('AT+RESET\r\n')
        #Need to get +RESET AND +READY before proceeding
        while(self._uart.any()<= 15):
            pass
        print(self._uart.read().decode().strip('\r\n'))

    def read_msg(self):
        if self._uart.any()==0:
            print('Nothing to show.')
        else:
            msg = ''
            while(self._uart.any()):
                msg = msg + self._uart.read(self._uart.any()).decode()
            #print(msg.strip('\r\n'))
            return msg.strip('\r\n')

#Reset the Lora module
#lora = RYLR998(tx_pin=12,rx_pin=13)
#lora.cmd('AT+RESET')
#sleep(3)

lora = RYLR998(tx_pin=12,rx_pin=13) # Sets the UART port to be used. Defaults to UART0 with tx Pin 0 and
                #rx Pin 1.  For UART1, add port_num=1 in the () which defaults to tx Pin 4
                #and rx Pin 5.  Optionally, you can assign the variables 'tx_pin' and 'rx_pin'
                # with the GPIO values you want.  Example: RYLR998(tx_pin=12,rx_pin=13)
sleep(2)
lora.cmd('AT+PARAMETER=8,7,1,12')
sleep(2)

lora.set_addr(clientAddr)  # Sets the LoRa address
sleep(2)
#Optionally create a NetworkId for your group of transceivers
lora.set_networkid(secrets.lora_nid)
sleep(2)
chkNetId = lora.cmd('AT+NETWORKID?',retrn=True)
print(f"Current Network Id: {chkNetId.split('=')[1]}")
#Optionally create a 8 char password for simple encryption (chars 0-9 and A-F only), don't lose power on either side if you set password
#this has been VERY unreliable.
#lora.set_pswd(secrets.lora_pswd)

#Below are the two loops to choose from.  Either set up to read messages, or setup to send messages

#Standby to read msg's as they come in
'''
while True:
    test = lora.read_msg()
    if type(test) == list:
        for item in test:
            if 'RCV=' in item:
                print(item.split(',')[2])
                #Optionally reply to sender
                lora.send_msg(item.split(',')[0].replace('RCV=',''),'Yep')
    sleep(1)

#Send msg's and check for replies
led.toggle()
iter = 1
while True:
    msgToSend = f'Sending message number {iter}'
    lora.send_msg(2,msgToSend)
    iter += 1
    sleep(1)
    test = lora.read_msg()
    if '+RCV=' in test:
        print(test)
        #led.toggle()

    else:
        print('no reply')
    sleep(0.5)'''


