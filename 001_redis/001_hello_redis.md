# Redis

Redis 是一个nosql 数据库（非结构化的数据库）主要是以【key-value】的方式存储的

## redis key

redis key 是一个字符串，可以包含任意的字符，但是不能包含换行符，否则会报错

## redis value

redis 的value 包含很多格式，通常说的数据类型指的是value的数据类型，有以下集中基本数据类型

- String 字符串
- Hash 哈希表(map/dict)
- List 列表
- Set 集合
- ZSet 有序集合

## redis 的通用命令

通用命令指的是部分数据类型，都可以只用的指令

- KEYS 获取指规则的key值
分布
```redis
 KEYS pattern
 summary: Find all keys matching the given pattern

 -- 数据量特别多的时候效率不高
 keys *   ：获取所有键值对的key
 keys a*  ：获取所有以a开头的键值对的key
 keys *a* ：获取所有包含a的键值对的key
 
```

- DEL 删除指定的key的键值对

```redis
 DEL key1 [key2 ...]
 summary: Delete a key

 -- 删除指定的key
 DEL key1 [key2 key3] ：删除key1 key2 key3,返回删除的个数
```

- EXISTS 判断指定的key是否存在 存在返回:1 不存在返回:0

```redis
 EXISTS key1 [key2 ...]
 summary: Determine if a key exists

 -- 判断key是否存在 当传入多个key值时，只要有一个key存在就返回1
 EXISTS name hello ：判断name hello是否存在 其中name不存在  hello存在 所以返回 1
```

- EXPIRE 给指定的key设置过期时间，当时间为归0之后自动删除改key

```redis
 EXPIRE key seconds
 summary: Set a key‘s time to live in seconds

 -- 设置key的过期时间 单位是s
 EXPIRE name 30 ：name的过期时间为30s，过期后自动删除
```

- TTL 查看一个key的剩余有效期 返回的是xxx s

```redis
 TTL key
 summary: Get the time to live for a key

 -- 返回值  -1：不会过期 -2：不存在 >0: 返回的是剩余有效时间
 127.0.0.1:6379> ttl name
 (integer) 93
```
## Key的结构层次划分
redis为了纺织不同的功能的key值重复，使用“:” 拼接key的长度，进行分成

```redis
127.0.0.1:6379> set xc:xc_flask:name xc_name
OK
127.0.0.1:6379> set xb:xb_python:name xb_pyton
OK

-- 分级结构
xc
 xc_flask
  name
    ->xc_flask
xb
 xb_python
  name
  ->xc_python
  
本质上还是两个字符串，只不过按照 : 拼接分成，分别属于不同功能的key
```