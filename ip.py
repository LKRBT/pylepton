import yaml
import time
import socket
import psutil

def get_ip_address(interface_name):
    addrs = psutil.net_if_addrs()
    if interface_name in addrs:
        for addr in addrs[interface_name]:
            if addr.family == socket.AF_INET:
                return addr.address
    return None

def update_yaml_file(file_path, value):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)

    if 'PI' in data and 'HOST' in data['PI']:
        data['PI']['HOST'] = value

    with open(file_path, 'w') as file:
        yaml.safe_dump(data, file)

if __name__ == "__main__":
	wifi_ip = None
	
	while not wifi_ip:
		wifi_ip = get_ip_address('wlan0')
		if not wifi_ip:
			print("Waiting for Wi-Fi IP address...")
			time.sleep(5)
		
	print(f"Wi-Fi IP Address: {wifi_ip}")
    
	yaml_file_path = '/home/raspberry/pylepton/configs/config.yaml'  
    
	update_yaml_file(yaml_file_path, wifi_ip)
	print(f"Updated wifi_ip in {yaml_file_path} with {wifi_ip}")