import dht
import machine
import network
import utime as time
import urequests as requests

import config


def _device_id():
    import binascii

    return binascii.hexlify(machine.unique_id()).decode("utf-8")


DEVICE_ID = _device_id()
REQUEST_HEADERS = {
    "content-type": "application/json",
    "snow-device-mac": DEVICE_ID,
}


def wifi_connect():
    """Connect to the configured Wi-Fi network."""
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print("connecting to network...")
        sta_if.active(True)
        sta_if.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
        while not sta_if.isconnected():
            time.sleep(1)
    print("network config:", sta_if.ifconfig())


def get_current_time():
    """Obtain the current Unix time."""
    response = requests.get("http://worldtimeapi.org/api/timezone/Etc/UTC")
    if response.status_code != 200:
        raise RuntimeError("Cannot get current time!")
    return response.json()["unixtime"]


def get_measurement():
    """Obtains the current sensor measurement and timestamps it"""
    d = dht.DHT11(machine.Pin(config.DHT11_PIN))
    d.measure()
    temperature_c = d.temperature()
    temperature_f = temperature_c * 9 / 5 + 32
    return {
        "timestamp": get_current_time(),
        "temperature": {
            "celsius": temperature_c,
            "fahrenheit": temperature_f,
        },
        "humidity": d.humidity(),
    }


def prime_measurement_sensor():
    try:
        _ = get_measurement()
    except:
        pass
    finally:
        time.sleep(1)


def send_measurement(measurement: dict):
    payload = {
        "device_id": DEVICE_ID,
        "measurement": measurement,
    }
    response = requests.post(config.WEBHOOK_URL, headers=REQUEST_HEADERS, json=payload)

    if response.status_code >= 400:
        raise RuntimeError("Cannot send measurement")


def show_error():
    """Blink the ESP8266 LED a few times to indicate that an error has
    occurred.
    """
    led = machine.Pin(config.LED_PIN_0, machine.Pin.OUT)
    for i in range(5):
        time.sleep(0.5)
        led.on()
        time.sleep(0.5)
        led.off()
    led.on()


def deep_sleep():
    """Put the ESP8266 board into deep sleep mode for the configured length
    of time.
    At the end of the deep sleep period the board will reboot.
    """
    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
    rtc.alarm(rtc.ALARM0, config.INTERVAL * 1000)
    machine.deepsleep()


def run():
    import sys

    try:
        wifi_connect()

        prime_measurement_sensor()
        measurement = get_measurement()
        print(
            "[{}] TempC = {}C, TempF = {}F, Humidity = {}%".format(
                measurement["timestamp"],
                measurement["temperature"]["celsius"],
                measurement["temperature"]["fahrenheit"],
                measurement["humidity"],
            )
        )

        send_measurement(measurement)
    except Exception as ex:
        sys.print_exception(ex)
        show_error()

    if config.DEPLOYED:
        deep_sleep()


run()
