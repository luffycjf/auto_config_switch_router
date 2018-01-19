#! /usr/bin/python
# -*- coding:utf-8 -*-

import paramiko,time,telnetlib,sys,os
import multiprocessing

try:
    from config import config
except:
    config = {'config_username':'','config_password':'','ssh_port':'22','login_method':'telnet','multiprocess':'2'}

def config_dev_ssh(ip, commands):
    username = config['config_username']
    password = config['config_password']
    port = 22
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(ip, port , username, password, timeout=5)
    except:
        out = "device_ip: %s is can't login\n"%ip
        print  out
        return out
    a = client.invoke_shell()
    a.recv('')
    for command in commands:
        a.send(command+'\r')
        time.sleep(1)
    print 'device_ip: %s is done !'%ip
    return a.recv('')

def config_dev_tel(ip, commands):
    username = config['config_username']
    password = config['config_password']
    try:
        handler = telnetlib.Telnet(ip,timeout=3)
        handler.read_until(config['login_user_identification'])
        handler.write(username+'\r')
        handler.read_until(config['login_password_identification'])
        handler.write(password+'\r')
    except:
        out = "device_ip: %s is can't login\n"%ip
        print out
        return out
    for command in commands:
        handler.write(command+'\r')
        time.sleep(1)
    handler.write('$$\r')
    print 'device_ip: %s is done !'%ip

def readconfigs(config_name):
    f = open(config_name)
    results = f.read()
    result = {}
    ip_list = []
    for i in results.split('$IP:'):
        if i != '':
            for j in i.split('$CONFIG:')[0].split():
                ip = j
                commands = []
                for k in i.split('$CONFIG:')[1].split('\n'):
                    if k != '':
                        commands.append(k)
                result[ip] = commands
                ip_list.append(ip)
    return result,ip_list


if __name__== '__main__':
    result,ip_list = readconfigs('configuration.txt')
    pool = multiprocessing.Pool(processes = int(config['multiprocess']))
    process = []
    for i in ip_list:
        if config['login_method'] == 'telnet':
            process.append(pool.apply_async(config_dev_tel, (i,result[i],)))
        else:
            process.append(pool.apply_async(config_dev_ssh, (i,result[i],)))
    pool.close()
    pool.join()
    print "all done!"
    outs = ''
    for o in process:
        outs += o.get()
    with open ('result.txt','a') as f:
        f.write(outs)
