# server.py - Main server file

# Imports
import paho.mqtt.client as mqtt
import requests
import recommender
import json
import threading
import queue
import config

# Constants for MQTT
TEST_FEED = "charliemm/feeds/test-feed"
RECOMMENDATIONS_FEED = "charliemm/feeds/project.recommendations"
UPDATES_FEED = "charliemm/feeds/project.updates"
STATUS_FEED = "charliemm/feeds/project.status"

# Queue for incoming messages
message_queue = queue.Queue()

# Callback for when server connects to the MQTT broker
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribe to all feeds
    client.subscribe("$SYS/#")
    client.subscribe(TEST_FEED, qos=2)
    client.subscribe(RECOMMENDATIONS_FEED, qos=2)
    client.subscribe(UPDATES_FEED, qos=2)
    client.subscribe(STATUS_FEED, qos=2)

# Test function for sending and receiving simple messages
def mqtt_test(msg):
    print("Running mqtt_test()")
    print(str(msg))
    return

# Handle messages containing a list of new visitors
def visitor_update(msg):
    print("Running visitor_update()")
    print(str(msg))
    location = msg[0]
    num_vis = msg[1]
    if int(num_vis) == 0:
        print("No visitors to update")
        return
    else:
        vis_list = ''
        for i in range(int(num_vis) - 1):
            vis_list += msg[i + 2] + ','
        vis_list += msg[-1]
        # Create JSON string and POST to Sheets
        msg_info = {
        'type' : "0",
        'location' : location,
        'numvis' : num_vis,
        'visitors' : vis_list,
        }
        post_visitor_update_Sheets(msg_info)
    return

# POSTs visitor update to Sheets
def post_visitor_update_Sheets(data):
    url_data = config.DB_URL + "?type=" + data['type'] + "&location=" + data['location'] + "&numvis=" + data['numvis'] + "&visitors=" + data['visitors']
    r = requests.post(url_data, data=json.dumps(data))
    print(r.status_code)   

# Handle messages with user ratings
def visitor_recommendation(msg):
    print("Running visitor_recommendation()")
    # Update Sheets with new ratings
    print("Updating user ratings")
    user_info = {
        'type' : "1",
        'location' : msg[0],
        'user' : msg[1],
        'rating' : msg[2],
        'context' : msg[3],
    }
    post_rating_Sheets(user_info)
    # GET user's ratings from Sheets
    print("Fetching recommendations for user", user_info['user'], "at device", user_info['location'])
    user_rats = get_user_Sheets(user_info['user'])
    # Get recommendation from recommender system
    print("Generating recommendations")
    recs = recommender.get_recommendations(user_rats[1:], user_info['context'])
    out_msg = user_info['location'] + "," + user_info['user']
    for i in recs:
        out_msg += "," + str(i)
    # Publish message with recommendations to MQTT broker
    print("Sending recommendations")
    client.publish(RECOMMENDATIONS_FEED, payload=out_msg, qos=1, retain=False)
    return

# GETs user information from Sheets
def get_user_Sheets(user):
    data = {
        'user' : user,
    }

    url_data = config.DB_URL + "?user=" + data['user']
    r = requests.get(url_data, params=json.dumps(data))
    user_rats = r.text
    user_rats = list(user_rats.split(","))
    # If user has no rating for a location, set to 0
    for i in range(len(user_rats) - 1):
        if user_rats[i + 1] == '':
            user_rats[i + 1] = 0
        else:
            user_rats[i + 1] = int(user_rats[i + 1])
    return user_rats

# POSTs user ratings to Sheets
def post_rating_Sheets(data):
    url_data = config.DB_URL + "?type=" + data['type'] + "&user=" + data['user'] + "&rating=" + data['rating'] + "&location=" + data['location']
    r = requests.post(url_data, data=json.dumps(data))
    print(r.status_code)   

# Handle messages regarding location status
def status_update(msg):
    print("Running status_update()")
    print(str(msg))
    return

# Message handler
def message_handler(msg):
    print("Running message_handler()")
    msg_in = msg.payload.decode().split(",")
    if(msg.topic == TEST_FEED):
        mqtt_test(msg_in[1:])
    elif(msg.topic == RECOMMENDATIONS_FEED):
        visitor_recommendation(msg_in[1:])
    elif(msg.topic == UPDATES_FEED):
        visitor_update(msg_in[1:])
    elif(msg.topic == STATUS_FEED):
        status_update(msg_in[1:])
    return

# Callback for when a message is received from the MQTT broker
# Function called depends on topic published to
def on_message(client, userdata, msg):
    msg_in = msg.payload.decode().split(",")
    if (msg_in[0] == "S"):
        message_queue.put(msg)

# Connect to Adafruit IO MQTT broker
client = mqtt.Client(client_id="Server")
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(config.MQTT_USER, password=config.MQTT_PASS)

client.connect(config.MQTT_BROKER, port=1883)

# Start MQTT client, runs indefinetely
client.loop_start()

while True:
    if not message_queue.empty():
        msg = [message_queue.get()]
        threading.Thread(target=message_handler, args=(msg), daemon=True).start()