# MQTT daemon for usbrelay
# Publishes a state topic for each connected usbrelay and subscribes to command topics  for each relay
# Topics are stat/SERIAL/RELAY or cmnd/SERIAL/RELAY
# eg stat/QWERT/2 or cmnd/QWERT/2

import paho.mqtt.client as mqtt
import usbrelay_py
import time
import re
import sys

def publish_states(client):
    boards = usbrelay_py.board_details()
    print("Boards: ",boards)
    for board in boards:
        print("Board: ",board)
        relay = 1
        # determine the state of each relay and publish to the MQTT broker
        while(relay < board[1]+1):
            if ( board[2] & ( 1 << (relay -1) )):
                relay_state = "ON"
            else:
                relay_state = "OFF"
            
            
            topic = "{0}/{1}/{2}"
            topic_str = topic.format("stat",board[0],relay)
            print("State: ", topic_str, relay_state)
            client.publish(topic_str, relay_state)
            topic_str = topic.format("cmnd",board[0],relay)
            print("Subscribed: ", topic_str)
            client.subscribe(topic_str)
            relay += 1
        client.on_message=on_message 

def on_message(client, userdata, message):
    msg_state = str(message.payload.decode("utf-8"))
    print("received message: " ,message.topic, msg_state)
    # any message other than ON is OFF
    if( msg_state == "ON" ):
        relay_cmd = 1
    else:
        relay_cmd = 0
    
    content = re.split("/",message.topic)
    result = usbrelay_py.board_control(content[1],int(content[2]),relay_cmd)
    print("COntent: ", content , result)
    pub_str = "stat/{0}/{1}"
    client.publish(pub_str.format(content[1],content[2]), msg_state)

# read the server name or IP address from the command lin


if ( len(sys.argv) < 2 ):
    print("No mqtt broker name")
    exit()
mqttBroker = sys.argv[1]
#
# Count connected usbrelay modules, exit if none 
count = usbrelay_py.board_count()

if(count < 1):
    print("No usbrelay modules connected")
    exit()
else:
    print("Modules Connected: ",count)

# connect to the mqtt broker


client = mqtt.Client("Switch")
client.connect(mqttBroker) 
publish_states(client)

client.loop_forever()



