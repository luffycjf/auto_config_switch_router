# coding=utf-8

config = {
    'config_username':'test',     #有配置权限的帐号，如果不填会让你每次输入
    'config_password':'test',  #有配置权限帐号的密码，同上
    'ssh_port':'22',                  #ssh的端口号，默认是22
    'login_method':'telnet',             #登录方式，填写ssh或者telnet
    'login_user_identification':':',  #telnet方式需要填写对应设备的登录时账户输入的标识符，本人亲测大部分就是login:和username:,用:就行，不用改
    'login_password_identification':'assword:' #同上，输入密码的标识符
    'multiprocess':'2'                #多进程数量
}

