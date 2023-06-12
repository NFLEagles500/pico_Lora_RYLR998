#This script was updated for the RYLR998, using the original
#post and script for the RYLR896 provided by the poster below:
    # More details can be found in TechToTinker.blogspot.com 
    # George Bantique | tech.to.tinker@gmail.com

from machine import Pin, UART
from time import sleep_ms

class RYLR998:
    def __init__(self, port_num=0, tx_pin='', rx_pin=''):
        if tx_pin=='' and rx_pin=='':
            self._uart = UART(port_num, baudrate=115200)
            print(self._uart)
        else:
            uart0tx = [0,12,16]
            if tx_pin in uart0tx:
                self._uart = UART(0, baudrate=115200, tx=Pin(tx_pin), rx=Pin(rx_pin))
            else:
                self._uart = UART(1, baudrate=115200, tx=Pin(tx_pin), rx=Pin(rx_pin))
                
    def cmd(self, lora_cmd):
        self._uart.write('{}\r\n'.format(lora_cmd))
        while(self._uart.any()==0):
            pass
        reply = self._uart.readline()
        #print(reply.decode().strip('rn'))
    
    def test(self):
        self._uart.write('AT\r\n') #was 'ATrn'
        while(self._uart.any()==0):
            pass
        reply = self._uart.readline()
        #print(reply.decode().strip('rn'))

    def set_addr(self, addr):
        self._uart.write('AT+ADDRESS={}\r\n'.format(addr))
        while(self._uart.any()==0):
            pass
        reply = self._uart.readline()
        print('Address set to: {}'.format(addr))


    def send_msg(self, addr, msg):
        self._uart.write('AT+SEND={},{},{}\r\n'.format(addr,len(msg),msg))
        while(self._uart.any()==0):
            pass
        reply = self._uart.readline()
        #print(reply.decode().strip('rn'))
        
    def read_msg(self):
        if self._uart.any()==0:
            print('Nothing to show.')
        else:
            msg = ''
            while(self._uart.any()):
                msg = msg + self._uart.read(self._uart.any()).decode()
            print(msg)
            #print(msg.strip('rn'))
    
lora = RYLR998(tx_pin=12,rx_pin=13) # Sets the UART port to be used. Defaults to UART0 with tx Pin 0 and
                #rx Pin 1.  For UART1, add port_num=1 in the () which defaults to tx Pin 4
                #and rx Pin 5.  Optionally, you can assign the variables 'tx_pin' and 'rx_pin'
                # with the GPIO values you want.  Example: RYLR998(tx_pin=12,rx_pin=13)
sleep_ms(100)
lora.set_addr(1)  # Sets the LoRa address
