## 文件和目录命令

### 基础的文件命令

- 【ls/ll(ls -al)/tree】 显示当前目录下的文件和文件夹(显示的方式不同)

```shell
[xc@localhost ~]$ ls
公共  图片  音乐       compat-openssl10-1.0.2o-3.el8.x86_64.rpm    local_nginx  nginx_index_61.tar
模板  文档  桌面       compat-openssl10-1.0.2o-3.el8.x86_64.rpm.1  local_redis  RPM-GPG-KEY-mysql
视频  下载  atguigudb  dump.rdb      

[xc@localhost ~]$ ll
总用量 163028
drwxr-xr-x. 2 xc   xc           6  9月 17  2025 公共
drwxr-xr-x. 2 xc   xc           6  9月 17  2025 模板
drwxr-xr-x. 2 xc   xc           6  9月 17  2025 视频
...

xc@localhost ~]$ tree
.
├── 公共
├── 图片
...
├── 桌面
├── atguigudb
│   └── atguigudb.sql
├── compat-openssl10-1.0.2o-3.el8.x86_64.rpm
├── compat-openssl10-1.0.2o-3.el8.x86_64.rpm.1

```

- 【pwd】 显示当亲啊所有的目录文件路径

```shell
[xc@localhost ~]$ pwd
/home/xc

```

- 【mkdir -p 文件夹1 文件夹2 ...】 创建文件夹 -p 级联创建

```shell
[xc@localhost ~]$ mkdir -p local_dir/test1 local_dir/test2 local_dir/test3
[xc@localhost ~]$ cd local_dir/
[xc@localhost local_dir]$ tree
.
├── test1
├── test2
└── test3

```

- 【touch 文件1 文件2 ...】 创建文件

```shell
[xc@localhost local_dir]$ touch ikun.txt lanqiu.txt rap.txt

[xc@localhost local_dir]$ ll
总用量 0
-rw-r--r--. 1 xc xc 0  5月 19 13:12 ikun.txt
-rw-r--r--. 1 xc xc 0  5月 19 13:12 lanqiu.txt
-rw-r--r--. 1 xc xc 0  5月 19 13:12 rap.txt
drwxr-xr-x. 2 xc xc 6  5月 19 13:11 test1
drwxr-xr-x. 2 xc xc 6  5月 19 13:11 test2
drwxr-xr-x. 2 xc xc 6  5月 19 13:11 test3

```

- 【rm -rf 文件1 文件2 ...】 删除文件/文件夹(对递归删除) -r 递归删除 -f代表删除的是一个文件

```shell
[xc@localhost ~]$ rm -rf local

```

- 【cp 文件1 文件2】 将文件1复制到文件2

```shell
-- 文件1 有内容 文件2没有内容
[xc@localhost local_dir]$ cp ikun.txt lamqiu.txt

[xc@localhost local_dir]$ cat lamqiu.txt 
da jia hao
wo
shi
lian
xi
liang
nian
ban
de
ikun


```

- 【cp -r 目录1 目录2】 递归的将目录1 复制到目录2

```shell
[xc@localhost local_dir]$ cd test2
[xc@localhost test2]$ mkdir test2-1
[xc@localhost test2]$ mkdir test2-2
[xc@localhost test2]$ touch 1.info
[xc@localhost test2]$ tree
.
├── 1.info
├── test2-1
└── test2-2

[xc@localhost local_dir]$ cp -r test2 test1
[xc@localhost local_dir]$ tree
.
├── ikun.txt
├── lamqiu.txt
├── lanqiu.txt
├── rap.txt
├── test1
│   └── test2
│       ├── 1.info
│       ├── test2-1
│       └── test2-2
├── test2
│   ├── 1.info
│   ├── test2-1
│   └── test2-2
└── test3



```

- 【mv 目录|文件 目录1】 将目录或者文件移动到目录1下面

```shell
[xc@localhost local_dir]$ mv test1/test2/1.info test3
[xc@localhost local_dir]$ tree
.
├── ikun.txt
├── lamqiu.txt
├── lanqiu.txt
├── rap.txt
├── test1
│   └── test2
│       ├── test2-1
│       └── test2-2
├── test2
│   ├── 1.info
│   ├── test2-1
│   └── test2-2
└── test3
    └── 1.info


```

- 【cat 文件】 打开一个文件，查看文件的和内容

```shell
[xc@localhost local_dir]$ cat lamqiu.txt 
da jia hao
wo
shi
lian
xi
liang
nian
ban
de
ikun

```

- 【head -num 文件】 单开一个文件只显示前 num行

```shell
[xc@localhost local_dir]$ head -3 lamqiu.txt 
da jia hao
wo
shi
```

- 【tail -num 文件】 打开一个文件只显示后num行

```shell

[xc@localhost local_dir]$ tail -3 lamqiu.txt 
ban
de
ikun


```

### 检索

- 【grep ‘表达式’ 文件】 在文件中检索指定表达式的数据
```shell
[xc@localhost local_dir]$ grep 'an' /home/xc/local_dir/lamqiu.txt 
lian
liang
nian
ban

```
- 【grep -r ‘表达式’ 目录】 在指定目录下面递归检索
```shell
[xc@localhost local_dir]$ grep -r 'an' /home/xc/local_dir 
/home/xc/local_dir/ikun.txt:lian
/home/xc/local_dir/ikun.txt:liang
/home/xc/local_dir/ikun.txt:nian
/home/xc/local_dir/ikun.txt:ban
/home/xc/local_dir/lamqiu.txt:lian
/home/xc/local_dir/lamqiu.txt:liang
/home/xc/local_dir/lamqiu.txt:nian
/home/xc/local_dir/lamqiu.txt:ban

```
- 【find 目录1 -name ‘规则’】 再指定目录下面查找以指定规则的文件
```shell
[xc@localhost local_dir]$ find . -name 'l*.txt'
./lanqiu.txt
./lamqiu.txt

```
- 【find 目录 -size +10000k】在主文件夹中查找大于10000k的文件
```shell

```

### 压缩和解压

- 【tar -zxvf 压缩包名.tar.gz】 解压一个文件
- 【tar -zcvf 压缩包名.tar.gz 目标文件/文件夹】
    - z：调用 gzip 压缩，处理 .tar.gz 格式
    - c：create 创建新压缩包
    - v：verbose 显示压缩过程详情（可视化过程）
    - f：file 指定压缩包文件名，必须放最后
```shell
-- 压缩
[xc@localhost test1]$ tar -zcvf test.tar test2 .
test2/
test2/test2-2/
test2/test2-1/
./
./test2/
./test2/test2-2/
./test2/test2-1/
./test.tar

[xc@localhost test1]$ tree
.
├── test2
│   ├── test2-1
│   └── test2-2
└── test.tar


-- 解压
[xc@localhost test1]$ rm -rf test2
[xc@localhost test1]$ ls
test.tar

[xc@localhost test1]$ tar -zcvf test.tar .
./
./test.tar
****

```

### 问年间和文件夹权限
- 【chmod -R xxx 文件或文件夹】 设置文件或文件夹的权限
```shell
xc@localhost local_dir]$ ll
总用量 8
-rw-r--r--. 1 xc xc 49  5月 19 13:13 ikun.txt
drwxr-xr-x. 2 xc xc 22  5月 19 13:30 test1
drwxrwxrwx. 4 xc xc 50  5月 19 13:16 test2 --- 权限
drwxr-xr-x. 2 xc xc 20  5月 19 13:18 test3


[xc@localhost local_dir]$ cd test2/
[xc@localhost test2]$ ll
总用量 0
-rwxrwxrwx. 1 xc xc 0  5月 19 13:16 1.info
drwxrwxrwx. 2 xc xc 6  5月 19 13:16 test2-1
drwxrwxrwx. 2 xc xc 6  5月 19
```

