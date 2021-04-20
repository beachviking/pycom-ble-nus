"""
Created on Mon Apr 12 15:40:07 2021
@author: Gunnar Larsen
@license: MIT-license

This file contains a bare bone implementation of the Nordic Uart Service for BLE(NUS), running on a
Pycom device.
"""

from network import Bluetooth
from binascii import unhexlify

def unhex(s):
    return bytes(reversed(unhexlify(s.replace('-',''))))

class BLEUart:
    def __init__(self):
        self.status = {
            'connected' : False
        }

        self.rx_data = []

    def begin(self, name):
        self._ble = Bluetooth()      

        # Some apps require the service uuid to be part of the advertising packet for the device to show up
        # as Uart capable, like the Bluefruit Connect app
        self._ble.set_advertisement(name=name, service_uuid=unhex('6E400001-B5A3-F393-E0A9-E50E24DCCA9E'))
        #self._ble.set_advertisement(name=name)
        
        self._ble.callback(trigger=Bluetooth.CLIENT_CONNECTED | Bluetooth.CLIENT_DISCONNECTED, handler=self.conn_callback)
        self._ble.advertise(True)

        nus = self._ble.service(uuid=unhex('6E400001-B5A3-F393-E0A9-E50E24DCCA9E'), isprimary=True, nbr_chars=2)
        self.rx = nus.characteristic(uuid=unhex('6E400002-B5A3-F393-E0A9-E50E24DCCA9E'),
                                     #properties=Bluetooth.PROP_WRITE | Bluetooth.PROP_WRITE_NR,
                                     properties=Bluetooth.PROP_WRITE_NR,
                                     value='')
                                     
        self.tx = nus.characteristic(uuid=unhex('6E400003-B5A3-F393-E0A9-E50E24DCCA9E'),
                                     #properties=Bluetooth.PROP_READ | Bluetooth.PROP_NOTIFY,
                                     properties=Bluetooth.PROP_NOTIFY,
                                     value='')
                                     
        self.tx.callback(trigger=Bluetooth.CHAR_SUBSCRIBE_EVENT, handler=self.tx_subsc_callback)
        self.rx.callback(trigger=Bluetooth.CHAR_WRITE_EVENT, handler=self.rx_callback)

    def end(self):
        self.status['connected'] = False
        self.rx_data = []
        self._ble.disconnect_client()
        self._ble.deinit()

    def conn_callback(self, bt):
        events = bt.events()
        if  events & Bluetooth.CLIENT_CONNECTED:
            print("Client connected")
            self.status['connected'] = True
        elif events & Bluetooth.CLIENT_DISCONNECTED:
            print("Client disconnected")
            self.status['connected'] = False
            self.rx_data = []

    def rx_callback(self, chr, msg):
        data = chr.value()
        #print('BLE data received')
        strdata = str(data, 'utf-8')
        #print('> ', strdata)
        self.rx_data.append(strdata)

    def tx_subsc_callback(self, chr, msg):
        print("Client subscribed", chr.value())

    def write(self, msg):
        if self.status['connected'] == True:
            while len(msg):
                data = msg[:20]
                msg = msg[20:]
                print('BLE data send:')
                print('<', data)
                self.tx.value(data)
            
            self.tx.value('\r\n')

    def available_data(self):
        return (True if(len(self.rx_data) > 0) else False )

    def get_data(self):
        if self.available_data():
            data = self.rx_data[0]
            del self.rx_data[0]
            return data
        else:
            return 0