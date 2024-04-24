# This file is executed on every boot (including wake-boot from deepsleep)
import network
import usocket as socket
import utime
import urequests
from machine import Pin

# Create Access Point
ap_ssid = "ESP32_AP"
ap_password = ""
utime.sleep(1)
#ap = network.WLAN(network.AP_IF)
sta_if = network.WLAN(network.STA_IF)
utime.sleep(1)
#ap.active(True)
utime.sleep(1)
#ap.config(essid=ap_ssid, password=ap_password)
utime.sleep(1)
#print('Access point started ESP32_AP')
def do_connect():
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect('thetomsons', 'Esmeralda8933')
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())
    
do_connect()


#import uftpd
