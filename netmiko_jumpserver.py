import time
from netmiko import ConnectHandler, redispatch

zpe_username = "jump_server_username"
zpe_password = "XXXX"
zpe_hostname = "server_ip"
console_username = zpe_username
console_server = {
    "host": zpe_hostname,
    "username": console_username,
    "password": zpe_password,
    "device_type": "terminal_server",
}
print("ssh " + console_username + "@" + zpe_hostname)

net_connect = ConnectHandler(**console_server)
print (net_connect.find_prompt())
net_connect.write_channel("ssh username@router\n")
time.sleep(1)
net_connect.read_channel()
net_connect.write_channel("Router_password\n")
time.sleep(1)
net_connect.read_channel()
redispatch(net_connect, device_type='alcatel_sros')
command_output = net_connect.send_command('/configure router policy-options')
