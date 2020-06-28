
import paramiko
import sys
import exception_jumpssh as exceptions
import socket
import time
import subprocess
import telnetlib

class Login():
    def __init__(self,server_ip,server_user,server_passwd,node_user,node_passwd):
        self.server_ip = server_ip
        self.server_user = server_user
        self.server_passwd = server_passwd
        self.node_user = node_user
        self.node_passwd = node_passwd

    def connect(self):
        try:
            self.vm = paramiko.SSHClient()
            self.vm.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.vm.connect(self.server_ip,username=self.server_user,password=self.server_passwd)
        except paramiko.BadHostKeyException:
            raise exceptions.BadHostKeyException('Bad Host Keys')
        except paramiko.AuthenticationException:
            raise exceptions.AuthenticationFailed('Authentication Failed')
        except socket.error:
            raise exceptions.socketerror('Unable to connect')
        except paramiko.SSHException:
            raise exceptions.OtherError('Login Error')
        except:
            raise exceptions.SshError('ssh Error')

    def telnet_login_node(self,node_ip):
        try:
            self.vmtransport = self.vm.get_transport()
            dest_addr = (node_ip, 23) #edited#
            local_addr = (self.server_ip, 22) #edited#
            self.vmchannel = self.vmtransport.open_channel("direct-tcpip", dest_addr, local_addr,timeout=10)
        except paramiko.ChannelException:
            raise exceptions.HostUnkown('Name or service not known')
        user = self.node_user.encode("utf-8") + b'\r\n'
        password = self.node_passwd.encode("utf-8") + b'\r\n'
        self.prompt_telnet = node_ip.encode("utf-8") + b'#'
        try:
            self.tn = telnetlib.Telnet()
            self.tn.sock = self.vmchannel
            self.tn.read_until(b"username: ")
            self.tn.write(user)
            if password:
                self.tn.read_until(b"password: ")
                self.tn.write(password)
        except:
            raise exceptions.SshError('Telnet Error')

    def telnet_terminal_length_zero(self):
            self.tn.read_until(b"#")
            self.tn.write(b"terminal length 0\r\n")
            self.tn.read_until(b"#")

    def telnet_command_send(self,command):
        command = command.encode("utf-8") + b'\r\n'
        self.tn.write(command)
        output =  self.tn.read_until(self.prompt_telnet)
        return output.decode('ascii')

    def login_node(self,node_ip):
        try:
            self.vmtransport = self.vm.get_transport()
            dest_addr = (node_ip, 22) #edited#
            local_addr = (self.server_ip, 22) #edited#
            vmchannel = self.vmtransport.open_channel("direct-tcpip", dest_addr, local_addr)
        except paramiko.ChannelException:
            raise exceptions.HostUnkown('Name or service not known')
        self.connection = paramiko.SSHClient()
        self.connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.connection.connect(node_ip, username=self.node_user, password=self.node_passwd, sock=vmchannel)
        except paramiko.BadHostKeyException:
            raise exceptions.BadHostKeyException('Bad Host Keys')
        except paramiko.AuthenticationException:
            raise exceptions.AuthenticationFailed('Authentication Failed')
        except socket.error:
            raise exceptions.socketerror('Unable to connect')
        except paramiko.SSHException:
            raise exceptions.OtherError('Login Error')
        except:
            raise exceptions.SshError('ssh Error')

    def get_shell(self):
    	self.client = self.connection.invoke_shell()

    def prompt(self):
        connection_data = ''
        host = ''
        self.client.send('\n')
        time.sleep(2)
        resp = self.client.recv(9999)
        connection_data += resp.decode("utf-8", "ignore")
        if connection_data.endswith('# '):
            self.client.send('show system information  | match "System Name            :"\n')
            time.sleep(2)
            datax = self.client.recv(9999)
            host += datax.decode("utf-8", "ignore")
            prompts = host.split('\n')[1].split(':')[1].strip() + '# '
            self.prompt = prompts
            self.device = 'alu'
        elif connection_data.endswith('> '):
            self.client.send('show version | match Hostname:\n')
            time.sleep(3)
            datax = self.client.recv(9999)
            host += datax.decode("utf-8", "ignore")
            prompts = self.node_user + '@' + host.split('\n')[1].split(':')[1].strip() + '> '
            self.prompt = prompts
            self.device = 'juniper'
        elif connection_data.endswith('>'):
            self.client.send('display current-configuration | include sysname\n')
            time.sleep(6)
            datax = self.client.recv(9999)
            host += datax.decode("utf-8", "ignore")
            prompts = '<' + host.split('\n')[1].split()[1] + '>'
            self.prompt = prompts
            self.device = 'huwaei'
        elif connection_data.endswith('#'):
            self.client.send('show version | in uptime\n')
            time.sleep(2)
            datax = self.client.recv(9999)
            host += datax.decode("utf-8", "ignore")
            prompts = host.split('\n')[1].split()[0] + '#'
            self.prompt = prompts
            self.device = 'cisco'
        else:
            print ("Enter the prompt")
            self.prompt = input()
            print ("Enter the device vendor")
            self.device = input()
        return self.prompt,self.device

    def terminal_length_zero(self):
        connection_data = ''
        if 'alu' in self.device:
            self.client.send('environment no more' +'\n')
        elif 'juniper' in self.device:
            self.client.send('set cli screen-length 0' +'\n')
        elif 'huwaei' in self.device:
            self.client.send('screen-length 0 temporary' +'\n')
        elif 'cisco' in self.device:
            self.client.send('terminal length 0' +'\n')
        else:
            print ('Enter command to clear buffer of a vendor')
            manual_command = input()
            self.client.send(manual_command +'\n')
        time.sleep(2)
        while not connection_data.endswith(self.prompt):
            resp = self.client.recv(1024)
            connection_data += resp.decode()

    def command_send(self,command):
    	connection_data = ''
    	self.client.send(command +'\n') #edited#
    	time.sleep(2)
    	while not connection_data.endswith(self.prompt):
    		resp = self.client.recv(1024)
    		connection_data += resp.decode()
    		output = connection_data
    	return output

    def node_logout_telnet(self):
        self.tn.close()

    def node_logout(self):
    	self.connection.close()

    def logout(self):
    	self.vm.close()

if __name__ == '__main__':
    testing = Login('#serverip','#serverusername','#serverpasowrd','#routerusername','#routerpassowrd')
    testing.connect()
    try:
        testing.telnet_login_node("#routername")
        testing.telnet_terminal_length_zero()
        test_out = testing.telnet_command_send('#command')
        testing.node_logout_telnet()
        telnet = 'True'
    except:
        telnet = 'False'
    if 'False' in telnet:
        testing.login_node("#routername")
        testing.get_shell()
        testing.prompt()
        testing.terminal_length_zero()
        test_out = testing.command_send('#command')
        test_out1 = testing.command_send('#command')
        testing.node_logout()
    print (test_out)
    print (test_out1)
    testing.logout()
