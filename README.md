# auto_config_switch_router

为什么写这个脚本：本人一直是网络工程师，虽然待过bat中两家，但是在工作仍然会发现很多时候需要批量刷配置，为了节省刷配置时间，写了这个脚本

这个脚本在linux服务器上不用额外安装任何库，直接就能跑。

config.py 文件中可以设置设备登录密码等参数。
'config_username':'test',     #有配置权限的帐号，如果不填会让你每次输入
'config_password':'test',  #有配置权限帐号的密码，同上
'show_username':'test_show',       #只有show权限的帐号，如果不填会直接使用配置权限帐号
'show_password':'test_show',    #只有show权限的帐号的密码，如果不填会直接使用配置权限帐号的密码
'ssh_port':'22',                  #ssh的端口号，默认是22
'login_method':'',             #登录方式，填写ssh或者telnet
'login_user_identification':':',  #telnet方式需要填写对应设备的登录时账户输入的标识符，本人亲测大部分就是login:和username:,用:就行，不用改
'login_password_identification':'assword:' #同上，输入密码的标识符

configuration.txt 这个文件等同于我们的割接单
格式如下
$IP: 设备的管理IP
100.127.17.11
$CONFIG: 设备的配置命令
configure terminal
show vrf all
$CHECK:  对应配置命令的检查命令
terminal length 0
show clock
$CONFIG:
configure terminal
show vrf all
show history
$PING:   如果需要使用ping检测，请将IP贴在下面
10.185.135.240


每个设备操作需要包含$IP:、$CONFIG:、$CHECK:、$PING:，其中$CONFIG:、$CHECK:、$PING:可以重复使用。
