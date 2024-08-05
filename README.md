This Python script monitors the health of a Raspberry Pi device and publishes the data to AWS IoT Core. The script collects temperature, memory usage, CPU usage, and network statistics, and then sends this data to AWS IoT Core every 30 minutes.

**Prerequisites**

Raspberry Pi with the following Python libraries installed:
  1. psutil
  2. vcgencmd
  3. AWSIoTPythonSDK
