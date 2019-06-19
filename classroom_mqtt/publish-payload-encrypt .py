import time
import paho.mqtt.client as paho
from cryptography.fernet import Fernet


broker="broker.mqttdashboard.com"


def on_log(client, userdata, level, buf):
    print("log: ", buf)



client= paho.Client("client-pub")
client.on_log = on_log

#cipher_key = Fernet.generate_key()
cipher_key = b'0x3kqFR-uHFZezuHSRImCHZgBz9pSrMK9Lb9IDwk4Zg='
cipher = Fernet(cipher_key)
message = b'Hello'

encrypted_message = cipher.encrypt(message)
out_message = encrypted_message.decode()# turn it into a string to send

print("connecting to broker ", broker)
client.connect(broker)
client.loop_start()
print("publishing encrypted message ", encrypted_message)

client.publish("trial/encrypt", out_message, qos=1, retain=True)
time.sleep(4)
client.disconnect()
client.loop_stop()
