import json
import time
from datetime import datetime
import psutil
from vcgencmd import Vcgencmd
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient


vcgm = Vcgencmd()

def get_temperature():
    return vcgm.measure_temp()

def get_memory():
    mem_info = psutil.virtual_memory()
    mem_arm = mem_info.total / (1024 ** 2)  
    
    mem_gpu = vcgm.mem_gpu() if hasattr(vcgm, 'mem_gpu') else "N/A"
    return mem_arm, mem_gpu

def get_cpu_usage():
    return psutil.cpu_percent(interval=1)

def get_network_stats():
    net_io = psutil.net_io_counters()
    return net_io.bytes_sent / (1024 ** 2), net_io.bytes_recv / (1024 ** 2)  

def get_formatted_time():
    return datetime.now().strftime("%d-%m-%Y,%H:%M:%S")

def get_serial_id():
    try:
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if line.startswith('Serial'):
                    return line.split(':')[1].strip()
    except:
        return "Unknown"

# IoT endpoint
endpoint = "a184c9z7edjar9-ats.iot.ap-south-1.amazonaws.com"

# certificates
root_ca_path = "/home/pi/Documents/cert/AmazonRootCA1.pem"
private_key_path = "/home/pi/Documents/cert/a3ebf3a1ca495ec2b1ff941bfc7c774d90d6d2441549cf5cfc5a765fe803422c-private.pem.key"
cert_path = "/home/pi/Documents/cert/a3ebf3a1ca495ec2b1ff941bfc7c774d90d6d2441549cf5cfc5a765fe803422c-certificate.pem.crt"


raspberry_pi_id = get_serial_id()  

client = AWSIoTMQTTClient(raspberry_pi_id)
client.configureEndpoint(endpoint, 8883)
client.configureCredentials(root_ca_path, private_key_path, cert_path)


client.configureOfflinePublishQueueing(-1)  
client.configureDrainingFrequency(2)  
client.configureConnectDisconnectTimeout(10)  
client.configureMQTTOperationTimeout(5)  

# Connect to AWS IoT
try:
    client.connect()
    print("Connected to AWS IoT")
except Exception as e:
    print(f"Failed to connect to AWS IoT: {e}")


while True:
    try:
        temp = get_temperature()
        mem_arm, mem_gpu = get_memory()
        cpu_usage = get_cpu_usage()
        
        bytes_sent, bytes_recv = get_network_stats()
        payload = {
            "timestamp": get_formatted_time(),
            "temperature": temp,
            "mem_arm": mem_arm,
            "mem_gpu": mem_gpu,
            "cpu_usage": cpu_usage,
            "bytes_sent_mb": bytes_sent,
            "bytes_recv_mb": bytes_recv,
            "device_id": raspberry_pi_id
        }
        client.publish("raspberrypi/health", json.dumps(payload), 1)
        print(f"Published: {payload}")
    except Exception as e:
        print(f"Failed to publish message: {e}")
    time.sleep(1800)  
