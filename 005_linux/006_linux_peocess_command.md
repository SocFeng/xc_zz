## 系统和进程命令

### 进程相关
- 【top/htop】 显示所有在运行的进程
```shell
Cpu(s): 18.4 us,  1.0 sy,  0.0 ni, 75.1 id,  0.0 wa,  4.5 hi,  0.9 si,  0.0 st
MiB Mem :   1674.7 total,    185.8 free,    961.0 used,    707.3 buff/cache
MiB Swap:   2060.0 total,   1337.9 free,    722.1 used.    713.7 avail Mem 

    PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND                                          
   1389 xc        20   0 4260308 195176  54568 S  34.2  11.4  28:18.31 gnome-shell                                      
   6728 xc        20   0  957776  37576  25752 S   4.9   2.2   2:56.79 gnome-terminal-                                  
   2604 xc        20   0  674376   5188   2732 S   1.6   0.3   3:06.68 ibus-daemon                                      
  19133 xc        20   0  235924   7732   6148 R   1.0   0.5   0:00.17 top                                              
   2226 xc        20   0  389784   9780   7656 S   0.7   0.6  19:58.13 vmtoolsd                                         
     17 root      20   0       0      0      0 I   0.3   0.0   1:21.23 rcu_preempt                                      
    808 root      20   0  461764   5772   4632 S   0.3   0.3  16:56.27 vmtoolsd                                         
   1067 root      20   0 1876084  20436   7760 S   0.3   1.2   5:14.07 containerd
   
   
   
```

- 【ps】 希纳是活动的进程
```shell
[xc@localhost test2]$ ps
    PID TTY          TIME CMD
  15090 pts/1    00:00:02 bash
  19151 pts/1    00:00:00 ps

```

- 【kill 进程id】 结束某个进程运行

- 【lsof】 进程打开的文件

- 【ps aux | grep '进程名'】 检索进程名的id

```shell
[xc@localhost test2]$ ps aux | grep 'mysql'
mysql       1237  0.0  0.3 1547392 6172 ?        Ssl  5月17   0:59 /usr/libexec/mariadbd --basedir=/usr
root       15087  0.0  0.1 237024  2216 pts/0    S+   5月18   0:00 mysql
xc         19553  0.0  0.1 221820  2776 pts/1    S+   13:50   0:00 grep --color=auto mysql

```

### 网络相关
- 【ifconfig】 网络地址信息
```shell
[xc@localhost test2]$ ifconfig
br-4c56d5c33675: flags=4099<UP,BROADCAST,MULTICAST>  mtu 1500
        inet 172.18.0.1  netmask 255.255.0.0  broadcast 172.18.255.255
        ether 02:91:f4:c9:a0:34  txqueuelen 0  (Ethernet)
        RX packets 1126320  bytes 1607269311 (1.4 GiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 66141  bytes 5059740 (4.8 MiB)
        TX errors 0  dropped 1 overruns 0  carrier 0  collisions 0

br-cc41ce180b9f: flags=4099<UP,BROADCAST,MULTICAST>  mtu 1500
        inet 172.19.0.1  netmask 255.255.0.0  broadcast 172.19.255.255
        inet6 fe80::145b:85ff:fe80:a9a3  prefixlen 64  scopeid 0x20<link>
        ether 16:5b:85:80:a9:a3  txqueuelen 0  (Ethernet)
        RX packets 23  bytes 1339 (1.3 KiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 175  bytes 23641 (23.0 KiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

docker0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 172.17.0.1  netmask 255.255.0.0  broadcast 172.17.255.255
        inet6 fe80::4b6:4bff:fed1:262c  prefixlen 64  scopeid 0x20<link>
        ether 06:b6:4b:d1:26:2c  txqueuelen 0  (Ethernet)
        RX packets 154  bytes 19944 (19.4 KiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 227  bytes 28304 (27.6 KiB)
        TX errors 0  dropped 68 overruns 0  carrier 0  collisions 0

ens33: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.184.130  netmask 255.255.255.0  broadcast 192.168.184.255
        inet6 fe80::20c:29ff:feb8:37bf  prefixlen 64  scopeid 0x20<link>
        ether 00:0c:29:b8:37:bf  txqueuelen 1000  (Ethernet)
        RX packets 1126320  bytes 1607269311 (1.4 GiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 66141  bytes 5059740 (4.8 MiB)
        TX errors 0  dropped 1 overruns 0  carrier 0  collisions 0

lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        inet6 ::1  prefixlen 128  scopeid 0x10<host>
        loop  txqueuelen 1000  (Local Loopback)
        RX packets 98866  bytes 6909600 (6.5 MiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 98866  bytes 6909600 (6.5 MiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

veth4aee172: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet6 fe80::84dd:93ff:fe56:a949  prefixlen 64  scopeid 0x20<link>
        ether 86:dd:93:56:a9:49  txqueuelen 0  (Ethernet)
        RX packets 23  bytes 1339 (1.3 KiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 175  bytes 23641 (23.0 KiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

```

- 【ping 指定地址】 检查对某个网络是否通畅
```shell
[xc@localhost test2]$ ping www.baidu.com
PING www.wshifen.com (103.235.46.102) 56(84) 比特的数据。
64 比特，来自 103.235.46.102 (103.235.46.102): icmp_seq=1 ttl=128 时间=0.617 毫秒
64 比特，来自 103.235.46.102 (103.235.46.102): icmp_seq=2 ttl=128 时间=0.655 毫秒
64 比特，来自 103.235.46.102 (103.235.46.102): icmp_seq=3 ttl=128 时间=0.651 毫秒
64 比特，来自 103.235.46.102 (103.235.46.102): icmp_seq=4 ttl=128 时间=0.595 毫秒
64 比特，来自 103.235.46.102 (103.235.46.102): icmp_seq=5 ttl=128 时间=0.777 毫秒

```

- 【netstat -p 80】 显示监控的端口信息
```shell
xc@localhost test2]$ netstat -p 80
(Not all processes could be identified, non-owned process info
 will not be shown, you would have to be root to see it all.)
Active Internet connections (w/o servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name    
tcp        0      0 localhost.localdo:58610 151.101.1.91:https      TIME_WAIT   -                   
tcp        0      0 localhost.localdo:56094 93.243.107.34.bc.:https TIME_WAIT   -                   
tcp        0      0 localhost.localdo:33072 104.17.25.14:https      ESTABLISHED 19190/firefox       
tcp        0      0 localhost.localdo:40612 151.101.1.91:https      ESTABLISHED 19190/firefox       
tcp        0      0 localhost.localdo:57608 151.101.1.91:https      TIME_WAIT   -                   
tcp        0      0 localhost.localdo:58292 104.18.1.22:https       ESTABLISHED 19190/firefox       
tcp        0      0 localhost.localdo:46234 191.144.160.34.bc:https ESTABLISHED 19190/firefox     
```