import time
import paho.mqtt.client as paho
from cryptography.fernet import Fernet

broker = "broker.mqttdashboard.com"


def on_log(client, userdata, level, buf):
    print("log: ", buf)


def on_message(client, userdata, message):
   #time.sleep(1)
   print("receive payload ",message.payload)
   decrypted_message = cipher.decrypt(message.payload)
   print("\nreceived message =",str(decrypted_message.decode("utf-8")))


client = paho.Client("client-001")
# client.on_log = on_log

cipher_key =b'0x3kqFR-uHFZezuHSRImCHZgBz9pSrMK9Lb9IDwk4Zg='
cipher = Fernet(cipher_key)

client.on_message = on_message

print("connecting to broker ",broker)
client.connect(broker)
client.loop_start()
print("subscribing ")
client.subscribe("trial/encrypt", qos=1)
count=0
while count <5:
    time.sleep(1)
    count+=1

client.disconnect()
client.loop_stop()
