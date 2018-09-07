import os
import xml.etree.ElementTree as ET
for file in os.listdir("/home/log-transfer/incoming-logs/"):
    if file.endswith(".xml"):
        #print(file)
        currentLog = ET.parse(file)
        print(currentLog)