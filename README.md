## 背景介绍

本人在互联网工作多年，混迹过bat中两家，都是屌丝网工，即便两家自动化程度都已经非常高了，但网工在日常工作种任然少不了大量配置交换机。<br>
所以这里写一个python脚本，把可以自动化登录设备刷配置，然后显示检测命令结果和ping检测结果，从而减少人成本。<br>

github地址：<https://github.com/luffycjf/auto_config_switch_router>
<br>
这里也提供一个百度网盘的下载地址
链接: <https://pan.baidu.com/s/1qZEWsHI> 密码: ignz



## 设计思路

比较简单，就是实现读取操作单（configuration.txt）中的内容，获取需要配置的设备管理IP和命令以及检测步骤，然后通过配置文件（config.py）里面的参数来获取设备登录帐号密码和登录方式等信息进行自动化登录设备刷配置。
<br>
由于这个脚本会对每一步进行检测并提示操作者是否继续，所以变更单里面的操作顺序可能比较重要，所以没有使用多进程来做，串行逐个执行变更单的设备和配置。<br>
但是考虑到我们日常可能会用到需要刷大量设备配置，所以在文件夹（autoconfig_beta）中添加了无脑多进程批量刷配置的脚本，这个在最后再介绍。
<br>
这个脚本用python写的，而且不需要额外按照任何库，对于linux基础比较弱和没有python基础的网工来说可以是分分钟就能上手。<br>
就是界面有点丑。。。

## 操作简介

如上面介绍，config.py文件主要是配置登录设备的相关参数<br>

``` python
'config_username':'test',     #有配置权限的帐号，如果不填会让你每次输入,因为有些大厂就是动态的3A帐号密码，所以这块不填方便你每次输入
'config_password':'test',  #有配置权限帐号的密码，同上
'show_username':'test_show',       #只有show权限的帐号，如果不填会直接使用配置权限帐号，分离可以防止一些配置命令误敲
'show_password':'test_show',    #只有show权限的帐号的密码，如果不填会直接使用配置权限帐号的密码
'ssh_port':'22',                  #ssh的端口号，默认是22
'login_method':'telnet',             #登录方式，填写ssh或者telnet
'login_user_identification':':',  #telnet方式需要填写对应设备的登录时账户输入的标识符，本人亲测大部分就是login:和username:,用:就行，不用改
'login_password_identification':'assword:' #同上，输入密码的标识符,这个我看了juniper、cisco、hw、h3c基本都是这个，所以也不用改
``` 

操作单是文件 configuration.txt<br>
以下是一个demo

``` python
$IP:
10.1.1.11
$CONFIG:
configure terminal
interface eth1/1
ip add ress 1.1.1.1
$CHECK:
terminal length 0
show ip int brief
$PING:
1.1.1.1
$CONFIG:
configure terminal
hostname 123
$PING:
10.1.1.240
10.1.1.119

$IP:
10.1.1.12
$CONFIG:
configure terminal
interface eth1/1
ip add ress 2.2.2.2
no shutdown
$CHECK:
terminal length 0
show ip int brief
$PING:
2.2.2.2
```

可以看到每个设备需要包含$IP:、$CONFIG:、$CHECK:、$PING:等参数<br>
$IP:下只能填写一个设备的管理ip<br>
$CONFIG:下可以写条需要执行的命令<br>
$CHECK:下写多条进行展示的命令，为了防止一些设备show的东西很多要输入more，我建议在交换机上先输入terminal length 0（思科） screen-length 0 temporary（华为）其他也差不多，来防止出现more这种分屏显示（这块如果为了针对厂商做自动more一方面比较麻烦，有的厂商不是more，而且会有more显示到回显）<br>
$IP:下填写要ping的地址，因为我们做一些操作，经常怕把网干断了，所以需要ping检测一下<br>

由上面可知，一个管理IP可能存在多个$CONFIG:、$CHECK:、$PING:这样的组合步骤，所以支持一个$IP:下包含多个$CONFIG:、$CHECK:、$PING:这样组合的模块。

执行结果如下(这个和上面操作单的内容不符，随便找了设备测试的)<br>
![](http://182.61.38.60/jietu.png)<br>



## 多进程刷配置版

autoconfig_beta文件下是简单粗暴的批量多进程刷配置。<br>
正如前面所说，比如刷全网所有设备的acl或者snmp这种配置，全网上千台设备，一个个刷太累了，再或者巡检，让你去show全网设备的板卡信息，这也太累了是不是。<br>
由于设备量太大，配置简单（没啥风险，甚至就是为了巡检采集信息用），也没必要说每一步都要检查，所以直接多进程并发去下发命令，哐哐哐就是干！最后会把结果保存到文本result.txt中。<br>
如果有登录失败会爆出来
类似的也有一个config.py<br>
里面参数和之前类似，只是多了'multiprocess':'3'     #这个就是用来指定多进程的数量，指定几个就是同时登录几台设备去刷配置<br>

然后就是configuration.txt
只由 $IP:、$CONFIG:组成，结构清晰很多有木有
$IP: 可以由多个IP地址组成比如

``` python
$IP:
1.1.1.1
2.2.2.2
$CONFIG:
show run
show clock

$IP:
3.3.3.3
$CONFIG:
show time

```

执行过程就是，在1.1.1和2.2.2上执行相同的命令show run和show clock。<br>
在3.3.3.3上执行show time。<br>
如果可以登录就将结果保存在result.txt中，即便登录失败也会报出来并保存在result.txt中方便排错。<br>
由于多进程数量是3，所以会三台一起登录分别刷配置，高效很多有木有！


## 多进程采集-ssh

auto_show文件夹下onecollect.py是简单粗暴的批量多进程ssh采集。<br>
使用方法很简单，在config文件里面填下设备帐号密码IP和命令,最大五个进程。python onecollect.py抓取完信息会放在设备名生成的文件夹下，加上日期。
如果进行批量设备采集信息收集可以使用，效率杠杠的。
此版本可以抓全设备回显，是之前的升级版本.




