## 常见的Linux 系统命令操作

- 【uname】显示系统信息

```shell
[xc@localhost local_vim]$ uname
Linux
```

- 【uname -r】显示内核版本信息

```shell
[xc@localhost local_vim]$ uname -r
5.14.0-615.el9.x86_64
```

- 【hostname】显示主机系统名称

```shell
xc@localhost local_vim]$ hostname
localhost.localdomain

```

- 【hostname -i】显示系统ip地址

```shell
[xc@localhost local_vim]$ hostname -i
::1 127.0.0.1

```

- 【date】显示当前时间

```shell
[xc@localhost local_vim]$ date
2026年 05月 19日 星期二 12:30:51 CST

```

- 【w】显示系统当前登录的用户

```shell
[xc@localhost local_vim]$ w
 12:31:00 up 1 day, 14:07,  2 users,  load average: 0.17, 0.14, 0.15
USER     TTY        LOGIN@   IDLE   JCPU   PCPU WHAT
xc       seat0     244月26  0.00s  0.00s  0.00s /usr/libexec/gdm-wayland-session --register-session gnome-session
xc       tty2      244月26 24days  0.07s  0.07s /usr/libexec/gnome-session-binary

```

- 【whoami】显示当你的登录身份

```shell
[xc@localhost local_vim]$ whoami
xc

```


