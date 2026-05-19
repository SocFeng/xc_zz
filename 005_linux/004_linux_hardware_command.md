## 常见的Linux 硬件命令操作

- 【df -h】 显示磁盘空间大小
```shell
[xc@localhost local_vim]$ df -h
文件系统             容量  已用  可用 已用% 挂载点
devtmpfs             4.0M     0  4.0M    0% /dev
tmpfs                838M     0  838M    0% /dev/shm
tmpfs                335M  8.8M  327M    3% /run
/dev/mapper/cs-root   47G   12G   36G   24% /
/dev/sda1            960M  376M  585M   40% /boot
tmpfs                168M  124K  168M    1% /run/user/1000
/dev/sr1              13G   13G     0  100% /run/media/xc/CentOS-Stream-9-BaseOS-x86_64
/dev/sr0             171M  171M     0  100% /run/media/xc/CDROM
```
- 【free -m】 以MB的方式显示内存使用情况
```shell
[xc@localhost local_vim]$ free  # kb方式显示
               total        used        free      shared  buff/cache   available
Mem:         1714860      979268      202840        5232      716160      735592
Swap:        2109436      773728     1335708
[xc@localhost local_vim]$ free -g   #MB方式显示
               total        used        free      shared  buff/cache   available
Mem:               1           0           0           0           0           0
Swap:              2           0           1
[xc@localhost local_vim]$ free -m   #GB方式显示
               total        used        free      shared  buff/cache   available
Mem:            1674         979         175           5         699         695
Swap:           2059         755        1304
****
```

- 【ip addr】 显示网络信息
```shell
[xc@localhost local_vim]$ ip addr
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host 
       valid_lft forever preferred_lft forever
2: ens33: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether 00:0c:29:b8:37:bf brd ff:ff:ff:ff:ff:ff
    altname enp2s1
    inet 192.168.184.130/24 brd 192.168.184.255 scope global dynamic noprefixroute ens33
       valid_lft 1650sec preferred_lft 1650sec
    inet6 fe80::20c:29ff:feb8:37bf/64 scope link noprefixroute 
       valid_lft forever preferred_lft forever
3: br-4c56d5c33675: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc noqueue state DOWN group default 
    link/ether 02:91:f4:c9:a0:34 brd ff:ff:ff:ff:ff:ff
    inet 172.18.0.1/16 brd 172.18.255.255 scope global br-4c56d5c33675
       valid_lft forever preferred_lft forever
4: docker0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default 
    link/ether 06:b6:4b:d1:26:2c brd ff:ff:ff:ff:ff:ff
    inet 172.17.0.1/16 brd 172.17.255.255 scope global docker0
       valid_lft forever preferred_lft forever
    inet6 fe80::4b6:4bff:fed1:262c/64 scope link 
       valid_lft forever preferred_lft forever
23: veth4aee172@if2: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master docker0 state UP group default 
    link/ether 86:dd:93:56:a9:49 brd ff:ff:ff:ff:ff:ff link-netnsid 0
    inet6 fe80::84dd:93ff:fe56:a949/64 scope link 
       valid_lft forever preferred_lft forever
24: br-cc41ce180b9f: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc noqueue state DOWN group default 
    link/ether 16:5b:85:80:a9:a3 brd ff:ff:ff:ff:ff:ff
    inet 172.19.0.1/16 brd 172.19.255.255 scope global br-cc41ce180b9f
       valid_lft forever preferred_lft forever
    inet6 fe80::145b:85ff:fe80:a9a3/64 scope link 
       valid_lft forever preferred_lft forever

```
