import sys
import time
import dht
import machine
import urequests

import config


def show_error(power_pin):
    led1 = machine.Pin(config.LED_PIN_1, machine.Pin.OUT)
    led2 = machine.Pin(config.LED_PIN_2, machine.Pin.OUT)
    for _ in range(5):
        power_pin.off()
        led1.on()
        led2.off()
        time.sleep(0.5)
        power_pin.on()
        led1.off()
        led2.on()
        time.sleep(0.5)
    led1.on()
    led2.on()


def get_temperature_and_humidity():
    time.sleep(1)
    dht11 = dht.DHT11(machine.Pin(config.DHT11_PIN))
    dht11.measure()
    temperature = dht11.temperature()
    if config.FAHRENHEIT:
        temperature = temperature * 9 / 5 + 32
    return temperature, dht11.humidity()


def log_data(temperature, humidity):
    print("Invoking log webhook")
    response = urequests.post(
        config.WEBHOOK_URL,
        headers={
            "content-type": "application/json",
            "snow-device-mac": machine.unique_id(),
        },
        json={"temperature": temperature, "humidity": humidity},
    )

    if response.status_code < 400:
        print("Webhook invoked")
    else:
        print("Webhook failed")
        raise RuntimeError("Webhook failed")


def run():
    import wlan
    import ota

    power_pin = machine.Pin(config.LED_PIN_0, machine.Pin.OUT)
    power_pin.on()

    # Warm up the sensor
    try:
        get_temperature_and_humidity()
    except Exception as _:
        pass

    while True:
        try:
            wlan.connect_wlan(config.WIFI_SSID, config.WIFI_PASSWORD)
            ota.check_firmware()

            temperature, humidity = get_temperature_and_humidity()
            print(
                "Temperature = {temperature}, Humidity = {humidity}".format(
                    temperature=temperature, humidity=humidity
                )
            )
            log_data(temperature, humidity)
        except Exception as exc:
            sys.print_exception(exc)
            show_error(power_pin)
            break
        else:
            print(
                "Going into sleep for {seconds} seconds...".format(
                    seconds=config.LOG_INTERVAL
                )
            )
            time.sleep(config.LOG_INTERVAL)


run()