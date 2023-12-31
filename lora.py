#GT-U7 GPS Module guide: https://microcontrollerslab.com/neo-6m-gps-module-raspberry-pi-pico-micropython/
#About Device:  https://reyax.com/products/RYLR998
#AT Commands for Device:  https://reyax.com//upload/products_download/download_file/LoRa_AT_Command_RYLR998_RYLR498_EN.pdf
#This script was updated for the RYLR998, with a Raspberry Pico, using
#the original post and script for the RYLR896 provided by the poster below:
    # More details can be found in TechToTinker.blogspot.com 
    # George Bantique | tech.to.tinker@gmail.com


from time import sleep_ms, sleep
import secrets

clientAddr = int(1304) #Each client on your Lora network must have a unique address.
#Set the following if you plan to send messages to another client.
#Note that if you set the number 0, anything you send is broadcast to all members.
recieverAddr = int()

#optionally you can change parameters.  By default it chooses 9,7,1,12.
# 8,7,1,12 works for my current setup
parameters = '8,7,1,12'


#Check for Pico or Pico W to set on board led pin (pico=25,picow='LED')
from machine import Pin, UART
import os
devCheck = os.uname() #This is a tuple with key/value pairs.  machine has the string we want to compare
if 'Pico W' in devCheck.machine:
    led = Pin('LED', Pin.OUT)
elif 'Pico' in devCheck.machine:
    led = Pin(25, Pin.OUT)
else:
    print("Script written for Raspberry Pico devices.  Can't determine your onboard LED pin.")

#LED off while initializing Lora
led.value(0)
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
        while True:
            try:
                self._uart.write('{}\r\n'.format(lora_cmd))
                while(self._uart.any()==0):
                    pass
                sleep(2)
                reply = self._uart.read()
                sleep(0.2)
                if retrn:
                    return reply.decode().strip('\r\n')
                print(reply.decode().strip('\r\n'))
                break
            except UnicodeError:
                pass
            
    def test(self,retrn=False):
        self._uart.write('AT\r\n') #was 'ATrn'
        while(self._uart.any()<=2):
            pass
        sleep(0.5)
        reply = self._uart.readline()
        if retrn:
            return reply.decode()
        print(reply.decode())#.strip('rn'))

    def set_addr(self, addr, retrn=False):
        self._uart.write('AT+ADDRESS={}\r\n'.format(addr))
        if retrn:
            while(self._uart.any()<=2):
                pass
            reply = self._uart.read()
            sleep(0.5)
            return reply.decode().strip('\r\n')
        
    def set_pswd(self, cpin, retrn=False):
        self._uart.write('AT+CPIN={}\r\n'.format(cpin))
        if retrn:
            while(self._uart.any()<=2):
                pass
            reply = self._uart.read()
            sleep(0.5)
            return reply.decode().strip('\r\n')

    def set_networkid(self, netId, retrn=False):
        self._uart.write('AT+NETWORKID={}\r\n'.format(netId))
        if retrn:
            while(self._uart.any()<=2):
                pass
            reply = self._uart.read()
            sleep(0.5)
            return reply.decode().strip('\r\n')

    def send_msg(self, addr, msg, retrn=False): #max message size: 240 bytes
        #print(f"Attempting to send {addr} this message: {msg}")
        self._uart.write('AT+SEND={},{},{}\r\n'.format(addr,len(msg),msg))
        #If you want the response
        if retrn:
            while(self._uart.any()<=2):
                pass
            reply = self._uart.readline()
            sleep(0.2)
            try:
                return reply.decode().strip('\r\n')
            except UnicodeError:
                return 'UnicodeError'

    def read_msg(self):
        if self._uart.any()==0:
            return 'Nothing to show.'
        else:
            msg = ''
            while(self._uart.any()):
                try:
                    msg = msg + self._uart.read(self._uart.any()).decode()
                except UnicodeError:
                    pass
            return msg.strip('\r\n')


lora = RYLR998(tx_pin=12,rx_pin=13) # Sets the UART port to be used. Defaults to UART0 with tx Pin 0 and
                #rx Pin 1.  For UART1, add port_num=1 in the () which defaults to tx Pin 4
                #and rx Pin 5.  Optionally, you can assign the variables 'tx_pin' and 'rx_pin'
                # with the GPIO values you want.  Example: RYLR998(tx_pin=12,rx_pin=13)
sleep(2)
def initializeLoraModule():
    #Initialize device by first doing a factory reset
    lora.cmd('AT+FACTORY')
    sleep(0.5)
    #Reset the module
    lora.cmd('AT+RESET')
    sleep(0.5)
    #Set parameters
    lora.cmd(f'AT+PARAMETER={parameters}')
    sleep(0.5)
    #Optionally create a NetworkId for your group of transceivers
    if hasattr(secrets, 'lora_nid'):
        lora.set_networkid(secrets.lora_nid)
        sleep(0.2)
    #Optionally create a 8 char password for simple encryption (chars 0-9 and A-F only), don't lose power on either side if you set password
    if hasattr(secrets, 'lora_pswd'):
        lora.set_pswd(secrets.lora_pswd)
        sleep(0.2)
    #Set unique client address
    lora.set_addr(clientAddr) 
    sleep(0.2)

loraModuleReset = False
moduleAddr = lora.cmd('AT+ADDRESS?',retrn=True).split('=')[1]
moduleParams = lora.cmd('AT+PARAMETER?',retrn=True).split('=')[1]
if str(clientAddr) not in str(moduleAddr):
    print(f"{moduleAddr} not {clientAddr}")
    loraModuleReset = True
if hasattr(secrets, 'lora_nid'):
    moduleNetId = lora.cmd('AT+NETWORKID?',retrn=True).split('=')[1]
    if str(secrets.lora_nid) not in str(moduleNetId):
        print(f"{moduleNetId} not {secrets.lora_nid}")
        loraModuleReset = True
if hasattr(secrets, 'lora_pswd'):
    modulePswd = lora.cmd('AT+CPIN?',retrn=True).split('=')[1]
    if str(secrets.lora_pswd) not in str(modulePswd):
        print(f"{modulePswd} not {secrets.lora_pswd}")
        loraModuleReset = True

if str(parameters) not in str(moduleParams):
    print(f"{moduleParams} not {parameters}")
    loraModuleReset = True

if loraModuleReset:
    initializeLoraModule()

#If a console is connected, lets return all the lora attributes for quick debugging
print(f"ClientId: {lora.cmd('AT+ADDRESS?',retrn=True).split('=')[1]}")
print(f"Network Id: {lora.cmd('AT+NETWORKID?',retrn=True).split('=')[1]}")
print(f"Password: {lora.cmd('AT+CPIN?',retrn=True).split('=')[1]}")


#Below are the two loops to choose from.  Either set up to read messages, or setup to send messages

#Standby to read msg's as they come in
led.value(1) #In the case of reading messages, I just power on the onboard LED to let me
             #know the module is initiallized and running through the loop
while True:
    test = lora.read_msg()
    print(test)
    if '+RCV' in test:
        test = test.split(',')
        clientId = test[0].split('=')[1]
        messNum = test[2].split(' ')[3]
        lora.send_msg(clientId,f"{messNum} Yep")
    sleep(1)
'''
#Send msg's and check for replies
led.toggle()
iter = 1
while True:
    msgToSend = f'Sending message number {iter}'
    lora.send_msg(recieverAddr,msgToSend)
    iter += 1
    sleep(1)
    test = lora.read_msg()
    if '+RCV=' in test:
        print(test)
        #led.toggle()

    else:
        print('no reply')
    sleep(0.5)'''
