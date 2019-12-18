import paramiko
import sys
import exception_jumpssh as exceptions
import socket
import time
import subprocess

def connect(server_ip, user, passwd):
    try:
        vm = paramiko.SSHClient()
        vm.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        vm.connect(server_ip, username=user, password=passwd)
    except paramiko.BadHostKeyException:
        vm = 'BadHostKeyExceptions'
        raise exceptions.BadHostKeyException('Bad Host Keys')
    except paramiko.AuthenticationException:
        vm = 'WrongPassword'
        raise exceptions.AuthenticationFailed('Authentication Failed')
    except socket.error:
        vm = 'socketerror'
        raise exceptions.socketerror('Unable to connect')
    except paramiko.SSHException:
        vm = 'LoginError'
        raise exceptions.OtherError('Login Error')
    except:
        vm = 'LoginError'
        raise exceptions.SshError('ssh Error')
    return vm


def login_node(vm,node_ip,server_ip, username, password):
    try:
        vmtransport = vm.get_transport()
        dest_addr = (node_ip, 22) #edited#
        local_addr = (server_ip, 22) #edited#
        vmchannel = vmtransport.open_channel("direct-tcpip", dest_addr, local_addr)
    except paramiko.ChannelException:
        raise exceptions.HostUnkown('Name or service not known')
    connection = paramiko.SSHClient()
    connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        connection.connect(node_ip, username=username, password=password, sock=vmchannel)
    except paramiko.BadHostKeyException:
        connection = 'BadHostKeyExceptions'
        raise exceptions.BadHostKeyException('Bad Host Keys')
    except paramiko.AuthenticationException:
        connection = 'WrongPassword'
        raise exceptions.AuthenticationFailed('Authentication Failed')
    except socket.error:
        connection = 'socketerror'
        raise exceptions.socketerror('Unable to connect')
    except paramiko.SSHException:
        connection = 'LoginError'
        raise exceptions.OtherError('Login Error')
    except:
        connection = 'LoginError'
        raise exceptions.SshError('ssh Error')
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
