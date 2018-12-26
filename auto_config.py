#! /usr/bin/python
# -*- coding:utf-8 -*-

import paramiko,time,telnetlib,sys,os
import threading
try:
    from config import config
except:
    config = {'config_username':'','config_password':'','show_username':'','show_password':'','ssh_port':'22','login_method':''}


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
        stderr = ['^','ERROR','Error','error','invalid','Invalid','Ambiguous','ambiguous']
        stdout = ''
        res = 'success'
        for cmd in cmds.split('\n'):
            if cmd.strip():
                stdout += self.send_command(command=cmd,command_interval=command_interval,stdjudge=stdjudge,stdconfirm=stdconfirm)
        for err in stderr:
            if err in stdout:
                res = 'some command wrong'
        return res, stdout


def config_dev_ssh(ip, commands):
    try_times = 0
    while True:
        if config['config_username'] != '' and config['config_password'] != '':
            username = config['config_username']
            password = config['config_password']
            try_times = 2
        else:
            username = raw_input('请输入aaa用户名：')
            password = raw_input('请输入aaa密码： ')
        port = 22
        try_times += 1
        try:
            connection = ssh_comm(address=ip, username=username, password=password, port=port)
            break
        except:
            print 'wrong password,please try agagin!'
        if try_times > 2:
            sys.exit('wrong password more than tree times,out!')
    if password_config['show_username'] != '' and password_config['show_password'] != '':
        show_username = config['show_username']
        show_password = config['show_password']
    else:
        show_username = username
        show_password = password
    connection1 = ssh_comm(address=ip, username=show_username, password=show_password, port=port)
    for command in commands:
        if len(command['config']) != 0:
            res,stdout = connection.run(cmds=command['config'],command_interval=0.1,stdjudge='Y/N',stdconfirm='Y')
        if len(command['check']) != 0:
            res1,stdout1 = connection.run(cmds=command['check'],command_interval=0.1,stdjudge='Y/N',stdconfirm='Y')
            print stdout1
        if len(command['ping']) != 0:
            threads = []
            for ping_host in command['ping']:
                threads.append(threading.Thread(target = getpingloss,args=(ping_host,)))
            for t in threads:
                t.start()
            for t in threads:
                t.join()
        q = raw_input('请问是否继续，按q回车退出，任意键回车继续')
        if q == 'q':
            sys.exit()



def config_dev_tel(ip, commands):
    try_times = 0
    while True:
        if config['config_username'] != '' and config['config_password'] != '':
            username = config['config_username']
            password = config['config_password']
            try_times = 2
        else:
            username = raw_input('请输入aaa用户名：')
            password = raw_input('请输入aaa密码： ')
        try:
            handler = telnetlib.Telnet(ip,timeout=3)
            handler.read_until(config['login_user_identification'])
            handler.write(username+'\r')
            handler.read_until(config['login_password_identification'])
            handler.write(password+'\r')
            break
        except:
            print 'wrong password,please try agagin!'
            try_times += 1
        if try_times > 2:
            sys.exit('wrong password more than tree times,out!')
    handler1 = telnetlib.Telnet(ip,timeout=3)
    handler1.read_until(config['login_user_identification'])
    handler1.write(username+'\r')
    handler1.read_until(config['login_password_identification'])
    handler1.write(password+'\r')
    for command in commands:
        if len(command['config']) != 0:
            for config_command in command['config']:
                handler.write(config_command+'\r')
                time.sleep(1)
        if len(command['check']) != 0:
            for check_command in command['check']:
                handler1.write(check_command+'\r')
                time.sleep(1)
            handler1.write('$$\r')
            print handler1.read_until('$$')
        if len(command['ping']) != 0:
            threads = []
            for ping_host in command['ping']:
                threads.append(threading.Thread(target = getpingloss,args=(ping_host,)))
            for t in threads:
                t.start()
            for t in threads:
                t.join()
        q = raw_input('请问是否继续，按q回车退出，任意键回车继续')
        if q == 'q':
            sys.exit()

def getpingloss(ping_host):
    print 'ping %s   '%ping_host +[i for i in os.popen('ping %s -c 5'%ping_host).read().split(',') if 'packet loss' in i][0]

def readconfigs(config_name):
    f = open(config_name)
    results = f.read()
    result = {}
    ip_list = []
    for i in results.split('$IP:'):
        if i != '':
            ip = i.split()[0]
            commands = []
            for j in range(len(i.split('$CONFIG:'))):
                command = {}
                if (j > 0) and (i.split('$CONFIG:')[j]) != '':
                    try:
                        m = i.split('$CONFIG:')[j].split('$CHECK:')[0]
                        command['config'] = [ x.strip() for x in m.split('\n') if x.strip() != '']
                    except:
                        m = i.split('$CONFIG:')[j].split('$PING:')[0]
                        command['config'] = [ x.strip() for x in m.split('\n') if x.strip() != '']
                    try:
                        n = i.split('$CONFIG:')[j].split('$CHECK:')[1].split('$PING:')[0]
                        command['check'] = [ y.strip() for y in n.split('\n') if y.strip() != '']
                    except:
                        command['check'] = []
                    try:
                        t = i.split('$CONFIG:')[j].split('$CHECK:')[1].split('$PING:')[1]
                        command['ping'] = [ z.strip() for z in t.split('\n') if z.strip() != '']
                    except:
                        try:
                            t = i.split('$CONFIG:')[j].split('$PING:')[1]
                            command['ping'] = [ z.strip() for z in t.split('\n') if z.strip() != '']
                        except:
                            command['ping'] = []
                if command != {}:
                    commands.append(command)
            result[ip] = commands
            ip_list.append(ip)
    return result,ip_list


if __name__== '__main__':
    result,ip_list = readconfigs('configuration.txt')
    if config['login_method'] == '':
        config['login_method'] = raw_input('使用哪种登录方式ssh还是telnet,请输入telnet或者ssh')
    for i in ip_list:
        print(''.ljust(101,'#'))
        print 'device_ip: %s is configing !'%i
        if config['login_method'] == 'telnet':
            config_dev_tel(i,result[i])
        else:
            config_dev_ssh,(i,result[i])
        print 'device_ip: %s is done !'%i
        print(''.ljust(101,'#'))
        print('\n')
    print "all done!"
