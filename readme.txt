## WhereNext (2022 MAI Project) ##

WhereNext - An Autonomous Interactive Tourist Attraction Recommender Platform

### Project Contents ###
* pycom - Software for FiPy attraction displays
    * main.py - Main device file
    * comms.py - Functions for communications
    * config.py - Config file for storing constants used by the attraction displays
    * display.py - Functions for interacting with the touchscreen display
    * mqtt.py - Pycom MQTT library file

* server - Software for recommendations server
    * server.py - Main server file
    * recommender.py - Functions for generating recommendations for users
    * config.py - Constants used by the server
    * data_gen.py - Functions for generating simulated user data
    * matrix_factorization.py - Matrix factorization related functions
    * models - Old kNN models, no longer used by the system
    * data - csv files used by the recommender system
        * features.csv - Location feature information
        * ratings.csv - Simulated user ratings
        * mf_ratings.csv - Predicted user ratings following matrix factorization

* database - Software for Google Sheets database (Note: runs on Google servers)
    * database.js - Database communications for handling POSTs and GETs


### Set Up ###
Server
1. To run the project software, first install all packages contained in requirements.txt
    * (Note: Software has been tested for Python 3.10 on Windows 10)

Attraction Displays
1. To set up the FiPy and PySense boards, follow the Pycom 'Getting Started' guide: https://docs.pycom.io/gettingstarted/
    * Ensure IDE extensions are installed, and Pycom board firmware is updated
2. Edit 'config.py' 'WIFI_SSID' and 'WIFI_PASS' with the correct information for a local WiFi network


### Demo Instructions ###
To run the basic demo software, first complete set up as described above.
The server needs to run and set up before the attraction displays.

Server
1. Open the 'server' folder in its own IDE window
2. Run server.py
3. Wait for the message 'Connected with result code 0'

Attraction Displays
1. Open the 'pycom' folder in its own IDE window
2. Open the file 'main.py' in the editor
3. Open the Pymakr Console
3. Upload the project to the FiPy using the 'Upload' button from the Pycom IDE extension
4. After uploading is complete, select the 'Run' button from the Pycom IDE extension

### Demo Description ###
* This demo code will randomly enter the attraction display into active or standby mode
* In standby mode, the attraction display will scan for devcies for 30 seconds, send the gathered users to the server, and then sleep for 2 minutes
* In active mode the attraction display will identify the strongest BLE signal for 5 seconds, collect user inputs (automated for this demo), upload them to the server, and display recommendations once received
* Server and attraction display status can be seen in their respective terminals
* Updates to the database can be seen by opening the Google Sheets link provided above
* The attraction display location can be updated by changing 'DEVICE_ID' in 'config.py'
* The user inputs can be updated by changing lines 53 and 54 of 'display.py'
    * Note: Rating must be between 1 and 5, and 'context' must be one of the 7 types used by the system