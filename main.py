from iotery_embedded_python_sdk import Iotery
from read_temperature import current_cpu_temperature
from time import sleep, time
import paho.mqtt.client as mqtt
import ssl


# team ID found on the dashboard: https://iotery.io/system
TEAM_ID="088baf45-8d55-11e9-b121-d283610663ec" 
iotery = Iotery()
d = iotery.getDeviceTokenBasic(data={"key": "temp-sensor-key",
                                     "serial": "temp-sensor-1", "secret": "secret1"})

# set token for subsequent eatery calls
iotery.set_token(d["token"])

# get info about the device
me = iotery.getMe()

#  Set up the MQTT stuff
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    #once connected, subscribe to the command topic
    client.subscribe("devices/" + me["uuid"] + "/commands")
    

# The callback for when something is published to the broker.
def on_message(client, userdata, msg):
    print("Received from topic" + msg.topic)
    print("Message: " + str(msg.payload))

    if msg.topic == "devices/" + me["uuid"] + "/commands":
        # There is only one command for now, so we will just report.  If we add more later, we can look at the `commandTypeEnum` to control actions
        t = iotery.getCurrentTimestamp()
        temp = current_cpu_temperature()
        # https://iotery.io/docs/embedded/#tag/Embedded/paths/%7E1embedded%7E1devices%7E1:deviceUuid%7E1data/post
        data = {"packets":[{
            "timestamp": t,
            "deviceUuid": me["uuid"],
            "deviceTypeUuid": me["deviceTypeUuid"],
            "data":{"temperature": temp}
        }]}
        iotery.postData(deviceUuid=me["uuid"], data=data)
        print("data posted!")

client_id = TEAM_ID + ":" + str(iotery.getCurrentTimestamp()*1000) + ":" + me["uuid"] #Iotery client ID format
client = mqtt.Client(client_id)
client.on_connect = on_connect # set the connect handler to run when mqtt connects
client.on_message = on_message # the function that runs when we get a message

# username and password are your device's uuid and it's token we got back from auth above
client.username_pw_set(me["uuid"], password=d["token"])

# To use MQTTS (secure MQTT), we need to configure TLS
client.tls_set(ca_certs=None, certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED,
    tls_version=ssl.PROTOCOL_TLS, ciphers=None) 

#  connect to the broker
client.connect("mqtt.iotery.io", port=8885, keepalive=60)

client.loop_start() # make sure to start the mqtt loop!

# the main application loop!
while True:
    t = iotery.getCurrentTimestamp()
    temp = current_cpu_temperature()

    # https://iotery.io/docs/embedded/#tag/Embedded/paths/%7E1embedded%7E1devices%7E1:deviceUuid%7E1data/post
    data = {"packets":[{
        "timestamp": t,
        "deviceUuid": me["uuid"],
        "deviceTypeUuid": me["deviceTypeUuid"],
        "data":{"temperature": temp}
    }]}
    iotery.postData(deviceUuid=me["uuid"], data=data)
    sleep(60 * 5) # sleeps for 60 * 5 seconds (5 min)