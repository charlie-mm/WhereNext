# comms.py - Functions for communications
# Imports
import display
import config

# CONSTANTS
TEST_FEED = "charliemm/feeds/test-feed"
RECOMMENDATIONS_FEED = "charliemm/feeds/project.recommendations"
UPDATES_FEED = "charliemm/feeds/project.updates"
STATUS_FEED = "charliemm/feeds/project.status"

# Initialise variables
requested = 0

# MQTT Callback Function
def mqtt_cb(topic, msg):
    print("Running mqtt_cb()")
    global requested
    msg_in = msg.decode().split(",")
    topic = topic.decode()
    # Only cares about messages from the recommendations feed
    if (msg_in[0] == str(config.DEVICE_ID)):
        if(topic == RECOMMENDATIONS_FEED):
            requested = 0
            display.display_recommendations(msg_in[1:])
    return

# Send new visitors
def update_visitors(client, new_devices, visitors):
    print("Running update_visitors()")
    msg_visitors = ''
    msg_vis_count = 0
    # Gather newly identified users
    for user in new_devices:
        if user not in visitors:
            visitors.append(user)
            if msg_visitors == '':
                msg_visitors = str(user)
            else:
                msg_visitors += ',' + str(user)
            msg_vis_count += 1
    # Send update if there are new visitors
    if msg_vis_count > 0:
        msg = "S," + str(config.DEVICE_ID) + "," + str(msg_vis_count) + ',' + msg_visitors
        client.connect()
        client.subscribe(topic=UPDATES_FEED, qos=2)
        client.publish(topic=UPDATES_FEED, msg=msg)
        client.disconnect()
    return visitors

# Send location status
# Not used in current implementation
def update_status(client):
    print("Running update_status()")
    client.connect()
    client.subscribe(topic=STATUS_FEED, qos=2)
    client.publish(topic=STATUS_FEED, msg="S,Status")
    client.disconnect()
    return

# Request recommendation from server
def get_recommendation(client, data):
    print("Running get_recommendation()")
    global requested
    # Connect to broker and send user ratings
    client.connect()
    client.subscribe(topic=RECOMMENDATIONS_FEED, qos=2)
    msg_out = "S," + str(config.DEVICE_ID) + "," + str(data['user']) + "," + str(data['rating']) + "," + str(data['context'])
    client.publish(topic=RECOMMENDATIONS_FEED, msg=msg_out)
    requested = 1
    # Wait for recommendation
    while requested == 1:
        client.wait_msg()
    client.disconnect()
    return

# MQTT Test function
# Used for deubugging
def mqtt_test(client, msg):
    print("Running mqtt_test()")
    client.connect()
    client.subscribe(topic=TEST_FEED, qos=2)
    client.publish(topic=TEST_FEED, msg="S," + str(msg))
    client.disconnect()
    return