#!/usr/bin/python
#-*- coding:utf-8 -*-
# author:jeffrycheng

import time,re,paramiko,multiprocessing,os

try:
    from config import *
except:
    hosts = ''
    username = '' 
    password = ''
    cmds = ''

stdmore = re.compile(r"-[\S\s]*[Mm]ore[\S\s]*-")
hostname_endcondition = re.compile(r"\S+[#>\]]\s*$")

class ssh_comm(object):
    def __init__(self,address,username,password,port=22):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(address, port=port, username=username, password=password, look_for_keys=False,allow_agent=False)
        self.shell = self.client.invoke_shell()
        while True:
            time.sleep(0.5)
            if self.shell.recv_ready() or self.shell.recv_stderr_ready():
                break
        output = self.shell.recv(4096)
        while True:
            if hostname_endcondition.findall(output):
                self.hostname = hostname_endcondition.findall(output)[0].strip().strip('<>[]#')
                break
            while True:
                time.sleep(0.1)
                if self.shell.recv_ready() or self.shell.recv_stderr_ready():
                    break
            output += self.shell.recv(4096)
    def recv_all(self,interval,stdjudge,stdconfirm):
        endcondition = re.compile(r"%s[#>\]]\s*$"%self.hostname)
        while True:
            time.sleep(interval)
            if self.shell.recv_ready() or self.shell.recv_stderr_ready():
                break
        output = self.shell.recv(99999)
        if (stdjudge != '') and (stdjudge in output):
            self.shell.send(stdconfirm+'\n')
        while True:
            if stdmore.findall(output.split('\n')[-1]):
                break
            elif endcondition.findall(output):
                break
            while True:
                time.sleep(interval)
                if self.shell.recv_ready() or self.shell.recv_stderr_ready():
                    break
            output += self.shell.recv(99999)
        return output
    def send_command(self,command_interval,command,stdjudge,stdconfirm):
        command += "\n"
        self.shell.send(command)
        stdout = self.recv_all(interval=command_interval,stdjudge=stdjudge,stdconfirm=stdconfirm)
        data = stdout.split('\n')
        while stdmore.findall(data[-1]):
            self.shell.send(" ")
            tmp = self.recv_all(interval=command_interval,stdjudge=stdjudge,stdconfirm=stdconfirm)
            data = tmp.split('\n')
            stdout += tmp
        return stdout
    def close(self):
        if self.client is not None:
            self.client.close()
    def run(self,cmds,command_interval,stdjudge,stdconfirm):
        stdout = ''
        rc = 'success'
        for cmd in cmds.split('\n'):
            if cmd.strip():
                stdout += self.send_command(command=cmd,command_interval=command_interval,stdjudge=stdjudge,stdconfirm=stdconfirm)
        return rc, stdout

def writeoutput(address,username,password,cmds):
    try:
        connection = ssh_comm(address=address, username=username, password=password, port=22)
    except:
        rc = 'connection failed'
        return address,rc
    stdjudge = 'Y/N'
    stdconfirm = 'Y'
    rc,stdout = connection.run(cmds=cmds,command_interval=0.1,stdjudge=stdjudge,stdconfirm=stdconfirm)
    connection.close()
    hostname = connection.hostname.split('/')[-1].split(':')[-1]
#    hostname = os.popen('/usr/local/net-snmp/bin/snmpwalk -v 2c -c tcnw %s sysname -Oqv'%address).read().strip()
    if not os.path.exists(hostname):
        os.makedirs(hostname)
    filename = hostname+'-'+time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime(time.time()))
    with open ('%s/%s.txt'%(hostname,filename),'w') as f:
        f.write(stdout)
    return address,rc
    
def main(username,password,hosts,cmds):
    if username == '':
        username = raw_input('请输入aaa用户名：')
    if password == '':
        password = raw_input('请输入aaa密码： ')
    if hosts == '':
        hosts = raw_input('请输入主机地址： ')
    if cmds == '':
        cmds = raw_input('请输入采集命令： ')
    host_list = hosts.split('\n')
    if len(host_list) < 5:
        processnum = len(host_list)
    else:
        processnum = 5
    pool = multiprocessing.Pool(processes=processnum )
    process = []
    for host in host_list:
        if host:
            process.append(pool.apply_async(writeoutput, (host.strip(),username,password,cmds)))
    pool.close()
    pool.join()
    outs = ''
    for o in process:
        rc,ip = o.get()
        print '%s:  %s'%(ip,rc)

if __name__== '__main__':
    main(username,password,hosts,cmds)
