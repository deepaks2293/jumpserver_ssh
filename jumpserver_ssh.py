import paramiko
import sys
import subprocess
import time

def connect(server_ip, node_ip, user, passwd):
    try:
        vm = paramiko.SSHClient()
        vm.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        vm.connect(server_ip, username=user, password=passwd)
    except paramiko.BadHostKeyException:
        vm = 'BadHostKeyExceptions'
    except paramiko.AuthenticationException:
        vm = 'WrongPassword'
    except paramiko.socket.error:
        vm = 'socketerror'
    except paramiko.SSHException:
        vm = 'LoginError'
    except:
        vm = 'LoginError'
    return vm


def login_node(vm,node_ip,server_ip, username, password):
    try:
        vmtransport = vm.get_transport()
        dest_addr = (node_ip, 22) #edited#
        local_addr = (server_ip, 22) #edited#
        vmchannel = vmtransport.open_channel("direct-tcpip", dest_addr, local_addr)
        connection = paramiko.SSHClient()
        connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #jhost.load_host_keys('/home/osmanl/.ssh/known_hosts') #disabled#
        connection.connect(node_ip, username=username, password=password, sock=vmchannel)
    except paramiko.BadHostKeyException:
        connection = 'BadHostKeyExceptions'
    except paramiko.AuthenticationException:
        connection = 'WrongPassword'
    except paramiko.socket.error:
        connection = 'socketerror'
    except paramiko.SSHException:
        connection = 'LoginError'
    except:
        connection = 'LoginError'
    return connection

def get_shell(connection):
    client = connection.invoke_shell()
    return client

def terminal_length_zero(client,prompt,command):
    connection_data = ''
    client.send(command +'\n') #edited#
    while not connection_data.endswith(prompt):
            resp = client.recv(1024)
            connection_data += resp.decode()

def command_send(client,prompt,command):
    connection_data = ''
    output =''
    client.send(command +'\n') #edited#
    while not connection_data.endswith(prompt):
            resp = client.recv(1024)
            connection_data += resp.decode()
    output = connection_data
    return output

def node_logout(connection):
    connection.close()

def logout(vm):
    vm.close()
