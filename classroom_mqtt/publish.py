import paho.mqtt.client as paho
import time


def on_publish(client, userdata, mid):
    print("mid: " + str(mid))


def publish_message(msg,t):
    hostname = 'broker.mqttdashboard.com'
    client = paho.Client(client_id="1234", clean_session=False, userdata=None, protocol=paho.MQTTv311, )
    client.on_publish = on_publish
    client.will_set("trial/topic1", payload="bye!", qos=1, retain=False)
    client.username_pw_set("shankar", "shankar001")
    client.connect_async(hostname, 1883)
    client.loop_start()
    message = msg
    (rc, mid) = client.publish('trial/' + str(t), str(message), qos=1, retain=True)
    time.sleep(5)

    client.disconnect()
