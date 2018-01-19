#自动化刷网络设备配置+检测


##设计目的
本人在互联网工作多年，混迹过bat中两家，都是屌丝网工，即便两家自动化程度都已经非常高了，但网工在日常工作种任然少不了大量配置交换机。<br>
所以这里写一个python脚本，把可以自动化登录设备刷配置，然后显示检测命令结果和ping检测结果，从而减少人成本。

##设计思路

比较简单，就是实现读取操作单（configuration.txt）中的内容，获取需要配置的设备和命令已经检测步骤，然后通过配置文件（config.py）里面的参数来获取设备登录帐号密码和登录方式等信息进行自动化登录设备刷配置。
<br>
由于这个脚本会对每一步进行检测并提示操作者是否继续，所以没有使用多进程来做，串行逐个执行变更单的设备和配置。所以在文件夹（autoconfig_beta）中添加了无脑多进程批量刷配置的脚本。
<br>
这个脚本用python写的，而且不需要额外按照任何库，对于linux基础比较弱的网工来说可以是分分钟就能上手。


##操作简介
如上面介绍，config.py文件主要是配置登录设备的相关参数<br>
'config_username':'test',     #有配置权限的帐号，如果不填会让你每次输入,因为有些大厂就是动态的3A帐号密码<br>
'config_password':'test',  #有配置权限帐号的密码，同上<br>
'show_username':'test_show',       #只有show权限的帐号，如果不填会直接使用配置权限帐号<br>
'show_password':'test_show',    #只有show权限的帐号的密码，如果不填会直接使用配置权限帐号的密码<br>
'ssh_port':'22',                  #ssh的端口号，默认是22<br>
'login_method':'telnet',             #登录方式，填写ssh或者telnet<br>
'login_user_identification':':',  #telnet方式需要填写对应设备的登录时账户输入的标识符，本人亲测大部分就是login:和username:,用:就行，不用改<br>
'login_password_identification':'assword:' #同上，输入密码的标识符,这个我看了juniper、cisco、hw、h3c基本都是这个，所以也不用改<br>

操作单是
configuration.tx<br>

$IP:<br>
10.1.1.11<br>
$CONFIG:<br>
configure terminal<br>
interface eth1/1<br>
ip add ress 1.1.1.1<br>
$CHECK:<br>
terminal length 0<br>
show clock<br>
$PING:<br>
10.1.1.240<br>
$CONFIG:<br>
configure terminal<br>
hostname 123<br>
$PING:<br>
10.1.1.240<br>
10.1.1.119<br>


可以看到每个设备需要包含$IP:、$CONFIG:、$CHECK:、$PING:等参数<br>
$IP:下只能填写一个设备的管理ip<br>
$CONFIG:下可以写条需要执行的命令<br>
$CHECK:下写多条进行展示的命令，为了防止一些设备show的东西很多要输入more，我建议在交换机上先输入terminal length 0（思科） screen-length 0 temporary（华为）其他也差不多，来防止出现more这种分屏显示<br>
$IP:下填写要ping的地址，因为我们做一些操作，经常怕把网干断了，所以需要ping检测一下<br>

由上面可知，一个管理IP可能存在多个$CONFIG:、$CHECK:、$PING:这样的组合步骤，所以支持，一个$IP:下包含多个这样的模块。

执行结果如下<br>
![](https://github.com/luffycjf/auto_config_switch_router/blob/master/jietu.png)


##补充

autoconfig_beta文件下是简单粗暴的批量多进程刷配置。
比如刷全网所有设备的acl或者snmp这种配置，全网上千台设备，一个个刷太累了，再或者巡检，让你去show全网设备的板卡信息，这也太累了是不是。<br>
由于设备量太大，也没必要说每一步都要检查，所以直接多进程并发去下发命令，哐哐哐就是干！最后会把结果保存到文本result.txt中。<br>
如果有登录失败会爆出来
类似的也有一个config.py<br>
里面参数和之前类似，多了'multiprocess':'2'                #用来多进程数量<br>

然后就是configuration.txt
只由 $IP:、$CONFIG:组成
$IP:可以由多个IP地址组成
比如<br>
$IP:<br>
1.1.1.1<br>
2.2.2.2<br>
$CONFIG:<br>
show run<br>
show clock<br>
<br>
$IP:<br>
3.3.3.3<br>
$CONFIG:<br>
show time<br>

执行过程就是，在1.1.1和2.2.2上执行相同的命令show run和show clock。<br>
在3.3.3.3上执行show time。如果可以执行就将结果保存在result.txt中。