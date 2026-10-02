# ☕ Java 核心知识速查手册（完整扩充版）


---

## 一、Java 核心概念（跨平台灵魂）

-   **JVM (Java虚拟机)**：将 `.class` 字节码翻译成特定平台的机器码。是Java实现"一次编译，到处运行"的核心。
-   **JRE (Java运行环境)** = JVM + 核心类库。仅运行Java程序，安装JRE即可。
-   **JDK (Java开发工具包)** = JRE + 开发工具（如 `javac`, `jar`）。开发Java程序必须安装JDK。

### 跨平台原理
```
.java (源文件) --javac编译--> .class (字节码) --JVM解释执行--> 机器码
```
不同操作系统安装不同的JVM，但运行的是相同的字节码，由此实现跨平台。

### 常用命令
```bash
# 查看版本
java -version
javac -version

# 编译与运行
javac Hello.java      # 生成 Hello.class
java Hello            # 运行，不要加 .class 后缀
```

---

## 二、变量与基本数据类型

### 基本数据类型（Primitive Type）
| 类型 | 关键字 | 大小 | 取值范围 | 默认值 | 示例 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 字节型 | `byte` | 1字节 | -128 ~ 127 | 0 | `byte b = 10;` |
| 短整型 | `short` | 2字节 | -32,768 ~ 32,767 | 0 | `short s = 100;` |
| 整型 | `int` | 4字节 | -2^31 ~ 2^31-1 (约-21亿~21亿) | 0 | `int i = 1000;` |
| 长整型 | `long` | 8字节 | -2^63 ~ 2^63-1 | 0L | `long l = 100L;` |
| 单精度浮点 | `float` | 4字节 | 约 ±3.4E-38 ~ ±3.4E38 | 0.0f | `float f = 3.14f;` |
| 双精度浮点 | `double` | 8字节 | 约 ±1.7E-308 ~ ±1.7E308 | 0.0d | `double d = 3.14159;` |
| 字符型 | `char` | 2字节 | 0 ~ 65,535 (Unicode) | '\u0000' | `char c = 'A';` |
| 布尔型 | `boolean` | JVM规范未明确定义 | `true` 或 `false` | `false` | `boolean flag = true;` |

### 引用类型（Reference Type）
-   **类、接口、数组、枚举** 都属于引用类型。
-   **`String`**：最常用的引用类型，使用双引号，如 `String str = "Hello";`。

### 类型转换
-   **自动转换 (隐式)**：小范围类型 → 大范围类型，如 `int → long → float → double`。
-   **强制转换 (显式)**：大范围类型 → 小范围类型，可能丢失精度或溢出。
    ```java
    int a = 10;
    long b = a;        // 自动转换
    int c = (int) b;   // 强制转换
    ```

### 包装类（Wrapper Class）
每个基本类型都有对应的包装类，用于在需要对象的场景中使用（如集合）。
-   `int → Integer`, `long → Long`, `double → Double`, `boolean → Boolean`, `char → Character`
-   **自动装箱/拆箱**：
    ```java
    Integer i = 10;     // 自动装箱: int -> Integer
    int j = i;          // 自动拆箱: Integer -> int
    ```

---

## 三、运算符

> 运算符用法与C语言高度相似。

-   **算术**：`+`, `-`, `*`, `/`, `%`, `++`, `--`
-   **比较**：`==`, `!=`, `>`, `<`, `>=`, `<=` (结果为 `boolean`)
-   **逻辑**：`&&` (短路与), `||` (短路或), `!` (非)
-   **位运算**：`&`, `|`, `^`, `~`, `<<`, `>>`, `>>>` (无符号右移)
-   **赋值**：`=`, `+=`, `-=`, `*=`, `/=`, `%=`
-   **三目 (条件) 运算符**：`result = (a > b) ? a : b;`
-   **类型判断**：`instanceof`
    ```java
    if (obj instanceof String) {
        String s = (String) obj;
    }
    ```

### ⚠️ 重点：`==` vs `equals()`
-   **`==`**：
    -   基本类型：比较**值**是否相等。
    -   引用类型：比较**内存地址**是否相等（即是否指向同一个对象）。
-   **`equals()`**：是 `Object` 类的方法，默认行为同 `==`。但 `String`、`Integer` 等类重写了该方法，用于比较**内容**是否相等。**自定义类也必须重写 `equals()` 以实现内容比较。**

---

## 四、控制流

> 与C语言基本一致。

### 条件判断
```java
if (condition1) {
    // ...
} else if (condition2) {
    // ...
} else {
    // ...
}
```

### 选择语句 `switch`
支持 `int`, `String`, `enum`。
```java
// 传统写法，需加 break
switch (value) {
    case 1:
        System.out.println("One");
        break;
    case 2:
        System.out.println("Two");
        break;
    default:
        System.out.println("Other");
}

// Java 14+ 增强写法 (箭头表达式)，无需 break
switch (day) {
    case MONDAY, FRIDAY -> System.out.println("工作日");
    case SATURDAY, SUNDAY -> System.out.println("周末");
    default -> System.out.println("其他");
}
```

### 循环
-   `for (int i = 0; i < 10; i++) { ... }`
-   **增强 for 循环 (for-each)**：遍历数组或 `Iterable` 集合
    `for (String s : stringList) { System.out.println(s); }`
-   `while (condition) { ... }`
-   `do { ... } while (condition);`
-   `break;` / `continue;`

---

## 五、数组

### 声明与初始化
```java
int[] arr1 = new int[5];          // 默认值为 0
int[] arr2 = {1, 2, 3, 4, 5};    // 静态初始化
int[] arr3 = new int[]{1, 2, 3};  // 显式初始化
```

### 访问与遍历
```java
arr1[0] = 10;
int x = arr1[1];
int len = arr1.length;            // 数组长度属性

// 普通 for 循环
for (int i = 0; i < arr2.length; i++) { ... }
// 增强 for 循环
for (int num : arr2) { ... }
```

### 多维数组
```java
int[][] matrix = new int[3][4];   // 3行4列
int[][] matrix2 = {{1, 2}, {3, 4}};
```

---

## 六、面向对象（三大特性）

### 1. 封装 (Encapsulation)
将数据（属性）和行为（方法）包装在类中，并对外隐藏具体实现细节。
```java
class Person {
    private String name;  // 私有属性

    // 通过公共 getter/setter 访问
    public String getName() {
        return name;
    }
    public void setName(String name) {
        this.name = name;  // this 指向当前对象
    }
}
```

### 2. 继承 (Inheritance)
子类复用父类的属性和方法。Java 为**单继承**（一个类只能有一个直接父类）。
```java
class Animal {
    protected String name;  // protected: 子类可见
    public void eat() {
        System.out.println("吃东西");
    }
}

class Dog extends Animal {   // extends 关键字
    public void bark() {
        System.out.println("汪汪");
    }

    @Override               // 注解，表示重写父类方法
    public void eat() {
        System.out.println("狗在吃东西");
    }
}
```

#### `super` 关键字
-   `super.name`：访问父类属性。
-   `super.eat()`：调用父类方法。
-   `super()`：调用父类构造器，**必须在子类构造器的第一行**。

### 3. 多态 (Polymorphism)
父类引用指向子类对象，在运行时决定调用哪个方法。
```java
Animal a = new Dog();      // 向上转型 (自动)
a.eat();                   // 调用 Dog 的 eat() 方法

// 向下转型 (需要先判断)
if (a instanceof Dog) {
    Dog d = (Dog) a;
    d.bark();
}
```

---

## 七、访问修饰符

| 修饰符 | 本类 | 同包 | 子类 | 全局 |
| :--- | :---: | :---: | :---: | :---: |
| `private` | ✅ | ❌ | ❌ | ❌ |
| default (不写) | ✅ | ✅ | ❌ | ❌ |
| `protected` | ✅ | ✅ | ✅ | ❌ |
| `public` | ✅ | ✅ | ✅ | ✅ |

> **最佳实践**：属性用 `private`，方法用 `public`，工具类内部辅助方法用 `private`。

---

## 八、构造器与代码块

### 构造器
-   与类同名，无返回值。
-   `new` 对象时自动调用。
-   若未定义任何构造器，Java 会提供一个默认的无参构造器。若定义了有参构造器，则无参构造器不再自动生成。
```java
class Person {
    String name;

    // 无参构造器
    Person() {}

    // 有参构造器
    Person(String name) {
        this.name = name;
    }
}
```

### `this()` 与构造器重载
```java
Person() {
    this("默认名字"); // 调用有参构造器
}
```

### 初始化块
所有构造器执行前都会执行。
```java
{
    System.out.println("实例初始化块");
}

static {
    System.out.println("静态初始化块"); // 类加载时执行一次
}
```

---

## 九、关键字速查

| 关键字 | 作用 |
| :--- | :--- |
| `static` | 静态成员，属于类，所有实例共享 |
| `final` | 类不可继承 / 方法不可重写 / 变量变为常量 |
| `this` | 当前对象的引用 |
| `super` | 父类对象的引用 |
| `new` | 创建对象实例 |
| `instanceof` | 判断对象是否为特定类的实例 |
| `abstract` | 定义抽象类或抽象方法 |
| `interface` | 定义接口 |
| `implements` | 实现接口 |
| `extends` | 继承类 |
| `enum` | 定义枚举类型 |
| `synchronized` | 同步锁，用于线程安全 |
| `volatile` | 保证变量在多线程间的可见性，禁止指令重排 |
| `transient` | 序列化时忽略该字段 |
| `native` | 声明本地方法（由JNI实现） |

---

## 十、抽象类与接口

### 抽象类 (Abstract Class) - "is-a" 关系
-   使用 `abstract` 修饰。
-   可包含构造器、普通属性和普通方法。
-   抽象方法无方法体，必须由子类实现。
```java
abstract class Animal {
    abstract void makeSound();
    void sleep() {
        System.out.println("睡觉");
    }
}
```

### 接口 (Interface) - "can-do" 关系
-   使用 `interface` 定义，`implements` 实现。
-   Java 8+：可以包含 `default` 方法和 `static` 方法。
-   Java 9+：可以包含 `private` 方法。
-   属性默认为 `public static final`。
-   一个类可以实现**多个**接口。
```java
interface Flyable {
    void fly(); // 默认为 public abstract

    default void takeoff() {
        System.out.println("起飞");
    }
}

class Bird extends Animal implements Flyable {
    @Override void makeSound() { System.out.println("叽叽"); }
    @Override public void fly() { System.out.println("飞"); }
}
```

### 接口 vs 抽象类
| 特性 | 接口 | 抽象类 |
| :--- | :--- | :--- |
| 继承/实现 | 多实现 | 单继承 |
| 状态 (属性) | `public static final` | 可以有实例变量 |
| 构造器 | 无 | 有 |
| 方法类型 | `abstract`, `default`, `static`, `private` | 抽象、普通、静态、final |

---

## 十一、常用类

### `String`（不可变类）
```java
String s = "Hello";
s.length();                 // 5
s.charAt(0);                // 'H'
s.substring(0, 2);          // "He" [0,2)
s.indexOf("l");             // 2
s.equals("Hello");          // true (比较内容)
s.equalsIgnoreCase("hello");// true
s.toLowerCase();            // "hello"
s.toUpperCase();            // "HELLO"
s.trim();                   // 去除首尾空格
s.split(",");               // 按逗号分割为数组
s.replace("H", "J");        // "Jello"
s.contains("ell");          // true
s.isEmpty();                // false
s.isBlank();                // Java 11, 判断是否为空白字符串
```

### `StringBuilder` / `StringBuffer`
-   **可变字符串**，用于频繁拼接的场景。
-   `StringBuilder`：线程不安全，性能高。
-   `StringBuffer`：线程安全，性能较低。
```java
StringBuilder sb = new StringBuilder();
sb.append("Hello");
sb.insert(0, "Hi ");
sb.delete(0, 3);
sb.toString(); // "Hello"
```

### 包装类常用方法
```java
int num = Integer.parseInt("123");   // 字符串 -> int
String str = Integer.toString(123);  // int -> 字符串
Integer i = Integer.valueOf("123");  // 字符串 -> Integer
```

### 日期时间 API (Java 8+)
```java
import java.time.*;
import java.time.format.DateTimeFormatter;

LocalDate date = LocalDate.now();          // 当前日期
LocalTime time = LocalTime.now();          // 当前时间
LocalDateTime dt = LocalDateTime.now();    // 当前日期时间

dt.plusDays(1);              // 加一天
dt.minusHours(2);            // 减2小时

// 格式化
DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
String formatted = dt.format(formatter);
```

---

## 十二、集合框架（核心重点）

### 集合体系图
```
Iterable (接口)
│
└── Collection (接口)
│     ├── List (接口) [有序、可重复]
│     │    ├── ArrayList    (数组实现，查询快，增删慢)
│     │    ├── LinkedList   (双向链表实现，增删快，查询慢)
│     │    └── Vector       (线程安全，已过时)
│     ├── Set (接口) [无序、不重复]
│     │    ├── HashSet      (哈希表，最快)
│     │    ├── LinkedHashSet (哈希表+链表，保持插入顺序)
│     │    └── TreeSet      (红黑树，自动排序)
│     └── Queue (接口)
│          └── PriorityQueue (优先级队列)
│
└── Map (接口) [键值对]
      ├── HashMap          (最常用，无序)
      ├── LinkedHashMap    (保持插入顺序)
      ├── TreeMap          (按键排序)
      └── Hashtable        (线程安全，已过时)
```

### `List` 接口
```java
List<String> list = new ArrayList<>();
list.add("苹果");           // 添加
list.get(0);               // 获取
list.set(0, "香蕉");        // 修改
list.remove(0);            // 删除
list.size();               // 长度
list.contains("苹果");      // 是否包含

// 遍历
for (String s : list) { System.out.println(s); }
list.forEach(System.out::println); // Lambda
```

### `Set` 接口
```java
Set<String> set = new HashSet<>();
set.add("苹果");   // 重复元素会被忽略
set.contains("苹果");
set.remove("苹果");
```

### `Map` 接口
```java
Map<String, Integer> map = new HashMap<>();
map.put("苹果", 5);          // 添加/修改
map.get("苹果");            // 获取，不存在返回 null
map.getOrDefault("香蕉", 0); // 不存在返回默认值
map.containsKey("苹果");
map.remove("苹果");

// 遍历
for (Map.Entry<String, Integer> entry : map.entrySet()) {
    System.out.println(entry.getKey() + "=" + entry.getValue());
}
map.forEach((k, v) -> System.out.println(k + "=" + v));
```

### ⚠️ `HashMap` 原理（面试必考）
-   **底层**：数组 + 链表 + 红黑树 (JDK 8+)。
-   **初始容量**：16，**负载因子**：0.75。
-   **扩容**：当元素数量 > 容量 × 负载因子 时，扩容为原来的 **2 倍**。
-   **哈希冲突**：通过链地址法解决。当链表长度 **> 8** 且数组长度 **≥ 64** 时，链表转为红黑树，提高查询效率（O(n) → O(log n)）。
-   **最佳实践**：预估元素数量，指定初始容量，减少扩容开销。`Map<String, String> map = new HashMap<>(16);`

---

## 十三、泛型（编译时类型检查）

### 泛型类
```java
class Box<T> {
    private T content;
    public void set(T t) { this.content = t; }
    public T get() { return content; }
}
Box<String> box = new Box<>(); // 钻石语法
```

### 泛型方法
```java
public <E> void printArray(E[] arr) {
    for (E e : arr) { System.out.println(e); }
}
```

### 通配符
-   `List<?>`：未知类型，只能读，不能写。
-   `List<? extends T>`：T 或 T 的子类（上界）。
-   `List<? super T>`：T 或 T 的父类（下界）。

### PECS 原则 (Producer Extends, Consumer Super)
-   从集合中**读取**数据（生产）使用 `extends`。
-   向集合中**写入**数据（消费）使用 `super`。

> ⚠️ **类型擦除**：泛型信息在编译后会被擦除，`List<String>` 和 `List<Integer>` 在运行时都是 `List`。

---

## 十四、异常处理

### 异常体系
```
Throwable
├── Error            # JVM 错误，程序无法处理 (如 OutOfMemoryError)
└── Exception        # 程序可处理的异常
    ├── RuntimeException (非检查异常)
    │   ├── NullPointerException
    │   ├── ArrayIndexOutOfBoundsException
    │   ├── ClassCastException
    │   └── ArithmeticException
    └── 检查异常 (Checked Exception) [必须显式处理]
        ├── IOException
        ├── SQLException
        └── ClassNotFoundException
```

### 异常处理
```java
// try-catch-finally
try {
    int result = 10 / 0;
} catch (ArithmeticException e) {
    System.out.println("异常信息：" + e.getMessage());
} catch (Exception e) { // 捕获所有异常
    e.printStackTrace();
} finally {
    System.out.println("无论如何都会执行，通常用于释放资源");
}

// try-with-resources (Java 7+)
try (FileInputStream fis = new FileInputStream("test.txt")) {
    // 使用 fis
} catch (IOException e) {
    e.printStackTrace();
} // fis 自动关闭
```

### `throws` 与 `throw`
```java
// 声明异常，交给调用者处理
public void readFile() throws IOException { ... }

// 手动抛出异常
if (age < 0) {
    throw new IllegalArgumentException("年龄不能为负数");
}
```

### 自定义异常
```java
class MyBusinessException extends Exception {
    public MyBusinessException(String message) {
        super(message);
    }
}
```

---

## 十五、枚举 `enum`

用于定义常量集合，类型安全。
```java
enum Color { RED, GREEN, BLUE; }

Color c = Color.RED;
c.name();      // "RED"
c.ordinal();   // 0 (索引)

// 带属性和构造器的枚举
enum Status {
    SUCCESS(200, "成功"),
    ERROR(500, "失败");

    private final int code;
    private final String msg;

    Status(int code, String msg) {
        this.code = code;
        this.msg = msg;
    }
    // getter...
}
```

---

## 十六、注解 (Annotation)

### 内置注解
-   `@Override`：检查是否重写父类方法。
-   `@Deprecated`：标记方法或类已过时。
-   `@SuppressWarnings`：抑制编译警告。
-   `@FunctionalInterface`：标记函数式接口。

### 元注解
-   `@Target`：指定注解可用位置 (`METHOD`, `FIELD`, `CLASS` 等)。
-   `@Retention`：保留策略 (`SOURCE`, `CLASS`, `RUNTIME`)。
-   `@Documented`：是否生成文档。
-   `@Inherited`：子类是否继承该注解。

### 自定义注解与反射读取
```java
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface Log {
    String value() default "";
}

// 使用反射获取
Method method = obj.getClass().getMethod("doSomething");
if (method.isAnnotationPresent(Log.class)) {
    Log log = method.getAnnotation(Log.class);
    System.out.println(log.value());
}
```

---

## 十七、反射 (Reflection)

### 获取 `Class` 对象
```java
Class<?> clazz1 = Class.forName("com.example.Person");
Class<?> clazz2 = Person.class;
Class<?> clazz3 = new Person().getClass();
```

### 动态操作
```java
// 创建对象
Person p = (Person) clazz.getDeclaredConstructor().newInstance();

// 调用方法
Method method = clazz.getDeclaredMethod("setName", String.class);
method.setAccessible(true); // 突破 private 限制
method.invoke(p, "小明");

// 修改属性
Field field = clazz.getDeclaredField("name");
field.setAccessible(true);
field.set(p, "小红");
```

### 应用场景
-   Spring IoC / DI
-   ORM 框架 (如 MyBatis)
-   注解解析器
-   通用工具类库

> ⚠️ 反射性能较低，非必要不使用。`setAccessible(true)` 会破坏封装性。

---

## 十八、Lambda 表达式 (Java 8)

### 语法
`(parameters) -> { statements; }`

### 简化规则
1.  参数类型可省略。
2.  只有一个参数时，括号可省略。
3.  方法体只有一行时，花括号和 `return` 可省略。

### 示例
```java
// 传统匿名内部类
Runnable r1 = new Runnable() {
    @Override public void run() {
        System.out.println("Hello");
    }
};

// Lambda 表达式
Runnable r2 = () -> System.out.println("Hello");
```

### 常用函数式接口 (`java.util.function`)
| 接口 | 方法 | 描述 |
| :--- | :--- | :--- |
| `Consumer<T>` | `void accept(T t)` | 接收一个参数，无返回 |
| `Supplier<T>` | `T get()` | 无参数，有返回 |
| `Function<T, R>` | `R apply(T t)` | 接收一个，返回一个 |
| `Predicate<T>` | `boolean test(T t)` | 接收一个，返回布尔值 |

---

## 十九、Stream API (Java 8)

### 创建 Stream
```java
Stream<String> stream = list.stream();               // 串行流
Stream<String> parallelStream = list.parallelStream();// 并行流
Stream<Integer> ofStream = Stream.of(1, 2, 3);
```

### 中间操作 (懒加载)
`filter()`, `map()`, `flatMap()`, `distinct()`, `limit()`, `skip()`, `sorted()`, `peek()`

### 终端操作
`forEach()`, `collect()`, `count()`, `reduce()`, `anyMatch()`, `findFirst()`

### 示例
```java
List<Integer> list = Arrays.asList(1, 2, 3, 4, 5, 6);

// 筛选偶数，求平方，收集为 List
List<Integer> result = list.stream()
        .filter(n -> n % 2 == 0)      // [2, 4, 6]
        .map(n -> n * n)             // [4, 16, 36]
        .collect(Collectors.toList());

// 分组
Map<String, List<Person>> groupByName = persons.stream()
        .collect(Collectors.groupingBy(Person::getName));

// 求和
int sum = list.stream().reduce(0, Integer::sum);
```

---

## 二十、`Optional` (Java 8)

用于优雅地处理 `null`，避免 `NullPointerException`。
```java
// 创建
Optional<String> opt1 = Optional.of("value");   // 不能为 null
Optional<String> opt2 = Optional.ofNullable(null); // 可为 null
Optional<String> opt3 = Optional.empty();

// 使用
opt.isPresent();                    // 判断是否有值
opt.ifPresent(v -> System.out.println(v)); // 有值则执行
String v1 = opt.orElse("默认值");     // 提供默认值
String v2 = opt.orElseGet(() -> getDefault()); // 懒加载默认值
String v3 = opt.orElseThrow(RuntimeException::new); // 无值则抛异常

// 链式调用
String name = userRepository.findById(id)
        .map(User::getName)
        .orElse("未知用户");
```

> ⚠️ 不要对集合使用 `Optional`，集合为空时应返回空集合 `Collections.emptyList()`。

---

## 二十一、多线程与并发（重点）

### 创建线程的四种方式
```java
// 1. 继承 Thread
class MyThread extends Thread {
    public void run() { System.out.println("run"); }
}
new MyThread().start();

// 2. 实现 Runnable (推荐)
Runnable task = () -> System.out.println("run");
new Thread(task).start();

// 3. 实现 Callable (有返回值)
FutureTask<String> ft = new FutureTask<>(() -> "结果");
new Thread(ft).start();
String result = ft.get(); // 阻塞等待

// 4. 线程池 (推荐)
```

### 线程状态
`NEW` → `RUNNABLE` → `BLOCKED` / `WAITING` / `TIMED_WAITING` → `TERMINATED`

### 同步机制
#### `synchronized` (内置锁，可重入)
```java
// 锁当前实例
public synchronized void method() { ... }
// 锁 Class 对象
public static synchronized void staticMethod() { ... }
// 同步代码块
synchronized (this) { ... }
```

#### `Lock` (显式锁)
```java
Lock lock = new ReentrantLock();
lock.lock();
try {
    // 临界区
} finally {
    lock.unlock(); // 必须在 finally 中释放
}
```

#### `volatile`
-   保证变量在多个线程间的**可见性**。
-   禁止指令重排序。
-   **不保证原子性**。

#### `Atomic` 类 (CAS)
```java
AtomicInteger count = new AtomicInteger(0);
count.incrementAndGet(); // 原子操作 +1
```

### 线程池（必会）
```java
// 通过 Executors 创建 (不推荐，有风险)
ExecutorService pool1 = Executors.newFixedThreadPool(10);
ExecutorService pool2 = Executors.newCachedThreadPool();

// 手动创建 ThreadPoolExecutor (推荐，参数可控)
ThreadPoolExecutor pool = new ThreadPoolExecutor(
        5,                               // corePoolSize
        10,                              // maximumPoolSize
        60L,                             // keepAliveTime
        TimeUnit.SECONDS,
        new LinkedBlockingQueue<>(100),  // 工作队列
        Executors.defaultThreadFactory(),
        new ThreadPoolExecutor.CallerRunsPolicy() // 拒绝策略
);

// 提交任务
pool.execute(() -> System.out.println("无返回值"));
Future<String> future = pool.submit(() -> "有返回值");
String result = future.get();

// 关闭线程池
pool.shutdown();     // 不再接收新任务，等待已有任务完成
pool.shutdownNow();  // 立即停止
```

### 并发集合
-   `ConcurrentHashMap`：线程安全的 `HashMap`。
-   `CopyOnWriteArrayList`：读多写少场景。
-   `BlockingQueue` 系列：阻塞队列 (`ArrayBlockingQueue`, `LinkedBlockingQueue`)。

---

## 二十二、JVM 内存结构（面试必考）

### JVM 内存划分
```
┌──────────────────────────────────────────┐
│  堆 (Heap) [线程共享]                    │
│  ├── 新生代 (Young Generation)          │
│  │   ├── Eden (8/10)                    │
│  │   └── Survivor (2/10)                │
│  │       ├── From (S0)                  │
│  │       └── To (S1)                    │
│  └── 老年代 (Old Generation)             │
├──────────────────────────────────────────┤
│  方法区 (Method Area) [线程共享]         │
│  └── 运行时常量池                       │
├──────────────────────────────────────────┤
│  虚拟机栈 (VM Stack) [线程私有]          │
│  └── 局部变量表, 操作数栈, 方法出口等    │
├──────────────────────────────────────────┤
│  本地方法栈 (Native Method Stack)        │
├──────────────────────────────────────────┤
│  程序计数器 (PC Register) [线程私有]     │
└──────────────────────────────────────────┘
```

### 垃圾回收 (GC)
-   **可达性分析**：从 `GC Roots` 出发，无法到达的对象被判定为可回收。
-   **GC Roots**：栈中引用、静态变量、JNI 引用等。

### GC 算法
| 算法 | 描述 | 适用区域 |
| :--- | :--- | :--- |
| **标记-清除** | 标记存活对象，清除未标记对象。会产生内存碎片。 | 老年代 |
| **复制算法** | 将内存分为两块，只使用一块，存活对象复制到另一块。 | 新生代 |
| **标记-整理** | 标记存活对象，将其整理到连续内存空间。 | 老年代 |
| **分代收集** | 新生代使用复制算法，老年代使用标记-整理算法。 | 综合 |

### 常见垃圾回收器
-   **Serial**：单线程，Client 模式。
-   **Parallel Scavenge**：JDK 8 默认，关注吞吐量。
-   **CMS**：并发收集，低停顿（已废弃）。
-   **G1**：分区收集，JDK 9+ 默认，兼顾吞吐量和低停顿。
-   **ZGC**：低延迟，适用于大堆内存。

### JVM 常用调优参数
| 参数 | 说明 |
| :--- | :--- |
| `-Xms512m` | 初始堆大小 |
| `-Xmx1024m` | 最大堆大小 |
| `-Xmn256m` | 新生代大小 |
| `-XX:MetaspaceSize=128m` | 元空间初始高水位（不是"初始大小"） |
| `-XX:MaxMetaspaceSize=256m` | 元空间最大大小 |
| `-Xlog:gc*` | 打印 GC 日志（JDK 9+ 推荐，替代旧参数） |
| `-XX:+HeapDumpOnOutOfMemoryError` | OOM 时 Dump 堆内存快照 |

---

## 二十三、类加载机制

### 类加载器层次结构（双亲委派模型）

> **修正**：JDK 9 后为 Bootstrap / Platform / Application 三层，原 Extension ClassLoader 已被 Platform ClassLoader 取代，`lib/ext` 机制已移除。

```
Bootstrap ClassLoader (启动类加载器，加载 java.base 等核心模块)
        ↑
Platform ClassLoader (平台类加载器，JDK 9+)
        ↑
Application ClassLoader (应用类加载器，加载 classpath)
        ↑
Custom ClassLoader (自定义类加载器)
```

### 双亲委派机制
1.  当一个类加载器收到加载请求，先委派给父加载器去完成。
2.  只有当父加载器无法加载时，子加载器才尝试自己加载。
3.  **好处**：避免类重复加载，保证核心类库（如 `java.lang.String`）不被篡改。

### 类加载过程
**加载** → **验证** → **准备** → **解析** → **初始化** → **使用** → **卸载**

---

## 二十四、输入输出流 (IO/NIO)

### IO 流分类
-   **字节流**：处理二进制数据（如图片、音频）。
    -   `InputStream` / `OutputStream`
-   **字符流**：处理文本数据。
    -   `Reader` / `Writer`

### 常用 IO 示例
```java
// 读取文件 (字符流)
try (BufferedReader br = new BufferedReader(new FileReader("test.txt"))) {
    String line;
    while ((line = br.readLine()) != null) {
        System.out.println(line);
    }
}

// 写入文件 (字符流)
try (BufferedWriter bw = new BufferedWriter(new FileWriter("output.txt"))) {
    bw.write("Hello World");
}

// 复制文件 (字节流)
try (InputStream is = new FileInputStream("src.jpg");
     OutputStream os = new FileOutputStream("dst.jpg")) {
    byte[] buffer = new byte[1024];
    int len;
    while ((len = is.read(buffer)) != -1) {
        os.write(buffer, 0, len);
    }
}
```

### 序列化
```java
class User implements Serializable {
    private static final long serialVersionUID = 1L;
    private String name;
    private transient String password; // transient: 不序列化
}

// 序列化
try (ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream("user.ser"))) {
    oos.writeObject(user);
}
// 反序列化
try (ObjectInputStream ois = new ObjectInputStream(new FileInputStream("user.ser"))) {
    User user = (User) ois.readObject();
}
```

### NIO (New IO)
-   **核心组件**：`Channel` (通道), `Buffer` (缓冲区), `Selector` (多路复用器)。
-   **特点**：非阻塞，适用于高并发网络编程（如 Netty）。

### IO 模型对比
| 模型 | 特点 | 适用场景 |
| :--- | :--- | :--- |
| **BIO** | 同步阻塞，一连接一线程 | 连接数少，固定架构 |
| **NIO** | 同步非阻塞，Selector 多路复用 | 连接数多，连接时间短 |
| **AIO** | 异步非阻塞，回调机制 (Java 7+) | 连接数多，连接时间长 |

---

## 二十五、网络编程

### TCP Socket 示例
```java
// 服务端
try (ServerSocket server = new ServerSocket(8080);
     Socket socket = server.accept();
     BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
     PrintWriter out = new PrintWriter(socket.getOutputStream(), true)) {

    String msg = in.readLine();
    out.println("收到: " + msg);
}

// 客户端
try (Socket socket = new Socket("localhost", 8080);
     PrintWriter out = new PrintWriter(socket.getOutputStream(), true);
     BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()))) {
    out.println("Hello Server");
    String response = in.readLine();
}
```

### UDP 示例
```java
// 发送端
try (DatagramSocket socket = new DatagramSocket()) {
    byte[] data = "hello".getBytes();
    DatagramPacket packet = new DatagramPacket(data, data.length,
            InetAddress.getByName("localhost"), 8080);
    socket.send(packet);
}
```

### HTTP 请求
```java
URL url = new URL("https://api.example.com/data");
HttpURLConnection conn = (HttpURLConnection) url.openConnection();
conn.setRequestMethod("GET");
try (BufferedReader reader = new BufferedReader(new InputStreamReader(conn.getInputStream()))) {
    String line;
    while ((line = reader.readLine()) != null) {
        System.out.println(line);
    }
}
conn.disconnect();
```
> 实际开发中更推荐使用 Apache HttpClient 或 Spring 的 RestTemplate/WebClient。

---

## 二十六、JDBC 数据库访问

### 核心步骤
```java
// 1. 加载驱动 (JDBC 4.0+ 可自动加载)
Class.forName("com.mysql.cj.jdbc.Driver");

// 2. 建立连接
String url = "jdbc:mysql://localhost:3306/test?useSSL=false&serverTimezone=UTC";
try (Connection conn = DriverManager.getConnection(url, "root", "123456")) {

    // 3. 创建 Statement (或 PreparedStatement)
    String sql = "SELECT * FROM users WHERE id = ?";
    try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
        pstmt.setInt(1, 1);

        // 4. 执行查询
        try (ResultSet rs = pstmt.executeQuery()) {
            while (rs.next()) {
                int id = rs.getInt("id");
                String name = rs.getString("name");
            }
        }
    }
}
```

### `PreparedStatement` (防 SQL 注入)
```java
String sql = "INSERT INTO users (name, age) VALUES (?, ?)";
try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
    pstmt.setString(1, "小明");
    pstmt.setInt(2, 18);
    pstmt.executeUpdate();
}
```

### 事务管理
```java
conn.setAutoCommit(false);
try {
    // 执行多个 SQL
    conn.commit();
} catch (Exception e) {
    conn.rollback();
}
```

### 连接池 (HikariCP)
```java
HikariConfig config = new HikariConfig();
config.setJdbcUrl(url);
config.setUsername("root");
config.setPassword("123456");
try (HikariDataSource ds = new HikariDataSource(config);
     Connection conn = ds.getConnection()) {
    // 使用连接
}
```

> 实际开发中，通常使用 MyBatis 或 JPA 等 ORM 框架，简化 JDBC 操作。

---

## 二十七、常用工具类

### `Objects` (Java 7)
```java
Objects.requireNonNull(obj);          // 为 null 抛出 NPE
Objects.equals(a, b);                 // 安全比较
Objects.hashCode(obj);
Objects.toString(obj, "默认值");
```

### `Collections`
```java
Collections.sort(list);
Collections.reverse(list);
Collections.shuffle(list);
Collections.emptyList();              // 返回空不可变集合
Collections.singletonList(item);      // 单元素集合
Collections.unmodifiableList(list);   // 返回只读视图
```

### `Arrays`
```java
Arrays.sort(arr);
Arrays.binarySearch(arr, key);
Arrays.fill(arr, 0);
Arrays.copyOf(arr, newLength);
Arrays.equals(arr1, arr2);
Arrays.asList(1, 2, 3);               // 数组 -> List (固定长度)
```

### 其他
-   `UUID.randomUUID().toString()`：生成唯一 ID。
-   `ThreadLocal<T>`：每个线程保存自己的副本，常用于数据库连接、Session 等。**注意 `remove()`，防止内存泄漏。**

---

## 二十八、Java 版本新特性速览

| 版本 (LTS) | 核心新特性 |
| :--- | :--- |
| **Java 8** | Lambda, Stream API, Optional, 新日期时间 API, 接口 default/static 方法 |
| **Java 10** | `var` 局部变量类型推断 |
| **Java 11** | `String.isBlank()`, `Files.readString()`, HttpClient |
| **Java 17** | 密封类 (Sealed Classes), 文本块 (Text Blocks), Record 类, 模式匹配 instanceof, Switch 表达式 |
| **Java 21** | 虚拟线程 (Virtual Threads), Record 模式, 分代 ZGC；结构化并发为预览 API |

> **修正**：`var` 是 Java 10 引入，不是 Java 11；结构化并发在 Java 21 仍是预览特性。

---

## 二十九、常见框架速览

| 框架/组件 | 核心概念 |
| :--- | :--- |
| **Spring Framework** | IoC (控制反转), DI (依赖注入), AOP (面向切面), MVC, TX (事务) |
| **Spring Boot** | `@SpringBootApplication`, 自动配置, Starter 依赖, application.properties/yml |
| **MyBatis** | SQL 映射框架, `@Mapper`, XML 配置 |
| **Hibernate / JPA** | ORM 框架, `@Entity`, `@Table`, `@Id`, `@GeneratedValue` |
| **Netty** | 异步事件驱动网络框架, 常用于 RPC 和高性能网关 |

---

## 三十、性能优化技巧

1.  **字符串拼接**：循环内使用 `StringBuilder`。
2.  **指定 Map 初始容量**：减少扩容开销，如 `new HashMap<>(16)`。
3.  **避免频繁创建对象**：考虑使用对象池 (Object Pool)。
4.  **数据库批量操作**：使用 JDBC 的 `addBatch()` / `executeBatch()`。
5.  **合理使用缓存**：应用内缓存 (Caffeine) + 分布式缓存 (Redis)。
6.  **使用线程池**：代替手动创建线程。
7.  **减少数据库查询**：避免在循环内查询，可使用批量查询或连接查询。
8.  **使用 `try-with-resources`**：自动关闭资源。
9.  **谨慎使用并行流**：注意线程安全问题。
10. **JVM 调优**：根据应用特点设置合适的堆大小和 GC 策略。

---

## 三十一、常见陷阱与坑

| 陷阱 | 说明与解决方案 |
| :--- | :--- |
| **`==` 比较 String** | 应使用 `equals()` 比较内容。 |
| **浮点数精度问题** | `0.1 + 0.2 != 0.3`，使用 `BigDecimal`。 |
| **集合遍历时删除** | 使用 `Iterator.remove()` 或 Java 8 的 `removeIf()`。 |
| **空指针 (NPE)** | 熟练使用 `Optional`，或进行判空 `if (obj != null)`。 |
| **整数溢出** | 注意 `Integer.MAX_VALUE + 1` 会变成负数。 |
| **`equals` 和 `hashCode` 不一致** | 重写 `equals` 必须重写 `hashCode`，否则 `HashMap` 会有问题。 |
| **异常吞没** | `catch` 块中必须记录日志或抛出异常，绝对不能什么都不做。 |
| **线程安全问题** | 使用 `ConcurrentHashMap` 替代 `HashMap`。 |

---

## 三十二、速查小抄

### 常用代码片段
```java
// 输出与输入
System.out.println("Hello");
Scanner sc = new Scanner(System.in);
String input = sc.nextLine();

// 集合速选
ArrayList   // 快速存取
LinkedList  // 频繁头尾增删
HashSet     // 去重
TreeSet     // 自动排序
HashMap     // 键值对
ConcurrentHashMap // 线程安全键值对

// 线程与异步
new Thread(() -> System.out.println("run")).start();
Executors.newFixedThreadPool(10);
CompletableFuture.runAsync(() -> { ... });
```

### Maven 常用命令
```bash
mvn clean compile
mvn test
mvn package
mvn install
```

---

## 三十三、学习路线建议

1.  **阶段一：Java 基础 (1-2个月)**
    -   语法、面向对象、集合框架、异常、IO、多线程基础。
    -   实践：学生管理系统、简易聊天室。
2.  **阶段二：Java 进阶 (2-3个月)**
    -   JVM 原理、并发编程深入、网络编程、JDBC、设计模式 (单例、工厂、代理)。
3.  **阶段三：Java Web 与框架 (2-3个月)**
    -   Spring / Spring Boot, MyBatis / JPA。
    -   实践：博客系统、电商后台。
4.  **阶段四：分布式与微服务 (3个月+)**
    -   Redis, MQ, Spring Cloud, Docker, K8s。

---

## 三十四、面试重点排序

| 优先级 | 知识点 |
| :---: | :--- |
| ⭐⭐⭐ | 集合框架 (特别是 HashMap 原理), JVM (内存结构, GC, 类加载) |
| ⭐⭐⭐ | 多线程并发 (线程池, 锁, synchronized), Spring (IoC, AOP, 事务) |
| ⭐⭐ | MySQL (索引, SQL 优化), 设计模式 (单例, 工厂, 代理) |
| ⭐ | 网络编程, NIO, 数据结构与算法 |

---

## 三十五、常用设计模式（面试高频）

> 设计模式是面试中的"必考题"，这里只列最常考的 8 种，附带极简示例。

### 1. 单例模式（Singleton）
**确保一个类只有一个实例**，并提供一个全局访问点。

```java
// 懒汉式（双重检查锁，线程安全）—— 推荐
public class Singleton {
    private static volatile Singleton instance;
    private Singleton() {}
    public static Singleton getInstance() {
        if (instance == null) {
            synchronized (Singleton.class) {
                if (instance == null) {
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }
}

// 静态内部类方式 —— 最优雅
public class Singleton {
    private Singleton() {}
    private static class Holder {
        private static final Singleton INSTANCE = new Singleton();
    }
    public static Singleton getInstance() {
        return Holder.INSTANCE;
    }
}
```

### 2. 工厂模式（Factory）
**将对象的创建逻辑封装起来**，客户端不直接 `new`。

```java
interface Product { void use(); }
class ProductA implements Product { public void use() { System.out.println("A"); } }
class ProductB implements Product { public void use() { System.out.println("B"); } }

class Factory {
    public static Product create(String type) {
        if ("A".equals(type)) return new ProductA();
        if ("B".equals(type)) return new ProductB();
        throw new IllegalArgumentException();
    }
}
```

### 3. 代理模式（Proxy）
**为对象提供一个代理，控制对它的访问**。Spring AOP 底层就是动态代理。

```java
// 静态代理
interface Service { void execute(); }
class RealService implements Service { public void execute() { System.out.println("real"); } }
class ProxyService implements Service {
    private RealService real;
    public ProxyService(RealService real) { this.real = real; }
    public void execute() {
        System.out.println("before");
        real.execute();
        System.out.println("after");
    }
}
```

### 4. 策略模式（Strategy）
**定义一组算法，使它们可以互相替换**。

```java
interface Strategy { int doOperation(int a, int b); }
class Add implements Strategy { public int doOperation(int a, int b) { return a + b; } }
class Sub implements Strategy { public int doOperation(int a, int b) { return a - b; } }

class Context {
    private Strategy strategy;
    public Context(Strategy strategy) { this.strategy = strategy; }
    public int execute(int a, int b) { return strategy.doOperation(a, b); }
}
```

### 5. 模板方法模式（Template Method）
**定义一个算法的骨架，将某些步骤延迟到子类**。

```java
abstract class Game {
    abstract void init();
    abstract void play();
    abstract void end();
    public final void run() {  // 模板方法
        init();
        play();
        end();
    }
}
```

### 6. 观察者模式（Observer）
**对象间的一对多依赖关系**，当对象状态改变时，所有依赖者得到通知。

```java
// Java 内置支持：Observable + Observer（已过时，建议用 EventBus 或自定义）
```

### 7. 建造者模式（Builder）
**分步构建复杂对象**，Lombok 的 `@Builder` 就是它。

```java
User user = User.builder().name("张三").age(18).build();
```

### 8. 适配器模式（Adapter）
**让接口不兼容的类可以协同工作**。例如 `Arrays.asList()` 把数组适配成 List。

---

## 三十六、Java 8 之前的时间处理（遗留问题）

> 虽然推荐用 `java.time`，但老项目里大量存在，面试也常问。

```java
import java.util.Date;
import java.text.SimpleDateFormat;
import java.util.Calendar;

// Date 的坑：年份从 1900 开始，月份从 0 开始
Date d = new Date();
System.out.println(d.getYear() + 1900); // 需要 +1900
System.out.println(d.getMonth() + 1);   // 需要 +1

// SimpleDateFormat 线程不安全
SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
String formatted = sdf.format(d);

// Calendar 是替代方案
Calendar cal = Calendar.getInstance();
cal.set(2024, Calendar.JANUARY, 1);
cal.add(Calendar.DAY_OF_MONTH, 7);
```

> **改进**：Java 8 的 `LocalDateTime` 是不可变的、线程安全的，请优先使用。

---

## 三十七、`equals()` 与 `hashCode()` 契约（必知）

- **如果两个对象 `equals()` 为 `true`，它们的 `hashCode()` 必须相等**。
- **如果 `hashCode()` 相等，`equals()` 不一定为 `true`**（哈希冲突）。
- **在 `HashSet` / `HashMap` 中**，先比较 `hashCode()`，再比较 `equals()`。

```java
@Override
public boolean equals(Object o) {
    if (this == o) return true;
    if (o == null || getClass() != o.getClass()) return false;
    Person p = (Person) o;
    return age == p.age && Objects.equals(name, p.name);
}

@Override
public int hashCode() {
    return Objects.hash(name, age);
}
```

> **最佳实践**：使用 `Objects.hash()` 自动生成，或用 IDE 生成。

---

## 三十八、深拷贝 vs 浅拷贝

| 类型 | 说明 | 实现方式 |
| :--- | :--- | :--- |
| **浅拷贝** | 复制对象的基本类型字段，引用类型只复制引用 | `super.clone()` (需实现 `Cloneable`) |
| **深拷贝** | 完全复制整个对象树，包括所有引用对象 | 序列化 / 手动递归复制 / 拷贝构造函数 |

```java
// 通过序列化实现深拷贝（通用但性能较低）
public static <T> T deepCopy(T obj) throws Exception {
    ByteArrayOutputStream baos = new ByteArrayOutputStream();
    ObjectOutputStream oos = new ObjectOutputStream(baos);
    oos.writeObject(obj);
    ByteArrayInputStream bais = new ByteArrayInputStream(baos.toByteArray());
    ObjectInputStream ois = new ObjectInputStream(bais);
    return (T) ois.readObject();
}
```

---

## 三十九、JVM 调优实战参数

### 内存相关
```bash
-Xms2g               # 初始堆大小 2G
-Xmx2g               # 最大堆大小 2G（一般设置相同，避免扩容抖动）
-Xmn512m             # 新生代大小（G1 下不建议随意设）
-XX:MetaspaceSize=256m        # 元空间初始高水位
-XX:MaxMetaspaceSize=256m
-XX:MaxDirectMemorySize=1g    # 直接内存（NIO 用）
```

### GC 相关
```bash
-XX:+UseG1GC                              # 使用 G1 回收器（JDK9+ 默认）
-XX:MaxGCPauseMillis=200                  # 目标最大 GC 停顿时间（毫秒）
-XX:ParallelGCThreads=4                   # GC 并行线程数
-XX:ConcGCThreads=2                       # 并发 GC 线程数
-XX:G1HeapRegionSize=16m                  # G1 Region 大小
-XX:G1NewSizePercent=5                    # 新生代初始占比
```

### 调试与日志
```bash
-Xlog:gc*:file=/var/log/gc.log:time,uptime,level,tags   # JDK 9+ 统一日志
-XX:+HeapDumpOnOutOfMemoryError             # OOM 时 dump
-XX:HeapDumpPath=/var/log/heapdump.hprof
-XX:+DisableExplicitGC                      # 禁止代码中调用 System.gc()
```

> **修正**：JDK 9 起推荐使用 `-Xlog:gc*` 替代 `-XX:+PrintGCDetails -XX:+PrintGCDateStamps -Xloggc:...`。

---

## 四十、常见 OOM 场景及解决

| OOM 类型 | 原因 | 解决方案 |
| :--- | :--- | :--- |
| **`OutOfMemoryError: Java heap space`** | 堆内存不足，对象无法分配 | 增大 `-Xmx`，排查内存泄漏（用 MAT/JProfiler） |
| **`OutOfMemoryError: Metaspace`** | 元空间不足，加载类太多 | 增大 `-XX:MaxMetaspaceSize`，排查类加载器泄漏 |
| **`OutOfMemoryError: Direct buffer memory`** | 直接内存（NIO）不足 | 增大 `-XX:MaxDirectMemorySize`，检查 Netty 等框架 |
| **`OutOfMemoryError: unable to create new native thread`** | 线程数超过系统限制 | 减少线程数，检查线程池配置，调高系统 `ulimit -u` |
| **`StackOverflowError`** | 栈内存不足，通常为递归过深 | 检查递归终止条件，增大 `-Xss` |

---

## 四十一、JVM 性能监控工具

| 工具 | 用途 |
| :--- | :--- |
| `jps` | 查看当前 Java 进程列表 |
| `jstat` | 查看 JVM 统计信息（GC、类加载等） |
| `jmap` | 内存快照（dump） |
| `jstack` | 线程快照（查看死锁、线程状态） |
| `jcmd` | 综合性诊断命令（推荐） |
| `jconsole` | 可视化监控（JDK 自带） |
| `VisualVM` | 功能更全的可视化工具（推荐） |
| `MAT` / `JProfiler` / `Arthas` | 专业内存分析和性能诊断（阿里 Arthas 尤其推荐） |

**常用命令示例**：
```bash
jps -l                           # 查看 Java 进程
jstat -gc <pid> 1000 10          # 每秒打印一次 GC 信息，共 10 次
jmap -dump:live,format=b,file=heap.bin <pid>  # 强制 Full GC 并 dump
jstack <pid> > stack.log         # 导出线程栈
```

---

## 四十二、线程池的 7 个核心参数详解

```java
public ThreadPoolExecutor(
    int corePoolSize,           // 核心线程数（常驻）
    int maximumPoolSize,        // 最大线程数
    long keepAliveTime,         // 非核心线程空闲存活时间
    TimeUnit unit,              // 时间单位
    BlockingQueue<Runnable> workQueue,  // 任务队列
    ThreadFactory threadFactory,        // 线程工厂（可自定义线程名）
    RejectedExecutionHandler handler    // 拒绝策略
)
```

### 工作流程（必会）
1. 线程数 < `corePoolSize` → 创建新线程执行任务。
2. 线程数 ≥ `corePoolSize` → 任务放入队列。
3. 队列满，且线程数 < `maximumPoolSize` → 创建非核心线程执行任务。
4. 队列满，且线程数 = `maximumPoolSize` → 执行**拒绝策略**。

### 常用队列与拒绝策略
| 队列 | 特点 |
| :--- | :--- |
| `ArrayBlockingQueue` | 有界数组队列 |
| `LinkedBlockingQueue` | 可选有界链表队列（`newFixedThreadPool` 默认无界） |
| `SynchronousQueue` | 不存储任务，直接交给线程（`newCachedThreadPool` 用） |
| `PriorityBlockingQueue` | 优先级队列 |

| 拒绝策略 | 行为 |
| :--- | :--- |
| `AbortPolicy` | 抛 `RejectedExecutionException`（默认） |
| `CallerRunsPolicy` | 由调用线程执行（降级策略，推荐） |
| `DiscardPolicy` | 静默丢弃 |
| `DiscardOldestPolicy` | 丢弃队列中最旧的任务 |

---

## 四十三、`CompletableFuture` 异步编程（Java 8）

> 比 `Future` 强大得多，支持回调、组合、异常处理。

```java
// 创建异步任务
CompletableFuture<String> future = CompletableFuture.supplyAsync(() -> {
    // 耗时操作
    return "result";
});

// 链式处理
CompletableFuture<String> result = CompletableFuture.supplyAsync(() -> "hello")
        .thenApply(String::toUpperCase)   // 同步转换
        .thenCompose(s -> CompletableFuture.supplyAsync(() -> s + " world")) // 异步组合
        .exceptionally(e -> "fallback");  // 异常处理

// 组合多个 CompletableFuture
CompletableFuture<String> f1 = CompletableFuture.supplyAsync(() -> "A");
CompletableFuture<String> f2 = CompletableFuture.supplyAsync(() -> "B");
CompletableFuture<Void> all = CompletableFuture.allOf(f1, f2);
all.join(); // 等待所有完成

// 获取结果
String resultStr = result.join(); // 阻塞等待
resultStr = result.get(5, TimeUnit.SECONDS); // 带超时
```

### 常见静态方法
| 方法 | 说明 |
| :--- | :--- |
| `supplyAsync()` | 有返回值的异步任务 |
| `runAsync()` | 无返回值的异步任务 |
| `thenApply()` | 同步转换 |
| `thenCompose()` | 异步转换（flatMap） |
| `thenCombine()` | 组合两个任务的结果 |
| `thenAccept()` | 消费结果，无返回 |
| `exceptionally()` | 异常时回退 |
| `whenComplete()` | 无论成功或失败都执行 |

---

## 四十四、`ThreadLocal` 详解与内存泄漏

### 使用场景
- 每个线程保存独立的数据库连接、Session、用户信息。
- 替代参数传递（透传上下文）。

```java
public class UserContext {
    private static final ThreadLocal<User> currentUser = new ThreadLocal<>();
    public static void set(User user) { currentUser.set(user); }
    public static User get() { return currentUser.get(); }
    public static void clear() { currentUser.remove(); }
}

// 在拦截器中设置，在请求结束后清除
```

### ⚠️ 内存泄漏问题
- **原因**：`ThreadLocalMap` 的 key 是 `ThreadLocal` 对象的**弱引用**，但 value 是**强引用**。当 `ThreadLocal` 被 GC 后，key 变为 `null`，但 value 仍然存在，导致无法回收。
- **解决**：使用后务必调用 `remove()`（尤其在 `finally` 中）。

```java
try {
    UserContext.set(user);
    // 业务逻辑
} finally {
    UserContext.clear(); // 关键！
}
```

---

## 四十五、`ConcurrentHashMap` 原理深入（JDK 8）

| 特性 | 说明 |
| :--- | :--- |
| **底层** | 数组 + 链表 + 红黑树（与 `HashMap` 相同） |
| **线程安全机制** | CAS + `synchronized`（锁粒度细化到每个桶的头节点） |
| **读取** | 无锁（volatile 保证可见性） |
| **写入** | 对桶的首节点加 `synchronized` 锁 |
| **扩容** | 支持并发扩容，每个线程负责一部分（`transfer`） |
| **计数** | 使用 `CounterCell` 数组 + CAS 累加，替代全局计数器 |

> **对比 `Hashtable`**：`Hashtable` 是全局锁（`synchronized` 修饰整个方法），并发性能极差。
>
> **JDK 7 vs JDK 8**：JDK 7 用分段锁（Segment），JDK 8 改为 CAS + synchronized 锁桶头节点。

---

## 四十六、`CAS`（Compare-And-Swap）与 ABA 问题

### CAS 原理
- 一种**乐观锁**机制，三个操作数：内存位置 V、期望值 A、新值 B。
- 只有当 V 的值等于 A 时，才将其更新为 B，否则失败重试（自旋）。

```java
// AtomicInteger 源码简化
public final int incrementAndGet() {
    int current;
    int next;
    do {
        current = get();    // 获取当前值
        next = current + 1; // 计算新值
    } while (!compareAndSet(current, next)); // CAS 重试
    return next;
}
```

### ABA 问题
- **场景**：线程1 将值从 A 改为 B 再改回 A，线程2 检查时发现仍是 A，认为没有变化，但实际上已经变了。
- **解决**：使用 `AtomicStampedReference` 或 `AtomicMarkableReference`，通过版本号/标记位解决。

---

## 四十七、`synchronized` 与 `ReentrantLock` 对比

| 特性 | `synchronized` | `ReentrantLock` |
| :--- | :--- | :--- |
| 锁实现 | JVM 内置（C++ 实现） | Java 代码实现（`AbstractQueuedSynchronizer`） |
| 灵活性 | 简单，自动释放 | 需手动 `lock()` / `unlock()`（必须 finally） |
| 可中断性 | 不支持 | 支持 `lockInterruptibly()` |
| 超时获取锁 | 不支持 | 支持 `tryLock(timeout, unit)` |
| 公平锁 | 非公平 | 可指定公平/非公平（默认为非公平） |
| 条件变量 | `wait()` / `notify()` | `newCondition()` 支持多个 Condition |
| 性能 | JDK 1.6 后已优化，性能差距不大 | 大致相当 |

```java
// ReentrantLock 典型用法
Lock lock = new ReentrantLock();
lock.lock();
try {
    // 临界区
} finally {
    lock.unlock();
}
```

> **偏向锁**：JDK 15 起默认禁用，后续版本已移除，不宜再作为默认优化讲。

---

## 四十八、`CountDownLatch`、`CyclicBarrier`、`Semaphore` 对比

| 工具 | 用途 | 特点 |
| :--- | :--- | :--- |
| `CountDownLatch` | 等待多个线程完成 | 计数器只能减，不能复用 |
| `CyclicBarrier` | 多个线程互相等待，到达屏障点后一起执行 | 计数器可以重置，可复用 |
| `Semaphore` | 控制同时访问资源的线程数（限流） | 许可证机制 |

```java
// CountDownLatch
CountDownLatch latch = new CountDownLatch(3);
for (int i = 0; i < 3; i++) {
    new Thread(() -> {
        // 执行任务
        latch.countDown();
    }).start();
}
latch.await(); // 等待所有线程完成

// CyclicBarrier
CyclicBarrier barrier = new CyclicBarrier(3, () -> System.out.println("都到了"));
for (int i = 0; i < 3; i++) {
    new Thread(() -> {
        barrier.await(); // 等待其他线程
        // 继续执行
    }).start();
}
```

---

## 四十九、几种常用锁的概念

| 锁类型 | 说明 |
| :--- | :--- |
| **悲观锁** | 假设并发冲突高，每次操作都加锁（如 `synchronized`） |
| **乐观锁** | 假设并发冲突低，提交时检查冲突（如 CAS） |
| **公平锁** | 按线程请求顺序获取锁 |
| **非公平锁** | 允许线程"插队"，可能产生饥饿（`synchronized` 默认） |
| **可重入锁** | 同一个线程可以多次获取同一把锁（如 `synchronized` / `ReentrantLock`） |
| **读写锁** | `ReentrantReadWriteLock`，读共享、写独占 |
| **自旋锁** | 循环等待，不释放 CPU（适用于临界区很小） |
| **轻量级锁/重量级锁** | JVM 对 `synchronized` 的优化（偏向锁 → 轻量级锁 → 重量级锁） |

---

## 五十、Spring 常用注解大全

| 注解 | 用途 |
| :--- | :--- |
| `@Component` | 标识一个普通 Bean 被 Spring 管理 |
| `@Service` | 标识 Service 层 Bean（继承 `@Component`） |
| `@Repository` | 标识 DAO 层 Bean（继承 `@Component`，同时转换异常） |
| `@Controller` / `@RestController` | 标识 Web 控制器（`@RestController` = `@Controller` + `@ResponseBody`） |
| `@Autowired` | 按类型注入 |
| `@Resource` | 默认按名称注入，找不到再按类型（Java 标准） |
| `@Qualifier` | 指定注入的 Bean 名称（与 `@Autowired` 配合） |
| `@Value` | 注入配置属性（如 `${property.key}`） |
| `@Configuration` | 标识配置类 |
| `@Bean` | 在配置类中定义一个 Bean |
| `@Scope` | 指定 Bean 作用域（`singleton`, `prototype`, `request`, `session`） |
| `@Transactional` | 声明式事务管理 |
| `@Async` | 异步执行（需 `@EnableAsync`） |
| `@EventListener` | 监听事件 |
| `@Conditional` | 条件化配置（如 `@ConditionalOnProperty`） |
| `@Profile` | 指定不同环境配置（dev/prod/test） |
| `@EnableScheduling` / `@Scheduled` | 定时任务 |
| `@Cacheable` / `@CacheEvict` / `@CachePut` | 缓存管理 |

---

## 五十一、Spring Boot 自动配置原理（面试高频）

1. **`@SpringBootApplication`** 是一个组合注解，包含：
   - `@SpringBootConfiguration`（本质是 `@Configuration`）
   - `@EnableAutoConfiguration`（核心）
   - `@ComponentScan`

2. **`@EnableAutoConfiguration`** 通过 `@Import(AutoConfigurationImportSelector.class)` 导入。

3. `AutoConfigurationImportSelector` 会读取自动配置类列表：
   - Spring Boot 2.7 之前：`META-INF/spring.factories`
   - **Spring Boot 2.7+ / 3.x**：`META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`

4. Spring Boot 会**按条件**（`@Conditional`）判断这些自动配置类是否生效，例如：
   - `@ConditionalOnClass`：classpath 中存在某类
   - `@ConditionalOnMissingBean`：容器中不存在某 Bean
   - `@ConditionalOnProperty`：配置文件中存在指定属性

5. 最终生效的自动配置类会加载到 Spring 容器中。

> 可以通过 `application.properties` 中 `debug=true` 查看自动配置的匹配报告。

---

## 五十二、Spring AOP 核心概念

| 术语 | 说明 |
| :--- | :--- |
| **切面 (Aspect)** | 横切关注点的模块化（如日志、权限） |
| **连接点 (JoinPoint)** | 程序执行过程中的一个点（如方法执行） |
| **切入点 (Pointcut)** | 一组连接点的匹配规则 |
| **通知 (Advice)** | 在特定切入点上执行的动作 |
| **织入 (Weaving)** | 将切面应用到目标对象的过程 |

### 通知类型
```java
@Before("execution(* com.example.service.*.*(..))")
public void before() { ... }

@After("execution(* com.example.service.*.*(..))")
public void after() { ... }

@AfterReturning(pointcut = "...", returning = "result")
public void afterReturning(Object result) { ... }

@AfterThrowing(pointcut = "...", throwing = "ex")
public void afterThrowing(Exception ex) { ... }

@Around("...")
public Object around(ProceedingJoinPoint pjp) throws Throwable {
    // before
    Object result = pjp.proceed();
    // after
    return result;
}
```

---

## 五十三、MyBatis 核心原理

### 执行流程
1. 解析 XML 或注解中的 SQL，生成 `MappedStatement`。
2. 通过 `SqlSession` 的 `getMapper()` 生成 Mapper 接口的**动态代理对象**。
3. 调用 Mapper 方法 → 代理对象调用 `SqlSession` 的 `selectOne()` / `insert()` 等。
4. `SqlSession` 通过 `Executor` 执行 SQL，并处理参数映射、结果集映射。

### 核心组件
| 组件 | 职责 |
| :--- | :--- |
| `SqlSessionFactory` | 创建 `SqlSession` |
| `SqlSession` | 提供增删改查 API |
| `Executor` | 真正执行 SQL（包括缓存管理） |
| `StatementHandler` | 处理 JDBC Statement 的创建与参数设置 |
| `ParameterHandler` | 参数映射 |
| `ResultSetHandler` | 结果集映射 |
| `TypeHandler` | Java 类型与 JDBC 类型转换 |

---

## 五十四、JPA / Hibernate 核心注解

| 注解 | 用途 |
| :--- | :--- |
| `@Entity` | 标识实体类 |
| `@Table(name = "users")` | 指定表名 |
| `@Id` | 标识主键 |
| `@GeneratedValue(strategy = GenerationType.IDENTITY)` | 自增主键 |
| `@Column(name = "user_name", nullable = false)` | 字段映射 |
| `@Transient` | 忽略该字段（不映射到数据库） |
| `@OneToMany` / `@ManyToOne` | 一对多 / 多对一关系 |
| `@OneToOne` / `@ManyToMany` | 一对一 / 多对多关系 |
| `@JoinColumn(name = "user_id")` | 外键字段 |
| `@JoinTable` | 多对多中间表 |
| `@PrePersist` / `@PreUpdate` | 实体保存/更新前回调 |

---

## 五十五、缓存机制：本地缓存 vs 分布式缓存

| 类型 | 代表 | 优点 | 缺点 |
| :--- | :--- | :--- | :--- |
| **本地缓存** | Caffeine, Guava Cache, Ehcache | 极快、无网络开销 | 无法跨 JVM 共享，数据不一致 |
| **分布式缓存** | Redis, Memcached | 集中管理、可共享、持久化 | 有网络延迟、维护成本高 |

### 多级缓存策略
```
请求 → 本地缓存 (Caffeine) → 分布式缓存 (Redis) → 数据库 (DB)
```

---

## 五十六、消息队列（MQ）基础概念

| 概念 | 说明 |
| :--- | :--- |
| **Producer (生产者)** | 发送消息的一方 |
| **Consumer (消费者)** | 接收消息的一方 |
| **Broker** | 消息中间件服务端 |
| **Topic** | 发布/订阅模式的主题（如 Kafka、RocketMQ） |
| **Queue** | 点对点模式的队列（如 RabbitMQ） |
| **Partition** | 分区（Kafka 中的水平分片） |
| **Offset** | 消息在分区中的位置（Kafka） |
| **ACK** | 消息确认机制 |

### 常用 MQ
- **RabbitMQ**：易用、功能全，适合中小规模。
- **Kafka**：高吞吐、持久化，适合日志收集、大数据流。
- **RocketMQ**：阿里出品，适合金融级场景。

---

## 五十七、微服务核心组件（Spring Cloud）

| 组件 | 作用 |
| :--- | :--- |
| **服务注册中心** | Eureka / Nacos / Zookeeper（服务发现与注册） |
| **配置中心** | Spring Cloud Config / Nacos Config（集中管理配置） |
| **API 网关** | Spring Cloud Gateway / Zuul（路由、鉴权、限流） |
| **负载均衡** | Ribbon / Spring Cloud LoadBalancer（客户端负载均衡） |
| **断路器** | Hystrix / Resilience4j / Sentinel（熔断、降级、限流） |
| **链路追踪** | Sleuth + Zipkin / SkyWalking（分布式追踪） |
| **消息驱动** | Spring Cloud Stream（统一消息编程模型） |
| **安全** | Spring Security + OAuth2 / Keycloak |

---

## 五十八、性能优化进阶

### JVM 调优 Checklist
- [ ] 设置 `-Xms` = `-Xmx`，避免扩容抖动。
- [ ] 合理设置 `-Xmn`（G1 下不建议随意设）。
- [ ] 选择合适的 GC 回收器（G1 为默认推荐，大堆可用 ZGC）。
- [ ] 配置 OOM 自动 dump 以及 GC 日志，便于事后分析。
- [ ] 排查内存泄漏（使用 MAT / JProfiler / Arthas）。
- [ ] 分析 GC 频率和停顿时间，调整 `-XX:MaxGCPauseMillis`。

### 数据库优化 Checklist
- [ ] 为查询字段建立合适的索引（遵循最左前缀原则）。
- [ ] 避免 `SELECT *`，只查询必要字段。
- [ ] 使用 `EXPLAIN` 分析执行计划。
- [ ] 分页查询优化（避免大 offset，使用游标或子查询）。
- [ ] 读写分离（主从复制）。
- [ ] 分库分表（ShardingSphere / MyCat）。

### 代码层面优化 Checklist
- [ ] 使用批量操作（数据库 batch、Redis pipeline）。
- [ ] 减少锁粒度，避免持锁时间长。
- [ ] 谨慎使用反射，注意性能损耗。
- [ ] 使用池化技术（线程池、数据库连接池、对象池）。
- [ ] 合理使用缓存，避免缓存雪崩/击穿/穿透。
- [ ] 异步处理非核心流程（MQ / `@Async`）。

---

## 五十九、Docker 常用命令（配合 Java 部署）

```bash
# 镜像管理
docker build -t my-app:1.0 .      # 构建镜像
docker images                     # 查看镜像列表
docker rmi <image_id>             # 删除镜像

# 容器管理
docker run -d -p 8080:8080 --name my-app my-app:1.0  # 运行容器
docker ps -a                     # 查看所有容器
docker stop <container_id>       # 停止容器
docker rm <container_id>         # 删除容器
docker logs -f <container_id>    # 查看日志

# 进入容器
docker exec -it <container_id> /bin/bash

# Dockerfile 示例
FROM eclipse-temurin:17-jdk      # 推荐替代 openjdk:17-jdk-slim
WORKDIR /app
COPY target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

---

## 六十、Linux 常用命令（排查 Java 问题）

```bash
# 查看进程
ps -ef | grep java
jps -l

# 查看系统资源
top -H -p <pid>    # 查看进程内的线程 CPU 占用
free -h            # 查看内存
df -h              # 查看磁盘
netstat -tunlp     # 查看端口占用

# 查看日志
tail -f app.log
grep "ERROR" app.log | less

# 网络调试
curl -v http://localhost:8080/health
telnet localhost 8080

# 文件传输
scp -r app.jar user@host:/opt/app/
```

---

## 六十一、Git 常用命令速查

```bash
# 基础操作
git clone <url>
git add .
git commit -m "message"
git push origin main
git pull origin main

# 分支管理
git branch                # 查看本地分支
git checkout -b feature   # 创建并切换分支
git merge feature         # 合并分支
git rebase main           # 变基

# 撤销操作
git reset --hard HEAD^    # 回退到上一次提交
git revert <commit>       # 撤销某次提交（保留历史）
git stash                 # 暂存当前修改
git stash pop             # 恢复暂存

# 查看历史
git log --oneline --graph --all
git diff
```

---

## 六十二、常用 Maven / Gradle 依赖

### Maven 常用依赖坐标
```xml
<!-- Spring Boot Starter -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>

<!-- MyBatis -->
<dependency>
    <groupId>org.mybatis.spring.boot</groupId>
    <artifactId>mybatis-spring-boot-starter</artifactId>
    <version>3.0.3</version>
</dependency>

<!-- MySQL 驱动 -->
<dependency>
    <groupId>com.mysql</groupId>
    <artifactId>mysql-connector-j</artifactId>
    <version>8.0.33</version>
</dependency>

<!-- Redis -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
</dependency>

<!-- 工具类 -->
<dependency>
    <groupId>org.projectlombok</groupId>
    <artifactId>lombok</artifactId>
    <scope>provided</scope>
</dependency>
<dependency>
    <groupId>com.google.guava</groupId>
    <artifactId>guava</artifactId>
    <version>33.0.0-jre</version>
</dependency>

<!-- 测试 -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-test</artifactId>
    <scope>test</scope>
</dependency>
```

---

## 六十三、常见面试题补充

### 1. `String`, `StringBuilder`, `StringBuffer` 的区别？
| 类型 | 可变性 | 线程安全 | 性能 |
| :--- | :--- | :--- | :--- |
| `String` | 不可变 | 安全 | 最低（每次操作创建新对象） |
| `StringBuilder` | 可变 | 不安全 | 最高 |
| `StringBuffer` | 可变 | 安全（方法同步） | 次高 |

### 2. `ArrayList` 与 `LinkedList` 的区别？
- **底层**：`ArrayList` 是数组，`LinkedList` 是双向链表。
- **查询**：`ArrayList` O(1)，`LinkedList` O(n)。
- **增删**：`ArrayList` 尾部 O(1)，中间 O(n)；`LinkedList` 头尾 O(1)，中间 O(n)（需要先遍历）。
- **内存**：`ArrayList` 连续内存，`LinkedList` 每个元素有额外指针开销。

### 3. `HashSet` 如何保证元素不重复？
- 通过 `HashMap` 实现，元素作为 key，value 为固定 `PRESENT` 对象。
- 先计算 `hashCode()`，再调用 `equals()` 比较，都相同则视为重复。

### 4. `HashMap` 与 `Hashtable` 的区别？
| 特性 | `HashMap` | `Hashtable` |
| :--- | :--- | :--- |
| 线程安全 | 不安全 | 安全（`synchronized`） |
| 允许 null | key/value 均可为 null | 不允许 null |
| 效率 | 高 | 低 |
| 迭代器 | fail-fast | fail-safe（Enumeration） |

### 5. `synchronized` 和 `volatile` 的区别？
| 特性 | `synchronized` | `volatile` |
| :--- | :--- | :--- |
| 原子性 | 保证 | 不保证 |
| 可见性 | 保证 | 保证 |
| 防止指令重排 | 部分保证 | 保证 |
| 使用场景 | 复合操作（读-改-写） | 简单状态标记 |

### 6. `@Transactional` 失效的场景？
- 方法不是 `public` 的。
- 内部方法调用（`this.method()`，没有通过代理）。
- 异常被捕获且未重新抛出（事务只对未捕获的异常回滚）。
- 数据库引擎不支持事务（如 MyISAM）。
- 传播属性配置不当（如 `Propagation.NOT_SUPPORTED`）。

### 7. 什么是缓存穿透、缓存击穿、缓存雪崩？
| 问题 | 现象 | 解决方案 |
| :--- | :--- | :--- |
| **缓存穿透** | 查询不存在的数据，缓存和 DB 都 miss，大量请求打到 DB | 布隆过滤器 / 缓存空对象（短过期） |
| **缓存击穿** | 热点 key 过期，大量请求同时打到 DB | 互斥锁（`setnx`） / 逻辑过期 / 永不过期 |
| **缓存雪崩** | 大量 key 同时过期，或 Redis 宕机，导致 DB 压力骤增 | 过期时间添加随机值 / 高可用 Redis（哨兵/集群） |

### 8. 如何实现分布式锁？
| 方案 | 实现方式 | 注意点 |
| :--- | :--- | :--- |
| **Redis 分布式锁** | `SET key value NX EX timeout` + Lua 脚本释放 | 防死锁、防误删（value 用 UUID 校验） |
| **Zookeeper 分布式锁** | 创建临时顺序节点 + 监听前一个节点 | 可靠性高，性能较低 |
| **数据库悲观锁** | `SELECT ... FOR UPDATE` | 性能最差，不推荐 |

---

---

# 以下为扩充章节

---

## 六十四、基础语法补全与命名规范

### 注释

```java
// 单行注释

/*
 * 多行注释
 */

/**
 * Javadoc 文档注释
 * @author 张三
 * @version 1.0
 * @param name 用户名
 * @return 问候语
 */
public String greet(String name) { return "Hello " + name; }
```

Javadoc 常用标签：`@author`、`@version`、`@param`、`@return`、`@throws`、`@see`、`@since`、`@deprecated`。

### 包与导入

```java
package com.example.demo;            // 声明包，必须在第一行（除注释）

import java.util.List;               // 普通导入
import java.util.*;                  // 通配符导入（不推荐）
import static java.lang.Math.PI;     // 静态导入
import static java.lang.Math.*;      // 静态通配符导入
```

### 命名规范

| 元素 | 规范 | 示例 |
|------|------|------|
| 包名 | 全小写，域名倒写 | `com.example.demo` |
| 类名/接口名 | 大驼峰 | `UserService` |
| 方法/变量 | 小驼峰 | `getUserName`、`userName` |
| 常量 | 全大写 + 下划线 | `MAX_SIZE` |
| 抽象类 | `Abstract` 或 `Base` 前缀 | `AbstractService` |
| 异常类 | `Exception` 结尾 | `BusinessException` |
| 测试类 | `Test` 结尾 | `UserServiceTest` |

### 关键字与保留字

- 访问控制：`public`、`protected`、`private`
- 类/接口：`class`、`interface`、`enum`、`extends`、`implements`、`abstract`、`final`
- 包/导入：`package`、`import`
- 数据类型：`byte`、`short`、`int`、`long`、`float`、`double`、`char`、`boolean`、`void`
- 流程控制：`if`、`else`、`switch`、`case`、`default`、`while`、`do`、`for`、`break`、`continue`、`return`
- 异常：`try`、`catch`、`finally`、`throw`、`throws`
- 对象：`new`、`this`、`super`、`instanceof`
- 修饰符：`static`、`synchronized`、`volatile`、`transient`、`native`、`strictfp`
- 保留字：`const`、`goto`（未使用）
- 字面量：`true`、`false`、`null`

### main 方法与命令行参数

```java
public static void main(String[] args) {
    System.out.println("参数个数：" + args.length);
    for (String arg : args) {
        System.out.println(arg);
    }
}
```

### 输入输出

```java
// 输入
Scanner sc = new Scanner(System.in);
int n = sc.nextInt();
double d = sc.nextDouble();
String line = sc.nextLine();
String word = sc.next();     // 读取一个单词

// 输出
System.out.println("Hello");
System.out.printf("姓名：%s，年龄：%d，成绩：%.2f%n", name, age, score);
System.out.print("不换行");
```

| 占位符 | 说明 |
|--------|------|
| `%s` | 字符串 |
| `%d` | 整数 |
| `%f` | 浮点数 |
| `%.2f` | 保留两位小数 |
| `%n` | 换行（跨平台） |
| `%b` | 布尔值 |
| `%c` | 字符 |
| `%x` | 十六进制 |

### 可变参数

```java
public int sum(int... nums) {
    int total = 0;
    for (int n : nums) total += n;
    return total;
}
sum(1, 2, 3);      // 6
sum();             // 0
```

> 可变参数必须是参数列表的最后一项，且一个方法只能有一个。

### Math / Random / BigInteger / BigDecimal

```java
// Math
Math.abs(-5);        // 5
Math.max(1, 2);      // 2
Math.pow(2, 10);     // 1024.0
Math.sqrt(16);       // 4.0
Math.round(3.5);     // 4
Math.floor(3.9);     // 3.0
Math.ceil(3.1);      // 4.0
Math.random();       // [0.0, 1.0)

// Random
Random random = new Random();
random.nextInt(100); // [0, 100)
random.nextBoolean();

// BigInteger（大整数）
BigInteger a = new BigInteger("12345678901234567890");
BigInteger b = new BigInteger("98765432109876543210");
a.add(b);            // 加
a.multiply(b);       // 乘
a.mod(b);            // 取模
a.compareTo(b);      // 比较

// BigDecimal（精确小数）
BigDecimal x = new BigDecimal("0.1");
BigDecimal y = new BigDecimal("0.2");
x.add(y);            // 0.3
x.divide(y, 2, RoundingMode.HALF_UP); // 保留2位，四舍五入
```

> **重要**：`BigDecimal` 必须用字符串构造，不能用 `double`，否则精度丢失。

---

## 六十五、Object 类、内部类、重载与重写

### Object 类方法

| 方法 | 说明 |
|------|------|
| `toString()` | 返回对象的字符串表示，默认是类名 + 哈希码 |
| `equals(Object)` | 判断对象是否相等，默认比较地址 |
| `hashCode()` | 返回哈希码，与 `equals` 必须保持一致 |
| `getClass()` | 返回运行时类对象，不可重写 |
| `clone()` | 浅拷贝，需实现 `Cloneable` |
| `finalize()` | GC 前调用，已废弃（JDK 9 起标记 deprecated） |
| `wait()` / `notify()` / `notifyAll()` | 线程通信，必须在 `synchronized` 中调用 |

### 重载（Overload）vs 重写（Override）

| 特性 | 重载 | 重写 |
|------|------|------|
| 发生位置 | 同一个类 | 子类与父类 |
| 方法名 | 相同 | 相同 |
| 参数列表 | 必须不同 | 必须相同 |
| 返回值 | 可以不同 | 必须相同或协变 |
| 访问权限 | 无限制 | 不能比父类更严格 |
| 绑定时机 | 编译时（静态） | 运行时（动态） |
| 异常 | 无限制 | 不能抛出更宽泛的检查异常 |

### 内部类

```java
public class Outer {
    private int value = 10;

    // 1. 成员内部类
    class Inner {
        void show() { System.out.println(value); }
    }

    // 2. 静态内部类
    static class StaticInner {
        void show() { System.out.println("static"); }
    }

    // 3. 局部内部类
    void method() {
        class Local {
            void show() { System.out.println("local"); }
        }
        new Local().show();
    }

    // 4. 匿名内部类
    Runnable r = new Runnable() {
        @Override
        public void run() { System.out.println("anonymous"); }
    };
}
```

使用：

```java
Outer.Inner inner = new Outer().new Inner();
Outer.StaticInner si = new Outer.StaticInner();
```

> 局部内部类和匿名内部类中访问的局部变量必须是 `effectively final`。

### 接口默认方法冲突

```java
interface A { default void hello() { System.out.println("A"); } }
interface B { default void hello() { System.out.println("B"); } }

class C implements A, B {
    @Override
    public void hello() {
        A.super.hello();  // 显式选择
    }
}
```

### record 类

```java
public record Point(int x, int y) {}

Point p = new Point(1, 2);
p.x();  // 1
p.y();  // 2
```

`record` 自动生成：构造器、`equals()`、`hashCode()`、`toString()`、访问器。**不可变**，不能继承其他类，但可实现接口。

### 密封类

```java
public sealed interface Shape permits Circle, Rectangle {}

final class Circle implements Shape {}
non-sealed class Rectangle implements Shape {}
```

`sealed` 限制继承范围，`permits` 指定允许的子类，子类必须为 `final`、`sealed` 或 `non-sealed`。

---

## 六十六、字符串常量池与正则

### 字符串常量池

```java
String s1 = "hello";              // 常量池
String s2 = "hello";              // 复用常量池
String s3 = new String("hello");  // 堆中新对象
String s4 = s3.intern();          // 手动入池，返回常量池引用

System.out.println(s1 == s2);     // true
System.out.println(s1 == s3);     // false
System.out.println(s1 == s4);     // true
System.out.println(s1.equals(s3));// true
```

### String 不可变原因

- 字符串常量池可安全共享
- `hashCode` 可缓存，作为 `HashMap` key 高效
- 线程安全
- 适合做参数传递，防止意外修改

### 正则表达式

```java
import java.util.regex.*;

// 匹配
boolean matches = "13812345678".matches("1[3-9]\\d{9}");

// 查找
Pattern pattern = Pattern.compile("\\d+");
Matcher matcher = pattern.matcher("abc123def456");
while (matcher.find()) {
    System.out.println(matcher.group()); // 123, 456
}

// 替换
String result = "a1b2c3".replaceAll("\\d", "#"); // a#b#c#

// 分割
String[] parts = "a,b;c".split("[,;]");
```

| 符号 | 含义 |
|------|------|
| `.` | 任意字符（除换行） |
| `\d` | 数字 |
| `\D` | 非数字 |
| `\w` | 字母数字下划线 |
| `\W` | 非 `\w` |
| `\s` | 空白符 |
| `\S` | 非空白符 |
| `^` / `$` | 行首 / 行尾 |
| `*` / `+` / `?` | 0+ / 1+ / 0或1 |
| `{n}` / `{n,}` / `{n,m}` | 恰好 n 次 / 至少 n 次 / n 到 m 次 |

---

## 六十七、集合补充：Iterator、Comparator、Deque、BlockingQueue

### Iterator 与 fail-fast

```java
List<String> list = new ArrayList<>(List.of("a", "b", "c"));
Iterator<String> it = list.iterator();
while (it.hasNext()) {
    String s = it.next();
    if ("b".equals(s)) {
        it.remove();  // 正确：使用 Iterator.remove()
    }
}
```

- `fail-fast`：`ArrayList`、`HashMap` 等，遍历中结构改变会抛 `ConcurrentModificationException`。
- `fail-safe`：`CopyOnWriteArrayList`、`ConcurrentHashMap`，遍历时修改不会抛异常（弱一致性）。

### Comparable vs Comparator

```java
// Comparable：内部自然排序
class Person implements Comparable<Person> {
    int age;
    @Override
    public int compareTo(Person o) {
        return Integer.compare(this.age, o.age);
    }
}

// Comparator：外部定制排序
list.sort(Comparator.comparing(Person::getName).thenComparing(Person::getAge));
list.sort(Comparator.comparingInt(Person::getAge).reversed());
```

### Deque / ArrayDeque

```java
Deque<String> deque = new ArrayDeque<>();
deque.addFirst("a");
deque.addLast("b");
deque.peekFirst();  // a
deque.pollLast();   // b
```

常用作栈或队列：

```java
Deque<Integer> stack = new ArrayDeque<>();
stack.push(1); stack.push(2);
stack.pop();  // 2
```

### BlockingQueue

| 实现 | 特点 |
|------|------|
| `ArrayBlockingQueue` | 有界数组队列 |
| `LinkedBlockingQueue` | 可选有界链表队列 |
| `SynchronousQueue` | 不存储元素，直接交接 |
| `PriorityBlockingQueue` | 优先级队列 |
| `DelayQueue` | 延迟队列 |

```java
BlockingQueue<String> queue = new LinkedBlockingQueue<>(10);
queue.put("item");   // 阻塞入队
String item = queue.take(); // 阻塞出队
```

### 其他集合

| 集合 | 用途 |
|------|------|
| `EnumMap` | key 为枚举，性能高 |
| `EnumSet` | 枚举集合，位向量实现 |
| `WeakHashMap` | key 弱引用，适合缓存 |
| `IdentityHashMap` | 用 `==` 比较 key |
| `TreeMap` | 按键排序，红黑树 |

---

## 六十八、并发进阶：JMM、AQS、Condition、虚拟线程

### Java 内存模型（JMM）

- 每个线程有自己的**工作内存**，共享变量存储在主内存。
- 线程间通信必须通过主内存。
- **happens-before** 规则：
  - 程序顺序规则
  - 监视器锁规则（unlock 先于后续 lock）
  - volatile 写先于后续读
  - 传递性
  - 线程启动/终止规则

### 内存屏障

| 屏障 | 作用 |
|------|------|
| LoadLoad | 禁止读-读重排 |
| StoreStore | 禁止写-写重排 |
| LoadStore | 禁止读-写重排 |
| StoreLoad | 禁止写-读重排（最昂贵） |

### AQS（AbstractQueuedSynchronizer）

- `ReentrantLock`、`CountDownLatch`、`Semaphore`、`ReentrantReadWriteLock` 都基于 AQS。
- 核心：一个 `volatile int state` + CLH 双向队列。
- 独占模式：`tryAcquire` / `tryRelease`
- 共享模式：`tryAcquireShared` / `tryReleaseShared`

### Condition

```java
ReentrantLock lock = new ReentrantLock();
Condition notFull = lock.newCondition();
Condition notEmpty = lock.newCondition();

lock.lock();
try {
    while (queue.size() == CAP) notFull.await();
    queue.add(item);
    notEmpty.signal();
} finally {
    lock.unlock();
}
```

### StampedLock

```java
StampedLock lock = new StampedLock();
long stamp = lock.writeLock();
try { /* 写 */ } finally { lock.unlockWrite(stamp); }

long stamp2 = lock.tryOptimisticRead();
// 读数据
if (!lock.validate(stamp2)) {
    // 升级为悲观读
    stamp2 = lock.readLock();
    try { /* 读 */ } finally { lock.unlockRead(stamp2); }
}
```

### LongAdder

高并发计数场景，比 `AtomicLong` 性能更好（分段累加）。

```java
LongAdder adder = new LongAdder();
adder.increment();
adder.sum();
```

### 虚拟线程（Java 21 正式）

```java
// 创建虚拟线程
Thread.ofVirtual().start(() -> System.out.println("virtual"));

// 使用 Executors
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    executor.submit(() -> System.out.println("task"));
}
```

- 由 JVM 调度，不绑定 OS 线程。
- 适合 I/O 密集型任务，不适合 CPU 密集型。
- 不要池化虚拟线程。

### 死锁排查

```bash
jstack <pid> > stack.log
# 搜索 "Found one Java-level deadlock"
```

死锁四个必要条件：互斥、请求与保持、不可剥夺、循环等待。

---

## 六十九、JVM 进阶：对象创建、GC、JIT、类加载器

### 对象创建过程

1. 类加载检查
2. 分配内存（指针碰撞 / 空闲列表）
3. 初始化零值
4. 设置对象头（Mark Word、类型指针）
5. 执行 `<init>` 构造器

### TLAB

Thread Local Allocation Buffer，每个线程在 Eden 中预分配一小块内存，避免分配时加锁。

### 逃逸分析

- **方法逃逸**：对象被外部方法引用
- **线程逃逸**：对象被其他线程引用
- 未逃逸的对象可进行：
  - **栈上分配**
  - **锁消除**
  - **标量替换**

### 引用类型

| 类型 | 回收时机 | 用途 |
|------|----------|------|
| 强引用 | 永不（除非不可达） | 普通对象 |
| 软引用 `SoftReference` | 内存不足时 | 缓存 |
| 弱引用 `WeakReference` | 下次 GC | `WeakHashMap` |
| 虚引用 `PhantomReference` | 随时 | 对象回收跟踪 |

### GC 收集器对比

| 收集器 | 区域 | 算法 | 特点 |
|--------|------|------|------|
| Serial | 新生代 | 复制 | 单线程 |
| ParNew | 新生代 | 复制 | 多线程 |
| Parallel Scavenge | 新生代 | 复制 | 吞吐量优先 |
| Serial Old | 老年代 | 标记-整理 | 单线程 |
| Parallel Old | 老年代 | 标记-整理 | 吞吐量优先 |
| CMS | 老年代 | 标记-清除 | 低停顿，已废弃 |
| G1 | 整堆 | 分区 | JDK 9+ 默认 |
| ZGC | 整堆 | 染色指针 | 超低停顿（<1ms） |
| Shenandoah | 整堆 | 并发整理 | 低停顿 |

### JIT 编译

- 解释器 + 即时编译器（C1、C2）
- 热点代码探测：方法调用计数器、回边计数器
- 编译优化：内联、逃逸分析、循环展开、公共子表达式消除

### 字节码与 javap

```bash
javap -c -v MyClass.class   # 查看字节码
```

### 类加载器修正

> JDK 9 后：
> - Bootstrap 加载 `java.base` 等核心模块，不再加载 `rt.jar`
> - Extension ClassLoader 被 Platform ClassLoader 取代
> - `lib/ext` 机制已移除
> - 新增模块化系统（JPMS）

---

## 七十、JUnit 5 / Mockito / 日志

### JUnit 5

```java
import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;

class CalculatorTest {

    @BeforeEach
    void setUp() { /* 每个测试前 */ }

    @AfterEach
    void tearDown() { /* 每个测试后 */ }

    @Test
    @DisplayName("加法测试")
    void testAdd() {
        assertEquals(5, new Calculator().add(2, 3));
    }

    @Test
    void testException() {
        assertThrows(ArithmeticException.class, () -> 1 / 0);
    }

    @ParameterizedTest
    @ValueSource(ints = {1, 2, 3})
    void testPositive(int n) {
        assertTrue(n > 0);
    }
}
```

### Mockito

```java
// Mock 对象
UserRepository repo = mock(UserRepository.class);
when(repo.findById(1L)).thenReturn(new User("张三"));
verify(repo).findById(1L);

// Spy（部分真实调用）
List<String> list = spy(new ArrayList<>());
doReturn(100).when(list).size();
```

### SLF4J + Logback

```java
private static final Logger log = LoggerFactory.getLogger(MyService.class);

log.debug("调试信息: {}", value);
log.info("用户 {} 登录", username);
log.warn("警告");
log.error("异常", e);
```

**logback.xml 示例**：

```xml
<configuration>
    <appender name="STDOUT" class="ch.qos.logback.core.ConsoleAppender">
        <encoder>
            <pattern>%d{HH:mm:ss} [%thread] %-5level %logger{36} - %msg%n</pattern>
        </encoder>
    </appender>
    <root level="INFO">
        <appender-ref ref="STDOUT"/>
    </root>
</configuration>
```

### MDC（Mapped Diagnostic Context）

```java
MDC.put("traceId", UUID.randomUUID().toString());
try {
    log.info("请求处理");
} finally {
    MDC.clear();
}
```

---

## 七十一、Maven / Gradle / CI-CD

### Maven 生命周期

| 阶段 | 说明 |
|------|------|
| `validate` | 验证项目 |
| `compile` | 编译 |
| `test` | 测试 |
| `package` | 打包 |
| `verify` | 验证 |
| `install` | 安装到本地仓库 |
| `deploy` | 部署到远程仓库 |

### 依赖范围

| scope | 说明 |
|-------|------|
| `compile` | 默认，编译+运行+测试 |
| `provided` | 编译+测试，运行时不提供（如 servlet-api） |
| `runtime` | 运行+测试，编译不需要（如 JDBC 驱动） |
| `test` | 仅测试 |
| `system` | 本地系统路径（不推荐） |

### 依赖冲突

```bash
mvn dependency:tree           # 查看依赖树
mvn dependency:tree -Dverbose # 显示冲突
```

解决方式：
- **最短路径优先**
- **先声明优先**
- 使用 `<exclusions>` 排除
- 使用 `<dependencyManagement>` 统一版本

### Gradle 基础

```groovy
plugins {
    id 'java'
    id 'org.springframework.boot' version '3.2.0'
}

repositories { mavenCentral() }

dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-web'
    testImplementation 'org.junit.jupiter:junit-jupiter'
}

tasks.withType(JavaCompile) {
    options.encoding = 'UTF-8'
}
```

### CI/CD

```yaml
# GitHub Actions 示例
name: Build
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-java@v3
        with:
          java-version: '17'
      - run: mvn clean package
```

常用工具：Jenkins、GitLab CI、SonarQube、Checkstyle、SpotBugs。

---

## 七十二、Spring 进阶：Bean 生命周期、循环依赖、事务传播

### Bean 生命周期

1. 实例化（构造器）
2. 属性注入（`@Autowired`）
3. `BeanNameAware` / `BeanFactoryAware` / `ApplicationContextAware`
4. `BeanPostProcessor.postProcessBeforeInitialization`
5. `@PostConstruct` / `InitializingBean.afterPropertiesSet` / `init-method`
6. `BeanPostProcessor.postProcessAfterInitialization`（AOP 代理在此生成）
7. 使用
8. `@PreDestroy` / `DisposableBean.destroy` / `destroy-method`

### 循环依赖与三级缓存

| 缓存 | 名称 | 内容 |
|------|------|------|
| 一级 | `singletonObjects` | 完整 Bean |
| 二级 | `earlySingletonObjects` | 早期 Bean（未填充属性） |
| 三级 | `singletonFactories` | Bean 工厂（用于生成代理） |

- **只能解决单例 + 属性注入的循环依赖**。
- 构造器注入的循环依赖无法解决（会抛 `BeanCurrentlyInCreationException`）。

### 事务传播行为

| 传播行为 | 说明 |
|----------|------|
| `REQUIRED` | 默认，有则加入，无则新建 |
| `REQUIRES_NEW` | 总是新建，挂起当前 |
| `NESTED` | 嵌套事务（保存点） |
| `SUPPORTS` | 有则加入，无则以非事务运行 |
| `NOT_SUPPORTED` | 以非事务运行，挂起当前 |
| `MANDATORY` | 必须有事务，否则抛异常 |
| `NEVER` | 必须无事务，否则抛异常 |

### 事务隔离级别

| 级别 | 脏读 | 不可重复读 | 幻读 |
|------|------|------------|------|
| READ_UNCOMMITTED | 可能 | 可能 | 可能 |
| READ_COMMITTED | 否 | 可能 | 可能 |
| REPEATABLE_READ | 否 | 否 | 可能 |
| SERIALIZABLE | 否 | 否 | 否 |

### Spring MVC 执行流程

1. 请求 → `DispatcherServlet`
2. `HandlerMapping` 找到 Handler
3. `HandlerAdapter` 调用 Handler
4. 返回 `ModelAndView`
5. `ViewResolver` 解析视图
6. 渲染视图并返回

### 过滤器 vs 拦截器 vs AOP

| 特性 | Filter | Interceptor | AOP |
|------|--------|-------------|-----|
| 规范 | Servlet | Spring MVC | Spring |
| 作用范围 | 所有请求 | Controller 请求 | 方法级别 |
| 能否获取 Bean | 否 | 是 | 是 |
| 典型用途 | 编码、跨域 | 登录校验 | 日志、事务 |

### Spring Boot 3 变化

- `javax.*` → `jakarta.*`（Servlet、Persistence、Validation）
- 自动配置注册文件：`META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`
- 最低要求 Java 17
- 支持 GraalVM Native Image

---

## 七十三、MySQL / Redis / MQ

### MySQL 索引

- **B+ 树**：所有数据在叶子节点，叶子节点用链表连接，适合范围查询。
- **聚簇索引**：主键索引，叶子节点存整行数据。
- **二级索引**：叶子节点存主键值，需**回表**。
- **覆盖索引**：查询字段全在索引中，无需回表。
- **最左前缀原则**：联合索引 `(a, b, c)`，查询条件必须从 `a` 开始。
- **索引失效**：`LIKE '%x'`、函数操作、类型隐式转换、`OR` 连接非索引列。

```sql
EXPLAIN SELECT * FROM users WHERE name = '张三';
```

关键字段：`type`（访问类型）、`key`（使用的索引）、`rows`（扫描行数）、`Extra`（额外信息）。

### 事务与 MVCC

- **ACID**：原子性、一致性、隔离性、持久性。
- **MVCC**：多版本并发控制，通过 `undo log` + `ReadView` 实现读不加锁。
- **快照读** vs **当前读**：`SELECT` 是快照读，`SELECT ... FOR UPDATE` 是当前读。

### Redis 数据结构

| 类型 | 用途 |
|------|------|
| String | 缓存、计数器 |
| Hash | 对象存储 |
| List | 消息队列、时间线 |
| Set | 去重、共同好友 |
| ZSet | 排行榜、延时队列 |
| Bitmap | 签到、布隆过滤器 |
| HyperLogLog | UV 统计 |
| Geo | 地理位置 |
| Stream | 消息队列 |

### Redis 持久化

- **RDB**：快照，恢复快，可能丢数据。
- **AOF**：追加日志，数据安全，文件大，恢复慢。
- **混合持久化**：RDB + AOF（Redis 4.0+）。

### Redis 高可用

- **主从复制**：读写分离。
- **哨兵（Sentinel）**：自动故障转移。
- **集群（Cluster）**：分片存储，16384 个槽。

### MQ 核心问题

| 问题 | 解决方案 |
|------|----------|
| 消息丢失 | 生产者确认、持久化、消费者手动 ACK |
| 消息重复 | 幂等消费（唯一 ID + 去重表） |
| 消息顺序 | 单分区/单队列，或按业务 key 分区 |
| 消息积压 | 增加消费者、扩容分区 |
| 事务消息 | RocketMQ 事务消息、本地消息表 |

---

## 七十四、分布式与微服务进阶

### 分布式 ID

| 方案 | 特点 |
|------|------|
| UUID | 本地生成，无序，不适合做 DB 主键 |
| 数据库自增 | 简单，但性能瓶颈 |
| Redis INCR | 高性能，需持久化 |
| 雪花算法（Snowflake） | 64 位：时间戳 + 机器 ID + 序列号 |
| 美团 Leaf | 号段模式 + Snowflake |

### 限流算法

| 算法 | 特点 |
|------|------|
| 计数器 | 简单，有临界问题 |
| 滑动窗口 | 平滑，需存储 |
| 漏桶 | 恒定速率，不允许突发 |
| 令牌桶 | 允许突发，常用 |

### 熔断、降级、限流

- **熔断**：失败率达到阈值，直接拒绝请求（Sentinel、Resilience4j）。
- **降级**：返回兜底数据或默认值。
- **限流**：控制 QPS。

### 分布式事务

| 方案 | 说明 |
|------|------|
| 2PC / 3PC | 强一致，性能差 |
| TCC | Try-Confirm-Cancel，补偿型 |
| Saga | 长事务拆分为多个本地事务 |
| 本地消息表 | 最终一致 |
| 事务消息 | RocketMQ |
| Seata | 阿里开源，AT/TCC/Saga 模式 |

### 链路追踪

- **Sleuth + Zipkin**：Spring Cloud 生态。
- **SkyWalking**：国产，功能强大。
- **Jaeger**：CNCF 项目。

---

## 七十五、安全：JWT、OAuth2、SQL 注入、XSS

### JWT（JSON Web Token）

结构：`Header.Payload.Signature`

```java
// 生成
String token = Jwts.builder()
        .setSubject("user123")
        .setExpiration(new Date(System.currentTimeMillis() + 3600_000))
        .signWith(SignatureAlgorithm.HS256, secret)
        .compact();

// 解析
Claims claims = Jwts.parser()
        .setSigningKey(secret)
        .parseClaimsJws(token)
        .getBody();
```

> JWT 只做签名，不做加密，敏感信息不要放 Payload。

### OAuth2 四种模式

| 模式 | 适用场景 |
|------|----------|
| 授权码 | Web 应用（最安全） |
| 简化 | 纯前端应用 |
| 密码 | 信任的客户端 |
| 客户端凭证 | 服务间调用 |

### SQL 注入

```java
// ❌ 危险：字符串拼接
String sql = "SELECT * FROM users WHERE name = '" + name + "'";

// ✅ 安全：PreparedStatement
String sql = "SELECT * FROM users WHERE name = ?";
pstmt.setString(1, name);
```

### XSS / CSRF

- **XSS**：输出转义、CSP、HttpOnly Cookie。
- **CSRF**：CSRF Token、SameSite Cookie、验证 Referer。

### 密码存储

- 使用 **BCrypt** 或 **Argon2**，不要用 MD5/SHA1。
- 每个用户独立 salt。

```java
String hash = BCrypt.hashpw(password, BCrypt.gensalt());
boolean ok = BCrypt.checkpw(password, hash);
```

---

## 七十六、算法与数据结构

### 常见数据结构

| 结构 | 特点 | Java 实现 |
|------|------|-----------|
| 数组 | 随机访问 O(1) | `int[]` |
| 链表 | 增删 O(1) | `LinkedList` |
| 栈 | LIFO | `ArrayDeque` |
| 队列 | FIFO | `ArrayDeque` |
| 哈希表 | 平均 O(1) | `HashMap` |
| 二叉树 | 查找 O(log n) | `TreeMap` |
| 堆 | 最值 O(1) | `PriorityQueue` |
| 图 | 关系建模 | 邻接矩阵/表 |

### 排序算法

| 算法 | 平均 | 最坏 | 稳定 | 空间 |
|------|------|------|------|------|
| 冒泡 | O(n²) | O(n²) | ✅ | O(1) |
| 选择 | O(n²) | O(n²) | ❌ | O(1) |
| 插入 | O(n²) | O(n²) | ✅ | O(1) |
| 归并 | O(n log n) | O(n log n) | ✅ | O(n) |
| 快排 | O(n log n) | O(n²) | ❌ | O(log n) |
| 堆排 | O(n log n) | O(n log n) | ❌ | O(1) |

### 常见算法思想

- **双指针**：数组、链表问题
- **滑动窗口**：子串、子数组
- **二分查找**：有序数组
- **DFS / BFS**：树、图遍历
- **动态规划**：最优子结构 + 重叠子问题
- **贪心**：局部最优
- **回溯**：全排列、N 皇后
- **分治**：归并排序、快排

### 常用刷题模板

```java
// 二分查找
int left = 0, right = n - 1;
while (left <= right) {
    int mid = left + (right - left) / 2;
    if (arr[mid] == target) return mid;
    else if (arr[mid] < target) left = mid + 1;
    else right = mid - 1;
}

// 滑动窗口
int left = 0;
for (int right = 0; right < n; right++) {
    // 扩大窗口
    while (条件) {
        // 缩小窗口
        left++;
    }
}
```

---

## 七十七、Docker / K8s / Arthas / Linux 排查

### Docker 进阶

```dockerfile
# 多阶段构建
FROM maven:3.9-eclipse-temurin-17 AS build
WORKDIR /app
COPY pom.xml .
RUN mvn dependency:go-offline
COPY src ./src
RUN mvn package -DskipTests

FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=build /app/target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8080:8080"
    depends_on:
      - mysql
      - redis
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root
  redis:
    image: redis:7
```

### K8s 核心概念

| 对象 | 说明 |
|------|------|
| Pod | 最小调度单位 |
| Deployment | 管理 Pod 副本 |
| Service | 服务发现与负载均衡 |
| Ingress | 外部访问入口 |
| ConfigMap | 配置 |
| Secret | 敏感信息 |
| Namespace | 逻辑隔离 |

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
        - name: app
          image: my-app:1.0
          ports:
            - containerPort: 8080
```

### JVM 容器内存

```bash
-XX:MaxRAMPercentage=75.0   # 使用容器内存的 75%
-XX:InitialRAMPercentage=50.0
```

### Arthas 常用命令

```bash
# 启动
java -jar arthas-boot.jar

# 常用命令
dashboard              # 仪表盘
thread                 # 线程信息
thread -n 3            # CPU 最高的 3 个线程
jad com.example.Foo    # 反编译
watch com.example.Foo method '{params, returnObj}' # 方法监控
trace com.example.Foo method   # 方法调用链路
stack com.example.Foo method   # 调用栈
ognl '@java.lang.System@out.println("hi")' # 执行 OGNL
```

### Linux 排查

```bash
# 找出 CPU 高的线程
top -H -p <pid>
printf "%x\n" <tid>      # 线程 ID 转十六进制
jstack <pid> | grep -A 30 <hex_tid>

# 内存
jmap -histo <pid> | head -20
jmap -dump:live,format=b,file=heap.bin <pid>

# 磁盘 IO
iostat -x 1
iotop

# 网络
ss -tunlp
tcpdump -i eth0 port 8080
```

---

## 七十八、Java 9–21 新特性详细表

| 版本 | 特性 | 正式/预览 |
|------|------|-----------|
| 9 | 模块系统 JPMS、`jshell`、集合工厂方法 `List.of()` | 正式 |
| 10 | `var` 局部变量类型推断 | 正式 |
| 11 | `String.isBlank()`、`Files.readString()`、HttpClient | 正式 |
| 12 | Switch 表达式（预览）、`teeing` 收集器 | 预览 |
| 13 | 文本块（预览） | 预览 |
| 14 | Switch 表达式（正式）、`record`（预览）、`instanceof` 模式匹配（预览） | 混合 |
| 15 | 文本块（正式）、隐藏类、ZGC 正式 | 正式 |
| 16 | `record`（正式）、`instanceof` 模式匹配（正式）、`Stream.toList()` | 正式 |
| 17 | 密封类（正式）、移除 SecurityManager（废弃） | 正式 |
| 18 | UTF-8 默认字符集、简单 Web 服务器 | 正式 |
| 19 | 虚拟线程（预览）、结构化并发（孵化） | 预览 |
| 20 | 作用域值（孵化）、Record 模式（预览） | 预览 |
| 21 | 虚拟线程（正式）、Record 模式（正式）、分代 ZGC、模式匹配 Switch（正式）、结构化并发（预览） | 混合 |

### 常用新特性示例

```java
// var（Java 10）
var list = new ArrayList<String>();

// 文本块（Java 15）
String json = """
        {
          "name": "张三",
          "age": 18
        }
        """;

// record（Java 16）
public record User(String name, int age) {}

// instanceof 模式匹配（Java 16）
if (obj instanceof String s) {
    System.out.println(s.length());
}

// Switch 表达式（Java 14）
String result = switch (day) {
    case MONDAY, FRIDAY -> "工作日";
    case SATURDAY, SUNDAY -> "周末";
    default -> "其他";
};

// 密封类（Java 17）
public sealed interface Shape permits Circle, Rectangle {}

// 虚拟线程（Java 21）
Thread.ofVirtual().start(() -> System.out.println("hello"));

// Record 模式（Java 21）
if (obj instanceof Point(int x, int y)) {
    System.out.println(x + y);
}

// 模式匹配 Switch（Java 21）
String desc = switch (obj) {
    case Integer i -> "整数: " + i;
    case String s -> "字符串: " + s;
    default -> "未知";
};
```

---

## 总结：原稿修正清单

| 序号 | 原稿内容 | 修正 |
|------|----------|------|
| 1 | `var` 列为 Java 11 | `var` 是 Java 10 引入 |
| 2 | 结构化并发列为 Java 21 正式 | Java 21 仍为预览 |
| 3 | Spring Boot 自动配置用 `spring.factories` | Spring Boot 3 已改为 `AutoConfiguration.imports` |
| 4 | 类加载器有 Extension ClassLoader | JDK 9+ 改为 Platform ClassLoader |
| 5 | `-XX:MetaspaceSize` 称为"初始大小" | 应为"初始高水位" |
| 6 | GC 日志用 `-XX:+PrintGCDetails` | JDK 9+ 推荐 `-Xlog:gc*` |
| 7 | `openjdk:17-jdk-slim` | 推荐 `eclipse-temurin:17-jdk` |
| 8 | `@Resource` 只说按名称注入 | 默认按名称，找不到再按类型 |
| 9 | 偏向锁作为默认优化 | JDK 15 起禁用，后续移除 |
| 10 | G1 下建议设 `-Xmn` | G1 会自动管理新生代，不建议随意设 |
| 11 | `BigDecimal` 未强调构造方式 | 必须用字符串构造，避免精度丢失 |

---

> 本手册已覆盖 Java 从基础语法到分布式微服务的完整知识体系，可作为日常开发速查与面试复习的参考。