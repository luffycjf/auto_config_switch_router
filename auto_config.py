#! /usr/bin/python
# -*- coding:utf-8 -*-

import paramiko,time,telnetlib,sys,os
import threading
try:
    from config import config
except:
    config = {'config_username':'','config_password':'','show_username':'','show_password':'','ssh_port':'22','login_method':''}

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
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try_times += 1
        try:
            client.connect(ip, port , username, password, timeout=5)
            break
        except:
            print 'wrong password,please try agagin!'
        if try_times > 2:
            sys.exit('wrong password more than tree times,out!')
    a = client.invoke_shell()
    client1 = paramiko.SSHClient()
    client1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    if password_config['show_username'] != '' and password_config['show_password'] != '':
        show_username = config['show_username']
        show_password = config['show_password']
    else:
        show_username = username
        show_password = password
    client1.connect(ip, port , show_username,show_password, timeout=5)
    b = client1.invoke_shell()
    b.recv('')
    for command in commands:
        if len(command['config']) != 0:
            for config_command in command['config']:
                a.send(config_command+'\r')
                time.sleep(1)
        if len(command['check']) != 0:
            for check_command in command['check']:
                b.send(check_command+'\r')
                time.sleep(1)
            print b.recv('')
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
