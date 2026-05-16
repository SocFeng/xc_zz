
## String 类型

String类型值得是值的类型，在redis中做一些简单的数据结构存储
string类型数据存储的数据可以分为3类

- string 字符串 最大上限不超过510M
- int 整数
- float 浮点数

### String 数据类型格式
![img_1.png](img_1.png)

### String 常见的操作

- SET 添加或者修改一个key的值
```redis
 SET key value
 summary: Set the string value of a key

 -- 添加一个键值对 name:zhangshan  返回值是ok
 27.0.0.1:6379>  set name zhangshan
 OK
```
- GET 获取指定key的值
```redis
 GET key
 summary: Get the value of a key
 -- 返回指定键值对的值
 127.0.0.1:6379> get name
 "zhangshan"
```
- MSET 批量添加多对键值对
```redis
 MSET key value [key value ...]
 summary: Set multiple keys to multiple values
 
 -- 同时设置多对键值对
 127.0.0.1:6379> mset name1 LISI age 20
 OK
```
- MGET 批量获取多个键值对
```redis
 MGET key [key ...]
 summary: Get the values of all the given keys

 -- 批量获取多个键值对 指定key的value序列
 127.0.0.1:6379> mget name name1 age
 1) "zhangshan"
 2) "LISI"
 3) "30"
```
- INCR 递增一个key的值 +1（用于整数类型）
```redis
 INCR key
 summary: Increment the integer value of a key by one

 -- 给指定的key数字+1 
 127.0.0.1:6379> incr age
 (integer) 31
```
- INCRBY 个key的值增加指定大小
```redis
  INCRBY key increment
 summary: Increment the integer value of a key by the given amount
 
 -- 给指定的key的数字增加指定的整数大小
 127.0.0.1:6379> INCRBY age -5
 (integer) 26
```
- INCRBYFLOAT 让一个key指定增加指定的大小用于浮点数
```redis
  INCRBYFLOAT key increment
 summary: Increment the float value of a key by the given amount
 
 -- 给指定的key的数字增加指定的浮点数大小
 127.0.0.1:6379>  INCRBYFLOAT f 99.11
 "100.34000000000000341"
```
- SETNX 添加一个键值对，但是需要这个键值对不存在（前提这个key不存在）
```redis
 SETNX key value
 summary: Set the value of a key, only if the key does not exist
 
 -- 添加一个不存在的key的键值对，存在不添加返回 0 不存在添加 返回了
 127.0.0.1:6379> setnx name liului
 (integer) 0
```
- SETEX 添加一个键值对的时候，设置有效器
```redis
 SETEX key seconds value
 summary: Set the value and expiration of a key

 -- 添加一个键值对，并设置有效时间
 127.0.0.1:6379> setex ttname 300 hualal
 OK
```

- STRLEN 获取字符串的长度与
```redis
 STRLEN key
 summary: Get the length of the value stored in a key
 
 -- 获取指定key的值的字符串的长度（string int float）都可以
 127.0.0.1:6379> strlen name
 (integer) 5
 127.0.0.1:6379> strlen f
 (integer) 21
 127.0.0.1:6379> strlen age
 (integer) 2
```
- GETRANGE 获取指定key 在某个范围内的数据
```redis
  GETRANGE key start end
 summary: Get a substring of the string stored at a key

 -- 获取指定key的某个范围内的数据
 127.0.0.1:6379> get f
 "100.34000000000000341"
 127.0.0.1:6379> GETRANGE f 3 9
 ".340000"
```

- GETSET 获取指定key的值，并设置新的值
```redis
 GETSET key value
 summary: Set the string value of a key and return its old value
 -- 获取指定key的值，并设置新的值

 127.0.0.1:6379> getset name hello_world
 "llili"
```
