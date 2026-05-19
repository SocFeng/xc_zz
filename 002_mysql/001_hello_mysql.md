# MySQL 学习和回顾


-- 主要回顾高级知识 基础的基本上差不多不在回顾
## 基础

- SQL 结构化询语言

> 是一种标准的结构化的操作数据库的，查询语言，是一种标准的数据库查询语言，但是各个数据库依然有自己的标准。
> 基本语法基本语法相同，但是有自己的特色。

- SQL分类
    - DDL(数据定义语言)：数据库定义语言，用于数据库、数据表、视图、索引等数据库对象，还能用来创建、删除、修改数据库和数据表的结构。
        * CREATE
        * DROP
        * ALTER
        * ...
    - DML(数据管理语言)：用于添加、删除、更新和查询数据库的记录，并检查数据的完整性。
        * INSERT
        * SELECT
        * UPDATE
        * DELETE
        * ...
    - DCL(数据控制语言)：用于定义数据库、表、字段、用户的访问权限和安全级别.
        * GRANT
        * REVOKE
        * COMMIT
        * ROLLBACK
        * SAVEPOINT
        * ...
    - DQL(数据查询语言)：因为查询数据比较常用且重要，单独提取出来的

- 注释
  ```sql
    使用 '--'  来进行注释
    s使用 '#' 进行单行注释
    使用多行注释 "/* 内容*/" 
  
    -- SELECT * FROM USER
    # SELECT * FROM USER
    /*
        SELECT * FROM USER
        SELECT * FROM USER
    */
  
    
    ```
- 导入
  ```sql
    外部sql数据导入数据库
    MariaDB [mysql]> source /home/xc/atguigudb/atguigudb.sql
  
    MariaDB [atguigudb]> show databases;
    +--------------------+
    | Database           |
    +--------------------+
    | atguigudb          |
    | information_schema |
    | my_xc              |
    | mysql              |
    | performance_schema |
    +--------------------+
    5 rows in set (0.002 sec)
  
  
   -- 查看档期那数据库中的表
    MariaDB [atguigudb]> show tables;
    +---------------------+
    | Tables_in_atguigudb |
    +---------------------+
    | countries           |
    | departments         |
    | emp_details_view    |
    | employees           |
    | job_grades          |
    | job_history         |
    | jobs                |
    | locations           |
    | order               |
    | regions             |
    +---------------------+


   ```

### SELECT使用 (DSL)

### SQL的DDL、DML、DCL使用

### 其他数据库对象

### MySQL的特性

## 高级

### MySQL架构

### 索引及调优

### 事务

### 日志和备份
