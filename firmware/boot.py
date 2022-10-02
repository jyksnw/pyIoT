import gc
import machine
import upip


def main():
    """Main function. Runs after board boot, before main.py
    Connects to Wi-Fi and checks for latest OTA version.
    """

    gc.collect()
    gc.enable()

    import wlan

    wlan.connect_wlan()

    import ota

    ota.check_firmware()


if __name__ == "__main__":
    main()
