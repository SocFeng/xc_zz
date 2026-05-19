## 基本的SELECT语句

### 基本结构
```sql
SELECT 字段1,字段2 ...
FROM 表名
WHERE 条件语句1 [AND/OR 条件语句] ... 
GROUP BY 字段n
HAVING 分组后条件
ORDER BY 排序字段
LIMIT 分页限制 OFFSET 偏移数;
```

- 【查询指定列数据】: 字段1,字段2...
```sql
SELECT employee_id, first_name, last_name
FROM employees;

|employee_id|first_name |last_name  |
+----------+-----------+-----------+
|       100|Steven     |King       |
|       101|Neena      |Kochhar    |
|       102|Lex        |De Haan    |
.....

```
- 【查询所有字段】: *
```sql
SELECT *
FROM employeees;

|employee_id|first_name |last_name  |email   |phone_number      |hire_date |job_id    |salary |commission_pct|manager_id|department_id|
|-----------+-----------+-----------+--------+------------------+----------+----------+-------+--------------+----------+-------------+
|        100|Steven     |King       |SKING   |515.123.4567      |1987-06-17|AD_PRES   |24000.0|              |          |           90|
|        101|Neena      |Kochhar    |NKOCHHAR|515.123.4568      |1989-09-21|AD_VP     |17000.0|              |       100|           90|
|        102|Lex        |De Haan    |LDEHAAN |515.123.4569      |1993-01-13|AD_VP     |17000.0|              |       100|           90|
....
```

- 【数据列别名】: 字段 AS 新名字 或者 字段 "新名字"
```sql
SELECT employee_id, employee_id AS emp_id, first_name, first_name "FirstName"
FROM employees;

|employee_id|emp_id|first_name |FirstName  |
+-----------+------+-----------+-----------+
|        100|   100|Steven     |Steven     |
|        101|   101|Neena      |Neena      |
|        102|   102|Lex        |Lex        |
|        103|   103|Alexander  |Alexander  |
.... 
```
- 【去除重复行】: DISTINCT 字段名
```sql
--  将某一列数据去重;相同的departerment_id只出现一次
SELECT DISTINCT department_id
FROM employees;

|department_id|
+-------------+
|             |  -- 这里是NULL
|           10|
|           20|
|           30|
|           40|
...

如果多列同时去重 - 实际没有意义
SELECT DISTINCT department_id, salary
FROM employees;

|department_id|salary |
+-------------+-------+
|           90|24000.0|
|           90|17000.0|
|           60| 9000.0|
|           60| 6000.0|
|           60| 4800.0|
....
```
- 【空值】表示没有数据
  - 1 空值是 null
  - 2 空值不等于 0 '' 'null'
  - 3 空值运算 null与任数运算都是null 使用 IFNULL(字段名,替换值)，表示如果字段为null就用指定值类替换

- 【着重号】 `数据/字段/表名` 防止表名、字段名和系统关键字冲突
  ```sql
  -- 着重号
  SELECT *
  FROM `order`  -- 防止order表和系统字段 order by字段冲突

  |order_id|order_name|
  +--------+----------+
  |       1|shkstart  |
  |       2|tomcat    |
  |       3|dubbo     |
  ....
  ```
  
### 显示表结构
 - DESCRIBE/DESC 表名 :显示表中字段的详细信息
  ```sql
  DESCRIBE employees;

  |  Field       |Type       |Null|Key|Default|Extra|
  +--------------+-----------+----+---+-------+-----+
  |employee_id   |int(6)     |NO  |PRI|0      |     |
  |first_name    |varchar(20)|YES |   |       |     |
  |last_name     |varchar(25)|NO  |   |       |     |
  |email         |varchar(25)|NO  |UNI|       |     |
  |phone_number  |varchar(20)|YES |   |       |     |
  |hire_date     |date       |NO  |   |       |     |
  |job_id        |varchar(10)|NO  |MUL|       |     |
  |salary        |double(8,2)|YES |   |       |     |
  |commission_pct|double(2,2)|YES |   |       |     |
  |manager_id    |int(6)     |YES |MUL|       |     |
  |department_id |int(4)     |YES |MUL|       |     |
  ```
### 过滤数据
 - WHERE 条件语句 ；跟SELECT 进行匹配，查询指定的数据
  ```sql
    -- 查询部门编号为90的员工信息
    SELECT *
    FROM employees
    WHERE department_id = 90;

    |employee_id|first_name|last_name|email   |phone_number|hire_date |job_id |salary |commission_pct|manager_id|department_id|
    +-----------+----------+---------+--------+------------+----------+-------+-------+--------------+----------+-------------+
    |        100|Steven    |King     |SKING   |515.123.4567|1987-06-17|AD_PRES|24000.0|              |          |           90|
    |        101|Neena     |Kochhar  |NKOCHHAR|515.123.4568|1989-09-21|AD_VP  |17000.0|              |       100|           90|
    |        102|Lex       |De Haan  |LDEHAAN |515.123.4569|1993-01-13|AD_VP  |17000.0|              |       100|           90|
    ...
  ```

### 运算符
  - 【算数运算符】
    - 加：+
    - 减：-
    - 乘：*
    - 除：/或DIV
    - 模：%或MOD
  ```sql
    -- 常量可以直接替换成比字段来直接用
    SELECT
	100 AS "元数据",
	100 - 3 AS "减法",
	100 + 5 AS "加法",
	100 - 7.1 AS "减小数",
	100 + 4.3 AS "加小数",
	100 * 2 AS "乘法",
	100 * 2.3311 AS "乘小数",
	100 / 3 AS "除法",
	100 / 3.4 AS "除小数",
	100 DIV 3 AS "除法 DIV",
	100 DIV 3.4 AS "除小数 DIV",
	100 %3 AS "取余数 %",
	100 MOD 3 AS "取余数 MOD"

    
    |元数据|减法|加法 |减小数 |加小数  |乘法 |乘小数     |除法     |除小数    |除法 DIV|除小数 DIV|取余数 %|取余数 MOD|
    +-----+---+----+------+-------+----+----------+--------+---------+-------+---------+-------+--------+
    |  100| 97| 105|  92.9|  104.3| 200| 233.1100|  33.3333|  29.4118|     33|       29|      1|       1|

  ```
  - 【比较运算符】
    - 等于：=
    ```shell
    SELECT first_name,last_name,employee_id,salary 
    FROM employees
    WHERE salary = 9000
    LIMIT 5;
    
    first_name|last_name|employee_id|salary|
    ----------+---------+-----------+------+
    Alexander |Hunold   |        103|9000.0|
    Daniel    |Faviet   |        109|9000.0|
    Peter     |Hall     |        152|9000.0|
    Allan     |McEwen   |        158|9000.0|

    ```
    - 不等于：<>、!=
    ```shell
    SELECT first_name,last_name,employee_id,salary 
    FROM employees
    WHERE salary = 9000
    LIMIT 5;

    first_name|last_name|employee_id|salary |
    ----------+---------+-----------+-------+
    Steven    |King     |        100|24000.0|
    Neena     |Kochhar  |        101|17000.0|
    Lex       |De Haan  |        102|17000.0|
    Bruce     |Ernst    |        104| 6000.0|
    David     |Austin   |        105| 4800.0|
    ```
    - 小于：<
    ```shell
    SELECT first_name,last_name,employee_id,salary 
    FROM employees
    WHERE salary < 9000
    LIMIT 5;
    
    first_name|last_name|employee_id|salary|
    ----------+---------+-----------+------+
    Bruce     |Ernst    |        104|6000.0|
    David     |Austin   |        105|4800.0|
    Valli     |Pataballa|        106|4800.0|
    Diana     |Lorentz  |        107|4200.0|
    John      |Chen     |        110|8200.0|
    ```
    - 大于：>
    ```shell
    SELECT first_name,last_name,employee_id,salary 
    FROM employees
    WHERE salary > 20000
    LIMIT 5;
    
    first_name|last_name|employee_id|salary |
    ----------+---------+-----------+-------+
    Steven    |King     |        100|24000.0|
    ```
    - 小于等于：<=
    ```shell
    SELECT first_name,last_name,employee_id,salary 
    FROM employees
    WHERE salary <= 9000
    LIMIT 5;
    
    first_name|last_name|employee_id|salary|
    ----------+---------+-----------+------+
    Alexander |Hunold   |        103|9000.0|
    Bruce     |Ernst    |        104|6000.0|
    David     |Austin   |        105|4800.0|
    Valli     |Pataballa|        106|4800.0|
    Diana     |Lorentz  |        107|4200.0|
    ```
    - 大于等于：>=
    ```shell
    SELECT first_name,last_name,employee_id,salary 
    FROM employees
    WHERE salary >= 9000
    LIMIT 5;
    
    first_name|last_name|employee_id|salary |
    ----------+---------+-----------+-------+
    Steven    |King     |        100|24000.0|
    Neena     |Kochhar  |        101|17000.0|
    Lex       |De Haan  |        102|17000.0|
    Alexander |Hunold   |        103| 9000.0|
    Nancy     |Greenberg|        108|12000.0|
    ```


### 排序和分页
 - 排序: ORDER BY 字段名1 [DESC/ASC] 字段名2 [DECS/ACS]  按照对数据列进行排序
 - 分页: LIMIT nums OFFSET (page*nums)   limit nums 每页多少数据 offset 从头便宜多少条数据开始查询