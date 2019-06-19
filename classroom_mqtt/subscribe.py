import paho.mqtt.client as paho


def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))


def on_connect(client, userdata, flags, rc):
    print("CONNACK received with code %d." % (rc))


def subscribe_message(t):
    hostname = 'broker.mqttdashboard.com'
    # hostname = '10.0.33.89'

    client = paho.Client(client_id="1235", clean_session=False, userdata=None, protocol=paho.MQTTv311)
    client.connect(hostname, 1883)
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    client.on_connect = on_connect
    client.subscribe('trial/'+str(t), qos=1)

    client.loop_forever()
