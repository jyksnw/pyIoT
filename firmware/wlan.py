import time
import network


def connect_wlan(ssid, password):
    """Connects build-in WLAN interface to the network.
    Args:
        ssid: Service name of Wi-Fi network.
        password: Password for that Wi-Fi network.
    Returns:
        True for success, Exception otherwise.
    """
    import config

    sta_if = network.WLAN(network.STA_IF)
    ap_if = network.WLAN(network.AP_IF)
    sta_if.active(True)
    ap_if.active(False)

    if not sta_if.isconnected():
        print("Connecting to WLAN ({})...".format(ssid))
        sta_if.active(True)
        sta_if.connect(ssid, password)
        while not sta_if.isconnected():
            time.sleep(1)
            status = sta_if.status()
            if status not in [network.STAT_CONNECTING, network.STAT_GOT_IP]:
                print("Failed to connecto to WiFi. ErrNo:", status)
                raise RuntimeError("WLAN Connection Failed. ErrNo: " + str(status))
            else:
                pass

    return True
