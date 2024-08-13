# This file is executed on every boot (including wake-boot from deepsleep)
import network
import usocket as socket
import utime
import urequests
from machine import Pin, RTC, freq
from cazador_del_delta import read_json_config
# Create Access Point
freq(240000000)
print(f"the frequency is {freq()}")
ap_ssid = "ESP32_AP"
ap_password = ""

#print('Access point started ESP32_AP')
def do_connect(wifi_credentials):
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(wifi_credentials['ssid'], wifi_credentials['password'])

        for num in range(20):  # Try for 30 seconds
            if not sta_if.isconnected():
                print('Waiting for connection..',num,'/20 sec')
                utime.sleep(1)

    print('network config:', sta_if.ifconfig())
    if sta_if.isconnected():
        return True
    else:
        return False

wifi_credentials=read_json_config("wifi_client.json")

##############################################################
wifi_connection_ok = False

if wifi_credentials:
    wifi_connection_ok = do_connect(wifi_credentials)

if not wifi_connection_ok or not wifi_connection_ok:
    # Create Access Point
    print(f'Starting access point..please wait')
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


import ntptime
rtc = RTC()

rtc_ram = rtc.memory()
if rtc_ram == b'':
    rtc.init((2000, 1, 1, 0, 0, 0, 0, 0))
    try:
        ntptime.settime()
        now=rtc.datetime()
        now=f"{now[0]}_{now[1]}_{now[2]}_{now[3]}_{now[4]}_{now[5]}_{now[6]}"
        rtc.memory(now)
    except:
        print("Failed to sync date/time")
rtc_ram = rtc.memory()
print(f"first byte of RTC ram is: {rtc_ram}")


import utelnetserver
utelnetserver.start()
#import uftpd
