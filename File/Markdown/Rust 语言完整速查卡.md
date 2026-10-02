
---

# Rust 语言完整速查卡

---

## 一、Hello World 与环境搭建

### 最小完整程序

```rust
// main.rs
fn main() {
    println!("Hello World!");  // println! 是宏，自动换行
}
```

### 编译与运行

```bash
rustc main.rs -o main      # 直接编译
./main                     # 运行

cargo new project_name     # 创建新项目
cargo build                # 编译（debug模式）
cargo build --release      # 编译（release模式，优化）
cargo run                  # 编译并运行
cargo check                # 快速检查（不生成二进制）
cargo fmt                  # 自动格式化代码
cargo clippy               # 代码静态分析（lint）
```

### Cargo.toml 示例

```toml
[package]
name = "my_project"
version = "0.1.0"
edition = "2021"

[dependencies]
rand = "0.8"
serde = { version = "1.0", features = ["derive"] }
```

---

## 二、基本数据类型

### 整数类型

| 类型 | 大小 | 范围 |
|------|------|------|
| `i8` | 1 字节 | -128 ~ 127 |
| `u8` | 1 字节 | 0 ~ 255 |
| `i16` | 2 字节 | -32,768 ~ 32,767 |
| `u16` | 2 字节 | 0 ~ 65,535 |
| `i32` | 4 字节 | -2,147,483,648 ~ 2,147,483,647 |
| `u32` | 4 字节 | 0 ~ 4,294,967,295 |
| `i64` | 8 字节 | -9.22e18 ~ 9.22e18 |
| `u64` | 8 字节 | 0 ~ 1.84e19 |
| `i128` | 16 字节 | -1.70e38 ~ 1.70e38 |
| `u128` | 16 字节 | 0 ~ 3.40e38 |
| `isize` | 平台相关 | 指针大小（64位系统=8字节） |
| `usize` | 平台相关 | 指针大小（64位系统=8字节） |

### 浮点类型

| 类型 | 大小 | 精度 |
|------|------|------|
| `f32` | 4 字节 | 约 6-7 位小数 |
| `f64` | 8 字节 | 约 15-16 位小数（默认） |

### 布尔类型

```rust
let t: bool = true;
let f: bool = false;
```

### 字符类型

```rust
let c: char = 'A';        // 4字节 Unicode（支持中文、Emoji）
let emoji: char = '😊';
```

### 查看类型大小

```rust
println!("i32 大小: {} 字节", std::mem::size_of::<i32>());
println!("指针大小: {} 字节", std::mem::size_of::<&i32>());
```

---

## 三、变量与常量

### 变量声明与初始化

```rust
let x: i32 = 10;          // 不可变变量（默认）
let mut y = 20;           // 可变变量（类型自动推导）
let z;                    // 错误！变量必须初始化
z = 30;                   // 错误！不能先声明后初始化

const MAX_SIZE: u32 = 100;  // 常量（必须显式类型，编译时确定）
static APP_NAME: &str = "MyApp";  // 静态变量（全局生命周期）
```

### 变量遮蔽（Shadowing）

```rust
let x = 5;
let x = x + 1;            // 遮蔽旧变量
{
    let x = x * 2;        // 在块内遮蔽
    println!("{}", x);    // 12
}
println!("{}", x);        // 6（外层的值）
```

### 解构赋值

```rust
let (a, b) = (1, 2);
let [c, d] = [3, 4];
let Point { x, y } = point;  // 结构体解构
```

---

## 四、输入输出

### 输出宏 `println!` 和 `print!`

```rust
println!("Hello");              // 普通输出（换行）
print!("Hello");                // 普通输出（不换行）

// 格式化输出
println!("数字: {}", 100);      // {} 通用占位符
println!("浮点: {:.2}", 3.14159); // 保留2位小数
println!("十六进制: {:x}", 255); // 十六进制小写
println!("十六进制: {:X}", 255); // 十六进制大写
println!("二进制: {:b}", 10);    // 二进制
println!("八进制: {:o}", 255);   // 八进制
println!("科学计数: {:e}", 3.14); // 科学计数法

// 位置和命名参数
println!("{0} {1}, {1} {0}", "a", "b");  // a b, b a
println!("{name}: {age}", name="小明", age=18);

// 调试输出（Debug trait）
println!("{:?}", vec![1, 2, 3]);   // 调试格式
println!("{:#?}", vec![1, 2, 3]);  // 美化调试格式

// 宽度和对齐
println!("{:>10}", 12);    // 右对齐宽度10：        12
println!("{:<10}", 12);    // 左对齐宽度10：12
println!("{:^10}", 12);    // 居中对齐：    12
println!("{:0>5}", 12);    // 补零：00012
```

### 格式化宏 `format!`

```rust
let s = format!("{}-{}-{}", 2024, 12, 25);  // "2024-12-25"
```

### 输入 `stdin`

```rust
use std::io;

let mut input = String::new();
io::stdin().read_line(&mut input).expect("读取失败");
let num: i32 = input.trim().parse().expect("请输入数字");

// 读取多行
let mut line = String::new();
while io::stdin().read_line(&mut line).unwrap() > 0 {
    // 处理 line
    line.clear();
}
```

### 文件输入输出

```rust
use std::fs;
use std::io::{Write, BufRead, BufReader};

// 读取整个文件
let content = fs::read_to_string("data.txt").expect("读取失败");

// 逐行读取（大文件）
let file = fs::File::open("data.txt").expect("打开失败");
let reader = BufReader::new(file);
for line in reader.lines() {
    let line = line.unwrap();
    println!("{}", line);
}

// 写入文件
let mut file = fs::File::create("output.txt").expect("创建失败");
file.write_all(b"Hello, World!").expect("写入失败");
file.write_fmt(format_args!("数字: {}\n", 100)).expect("写入失败");
```

---

## 五、运算符

### 算术运算符

```rust
+    // 加法
-    // 减法
*    // 乘法
/    // 除法（整数除法截断小数）
%    // 取模（求余数）
```

**示例：**

```rust
let a = 10;
let b = 3;
let c = a + b;           // 13
let d = a / b;           // 3（整数除法）
let e = 10.0 / 3.0;      // 3.3333
let f = a % b;           // 1
```

### 赋值运算符

```rust
=    // 赋值
+=   // a += 1 等价于 a = a + 1
-=   // a -= 1
*=   // a *= 2
/=   // a /= 2
%=   // a %= 2
&=   // 位与赋值
|=   // 位或赋值
^=   // 异或赋值
<<=  // 左移赋值
>>=  // 右移赋值
```

### 比较运算符（返回 bool）

```rust
==   // 等于
!=   // 不等于
>    // 大于
<    // 小于
>=   // 大于等于
<=   // 小于等于
```

### 逻辑运算符（短路求值）

```rust
&&   // 逻辑与
||   // 逻辑或
!    // 逻辑非
```

### 位运算符

```rust
&    // 按位与
|    // 按位或
^    // 按位异或（相同为0，不同为1）
!    // 按位取反
<<   // 左移（乘以2的n次方）
>>   // 右移（除以2的n次方）
```

**位运算示例：**

```rust
let a: u8 = 0b1010;      // 10
let b: u8 = 0b1100;      // 12
let c = a & b;           // 0b1000 = 8
let d = a | b;           // 0b1110 = 14
let e = a ^ b;           // 0b0110 = 6
let f = !a;              // 0b11110101 = 245
let g = a << 1;          // 0b10100 = 20
let h = a >> 1;          // 0b0101 = 5
```

### 其他运算符

```rust
&        // 引用（取地址）
*        // 解引用
? :      // 三目运算符不存在，用 if-else 表达式替代
..       // 范围运算符
..=      // 包含范围
.        // 结构体成员
->       // 函数返回类型
::       // 路径分隔符（模块/关联函数）
@        // 绑定模式
?        // 错误传播
```

---

## 六、控制流

### `if` 表达式

```rust
if condition {
    // 条件为真时执行
}
```

### `if-else`

```rust
if condition {
    // 真
} else {
    // 假
}
```

### `if-else if-else`

```rust
if condition1 {
    // condition1 为真
} else if condition2 {
    // condition2 为真
} else {
    // 都不满足
}
```

**if 是表达式（可赋值）：**

```rust
let number = if condition { 5 } else { 10 };
```

### `loop` 循环（无限循环）

```rust
loop {
    // 无限执行
    if condition {
        break;        // 跳出循环
    }
}

// 带返回值
let result = loop {
    counter += 1;
    if counter == 10 {
        break counter * 2;   // 返回 20
    }
};
```

### `while` 循环

```rust
while condition {
    // 条件为真时重复执行
}
```

### `for` 循环

```rust
// 范围遍历
for i in 0..10 {          // 0 到 9（不包含10）
    println!("{}", i);
}

for i in 0..=10 {         // 0 到 10（包含10）
    println!("{}", i);
}

// 遍历集合
let arr = [1, 2, 3, 4, 5];
for item in &arr {        // 不可变引用
    println!("{}", item);
}

for item in &mut arr {    // 可变引用
    *item *= 2;
}

for (i, item) in arr.iter().enumerate() {  // 带索引
    println!("arr[{}] = {}", i, item);
}

// 反向遍历
for i in (0..10).rev() {
    println!("{}", i);
}

// 步长
for i in (0..10).step_by(2) {
    println!("{}", i);    // 0, 2, 4, 6, 8
}
```

### `break` 和 `continue`

```rust
break;        // 跳出当前循环
break value;  // 跳出并返回值（仅 loop）
continue;     // 跳过本次循环剩余代码，进入下一次迭代
```

### 循环标签（嵌套循环）

```rust
'outer: for i in 0..3 {
    for j in 0..3 {
        if i == j {
            continue 'outer;   // 跳到外层循环
        }
        println!("{}, {}", i, j);
    }
}
```

### `match` 模式匹配

```rust
match value {
    1 => println!("一"),
    2 => println!("二"),
    3..=9 => println!("三到九"),
    _ => println!("其他"),    // 下划线匹配所有
}

// match 是表达式
let result = match value {
    1 => "one",
    2 => "two",
    _ => "other",
};

// 枚举匹配
match color {
    Color::Red => println!("红色"),
    Color::Green => println!("绿色"),
    Color::Blue => println!("蓝色"),
}
```

### `if let` 和 `while let`

```rust
// 只匹配一种模式
if let Some(value) = some_option {
    println!("有值: {}", value);
} else {
    println!("无值");
}

while let Some(value) = iterator.next() {
    println!("{}", value);
}
```

---

## 七、元组

```rust
// 声明元组
let tup: (i32, f64, &str) = (10, 3.14, "hello");

// 解构
let (x, y, z) = tup;
println!("{}, {}, {}", x, y, z);

// 索引访问
let first = tup.0;     // 10
let second = tup.1;    // 3.14

// 单元素元组
let unit = (5,);
let unit2 = (5);       // 这是整数，不是元组
```

---

## 八、数组

### 一维数组

```rust
let arr: [i32; 5] = [1, 2, 3, 4, 5];  // [类型; 长度]
let arr = [1, 2, 3, 4, 5];             // 自动推导
let arr = [0; 10];                     // 10个0（初始化）
```

### 访问数组元素

```rust
let first = arr[0];      // 第一个元素（下标从0开始）
let second = arr[1];
// arr[10] 会 panic！（越界）
```

### 数组遍历

```rust
let arr = [1, 2, 3, 4, 5];
for i in 0..arr.len() {
    println!("{}", arr[i]);
}

for item in &arr {
    println!("{}", item);
}
```

### 数组切片

```rust
let arr = [1, 2, 3, 4, 5, 6];
let slice1 = &arr[0..3];   // [1, 2, 3]（不包含索引3）
let slice2 = &arr[..3];    // [1, 2, 3]
let slice3 = &arr[2..];    // [3, 4, 5, 6]
let slice4 = &arr[..];     // 全部
```

### 多维数组

```rust
let matrix: [[i32; 3]; 2] = [
    [1, 2, 3],
    [4, 5, 6],
];

let element = matrix[1][2];  // 6（第二行第三列）
```

### 数组大小

```rust
let len = arr.len();         // 元素个数
let bytes = std::mem::size_of_val(&arr);  // 字节数
```

---

## 九、向量（Vec）

```rust
// 创建向量
let mut v: Vec<i32> = Vec::new();
let v = vec![1, 2, 3, 4, 5];     // 宏创建
let v = vec![0; 10];             // 10个0

// 添加元素
v.push(6);
v.push(7);

// 删除元素
v.pop();        // 弹出最后一个元素（返回 Option）
v.remove(0);    // 移除索引0的元素

// 访问元素
let first = &v[0];             // 索引访问（可能panic）
let first = v.get(0);          // 安全访问（返回 Option）
if let Some(x) = v.get(10) {
    println!("{}", x);
}

// 遍历
for item in &v {
    println!("{}", item);
}

for item in &mut v {
    *item *= 2;
}

// 其他方法
v.len();           // 长度
v.is_empty();      // 是否为空
v.clear();         // 清空
v.contains(&3);    // 是否包含3
v.sort();          // 排序
v.reverse();       // 反转
```

---

## 十、字符串

### 字符串类型

```rust
let s1: &str = "hello";           // 字符串切片（不可变引用）
let s2: String = String::from("hello");  // 可拥有字符串
let s3 = "hello".to_string();     // 等价
let s4 = String::new();           // 空字符串
```

### 字符串操作

```rust
let mut s = String::from("hello");

// 追加
s.push(' ');             // 追加字符
s.push_str("world");     // 追加字符串

// 连接
let s1 = String::from("hello");
let s2 = String::from("world");
let s3 = s1 + &s2;       // hello world（s1被移动）
let s4 = format!("{}-{}", "hello", "world");  // 不移动所有权

// 索引（不能直接用下标）
let first = &s[0..1];    // 切片（可能panic）
for c in s.chars() {     // 遍历字符
    println!("{}", c);
}
for b in s.bytes() {     // 遍历字节
    println!("{}", b);
}

// 长度
let len = s.len();       // 字节数
let char_count = s.chars().count();  // 字符数

// 判断
s.is_empty();
s.contains("world");
s.starts_with("hello");
s.ends_with("world");

// 替换
let new = s.replace("world", "Rust");

// 分割
let parts: Vec<&str> = s.split(' ').collect();

// 去除空白
let trimmed = s.trim();

// 转换
let num = "123".parse::<i32>().unwrap();
let str = 456.to_string();
```

### 字符串切片

```rust
let s = String::from("hello world");
let hello = &s[0..5];    // "hello"
let world = &s[6..11];   // "world"
let all = &s[..];        // 全部
```

---

## 十一、所有权与借用

### 所有权规则

```rust
let s1 = String::from("hello");
let s2 = s1;              // s1 被移动，不能再使用
// println!("{}", s1);    // 错误！

let s3 = s2.clone();      // 深拷贝，s2 仍有效
println!("{}", s2);       // 可以

let x = 5;
let y = x;                // 复制（整数实现 Copy trait）
println!("{}", x);        // 可以
```

### 引用与借用

```rust
let s = String::from("hello");
let r1 = &s;              // 不可变引用
let r2 = &s;              // 可以有多个不可变引用
println!("{} {}", r1, r2);

let mut s = String::from("hello");
let r = &mut s;           // 可变引用（只能有一个）
r.push_str(" world");
println!("{}", r);
```

### 借用规则

1. 任何时刻，要么**一个可变引用**，要么**多个不可变引用**
2. 引用必须始终有效（**生命周期**）

```rust
// 错误示例
let r;
{
    let x = 5;
    r = &x;               // x 生命周期不够长
}
println!("{}", r);        // 错误！
```

### 函数所有权传递

```rust
fn take_ownership(s: String) {   // 获取所有权
    // s 在此函数结束后被 drop
}

fn borrow_immutable(s: &String) {  // 不可变借用
    println!("{}", s);
}

fn borrow_mutable(s: &mut String) {  // 可变借用
    s.push_str(" world");
}

let s = String::from("hello");
take_ownership(s);          // s 被移动
// println!("{}", s);       // 错误！

let s = String::from("hello");
borrow_immutable(&s);       // 借用
println!("{}", s);          // 有效
```

### 函数返回值所有权

```rust
fn give_ownership() -> String {
    let s = String::from("hello");
    s                         // 返回所有权
}

fn take_and_give_back(s: String) -> String {
    s                         // 返回所有权
}
```

---

## 十二、结构体

### 结构体定义

```rust
struct Person {
    name: String,
    age: u32,
    height: f64,
}
```

### 实例化

```rust
let p1 = Person {
    name: String::from("小明"),
    age: 18,
    height: 1.75,
};

// 字段简写
let name = String::from("小红");
let p2 = Person { name, age: 19, height: 1.65 };

// 更新语法
let p3 = Person { age: 20, ..p1 };   // 复制其他字段（需要 Copy）
```

### 访问成员

```rust
println!("名字: {}", p1.name);
p1.age = 19;          // 需要 mut
```

### 元组结构体

```rust
struct Color(u8, u8, u8);
let red = Color(255, 0, 0);
let first = red.0;    // 255
```

### 单元结构体

```rust
struct Unit;    // 不占内存，用于标记
```

### 方法

```rust
impl Person {
    // 关联函数（静态方法）
    fn new(name: &str, age: u32, height: f64) -> Person {
        Person {
            name: String::from(name),
            age,
            height,
        }
    }

    // 实例方法（&self 不可变引用）
    fn introduce(&self) {
        println!("我叫{}, 今年{}岁", self.name, self.age);
    }

    // 实例方法（&mut self 可变引用）
    fn birthday(&mut self) {
        self.age += 1;
    }

    // 实例方法（self 获取所有权）
    fn into_string(self) -> String {
        format!("{}:{}", self.name, self.age)
    }
}

let mut p = Person::new("小明", 18, 1.75);
p.introduce();
p.birthday();
let s = p.into_string();  // p 被移动
```

### 自动实现常用 trait

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
struct Point {
    x: i32,
    y: i32,
}
```

---

## 十三、枚举

### 枚举定义

```rust
#[derive(Debug)]
enum Color {
    Red,
    Green,
    Blue,
    Rgb(u8, u8, u8),         // 元组变体
    Hex { r: u8, g: u8, b: u8 },  // 结构体变体
}
```

### 枚举使用

```rust
let c1 = Color::Red;
let c2 = Color::Rgb(255, 0, 0);
let c3 = Color::Hex { r: 0, g: 255, b: 0 };

match c2 {
    Color::Red => println!("红色"),
    Color::Green => println!("绿色"),
    Color::Blue => println!("蓝色"),
    Color::Rgb(r, g, b) => println!("RGB({},{},{})", r, g, b),
    Color::Hex { r, g, b } => println!("#{:02X}{:02X}{:02X}", r, g, b),
}
```

### 枚举方法

```rust
impl Color {
    fn is_red(&self) -> bool {
        matches!(self, Color::Red)
    }
}
```

### `Option` 枚举

```rust
enum Option<T> {
    Some(T),
    None,
}

let some_num = Some(5);
let no_num: Option<i32> = None;

// 使用
let x = some_num.unwrap();     // 5（如果是None会panic）
let x = some_num.unwrap_or(0); // 5
let x = no_num.unwrap_or(0);   // 0
if let Some(value) = some_num {
    println!("{}", value);
}
```

### `Result` 枚举

```rust
enum Result<T, E> {
    Ok(T),
    Err(E),
}

let result: Result<i32, &str> = Ok(100);
let result2: Result<i32, &str> = Err("错误信息");

// 使用
let x = result.unwrap();         // 100（如果是Err会panic）
let x = result.unwrap_or(0);     // 100
if let Ok(value) = result {
    println!("{}", value);
}
```

### `match` 与 `if let`

```rust
match result {
    Ok(value) => println!("成功: {}", value),
    Err(e) => println!("失败: {}", e),
}

if let Ok(value) = result {
    println!("成功: {}", value);
}
```

---

## 十四、集合类型

### HashMap

```rust
use std::collections::HashMap;

// 创建
let mut map = HashMap::new();
map.insert("key1", 10);
map.insert("key2", 20);

// 访问
let value = map.get("key1");  // 返回 Option<&i32>
let value = map.get("key1").copied().unwrap_or(0);

// 遍历
for (key, value) in &map {
    println!("{}: {}", key, value);
}

// 更新
map.entry("key3").or_insert(30);  // 不存在则插入
*map.entry("key1").or_insert(0) += 5;  // 更新现有值

// 创建
let map: HashMap<&str, i32> = [("a", 1), ("b", 2)].iter().cloned().collect();
```

### HashSet

```rust
use std::collections::HashSet;

let mut set = HashSet::new();
set.insert(1);
set.insert(2);
set.insert(3);

set.contains(&2);  // true
set.remove(&2);

for item in &set {
    println!("{}", item);
}
```

### VecDeque（双端队列）

```rust
use std::collections::VecDeque;

let mut deque = VecDeque::new();
deque.push_back(1);
deque.push_front(2);
deque.pop_back();
deque.pop_front();
```

### BTreeMap（有序Map）

```rust
use std::collections::BTreeMap;

let mut map = BTreeMap::new();
map.insert("a", 1);
map.insert("b", 2);
// 按键排序
```

---

## 十五、迭代器

### 创建迭代器

```rust
let v = vec![1, 2, 3, 4, 5];

// 迭代器
let iter = v.iter();          // 不可变引用
let iter = v.iter_mut();      // 可变引用
let iter = v.into_iter();     // 取得所有权
```

### 迭代器适配器（惰性）

```rust
let v = vec![1, 2, 3, 4, 5];

// map：转换
let doubled: Vec<_> = v.iter().map(|x| x * 2).collect();

// filter：过滤
let evens: Vec<_> = v.iter().filter(|x| *x % 2 == 0).collect();

// filter_map：过滤+转换
let nums: Vec<_> = vec!["1", "2", "abc", "3"]
    .iter()
    .filter_map(|s| s.parse::<i32>().ok())
    .collect();  // [1, 2, 3]

// enumerate：带索引
for (i, x) in v.iter().enumerate() {
    println!("v[{}] = {}", i, x);
}

// skip/take：跳过/取前N
let first3: Vec<_> = v.iter().take(3).collect();
let skip2: Vec<_> = v.iter().skip(2).collect();

// rev：反转
let reversed: Vec<_> = v.iter().rev().collect();

// zip：压缩
let v1 = vec![1, 2, 3];
let v2 = vec!['a', 'b', 'c'];
let zipped: Vec<_> = v1.iter().zip(v2.iter()).collect();
```

### 消费者（执行）

```rust
let v = vec![1, 2, 3, 4, 5];

let sum: i32 = v.iter().sum();
let product: i32 = v.iter().product();
let count = v.iter().count();
let max = v.iter().max();
let min = v.iter().min();

let all_positive = v.iter().all(|x| *x > 0);    // true
let any_negative = v.iter().any(|x| *x < 0);    // false

let found = v.iter().find(|x| **x == 3);        // Some(&3)

let first = v.iter().next();     // Option<&i32>
let last = v.iter().last();      // Option<&i32>

// fold：折叠
let sum = v.iter().fold(0, |acc, x| acc + x);
```

### 自定义迭代器

```rust
struct Counter {
    count: u32,
}

impl Counter {
    fn new() -> Counter {
        Counter { count: 0 }
    }
}

impl Iterator for Counter {
    type Item = u32;

    fn next(&mut self) -> Option<Self::Item> {
        self.count += 1;
        if self.count <= 5 {
            Some(self.count)
        } else {
            None
        }
    }
}
```

---

## 十六、闭包

### 定义闭包

```rust
// 无参数
let greet = || println!("Hello");
greet();

// 带参数
let add = |a: i32, b: i32| a + b;
println!("{}", add(3, 5));

// 类型推导
let add = |a, b| a + b;
```

### 闭包捕获环境

```rust
let x = 10;

// 不可变引用（Fn）
let print_x = || println!("{}", x);
print_x();

// 可变引用（FnMut）
let mut y = 20;
let mut add_y = || {
    y += 1;
    println!("{}", y);
};
add_y();

// 取得所有权（FnOnce）
let s = String::from("hello");
let consume = || {
    println!("{}", s);
    // s 在这里被 drop
};
consume();
// println!("{}", s);   // 错误！
```

### 闭包作为参数

```rust
fn apply<F>(f: F, x: i32) -> i32
where
    F: Fn(i32) -> i32,
{
    f(x)
}

let square = |x| x * x;
println!("{}", apply(square, 5));  // 25
```

### 返回闭包

```rust
fn make_multiplier(factor: i32) -> impl Fn(i32) -> i32 {
    move |x| x * factor   // move 转移所有权
}

let times_3 = make_multiplier(3);
println!("{}", times_3(10));  // 30
```

---

## 十七、模块系统

### 项目结构

```
my_project/
├── Cargo.toml
└── src/
    ├── main.rs          # 入口文件（二进制）
    ├── lib.rs           # 库文件
    ├── module1.rs       # 模块
    └── module2/
        ├── mod.rs       # 模块目录
        └── submod.rs
```

### 模块定义

```rust
// 在 lib.rs 或 main.rs 中
mod math {
    pub fn add(a: i32, b: i32) -> i32 {
        a + b
    }

    pub mod advanced {
        pub fn multiply(a: i32, b: i32) -> i32 {
            a * b
        }
    }
}

// 使用
use math::add;
use math::advanced::multiply;

fn main() {
    println!("{}", add(1, 2));
    println!("{}", multiply(3, 4));
}
```

### 模块文件

```rust
// math.rs
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

// main.rs
mod math;    // 声明模块
use math::add;
```

### 模块目录

```rust
// math/mod.rs
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

pub mod advanced;   // 声明子模块

// math/advanced.rs
pub fn multiply(a: i32, b: i32) -> i32 {
    a * b
}
```

### `use` 导入

```rust
use std::collections::HashMap;
use std::io::{self, Write};
use std::fmt::Result as FmtResult;  // 重命名
use std::sync::*;    // 通配符（谨慎使用）
```

### `pub` 可见性

```rust
pub fn public_func() {}       // 公开
fn private_func() {}          // 私有（默认）
pub(self) fn inner() {}       // 当前模块可见
pub(crate) fn crate_func() {} // 整个crate可见
pub(super) fn parent() {}     // 父模块可见
```

### 预导入（Prelude）

```rust
use std::prelude::v1::*;      // 标准库预导入
// 很多类型已经默认可用：Option, Result, Vec, String 等
```

---

## 十八、错误处理

### `Result` 处理

```rust
use std::fs::File;
use std::io::{self, Read};

// 1. unwrap（失败会panic）
let file = File::open("file.txt").unwrap();

// 2. expect（panic时显示自定义信息）
let file = File::open("file.txt")
    .expect("无法打开文件");

// 3. if let
if let Ok(file) = File::open("file.txt") {
    // 处理文件
} else {
    println!("文件打开失败");
}

// 4. match
match File::open("file.txt") {
    Ok(file) => { /* 处理 */ }
    Err(e) => println!("错误: {}", e),
}
```

### `?` 运算符（错误传播）

```rust
fn read_file() -> Result<String, io::Error> {
    let mut file = File::open("file.txt")?;   // 若错误则提前返回
    let mut content = String::new();
    file.read_to_string(&mut content)?;
    Ok(content)
}

// 使用
let content = read_file().unwrap_or_else(|e| {
    println!("读取失败: {}", e);
    String::new()
});
```

### 自定义错误类型

```rust
use std::fmt;

#[derive(Debug)]
struct MyError {
    message: String,
}

impl fmt::Display for MyError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "{}", self.message)
    }
}

impl std::error::Error for MyError {}

fn do_something() -> Result<i32, MyError> {
    Err(MyError {
        message: String::from("出错了"),
    })
}
```

### `anyhow` 简化错误处理

```rust
use anyhow::{Result, Context, anyhow};

fn read_config() -> Result<String> {
    let content = std::fs::read_to_string("config.toml")
        .context("读取配置文件失败")?;
    Ok(content)
}

fn main() -> Result<()> {
    let config = read_config()?;
    println!("{}", config);
    Ok(())
}
```

### `thiserror` 自定义错误

```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum DataError {
    #[error("IO 错误: {0}")]
    Io(#[from] std::io::Error),
    #[error("解析错误: {0}")]
    Parse(#[from] std::num::ParseIntError),
    #[error("数据无效: {0}")]
    InvalidData(String),
}
```

---

## 十九、泛型

### 泛型函数

```rust
fn largest<T: PartialOrd>(list: &[T]) -> &T {
    let mut largest = &list[0];
    for item in list {
        if item > largest {
            largest = item;
        }
    }
    largest
}

let numbers = vec![1, 2, 3, 4, 5];
println!("{}", largest(&numbers));  // 5
```

### 泛型结构体

```rust
struct Point<T> {
    x: T,
    y: T,
}

let p1 = Point { x: 1, y: 2 };
let p2 = Point { x: 1.0, y: 2.0 };

impl<T> Point<T> {
    fn x(&self) -> &T {
        &self.x
    }
}
```

### 泛型枚举

```rust
enum Result<T, E> {
    Ok(T),
    Err(E),
}
```

### 多参数泛型

```rust
struct Point<T, U> {
    x: T,
    y: U,
}

let p = Point { x: 1, y: 2.0 };
```

### 泛型约束

```rust
// T: PartialOrd + Copy
fn largest<T: PartialOrd + Copy>(list: &[T]) -> T { ... }

// where 子句
fn largest<T>(list: &[T]) -> T
where
    T: PartialOrd + Copy,
{ ... }
```

---

## 二十、Trait

### 定义 Trait

```rust
trait Printable {
    fn print(&self);

    // 默认实现
    fn show(&self) {
        println!("显示");
    }
}
```

### 实现 Trait

```rust
struct Person {
    name: String,
    age: u32,
}

impl Printable for Person {
    fn print(&self) {
        println!("{}: {}", self.name, self.age);
    }
}

let p = Person { name: String::from("小明"), age: 18 };
p.print();   // 调用
```

### 常见 Trait

```rust
// Debug
#[derive(Debug)]
struct Point { x: i32, y: i32 }

// Clone
#[derive(Clone)]
struct Data { value: i32 }

// Copy（必须实现Clone）
#[derive(Copy, Clone)]
struct Simple { x: i32 }

// PartialEq / Eq
#[derive(PartialEq, Eq)]
struct Id(u32);

// Hash
#[derive(Hash)]
struct User { id: u32 }

// Default
#[derive(Default)]
struct Config {
    timeout: u32,
    retries: u32,
}
let config = Config::default();

// From/Into
impl From<&str> for Person {
    fn from(name: &str) -> Self {
        Person { name: name.to_string(), age: 18 }
    }
}
let p = Person::from("小明");
```

### Trait Bound

```rust
fn print_value<T: Printable>(value: T) {
    value.print();
}

// 多个Trait
fn process<T: Printable + Clone>(value: T) {
    value.print();
    let copy = value.clone();
}

// where 子句
fn process<T>(value: T)
where
    T: Printable + Clone,
{
    // ...
}
```

### 关联类型

```rust
trait Container {
    type Item;    // 关联类型
    fn get(&self) -> Self::Item;
}

struct Box<T> {
    value: T,
}

impl<T> Container for Box<T> {
    type Item = T;
    fn get(&self) -> T {
        self.value
    }
}
```

### Derive 宏

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Default)]
struct MyStruct {
    // ...
}
```

### 标准库 Trait

```rust
// Display：用户友好输出（用于格式化）
impl std::fmt::Display for Person {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        write!(f, "{} ({})", self.name, self.age)
    }
}
println!("{}", p);

// Drop：析构
impl Drop for Person {
    fn drop(&mut self) {
        println!("{} 被销毁", self.name);
    }
}

// Iterator
impl Iterator for Counter { ... }
```

### Trait 对象（动态分发）

```rust
trait Drawable {
    fn draw(&self);
}

struct Circle;
impl Drawable for Circle {
    fn draw(&self) { println!("画圆"); }
}

struct Square;
impl Drawable for Square {
    fn draw(&self) { println!("画方"); }
}

fn draw_all(items: &[&dyn Drawable]) {
    for item in items {
        item.draw();
    }
}

let circle = Circle;
let square = Square;
draw_all(&[&circle, &square]);
```

---

## 二十一、生命周期

### 生命周期标注

```rust
// 'a 表示生命周期参数
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}

let s1 = String::from("hello");
let s2 = String::from("world");
let result = longest(&s1, &s2);
```

### 结构体生命周期

```rust
struct Excerpt<'a> {
    part: &'a str,
}

let text = String::from("hello world");
let excerpt = Excerpt { part: &text[0..5] };
```

### 生命周期省略规则

```rust
// 每个参数都有自己的生命周期
fn first_word(s: &str) -> &str { ... }  // 等价于：
fn first_word<'a>(s: &'a str) -> &'a str { ... }

// 方法中的省略
impl<'a> MyStruct<'a> {
    fn get(&self) -> &str { ... }  // 等价于：
    // fn get(&'a self) -> &'a str { ... }
}
```

### `'static` 生命周期

```rust
let s: &'static str = "hello";   // 整个程序存活
let num: i32 = 42;
let p = &'static num;            // 错误！
```

---

## 二十二、智能指针

### `Box<T>`（堆分配）

```rust
let b = Box::new(5);
println!("{}", b);

// 递归类型
enum List {
    Cons(i32, Box<List>),
    Nil,
}
```

### `Rc<T>`（引用计数）

```rust
use std::rc::Rc;

let a = Rc::new(5);
let b = Rc::clone(&a);
println!("引用计数: {}", Rc::strong_count(&a));  // 2
```

### `Arc<T>`（原子引用计数，线程安全）

```rust
use std::sync::Arc;
use std::thread;

let a = Arc::new(5);
let b = Arc::clone(&a);
thread::spawn(move || {
    println!("{}", b);
});
```

### `RefCell<T>`（内部可变性）

```rust
use std::cell::RefCell;

let x = RefCell::new(5);
*x.borrow_mut() = 10;
println!("{}", x.borrow());  // 10

// 运行时借用检查
let mut_ref = x.borrow_mut();
let borrow = x.borrow();    // 编译通过，运行时panic！
```

### 组合使用

```rust
use std::rc::Rc;
use std::cell::RefCell;

let shared = Rc::new(RefCell::new(42));
let clone1 = Rc::clone(&shared);
let clone2 = Rc::clone(&shared);

*clone1.borrow_mut() += 1;   // 所有引用看到43
println!("{}", clone2.borrow());  // 43
```

---

## 二十三、并发编程

### 线程

```rust
use std::thread;
use std::time::Duration;

let handle = thread::spawn(|| {
    for i in 1..=5 {
        println!("子线程: {}", i);
        thread::sleep(Duration::from_millis(1));
    }
});

for i in 1..=3 {
    println!("主线程: {}", i);
    thread::sleep(Duration::from_millis(1));
}

handle.join().unwrap();  // 等待子线程
```

### `move` 闭包传递所有权

```rust
let data = vec![1, 2, 3];
let handle = thread::spawn(move || {
    println!("{:?}", data);  // data 被移动到线程
});
handle.join().unwrap();
// println!("{:?}", data);   // 错误！
```

### 消息传递（`mpsc`）

```rust
use std::sync::mpsc;
use std::thread;

let (tx, rx) = mpsc::channel();

thread::spawn(move || {
    tx.send(42).unwrap();
    tx.send(100).unwrap();
});

for received in rx {
    println!("收到: {}", received);
}

// 多个发送者
let (tx, rx) = mpsc::channel();
let tx1 = tx.clone();
// ...
```

### 互斥锁（`Mutex`）

```rust
use std::sync::{Arc, Mutex};

let counter = Arc::new(Mutex::new(0));
let mut handles = vec![];

for _ in 0..10 {
    let counter = Arc::clone(&counter);
    let handle = thread::spawn(move || {
        let mut num = counter.lock().unwrap();
        *num += 1;
    });
    handles.push(handle);
}

for handle in handles {
    handle.join().unwrap();
}
println!("{}", *counter.lock().unwrap());  // 10
```

### 读写锁（`RwLock`）

```rust
use std::sync::{Arc, RwLock};

let data = Arc::new(RwLock::new(0));
let read = data.read().unwrap();   // 多个读
// let write = data.write().unwrap(); // 独占写
```

### 原子类型

```rust
use std::sync::atomic::{AtomicUsize, Ordering};

let counter = AtomicUsize::new(0);
counter.fetch_add(1, Ordering::SeqCst);
println!("{}", counter.load(Ordering::SeqCst));
```

### `async/await`

```rust
use tokio;  // 或 async-std

#[tokio::main]
async fn main() {
    let result = async_task().await;
    println!("{}", result);
}

async fn async_task() -> i32 {
    tokio::time::sleep(tokio::time::Duration::from_secs(1)).await;
    42
}
```

---

## 二十四、宏

### 声明宏（`macro_rules!`）

```rust
// 简单宏
macro_rules! say_hello {
    () => {
        println!("Hello!");
    };
}

// 带参数
macro_rules! add {
    ($a:expr, $b:expr) => {
        $a + $b
    };
}

// 可变参数
macro_rules! vec {
    ($($x:expr),*) => {
        {
            let mut temp_vec = Vec::new();
            $(
                temp_vec.push($x);
            )*
            temp_vec
        }
    };
}

// 使用
say_hello!();
println!("{}", add!(3, 5));
let v = vec![1, 2, 3, 4];
```

### 常用宏

```rust
println!();          // 打印（换行）
print!();            // 打印（不换行）
format!();           // 格式化字符串
unreachable!();      // 不可达代码
todo!();             // 未实现代码
unimplemented!();    // 未实现
dbg!();              // 调试输出
include_str!();      // 包含字符串字面量
include_bytes!();    // 包含字节数组
file!();             // 当前文件名
line!();             // 当前行号
column!();           // 当前列号
stringify!();        // 转为字符串字面量
concat!();           // 连接字符串
```

### 自定义派生宏（`derive`）

```rust
use proc_macro::TokenStream;

#[proc_macro_derive(Hello)]
pub fn hello_derive(input: TokenStream) -> TokenStream {
    // 生成代码
}
```

---

## 二十五、标准库概览

### 常用头文件（use）

```rust
use std::fs;                // 文件系统
use std::io;                // 输入输出
use std::path::Path;        // 路径
use std::env;               // 环境变量
use std::process;           // 进程
use std::net;               // 网络
use std::thread;            // 线程
use std::time;              // 时间
use std::collections::*;    // 集合
use std::sync::*;           // 同步
use std::fmt;               // 格式化
use std::error;             // 错误
use std::str;               // 字符串
use std::char;              // 字符
use std::mem;               // 内存操作
use std::ptr;               // 指针操作
use std::borrow;            // 借用
use std::convert;           // 转换
use std::iter;              // 迭代器
use std::ops;               // 运算符重载
use std::hash;              // 哈希
use std::any;               // 类型动态
use std::cell;              // 内部可变性
use std::rc;                // 引用计数
use std::pin;               // 固定
use std::future;            // 异步
use std::task;              // 任务
```

### 文件系统

```rust
use std::fs;
use std::path::Path;

// 文件操作
fs::read("file.txt")?;
fs::write("file.txt", "content")?;
fs::read_to_string("file.txt")?;
fs::remove_file("file.txt")?;
fs::rename("old", "new")?;
fs::copy("src", "dst")?;

// 目录操作
fs::create_dir("dir")?;
fs::create_dir_all("dir/sub")?;
fs::remove_dir("dir")?;
fs::remove_dir_all("dir")?;

// 遍历目录
for entry in fs::read_dir(".")? {
    let entry = entry?;
    println!("{}", entry.file_name().to_string_lossy());
}

// 元数据
let metadata = fs::metadata("file.txt")?;
metadata.is_file();
metadata.is_dir();
metadata.len();
metadata.modified()?;
```

### 环境变量

```rust
use std::env;

// 获取
let path = env::var("PATH").unwrap_or("".to_string());
let args: Vec<String> = env::args().collect();

// 设置
env::set_var("MY_VAR", "value");
env::remove_var("MY_VAR");

// 其他
env::current_dir()?;
env::set_current_dir("/path")?;
env::home_dir();  // 返回 Option<PathBuf>
```

### 时间

```rust
use std::time::{Instant, Duration};

let start = Instant::now();
// ... 代码 ...
let duration = start.elapsed();
println!("耗时: {:?}", duration);

let dur = Duration::from_secs(5);
std::thread::sleep(dur);
```

---

## 二十六、常见陷阱与最佳实践

### 常见陷阱

**陷阱1：所有权移动**
```rust
let s = String::from("hello");
let t = s;
println!("{}", s);   // 错误！s 被移动
```

**陷阱2：可变借用冲突**
```rust
let mut s = String::from("hello");
let r1 = &mut s;
let r2 = &mut s;     // 错误！不能同时有多个可变借用
```

**陷阱3：借用与可变同时存在**
```rust
let mut s = String::from("hello");
let r1 = &s;
let r2 = &mut s;     // 错误！不可变借用时不能可变借用
println!("{}", r1);
```

**陷阱4：生命周期不够长**
```rust
let r;
{
    let s = String::from("hello");
    r = &s;           // s 生命周期不够长
}
println!("{}", r);    // 错误！
```

**陷阱5：整数溢出**
```rust
let x: u8 = 255;
let y = x + 1;        // Debug模式panic，Release模式溢出
```

**陷阱6：match 非穷尽**
```rust
match value {
    1 => println!("一"),
    // 缺少 _ => ...
}
// 编译错误！
```

**陷阱7：Vec 遍历时修改**
```rust
let mut v = vec![1, 2, 3];
for item in &v {      // 不可变借用
    v.push(4);        // 错误！尝试修改
}
```

**陷阱8：闭包捕获移动**
```rust
let s = String::from("hello");
let f = || println!("{}", s);
f();
println!("{}", s);    // 错误！s 被闭包捕获
```

### 最佳实践

1. **使用 `cargo clippy`** 检查代码
2. **使用 `rustfmt`** 格式化代码
3. **优先使用 `match`** 而非 `if let`（除非只有一个分支）
4. **使用 `unwrap` 只用于原型**，生产用 `?` 或 `expect`
5. **使用 `impl Trait`** 简化泛型
6. **避免返回借用**，返回拥有类型
7. **使用 `Option` 和 `Result`** 表示可选/错误
8. **减少 `unsafe`** 使用
9. **使用单元测试**（`#[test]`）
10. **使用文档注释**（`///`）

---

## 二十七、测试

### 单元测试

```rust
#[cfg(test)]
mod tests {
    #[test]
    fn test_add() {
        assert_eq!(2 + 2, 4);
    }

    #[test]
    fn test_fail() -> Result<(), String> {
        if 2 + 2 == 5 {
            Ok(())
        } else {
            Err("2+2不等于5".to_string())
        }
    }

    #[test]
    #[should_panic]
    fn test_panic() {
        panic!("预期panic");
    }

    #[test]
    #[ignore]
    fn test_slow() {
        // 耗时测试，默认跳过
    }
}
```

### 集成测试（`tests/` 目录）

```rust
// tests/integration_test.rs
use my_project::add;

#[test]
fn test_add_integration() {
    assert_eq!(add(2, 2), 4);
}
```

### 文档测试

```rust
/// 加法函数
///
/// # Examples
///
/// ```
/// let result = my_project::add(2, 3);
/// assert_eq!(result, 5);
/// ```
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}
```

---

## 二十八、编译与链接

### 编译选项

```bash
# 不同优化级别
cargo build                     # debug（无优化）
cargo build --release           # release（优化）
cargo build --profile=dev       # 自定义

# 目标平台
cargo build --target x86_64-unknown-linux-gnu
rustc --target wasm32-unknown-unknown main.rs

# 其他
cargo build --features feature1  # 启用特性
cargo build --no-default-features
```

### `Cargo.toml` 配置文件

```toml
[package]
name = "my_project"
version = "0.1.0"
edition = "2021"
authors = ["Your Name <email@example.com>"]
description = "A description"
license = "MIT"
repository = "https://github.com/user/repo"
readme = "README.md"
homepage = "https://example.com"
documentation = "https://docs.rs/my_project"
categories = ["science", "tools"]
keywords = ["rust", "cli"]

[dependencies]
rand = "0.8"
serde = { version = "1.0", features = ["derive"] }
tokio = { version = "1.0", features = ["full"] }

[dev-dependencies]
criterion = "0.3"

[build-dependencies]
cc = "1.0"

[features]
default = ["feature1"]
feature1 = []
feature2 = ["some-dependency/feature"]

[profile.release]
lto = true          # 链接时优化
opt-level = 3
codegen-units = 1   # 减少并行单位，优化大小

[workspace]
members = ["lib1", "lib2"]
```

---

## 二十九、Rust 学习路线图

```
┌─────────────────────────────────────────────────────────────┐
│                    Rust 学习路线                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🟢 入门阶段                                               │
│  ├── Hello World 与环境搭建（cargo）                       │
│  ├── 基本数据类型与变量                                    │
│  ├── 输入输出（println/format）                            │
│  └── 控制流（if/loop/while/for/match）                    │
│                                                             │
│  🟡 基础阶段                                               │
│  ├── 所有权、借用、生命周期                                │
│  ├── 元组、数组、向量、字符串                              │
│  ├── 结构体、枚举                                          │
│  ├── 函数、闭包、迭代器                                    │
│  └── 模块系统                                              │
│                                                             │
│  🟠 进阶阶段                                               │
│  ├── 泛型与 Trait                                          │
│  ├── 错误处理（Result/anyhow/thiserror）                  │
│  ├── 智能指针（Box/Rc/RefCell/Arc）                       │
│  └── 生命周期进阶                                          │
│                                                             │
│  🔴 高级阶段                                               │
│  ├── 并发编程（线程/Mutex/Channel）                       │
│  ├── 异步编程（async/await）                              │
│  ├── 宏（macro_rules/过程宏）                             │
│  ├── Unsafe Rust                                           │
│  └── FFI（C语言交互）                                      │
│                                                             │
│  ⚫ 专家阶段                                               │
│  ├── 编译器插件与自定义 derive                            │
│  ├── 性能优化（profiling/benchmark）                      │
│  ├── 标准库源码阅读                                        │
│  └── WebAssembly / 嵌入式开发                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📚 附录：常用命令速查

| 命令 | 说明 |
|------|------|
| `cargo new <name>` | 创建新项目 |
| `cargo build` | 编译（debug） |
| `cargo build --release` | 编译（release） |
| `cargo run` | 编译并运行 |
| `cargo check` | 快速检查（不生成二进制） |
| `cargo test` | 运行测试 |
| `cargo bench` | 运行基准测试 |
| `cargo doc` | 生成文档 |
| `cargo fmt` | 格式化代码 |
| `cargo clippy` | 静态分析 |
| `cargo clean` | 清除编译产物 |
| `cargo update` | 更新依赖 |
| `cargo add <crate>` | 添加依赖（需要 cargo-edit） |
