# This file is executed on every boot (including wake-boot from deepsleep)
import network
import usocket as socket
import utime
import urequests
from machine import Pin, RTC, freq
from globales import read_json_config
import wifimgr

# Create Access Point
freq(240000000)
print(f"the frequency is {freq()}")


wlan = wifimgr.get_connection()
if wlan is None:
    print("Could not initialize the network connection.")
    while True:
        pass  # you shall not pass :D



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

#import uftpd
