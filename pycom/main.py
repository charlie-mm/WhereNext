# main.py - Main device loop
# Imports
import pycom
import os
import time
import machine
import ubinascii
import uhashlib
import comms
import display
from network import Bluetooth, WLAN
from mqtt import MQTTClient
import config

# Initialise variables
scanning = 0
new_devices = []
visitors = []

# WiFi setup
wlan = WLAN(mode=WLAN.STA)
wlan.connect(ssid=config.WIFI_SSID, auth=(WLAN.WPA2, config.WIFI_PASS))
while not wlan.isconnected():
    machine.idle()
print("WiFi connected succesfully")
print(wlan.ifconfig())

# BLE event handler
# Adds all newly found BLE devices to list
def ble_add_device(bt_o):
    global visitors, new_devices
    adv = bt.get_adv()
    if adv:
        mac_hash = ubinascii.hexlify(uhashlib.sha256(adv.mac).digest())
        mac_hash = mac_hash.decode("utf-8")
        if mac_hash not in visitors and mac_hash not in new_devices:
            new_devices.append(mac_hash)

# Stops background scans and sends visitors update to server
def ble_disable_background_scan(t):
    global scanning, new_devices, visitors
    print("Running ble_disable_background_scan()")
    if scanning == 1:
        bt.stop_scan()
        scanning = 0
        if new_devices:
            visitors = comms.update_visitors(client, new_devices, visitors)
            new_devices = []
    else:
        print("No users to upload")

# Get ID of closest device
def ble_get_closest(scan_time):
    global scanning
    print("Running ble_get_closest()")

    # Disable background scanning if enabled
    if scanning == 1:
        ble_disable_background_scan(1)

    max_strength = 100
    max_device  = '0'
    # Attempt 3 times max
    for i in range(3):
        bt.start_scan(scan_time)
        while bt.isscanning():
            adv = bt.get_adv()
            if adv:
                ble_strength = abs(adv.rssi)
                if ble_strength < max_strength:
                    max_strength = ble_strength
                    max_device = ubinascii.hexlify(uhashlib.sha256(adv.mac).digest())
                    max_device = max_device.decode("utf-8")

        # If device found, break from for loop
        if max_device != '0':
            break

    # If no device found after 3 attempts
    if max_device == '0':
        # SHOW ERROR ON DISPLAY EXPLAINING BLE DEVICE REQUIRED TO USE
        print("Error finding nearby device")
    return max_device

# BLE Setup
bt = Bluetooth()
bt.callback(trigger=Bluetooth.NEW_ADV_EVENT, handler=ble_add_device)
print("BLE Setup")

# Communications setup
client = MQTTClient("Pycom No." + str(config.DEVICE_ID), config.MQTT_BROKER,user=config.MQTT_USER, password=config.MQTT_PASS, port=1883)
client.set_callback(comms.mqtt_cb)

# Demo variables
p_active = 0.5

# Main loop
while True:
    print("Running...")
    chance = os.urandom(1)[0] / 255

    # 50% chance of user, system enters active mode
    if chance <= p_active:
        print("ACTIVE MODE - Identifying user")
        # Scan nearby users for 5 seconds
        closest_id = ble_get_closest(5)
        # Read user inputs from display
        data = display.get_inputs(closest_id)
        # Get reommendations from the server
        comms.get_recommendation(client, data)

    # 50% chance of no user, system enters standby mode
    else:
        print("STANDBY MODE - Beginning background scanning")
        # Perform a 30 second background scan
        bt.start_scan(-1)
        scanning = 1
        # Transmit users identified once timer ends
        t = machine.Timer.Alarm(ble_disable_background_scan, 30.0)
        while scanning == 1:
            pass
    
    # Sleep for 2 minutes after loop ends
    print("Sleeping...")
    time.sleep(120)