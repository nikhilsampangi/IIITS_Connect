import time
import paho.mqtt.client as paho
import hashlib

broker = "broker.mqttdashboard.com"
topic = "data/files"
qos = 1
data_block_size = 2000
filename = "gif.mp4"
file_out = "copy-" + filename
fout = open(file_out, "wb")


def process_message(msg):
    """ This is the main receiver code
       """
    print("received ")
    global bytes_in
    if len(msg) == 200:  # is header or end
        print("found header")
        msg_in = msg.decode("utf-8")
        msg_in = msg_in.split(",,")
        print(msg_in)
        if msg_in[0] == "end":  # is it really last packet?
            in_hash_final = in_hash_md5.hexdigest()
            if in_hash_final == msg_in[2]:
                print("File copied OK -valid hash  ", in_hash_final)
                return -1
            else:
                print("Bad file receive   ", in_hash_final)
            return False
        else:
            if msg_in[0] != "header":
                in_hash_md5.update(msg)
                return True
            else:
                return False
    else:
        bytes_in = bytes_in + len(msg)
        in_hash_md5.update(msg)
        print("found data bytes= ", bytes_in)
        return True


# define callback
def on_message(client, userdata, message):
    # time.sleep(1)
    global run_flag
    # print("received message =",str(message.payload.decode("utf-8")))
    ret = process_message(message.payload)
    if ret:
        fout.write(message.payload)
    if ret == -1:
        run_flag = False  # exit receive loop
        print("complete file received")




bytes_in = 0
client = paho.Client("client-receive-001")
client.on_message = on_message
client.mid_value = None

print("connecting to broker ", broker)
client.connect(broker)

print("subscribing ")
client.subscribe(topic)
time.sleep(2)
start = time.time()
time_taken = time.time() - start
in_hash_md5 = hashlib.md5()
run_flag = True

while run_flag:
    client.loop(00.1)  # manual loop
    pass
client.disconnect()
client.loop_stop()
fout.close()
