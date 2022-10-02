import machine


def check_firmware():
    print("Checking firmware for updates")
    import senko

    OTA = senko.Senko(
        user="jyksnw",
        repo="pyIoT",
        working_dir="firmware",
        files=["ota.py", "wlan.py", "boot.py", "main.py"],
    )

    if OTA.update():
        print("Updated to the latest version! Rebooting...")
        machine.reset()
