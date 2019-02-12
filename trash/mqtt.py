import paho.mqtt.client as mqtt


def on_message(client, userdata, message):
    print("Received message:{} on topic {}".format(message.payload, message.topic))

def send_msg():
    client = mqtt.Client()
    client.tls_set(ca_certs="mosquitto.org.crt",certfile="client.crt",keyfile="client.key")
    print(client.connect("test.mosquitto.org",port=8884))
    msg = input()
    msg_info = client.publish("IC.embedded/HAGI/test",msg)
    #msg_info is result of publish()
    error = mqtt.error_string(msg_info.rc)
    print(error)

    client.on_message = on_message
    client.subscribe("IC.embedded/HAGI/#")
    client.loop_start()

    while True:
        pass


send_msg()
