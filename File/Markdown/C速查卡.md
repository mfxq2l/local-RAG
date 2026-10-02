# C 语言完整速查卡（扩充版）

---

## 一、Hello World 与环境搭建

### 最小完整程序

```c
#include <stdio.h>

int main(void) {
    printf("Hello World\n");
    return 0;
}
```

### 编译与运行

```bash
gcc hello.c -o hello
./hello

gcc -Wall -Wextra hello.c -o hello
gcc -g hello.c -o hello
gcc -O2 hello.c -o hello
```

### 多文件编译

```bash
gcc main.c add.c -o program
gcc -c main.c
gcc main.o add.o -o program
```

---

## 二、基本数据类型

### 整数类型

| 类型 | 大小 | 范围 | 标准保证的最小大小 |
|------|------|------|-------------------|
| `char` | 1 字节 | -128 ~ 127 或 0 ~ 255 | 至少 8 位 |
| `unsigned char` | 1 字节 | 0 ~ 255 | 至少 8 位 |
| `short` | 2 字节 | -32,768 ~ 32,767 | 至少 16 位 |
| `int` | 4 字节 | -2,147,483,648 ~ 2,147,483,647 | 至少 16 位（通常 32 位） |
| `unsigned int` | 4 字节 | 0 ~ 4,294,967,295 | — |
| `long` | 8 字节（64位） | 范围很大 | 至少 32 位 |
| `long long` | 8 字节 | 范围更大 | 至少 64 位（C99+） |

> **注意**：C 标准只规定了各类型的最小位数，实际大小取决于平台。使用 `<limits.h>` 中的 `INT_MAX` 等宏获取实际值。

### 定长整数类型（`<stdint.h>`，C99+）

```c
int8_t, uint8_t, int16_t, uint16_t, int32_t, uint32_t, int64_t, uint64_t
intptr_t, uintptr_t   // 可容纳指针的整数类型
intmax_t, uintmax_t   // 最大宽度整数
```

> 需要精确宽度时优先使用定长类型，而非 `int`/`long`。

### 浮点类型

| 类型 | 大小 | 精度 |
|------|------|------|
| `float` | 4 字节 | 约 6-7 位小数 |
| `double` | 8 字节 | 约 15-16 位小数（推荐） |
| `long double` | 16 字节 | 精度更高 |

### `void` 与 `_Bool`

```c
void          // 无类型
_Bool         // 布尔类型（C99+），需 #include <stdbool.h> 使用 bool/true/false
size_t        // sizeof 返回值类型，无符号
```

---

## 三、变量与常量

### 变量声明与初始化

```c
int a;                // 未初始化（垃圾值）
int b = 10;           // 初始化
int c = 10, d = 20;   // 同时声明
const int e = 100;    // 常量
static int f = 0;     // 静态变量
extern int g;         // 外部变量声明
```

### 变量的作用域与存储期

```c
int global_var = 100;        // 全局变量，静态存储期
static int file_static = 50; // 文件作用域静态变量

void func(void) {
    int local = 10;          // 自动存储期
    static int count = 0;    // 静态存储期，只初始化一次
    count++;
}
```

### 字面量常量

```c
10              // 十进制
0x0F            // 十六进制（15）
0755            // 八进制（493）
0b1010          // 二进制（C23 正式）
10L / 10LL      // long / long long
10U             // unsigned
3.14            // double
3.14f           // float
1'000'000       // 数字分隔符（C23 正式）
'a'             // 字符常量
"hello"         // 字符串常量
u8"hello"       // UTF-8 字符串字面量（C11，C23 类型改为 char8_t[]）
'\n', '\t', '\\', '\'', '\"', '\0'
'\x41'          // 十六进制转义（'A'）
```

---

## 四、输入输出

### `printf` 格式占位符

```c
printf("整数: %d\n", 100);
printf("浮点: %f\n", 3.14);
printf("字符: %c\n", 'A');
printf("字符串: %s\n", "hello");
printf("指针: %p\n", (void*)&a);
printf("无符号: %u\n", 100U);
printf("十六进制: %x / %X\n", 255, 255);
printf("八进制: %o\n", 255);
printf("科学计数: %e\n", 3.14);
printf("百分比: %%\n");
printf("size_t: %zu\n", sizeof(int));
printf("int64_t: %" PRId64 "\n", (int64_t)100);  // <inttypes.h>
```

### 格式控制

```c
printf("%5d\n", 12);      // 右对齐宽度5
printf("%-5d\n", 12);     // 左对齐宽度5
printf("%05d\n", 12);     // 补零
printf("%.2f\n", 3.14159); // 2位小数
printf("%10.2f\n", 3.14); // 宽度10，2位小数
```

### `scanf` 输入

```c
int num;
scanf("%d", &num);

char str[100];
scanf("%99s", str);        // 安全：限制长度

char c;
scanf(" %c", &c);          // 空格跳过空白
```

### 字符与字符串输入输出

```c
int ch = getchar();
putchar(ch);

char line[100];
fgets(line, sizeof(line), stdin);  // 安全读取一行
fputs(line, stdout);
```

### 文件输入输出

```c
FILE *fp = fopen("data.txt", "r");
if (fp == NULL) {
    perror("打开文件失败");
    return 1;
}
fprintf(fp, "写入: %d\n", 100);
fscanf(fp, "%d", &num);
fclose(fp);
```

---

## 五、运算符

### 算术运算符

```c
+ - * / % ++ --
```

> 整数除法截断小数；`%` 只能用于整数；`/` 或 `%` 的右操作数为零是未定义行为（见第二十三章）。

### 赋值运算符

```c
= += -= *= /= %= &= |= ^= <<= >>=
```

### 比较运算符

```c
== != > < >= <=
```

### 逻辑运算符

```c
&& || !    // && 和 || 短路求值
```

### 位运算符

```c
& | ^ ~ << >>
```

### 其他运算符

```c
sizeof  &  *  ?:  ,  ()  []  .  ->  (type)
```

### 运算符优先级

| 优先级 | 运算符 | 结合性 |
|--------|--------|--------|
| 1 | `() [] -> .` | 左 |
| 2 | `! ~ ++ -- + - * & (type) sizeof` | 右 |
| 3 | `* / %` | 左 |
| 4 | `+ -` | 左 |
| 5 | `<< >>` | 左 |
| 6 | `< <= > >=` | 左 |
| 7 | `== !=` | 左 |
| 8 | `&` | 左 |
| 9 | `^` | 左 |
| 10 | `\|` | 左 |
| 11 | `&&` | 左 |
| 12 | `\|\|` | 左 |
| 13 | `?:` | 右 |
| 14 | `= += -=` 等 | 右 |
| 15 | `,` | 左 |

---

## 六、控制流

### `if` / `if-else` / `else if`

```c
if (cond1) { ... }
else if (cond2) { ... }
else { ... }
```

### `switch`

```c
switch (expr) {          // expr 必须是整数类型
    case 1: ...; break;
    case 2:
    case 3: ...; break;  // 共用代码
    default: ...; break;
}
```

### 循环

```c
while (cond) { ... }
do { ... } while (cond);   // 至少执行一次
for (init; cond; update) { ... }
```

### `break` / `continue` / `goto`

```c
break;      // 跳出循环或 switch
continue;   // 跳过本次剩余代码
goto label; // 谨慎使用
label: ...
```

> C23 允许 `case` 和 `default` 标签后跟声明，且 `case` 前也可有语句。

---

## 七、数组

### 一维数组

```c
int arr[5];
int arr[5] = {1, 2, 3, 4, 5};
int arr[] = {1, 2, 3};          // 自动推断大小
int arr[5] = {1, 2};            // 后 3 个补 0
```

### 二维数组

```c
int matrix[3][4];
int matrix[3][4] = {{1,2,3,4},{5,6,7,8},{9,10,11,12}};
```

### 变长数组（VLA，C99）

```c
int n = 10;
int arr[n];   // 大小运行时确定
```

> VLA 在 C11 中变为可选特性，C23 中仍为可选。

### 数组大小计算

```c
int arr[] = {1,2,3,4,5};
int size = sizeof(arr) / sizeof(arr[0]);
```

### 字符数组与字符串

```c
char str[10] = "hello";           // 含 '\0'
char str[] = "hello";             // 自动推断为 6
char str[] = {'h','e','l','l','o','\0'};
```

### 字符串操作（`<string.h>`）

```c
strcpy, strncpy, strcat, strncat, strlen, strcmp, strncmp,
strchr, strstr, memcpy, memmove, memset, memcmp
```

---

## 八、指针

### 指针基础

```c
int a = 10;
int *p = &a;
printf("%p\n", (void*)p);
printf("%d\n", *p);
*p = 20;
```

### NULL 指针

```c
int *p = NULL;
if (p == NULL) { ... }
```

### 指针与数组

```c
int arr[5] = {1,2,3,4,5};
int *p = arr;          // 等价于 &arr[0]
p + 1;                 // 指向下一个元素
p[2];                  // 等价于 *(p+2)
```

### 指针数组 vs 数组指针

```c
int *arr[10];      // 指针数组：10 个 int*
int (*arr)[10];    // 数组指针：指向含 10 个 int 的数组
```

### `const` 与指针

```c
const int *p;        // 指向常量的指针：不能修改 *p
int *const p;        // 常量指针：不能修改 p 的指向
const int *const p;  // 都不能改
```

### 多级指针

```c
int a = 10;
int *p = &a;
int **pp = &p;
**pp = 20;
```

### 野指针

```c
int *p;      // 未初始化
*p = 10;     // 未定义行为
```

---

## 九、函数

### 函数定义与声明

```c
int add(int a, int b) { return a + b; }
int add(int a, int b);   // 原型声明
```

### 参数传递

```c
void swap(int *x, int *y) {  // 指针传递才能修改实参
    int t = *x; *x = *y; *y = t;
}
```

### 数组作为参数

```c
void print(int arr[], int size) { ... }
void print(int *arr, int size) { ... }   // 等价
```

### 函数指针

```c
int (*func_ptr)(int, int) = add;
int result = func_ptr(3, 5);
```

### 可变参数

```c
#include <stdarg.h>
int sum(int count, ...) {
    va_list args;
    va_start(args, count);
    int total = 0;
    for (int i = 0; i < count; i++) total += va_arg(args, int);
    va_end(args);
    return total;
}
```

### `_Noreturn`（C11，C23 弃用）

```c
_Noreturn void fatal(const char *msg) {
    fprintf(stderr, "%s\n", msg);
    exit(1);
}
```

> C23 中 `_Noreturn` 被弃用，推荐使用 `[[noreturn]]` 属性。

---

## 十、动态内存管理

```c
#include <stdlib.h>

int *p = malloc(10 * sizeof(int));    // 不初始化
int *q = calloc(10, sizeof(int));     // 初始化为 0
p = realloc(p, 20 * sizeof(int));     // 调整大小
free(p);
p = NULL;
```

### 常见错误

- 忘记释放 → 内存泄漏
- 使用已释放内存 → 悬空指针
- 重复释放 → double free
- 越界访问 → 未定义行为

### 检测工具

```bash
valgrind --leak-check=full ./program
```

---

## 十一、结构体、联合体、枚举

### 结构体

```c
struct Person {
    char name[50];
    int age;
};

struct Person p = {"小明", 18};
struct Person *ptr = &p;
ptr->age = 20;
```

### `typedef`

```c
typedef struct Person Person;
typedef struct { char name[50]; int age; } Student;
```

### 结构体内存对齐

```c
struct Person {
    char name[50];
    int age;          // 可能插入填充字节
};
printf("%zu\n", sizeof(struct Person));
```

> 结构体大小是最大对齐成员对齐值的整数倍（见第二十三章内存对齐）。

### 联合体

```c
union Data { int i; float f; char str[20]; };
union Data d;
d.i = 10;   // 覆盖之前的值
```

### 枚举

```c
enum Color { RED, GREEN, BLUE };
enum Status { STOP = 0, RUNNING = 1 };
```

---

## 十二、预处理器

### 宏定义

```c
#define PI 3.14159
#define SQUARE(x) ((x)*(x))    // 必须加括号
#define MAX(a,b) ((a)>(b)?(a):(b))
```

### 多行宏

```c
#define SWAP(a,b) do { \
    typeof(a) temp = (a); \
    (a) = (b); \
    (b) = temp; \
} while(0)
```

### 条件编译

```c
#ifdef DEBUG
    ...
#endif

#ifndef HEADER_H
#define HEADER_H
...
#endif

#if defined(WIN32)
    ...
#elif defined(LINUX)
    ...
#endif
```

### 预定义宏

```c
__FILE__  __LINE__  __DATE__  __TIME__  __func__  __STDC__
__STDC_VERSION__   // C23: 202311L
```

### `#` 和 `##`

```c
#define STR(x) #x          // 转为字符串
#define CONCAT(x,y) x##y   // 拼接
```

### `_Pragma`（C99）

```c
#define DO_PRAGMA(x) _Pragma(#x)
```

### C23 新增

```c
#warning "自定义警告信息"     // C23 正式
#embed "file.bin"              // C23 新增，嵌入二进制文件
__VA_OPT__(...)                // C23 正式，可变参数宏中可选内容
```

---

## 十三、常用标准库

### 头文件速览

```c
#include <stdio.h>     // 输入输出
#include <stdlib.h>    // malloc, rand, atoi, qsort
#include <string.h>    // 字符串操作
#include <math.h>      // 数学（链接 -lm）
#include <time.h>      // 时间
#include <ctype.h>     // 字符处理
#include <limits.h>    // 整数限制
#include <float.h>     // 浮点限制
#include <stdbool.h>   // bool（C99+）
#include <stdint.h>    // 定长整数（C99+）
#include <inttypes.h>  // 定长整数格式化宏
#include <assert.h>    // 断言
#include <errno.h>     // 错误码
#include <stdarg.h>    // 可变参数
#include <stddef.h>    // size_t, NULL, offsetof
```

### 常用函数

```c
// stdlib.h
atoi, atol, atof, strtol, strtod, rand, srand, malloc, free, qsort, bsearch, exit, abort

// string.h
strcpy, strncpy, strcat, strncat, strlen, strcmp, strncmp, strchr, strstr,
memcpy, memmove, memset, memcmp

// math.h
sin, cos, tan, asin, acos, atan, atan2, sqrt, pow, exp, log, log10,
fabs, ceil, floor, fmod, round, trunc

// ctype.h
isalpha, isdigit, isalnum, islower, isupper, isspace, tolower, toupper
```

### C23 新增库头文件

```c
#include <stdbit.h>    // 位操作：stdc_leading_zeros, stdc_trailing_zeros, stdc_count_ones 等
#include <stdckdint.h> // 检查整数溢出：ckd_add, ckd_sub, ckd_mul
```

---

## 十四、文件操作

### 打开模式

| 模式 | 说明 |
|------|------|
| `"r"` | 只读，文件必须存在 |
| `"w"` | 写入，不存在则创建，存在则清空 |
| `"a"` | 追加 |
| `"r+"` | 读写 |
| `"w+"` | 读写，清空 |
| `"a+"` | 读写追加 |
| `"rb"` / `"wb"` / `"ab"` | 二进制模式 |

### 文件操作函数

```c
fopen, fclose, fgetc, fputc, fgets, fputs,
fprintf, fscanf, fwrite, fread,
fseek, ftell, rewind, feof, ferror, perror
```

### C11 安全函数（Annex K，可选）

```c
// 需要实现支持，非所有编译器都提供
fopen_s, strcpy_s, sprintf_s, memcpy_s
```

> Annex K 是 C11 的可选规范，CERT C 推荐使用，但实际支持有限。

---

## 十五、高级指针与内存

### 函数指针数组

```c
int (*ops[])(int, int) = {add, sub, mul};
int result = ops[0](3, 5);
```

### `restrict`（C99）

```c
void copy(int *restrict dest, const int *restrict src, int n) {
    for (int i = 0; i < n; i++) dest[i] = src[i];
}
```

### `volatile`

```c
volatile int flag = 0;   // 禁止编译器优化
```

### `_Atomic`（C11）

```c
#include <stdatomic.h>
atomic_int counter = 0;
atomic_fetch_add(&counter, 1);
```

### `alignas` / `alignof`（C11）

```c
#include <stdalign.h>
alignas(16) int arr[10];
printf("%zu\n", alignof(int));
```

### C23 新增：`nullptr`

```c
int *p = nullptr;   // C23 正式关键字
```

### C23 新增：`typeof`

```c
typeof(x) y = x;    // C23 正式
```

### C23 新增：`constexpr`

```c
constexpr int SIZE = 100;   // 编译期常量，可用于数组大小
```

### C23 新增：`_BitInt`

```c
_BitInt(7) x = 100;         // 精确位宽整数
```

### C23 新增：`_Decimal32` / `_Decimal64` / `_Decimal128`

```c
_Decimal64 d = 1.23DD;      // 十进制浮点
```

---

## 十六、链表与数据结构

### 单向链表

```c
typedef struct Node {
    int data;
    struct Node *next;
} Node;

Node* create_node(int data);
void insert_head(Node **head, int data);
void insert_tail(Node **head, int data);
void delete_node(Node **head, int data);
void print_list(Node *head);
void free_list(Node *head);
```

### 栈（基于数组）

```c
typedef struct Stack {
    int *data;
    int top;
    int capacity;
} Stack;
```

### 队列（循环队列）

```c
typedef struct Queue {
    int *data;
    int front;
    int rear;
    int size;
    int capacity;
} Queue;
```

---

## 十七、位操作技巧

```c
// 检查第 n 位
int is_bit_set(int x, int n) { return (x >> n) & 1; }

// 设置第 n 位
int set_bit(int x, int n) { return x | (1 << n); }

// 清除第 n 位
int clear_bit(int x, int n) { return x & ~(1 << n); }

// 翻转第 n 位
int toggle_bit(int x, int n) { return x ^ (1 << n); }

// 最低位 1
int lowbit(int x) { return x & -x; }

// 判断 2 的幂
int is_power_of_two(int x) { return x > 0 && (x & (x - 1)) == 0; }

// 统计 1 的个数（Brian Kernighan）
int count_bits(int x) {
    int count = 0;
    while (x) { x &= (x - 1); count++; }
    return count;
}

// 交换两个数
a ^= b; b ^= a; a ^= b;
```

### C23 `<stdbit.h>` 位操作

```c
stdc_leading_zeros(x)     // 前导零个数
stdc_trailing_zeros(x)    // 尾随零个数
stdc_count_ones(x)        // 1 的个数
stdc_count_zeros(x)       // 0 的个数
stdc_bit_width(x)         // 位宽
```

---

## 十八、错误处理与调试

### `errno`

```c
#include <errno.h>
#include <string.h>

FILE *fp = fopen("nonexist.txt", "r");
if (fp == NULL) {
    printf("错误: %s\n", strerror(errno));
    perror("fopen");
}
```

### 断言

```c
#include <assert.h>
assert(ptr != NULL);
```

> C23 中 `static_assert` 成为关键字，`assert.h` 不再需要 `_Static_assert` 宏。

### 调试宏

```c
#ifdef DEBUG
    #define DEBUG_PRINT(fmt, ...) fprintf(stderr, fmt, ##__VA_ARGS__)
#else
    #define DEBUG_PRINT(fmt, ...)
#endif
```

### GDB 常用命令

```bash
gcc -g program.c -o program
gdb program

break main          # 断点
run                 # 运行
next                # 下一步（不进入函数）
step                # 下一步（进入函数）
print var           # 打印变量
backtrace           # 调用栈
continue            # 继续
quit                # 退出
```

### Valgrind

```bash
valgrind --leak-check=full ./program
```

---

## 十九、C 标准演进（C89 → C23）

### 标准版本总览

| 标准 | 发布年份 | 别名 | 关键特性 |
|------|----------|------|----------|
| C89 / C90 | 1989/1990 | ANSI C | 基础语言、标准库 |
| C95 | 1995 | 修正案 | 宽字符、`__STDC_VERSION__` |
| C99 | 1999 | — | `//` 注释、`inline`、VLA、`long long`、`stdint.h`、`stdbool.h`、复合字面量、指定初始化器 |
| C11 | 2011 | — | `_Generic`、`_Static_assert`、`_Alignas`/`_Alignof`、`_Noreturn`、`_Atomic`、`threads.h`、匿名结构体/联合体、`alignas`/`alignof` 宏 |
| C17 | 2018 | — | C11 的缺陷修复，无新特性 |
| C23 | 2024 | ISO/IEC 9899:2024 | 二进制字面量、数字分隔符、`nullptr`、`typeof`、`constexpr`、`_BitInt`、十进制浮点、`#embed`、`#warning`、`[[attributes]]`、`static_assert`/`thread_local` 成为关键字、`u8` 字符类型、空初始化器 `{}`、标签后声明 |

### C11 详细特性

**`_Generic` 泛型选择**

```c
#define abs(x) _Generic((x), \
    int: abs_int, \
    float: abs_float, \
    double: abs_double \
)(x)
```

**`_Static_assert` 静态断言**

```c
_Static_assert(sizeof(int) == 4, "int 必须是4字节");
```

**`_Alignas` / `_Alignof`**

```c
_Alignas(16) int arr[10];
printf("%zu\n", _Alignof(int));
```

**多线程（`<threads.h>`）**

```c
#include <threads.h>
int thread_func(void *arg) { return 0; }
thrd_t t;
thrd_create(&t, thread_func, NULL);
thrd_join(t, NULL);
```

**原子操作（`<stdatomic.h>`）**

```c
atomic_int counter = 0;
atomic_fetch_add(&counter, 1);
```

### C23 详细特性

**二进制字面量与数字分隔符**

```c
int x = 0b1010;
int y = 1'000'000;
```

**`nullptr`**

```c
int *p = nullptr;
```

**`typeof`**

```c
typeof(x) y = x;
```

**`constexpr`**

```c
constexpr int SIZE = 100;
int arr[SIZE];
```

**`_BitInt`**

```c
_BitInt(7) x = 100;
```

**十进制浮点**

```c
_Decimal32, _Decimal64, _Decimal128
```

**`#embed`**

```c
#embed "icon.bin"
```

**`#warning`**

```c
#warning "这是一条自定义警告"
```

**属性（`[[...]]`）**

```c
[[nodiscard]] int compute(void);
[[maybe_unused]] int x;
[[deprecated]] void old_func(void);
[[noreturn]] void fatal(void);
```

**`static_assert` 和 `thread_local` 成为关键字**

```c
static_assert(sizeof(int) == 4, "int must be 4 bytes");
thread_local int tls_var;
```

**空初始化器 `{}`**

```c
int arr[10] = {};    // C23 正式
```

**标签后声明**

```c
label:
    int x = 10;      // C23 允许
```

**`u8` 字符类型**

```c
char8_t c = u8'A';   // C23
```

---

## 二十、未定义行为与实现定义行为

### 未定义行为（UB）

C 标准在 Annex J.2 中列出了 191 种未定义行为。常见示例：

| 类别 | 示例 |
|------|------|
| 除零 | `10 / 0`、`10 % 0` |
| 越界访问 | `arr[10]` 当 `arr` 大小为 10 |
| 使用未初始化变量 | `int x; printf("%d", x);` |
| 空指针解引用 | `int *p = NULL; *p = 1;` |
| 释放后使用 | `free(p); *p = 1;` |
| 双重释放 | `free(p); free(p);` |
| 有符号整数溢出 | `INT_MAX + 1` |
| 返回局部变量地址 | `int* f() { int x; return &x; }` |
| 数据竞争 | 多线程无同步地访问共享变量 |
| 修改字符串字面量 | `char *s = "hi"; s[0] = 'H';` |
| `realloc` 大小为 0 | C23 起行为未定义 |

> **依赖 UB 的程序在不同编译器、不同优化级别下行为可能完全不同，必须避免。**

### 实现定义行为

C 标准在 Annex J.3 中列出了 112 种实现定义行为。示例：

- 字节中的位数
- 有符号整数的表示方式（补码/反码/原码）
- 浮点舍入方向
- `char` 是否有符号
- 右移有符号负数的结果

> 实现定义行为是可移植性问题的常见来源。C23 要求有符号整数必须使用补码表示，消除了这一实现差异。

### 未指定行为

C 标准在 Annex J.1 中列出未指定行为，如函数参数求值顺序、`f2() + f3()` 中两个函数的调用顺序等。

---

## 二十一、安全编程（CERT C）

### CERT C 概述

SEI CERT C Secure Coding Standard 是针对 C 语言的安全编码标准，最初为 C11 开发，也可应用于 C99。它包含 **规则（Rules）** 和 **建议（Recommendations）** ，目标是消除不安全编码实践。

### 核心安全编码规则

| 规则 | 说明 |
|------|------|
| **EXP** | 表达式：避免依赖未定义行为、避免整数溢出 |
| **INT** | 整数：确保无符号整数不回绕、避免有符号溢出 |
| **STR** | 字符串：确保字符串有终止符、避免缓冲区溢出 |
| **MEM** | 内存：确保指针有效、避免释放后使用、避免双重释放 |
| **ARR** | 数组：确保数组索引在边界内 |
| **FIO** | 文件 IO：避免复制 FILE 对象、正确关闭文件 |
| **MSC** | 杂项：避免在信号处理中调用非异步安全函数 |

### 安全编码实践

```c
// ❌ 不安全：strcpy 无边界检查
char buf[10];
strcpy(buf, user_input);

// ✅ 安全：使用 snprintf 或 strncpy 并手动终止
snprintf(buf, sizeof(buf), "%s", user_input);

// ❌ 不安全：整数溢出
int size = user_len * 2;
char *p = malloc(size);

// ✅ 安全：检查溢出
if (user_len > SIZE_MAX / 2) { /* 处理错误 */ }
size_t size = user_len * 2;

// ❌ 不安全：使用已释放内存
free(p);
printf("%d", *p);

// ✅ 安全
free(p);
p = NULL;
```

### 推荐使用 Annex K 安全函数（如果可用）

```c
strcpy_s(dest, dest_size, src);
sprintf_s(buf, buf_size, fmt, ...);
memcpy_s(dest, dest_size, src, n);
```

> Annex K 是 C11 的可选规范，并非所有编译器都实现。

---

## 二十二、编译器扩展（GCC / Clang）

### GCC 常用扩展

```c
// 语句表达式
#define MAX(a,b) ({ typeof(a) _a = (a); typeof(b) _b = (b); _a > _b ? _a : _b; })

// 属性
__attribute__((packed)) struct Packed { ... };
__attribute__((aligned(16))) int arr[4];
__attribute__((noreturn)) void fatal(void);
__attribute__((deprecated)) void old_func(void);
__attribute__((unused)) int x;

// 内联汇编
__asm__ volatile ("nop");

// 预取
__builtin_prefetch(ptr);

// 分支预测
if (__builtin_expect(cond, 1)) { ... }

// 类型兼容
__builtin_types_compatible_p(type1, type2);
```

### Clang 扩展

Clang 高度兼容 GCC 扩展，并增加了自己的特性：

```c
// Clang 属性
[[clang::fallthrough]];
[[clang::no_sanitize("address")]];

// 诊断控制
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wunused-variable"
// ...
#pragma clang diagnostic pop
```

### `-fms-extensions`

在 Clang 中启用 Microsoft 扩展。

---

## 二十三、内存对齐详解

### 对齐基础

- 每个类型有**对齐要求**（alignment requirement），通常是其大小的幂。
- `int` 通常对齐到 4 字节，`double` 通常对齐到 8 字节。
- 结构体的对齐等于其最严格对齐成员的对齐，大小是该对齐的倍数。

### 结构体填充

```c
struct Example {
    char c;      // 偏移 0
    // 3 字节填充
    int i;       // 偏移 4
    char d;      // 偏移 8
    // 3 字节填充
};               // sizeof = 12
```

### 控制对齐

```c
// C11
#include <stdalign.h>
alignas(16) int arr[10];
printf("%zu\n", alignof(int));

// GCC/Clang 扩展
struct __attribute__((packed)) Packed { ... };
```

### `offsetof`

```c
#include <stddef.h>
size_t off = offsetof(struct Example, i);
```

---

## 二十四、构建系统（CMake）

### 基本 `CMakeLists.txt`

```cmake
cmake_minimum_required(VERSION 3.20)
project(MyProject C)

set(CMAKE_C_STANDARD 23)
set(CMAKE_C_STANDARD_REQUIRED ON)

add_executable(myapp main.c add.c)
target_include_directories(myapp PRIVATE include)
target_link_libraries(myapp PRIVATE m)
target_compile_options(myapp PRIVATE -Wall -Wextra -Werror)
```

### 常用命令

```bash
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build
cmake --build build --target install
```

### 添加库

```cmake
add_library(mylib STATIC lib.c)
target_include_directories(mylib PUBLIC include)
target_link_libraries(myapp PRIVATE mylib)
```

---

## 二十五、静态分析工具

| 工具 | 特点 |
|------|------|
| **Clang Static Analyzer** | LLVM 项目，路径敏感、过程间分析 |
| **GCC `-fanalyzer`** | GCC 10+ 内置静态分析器 |
| **Cppcheck** | 开源，轻量，适合 CI |
| **Splint** | 注解辅助的轻量静态检查 |
| **Smatch** | 专注于 Linux 内核的静态分析 |
| **IKOS** | 基于抽象解释的 C/C++ 静态分析 |
| **Astrée** | 用于嵌入式安全关键系统的形式化验证工具 |

### 使用示例

```bash
# GCC 静态分析
gcc -fanalyzer -Wall -Wextra main.c -o main

# Clang 静态分析
clang --analyze main.c

# Cppcheck
cppcheck --enable=all --inconclusive main.c
```

---

## 二十六、单元测试框架

| 框架 | 特点 | 适用场景 |
|------|------|----------|
| **Unity** | 极轻量，单文件，嵌入式友好 | 嵌入式、资源受限环境 |
| **Check** | 支持测试套件、Mock，功能较全 | 桌面/服务器项目 |
| **CUnit** | 类 JUnit 风格，简单易用 | 常规 C 项目 |
| **cmocka** | 支持 Mock/Stub，内存泄漏检测 | 需要 Mock 的项目 |
| **Criterion** | 跨平台，支持参数化测试 | 现代 C 项目 |
| **CppUTest** | 内置内存泄漏检测，TDD 友好 | C/C++ 混合项目 |

### Unity 示例

```c
#include "unity.h"

void setUp(void) {}
void tearDown(void) {}

void test_add(void) {
    TEST_ASSERT_EQUAL(5, add(2, 3));
}

int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_add);
    return UNITY_END();
}
```

---

## 二十七、常见陷阱与最佳实践

### 常见陷阱

| 陷阱 | 示例 |
|------|------|
| 数组越界 | `arr[5] = 10;` |
| 字符串缺少终止符 | `char str[3] = "abc";` |
| 返回局部变量地址 | `return &x;` |
| 使用未初始化变量 | `int x; printf("%d", x);` |
| 整数溢出 | `INT_MAX + 1` |
| 内存泄漏 | 忘记 `free` |
| 重复释放 | `free(p); free(p);` |
| 有符号/无符号比较 | `int i = -1; unsigned u = 1; if (i > u)` |
| 忘记 `break` in switch | 意外贯穿 |
| 浮点相等比较 | `0.1 + 0.2 == 0.3` |

### 最佳实践

1. **指针使用前检查 NULL**
2. **使用 `size_t` 表示大小**
3. **使用 `const` 保护不修改的值**
4. **使用 include guard 或 `#pragma once`**
5. **函数单一职责**
6. **C99+：变量在使用处声明**
7. **使用 `static` 限制作用域**
8. **编译时开启 `-Wall -Wextra -Werror`**
9. **使用定长整数类型（`stdint.h`）**
10. **使用静态分析工具和单元测试**

---

## 二十八、编译与链接

### 编译四步骤

```bash
gcc -E main.c -o main.i    # 预处理
gcc -S main.i -o main.s    # 编译为汇编
gcc -c main.s -o main.o    # 汇编为目标文件
gcc main.o -o main         # 链接
```

### 常用编译选项

| 选项 | 说明 |
|------|------|
| `-Wall` | 显示所有警告 |
| `-Wextra` | 额外警告 |
| `-Werror` | 警告视为错误 |
| `-O0` ~ `-O3` | 优化级别 |
| `-g` | 调试信息 |
| `-std=c17` / `-std=c23` | 指定标准 |
| `-DDEBUG` | 定义宏 |
| `-I/path` | 头文件路径 |
| `-L/path` | 库路径 |
| `-lm` | 链接数学库 |
| `-static` | 静态链接 |
| `-shared` | 共享库 |
| `-fPIC` | 位置无关代码（共享库） |
| `-fanalyzer` | GCC 静态分析 |
| `-fsanitize=address` | AddressSanitizer |
| `-fsanitize=undefined` | UndefinedBehaviorSanitizer |

### 创建静态库

```bash
gcc -c add.c sub.c
ar rcs libmymath.a add.o sub.o
gcc main.c -L. -lmymath -o program
```

### 创建动态库

```bash
gcc -fPIC -c add.c sub.c
gcc -shared -o libmymath.so add.o sub.o
gcc main.c -L. -lmymath -o program
```

---

## 二十九、速查小抄

```
类型：int, char, float, double, void, size_t, bool, int32_t, uint64_t
格式：%d, %f, %c, %s, %p, %zu, %" PRId64 "
函数：printf, scanf, malloc, free, strcpy, strlen, fopen, fclose
指针：*p 解引用, &a 取地址, p->x 结构体指针, NULL
内存：malloc, calloc, realloc, free, memcpy, memset
编译：gcc -Wall -Wextra -g -std=c17 main.c -o main
调试：gdb ./main; break main; run; print var; next; step
测试：Unity, Check, CUnit, cmocka
静态分析：gcc -fanalyzer, clang --analyze, cppcheck
构建：cmake -B build && cmake --build build
```

---

## 三十、C 语言学习路线图

```
🟢 入门
├── Hello World、编译运行
├── 数据类型、变量、常量
├── 输入输出（printf/scanf）
└── 运算符与表达式

🟡 基础
├── 控制流（if/switch/for/while）
├── 数组与字符串
├── 函数、参数传递
└── 指针基础

🟠 进阶
├── 动态内存管理（malloc/free）
├── 结构体/联合体/枚举
├── 文件操作
└── 预处理器

🔴 高级
├── 高级指针（函数指针/多级指针）
├── 数据结构（链表/栈/队列）
├── 位操作
└── 内存对齐

⚫ 专家
├── 编译链接原理
├── 未定义行为与实现定义行为
├── 安全编程（CERT C）
├── 调试与性能分析（GDB/Valgrind/Sanitizer）
├── 静态分析与单元测试
├── CMake 构建系统
└── C 标准演进（C89–C23）
```

---

> 本速查卡覆盖从 C 语言基础到专家级主题，参考 ISO/IEC 9899 标准、SEI CERT C 安全编码标准、GCC 官方文档等权威来源，可作为日常开发与系统学习参考。