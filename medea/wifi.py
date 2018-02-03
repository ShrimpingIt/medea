def connect(ssid, auth, timeout=16000):
    from network import WLAN, STA_IF, AP_IF
    global uplink
    uplink = WLAN(STA_IF)
    uplink.active(True)
    uplink.connect(ssid, auth)
    started= ticks_ms()
    while True:
        if uplink.isconnected():
            return True
        else:
            if ticks_diff(ticks_ms(), started) < timeout:
                sleep_ms(100)
                continue
            else:
                return False