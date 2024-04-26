# This file is executed on every boot (including wake-boot from deepsleep)
import network
import usocket as socket
import utime
import urequests
from machine import Pin
from globales import read_json_config
# Create Access Point
ap_ssid = "ESP32_AP"
ap_password = ""
utime.sleep(1)
#ap = network.WLAN(network.AP_IF)
utime.sleep(1)
#ap.active(True)
utime.sleep(1)
#ap.config(essid=ap_ssid, password=ap_password)
utime.sleep(1)
#print('Access point started ESP32_AP')
def do_connect(wifi_credentials):
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(wifi_credentials['ssid'], wifi_credentials['password'])
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())
    
wifi_credentials=read_json_config("wifi_client.json")
if wifi_credentials:
    do_connect(wifi_credentials)

else:
    # Create Access Point
    ap_ssid = "Cazador"
    ap_password = ""
    #utime.sleep(1)
    ap = network.WLAN(network.AP_IF)
    #utime.sleep(1)
    ap.active(True)
    #utime.sleep(1)
    ap.config(essid=ap_ssid, password=ap_password)
    #utime.sleep(1)
    print(f'Access point started: SSID = {ap_ssid}, password = {ap_password}')
    print('network config:', ap.ifconfig())

#import uftpd
