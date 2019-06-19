from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
import time
import hashlib
from cryptography.fernet import Fernet
from django.urls import reverse
import publish
import paho.mqtt.client as paho
from authentication.forms import Registration, PublishMessage, PublishFile, CreateTopic
from authentication.models import Topic, Usertype, Messages, SentFiles, SentKey


def register_all(request):
    return render(request, 'authentication/register_all.html')


def home_page(request):
    all_topics = Topic.objects.all()
    return render(request, 'authentication/home_page.html', {'topics': all_topics})


def login_user(request):
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            u = User.objects.get(username=user)
            login(request, user)
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            if 'next' in request.GET:
                return redirect(request.GET.get('next'))
            if u.usertype.is_teacher:
                return redirect('authentication:publish_message')
            elif u.usertype.is_student:
                return redirect('authentication:publish_message')

            else:
                return HttpResponse('User does not exist')

    return render(request, 'authentication/login.html', {'form': form})


@login_required
def logout_user(request):
    logout(request)


def register_student(request):
    form = Registration()
    if request.method == 'POST':
        form = Registration(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            ut = Usertype.objects.create(user=user, is_student=True)
            ut.save()

            return redirect('authentication:login_user')

    return render(request, 'authentication/register.html', {'form': form})


def register_teacher(request):
    form = Registration()
    if request.method == 'POST':
        form = Registration(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            ut = Usertype.objects.create(user=user, is_teacher=True)
            ut.save()

            return redirect('authentication:login_user')

    return render(request, 'authentication/register.html', {'form': form})


def subscribe_options(request):
    return render(request, 'authentication/subscribe_options.html')


def publish_options(request, t_id=None):
    return render(request, 'authentication/publish_options.html', {'t_id': t_id})


def publish_encrypted_message(request, key):
    cipher = Fernet(key)
    client = paho.Client(client_id="1234", clean_session=False, userdata=None, protocol=paho.MQTTv311, )
    broker = "broker.mqttdashboard.com"
    message = b'This is an encrypted message'

    encrypted_message = cipher.encrypt(message)
    out_message = encrypted_message.decode()  # turn it into a string to send

    print("connecting to broker ", broker)
    client.connect(broker)
    client.loop_start()
    print("publishing encrypted message ", encrypted_message)

    client.publish("trial/encrypted_message", out_message, qos=1, retain=True)
    time.sleep(4)
    client.disconnect()
    client.loop_stop()


def receive_key(request):
    hostname = 'broker.mqttdashboard.com'
    client = paho.Client(client_id="1235", clean_session=False, userdata=None, protocol=paho.MQTTv311)
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(hostname, 1883)
    client.subscribe("trial/encrypt", qos=1)
    client.loop_forever()


def publish_encrypt_key(request):
    cipher_key = Fernet.generate_key()
    cipher = Fernet(cipher_key)
    print(cipher_key)
    print(type(cipher))
    k = SentKey.objects.create(key=cipher_key)
    k.save()

    def on_publish(client, userdata, mid):
        print("mid: " + str(mid))

    hostname = 'broker.mqttdashboard.com'
    broker = "broker.mqttdashboard.com"

    client = paho.Client(client_id="1234", clean_session=False, userdata=None, protocol=paho.MQTTv311, )
    client.on_publish = on_publish
    client.will_set("trial/topic2", payload="bye!", qos=1, retain=False)
    client.username_pw_set("shankar", "shankar001")
    client.connect_async(hostname, 1883)
    client.loop_start()
    i = 0
    while i < 1:
        message = cipher_key
        (rc, mid) = client.publish("trial/key", message, qos=1, retain=True)
        time.sleep(2)
        i = i + 1

    client.disconnect()
    return HttpResponse('Key is sent')


def publish_message(request, t_id=None):
    form = PublishMessage()
    count = 1
    if request.method == 'POST':
        form = PublishMessage(request.POST)
        if form.is_valid():
            print('Form is valid')
            topic = Topic.objects.get(pk=t_id)
            message = form.cleaned_data['message']
            while count < 100:
                publish.publish_message(message, topic)
                count += 1
        else:
            print('Form is invalid')

    return render(request, 'authentication/publish_message.html', {'form': form})


bytes_in = 0
bytes_out = 0


def rcv_file(fname):
    broker = "broker.mqttdashboard.com"
    topic = "data/file_send"
    qos = 1
    data_block_size = 2000
    filename = fname
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
            print("found data bytes =", bytes_in)
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


def snd_file(request, fname):
    global bytes_out
    broker = "broker.mqttdashboard.com"
    topic = "data/file_send"
    qos = 1
    filename = fname

    file = filename.split('.')
    data_block_size = 2000
    fo = open(filename, "rb")
    file_out = "copy-" + filename
    fout = open(file_out, "wb")

    def on_publish(client, userdata, mid):
        # logging.debug("pub ack "+ str(mid))
        client.mid_value = mid
        client.puback_flag = True

    # waitfor loop
    def wait_for(client, msgType, period=0.25, wait_time=40, running_loop=False):
        client.running_loop = running_loop  # if using external loop
        wcount = 0
        # return True
        while True:
            # print("waiting"+ msgType)
            if msgType == "PUBACK":
                if client.on_publish:
                    if client.puback_flag:
                        return True

            if not client.running_loop:
                client.loop(.01)  # check for messages manually
            time.sleep(period)
            # print("loop flag ",client.running_loop)
            wcount += 1
            if wcount > wait_time:
                print("return from wait loop taken too long")
                return False
        return True

    def c_publish(client, topic, out_message, qos):
        res, mid = client.publish(topic, out_message, qos)  # publish
        # return

        if res == 0:  # published ok
            if wait_for(client, "PUBACK", running_loop=True):
                if mid == client.mid_value:
                    print("match mid ", str(mid))
                    client.puback_flag = False  # reset flag
                else:
                    print("quitting")
                    raise SystemExit("not got correct puback mid so quitting")

            else:
                raise SystemExit("not got puback so quitting")

    def send_header(filename):
        header = "header" + ",," + filename + ",,"
        header = bytearray(header, "utf-8")
        header.extend(b',' * (200 - len(header)))
        print(header)
        c_publish(client, topic, header, qos)

    def send_end(filename):
        end = "end" + ",," + filename + ",," + out_hash_md5.hexdigest()
        end = bytearray(end, "utf-8")
        end.extend(b',' * (200 - len(end)))
        print(end)
        c_publish(client, topic, end, qos)

    client = paho.Client("client-001")

    client.on_publish = on_publish

    client.puback_flag = False  # use flag in publish ack
    client.mid_value = None

    print("connecting to broker ", broker)
    client.connect(broker)
    client.loop_start()

    print("subscribing ")
    client.subscribe(topic)  # subscribe

    time.sleep(2)
    start = time.time()
    print("publishing ")
    send_header(filename)
    Run_flag = True
    count = 0
    out_hash_md5 = hashlib.md5()
    in_hash_md5 = hashlib.md5()

    while Run_flag:
        chunk = fo.read(data_block_size)
        if chunk:
            out_hash_md5.update(chunk)  # update hash
            out_message = chunk
            # print(" length =",type(out_message))
            bytes_out = bytes_out + len(out_message)

            c_publish(client, topic, out_message, qos)


        else:
            # end of file so send hash
            out_message = out_hash_md5.hexdigest()
            send_end(filename)
            Run_flag = False

    time_taken = time.time() - start
    print("took ", time_taken)
    print("bytes sent =", bytes_out)
    time.sleep(500)
    client.disconnect()  # disconnect
    client.loop_stop()  # stop loop
    fout.close()
    fo.close()


def send_file(request):
    form = PublishFile()
    if request.method == 'POST':
        form = PublishFile(request.POST)
        if form.is_valid():
            form.save()
            file_name = form.cleaned_data['name']

            def on_publish(client, userdata, mid):
                print("mid: " + str(mid))

            hostname = 'broker.mqttdashboard.com'
            # hostname = '10.0.33.89'

            client = paho.Client(client_id="1234", clean_session=False, userdata=None, protocol=paho.MQTTv311, )
            client.on_publish = on_publish
            client.will_set("trial/topic2", payload="bye!", qos=1, retain=False)
            client.username_pw_set("shankar", "shankar001")
            client.connect_async(hostname, 1883)
            client.loop_start()
            i = 0
            while i < 1:
                message = file_name
                (rc, mid) = client.publish("trial/file_share_name", str(message), qos=1, retain=True)
                time.sleep(2)
                i = i + 1
            client.disconnect()
        else:
            print('Form is not valid')

    return render(request, 'authentication/publish_file.html', {'form': form})


def start_key_message(request):
    key = SentKey.objects.filter()[0]
    return HttpResponseRedirect(reverse('authentication:publish_encrypt_message', args=(key,)))


def start_file_send(request):
    file = SentFiles.objects.filter().order_by('-id')[0]
    temp = str(file)
    print(temp)
    # return HttpResponse('File send')
    return HttpResponseRedirect(reverse('authentication:snd_file', args=(temp,)))


def receive_file(request):
    file_topic = Messages.objects.filter(message__contains='jpg')[0]
    file_name = file_topic.message
    temp = str(file_name)
    name = temp[:-1]
    file_name = name[1:]
    print(file_name)
    rcv_file(file_name)


def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    temp = str(msg.payload).strip('b')
    msg = Messages.objects.create(topic=msg.topic, message=temp)
    msg.save()


def on_connect(client, userdata, flags, rc):
    print("CONNACK received with code %d." % (rc))


def subscribe_file(request):
    hostname = 'broker.mqttdashboard.com'
    client = paho.Client(client_id="1235", clean_session=False, userdata=None, protocol=paho.MQTTv311)
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(hostname, 1883)
    client.subscribe("trial/file_share_name", qos=1)
    client.loop_forever()


def subs(request,t_id=None):
    hostname = 'broker.mqttdashboard.com'
    topic = Topic.objects.get(pk=t_id)
    temp = str(topic)
    client = paho.Client(client_id="1235", clean_session=False, userdata=None, protocol=paho.MQTTv311)
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(hostname, 1883)
    client.subscribe("trial/"+temp, qos=1)
    client.loop_forever()
    # count = 0
    # while count < 3:
    #     time.sleep(1)
    #     count += 1
    # client.loop_stop()
    # subscribe.subscribe_message(topic)


def show_messages(request, tname):
    messages = Messages.objects.filter(topic__contains=tname).exclude(message__contains='bye')
    return render(request, 'authentication/show_messages.html', {'messages': messages})


def tpc(request):
    form = CreateTopic()
    if request.method == 'POST':
        form = CreateTopic(request.POST)
        if form.is_valid():
            form.save()
            return redirect('authentication:publish_message')
        else:
            print('Form is invalid')
    return render(request, 'authentication/create_topic.html', {'form': form})
