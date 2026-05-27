# 什么是MVCC多版本并发控制

数据库将每行的数据，维护多个版本，读操作读取某个时间点的快照版本，写炒作创建新的版本，这样实现读不阻塞，写不阻塞。

* 提高斌发新能
* 实现了: 1 可重复读 2 读已提交

## 原理

通过三个隐藏的字段 + Read View + Undo Log 实现

### 隐藏字段
作用是标记事务和数据，以及串联各个版本
- DB_TRX_ID：最近更新这条事务的id
- DB_ROLL_PTR：指向Undo Log中的旧版本
- DB_ROW_ID：数据行的ID

### Read View
用于查询，读取哪一个版本的数据
- 当前事务id
- 当前未提交的事务id  min_tr_id
- 未开始的事务id(已被分配的事务id的最大值+1)  max_trx_id

### 流程
每当一个事务修改了某行数机就通过Undo log做一个版本
这个版本包含，当前修改事务的id 数据的行id 旧数据的地址

- 数据开始读取的流程：
```shell
最新修改的版本数据的修改的事务id: DB_TRX_ID
Read View中当前事务id: creator_trx_id
Read View中未提交的事务id最小值:min_trx_id
Read View中 已分配的事务最大id+1:max_trx_id
  
   if DB_TRX_ID == creator_trx_id:
        return 当前事务保存的数据能够直接读取
   if DB_TRX_ID < min_trx_id:
        return 最新版本的数据是已经提交的数据,直接读取
   if DB_TRX_ID >= max_trx_id:
        return 不能读取数据
   if min_trx_id < DB_TRX_ID < max_trx_id:
        根据指针找历史版本数据指导找到，历史数据中DB_TRX_ID
        再从到到位执行以下判断
```

MVCC中实现 实现读已提交和不可重复读的区别就是:
- 读已提交，每个读取都会创建一个Read View
- 可重复读：只有第一次创建的时候会创建Read View



