## 存储引擎
见简单的来说存储引擎就是表的类型，接收上层的指令
- InnoDB： 支持事务（事务的提交和回滚）
  - ibdata 存放存放数据信息
  - xxx.frm 表结构
  - xxx.ibd 存储数据信息和索引信息
- MyISAM：
  - xxx.myd 数据信息文件 
  - xxx.myi 存放索引信息文件  
  - xxx.sdi 存放表结构文件


## InnoDB和MyISAM的区别
1. InnoDB支持事务，行锁，外键，奔溃恢复
2. MyISAM不支持事务，表锁，查询快
