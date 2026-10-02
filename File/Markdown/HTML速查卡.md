
# HTML 速查卡

---

## 一、文档基础模板

```html
<!DOCTYPE html>                <!-- 声明这是HTML5文档，必须写在第一行 -->
<html lang="zh-CN">            <!-- 整个网页的根标签，lang="zh-CN"表示中文 -->
<head>                         <!-- 头部：放网页的配置信息，用户看不到 -->
    <meta charset="UTF-8">     <!-- 设置编码为UTF-8，让中文不乱码，必须有 -->
    <meta name="viewport"      <!-- 移动端适配，让手机也能正常显示 -->
          content="width=device-width, initial-scale=1.0">  <!-- 宽度=设备宽度，初始缩放=1倍 -->
    
    <title>网页标题</title>     <!-- 浏览器标签页上显示的文字，必须有 -->
    
    <meta name="description"    <!-- 网页描述，影响搜索引擎结果 -->
          content="这是网页的简短描述，会在搜索结果中显示">
    
    <link rel="stylesheet"      <!-- 链接外部CSS文件，用来美化页面 -->
          href="style.css">     <!-- href是文件路径 -->
    
    <link rel="icon"            <!-- 浏览器标签页上的小图标 -->
          href="favicon.ico">   <!-- 一般用.ico或.png格式 -->
</head>

<body>                         <!-- 主体：用户能看到的所有内容都写在这里 -->
    <!-- 页面内容写这里 -->
</body>
</html>                        <!-- 结束html标签 -->
```

---

## 二、文本标签

```html
<!-- 标题标签：数字越小字越大，h1最大，h6最小 -->
<h1>一级标题</h1>              <!-- 最重要的标题，一个页面建议只用一次 -->
<h2>二级标题</h2>              <!-- 章节标题 -->
<h3>三级标题</h3>              <!-- 子章节标题 -->
<h4>四级标题</h4>
<h5>五级标题</h5>
<h6>六级标题</h6>              <!-- 最小的标题 -->

<!-- 段落标签 -->
<p>这是一个段落。浏览器会自动在段落前后添加空行。</p>
<p>这是另一个段落。多个空格和换行在HTML中会被压缩成一个空格。</p>

<!-- 换行和分割线 -->
第一行文字<br>                 <!-- <br>是换行，自闭合标签，不需要结束标签 -->
第二行文字
<hr>                          <!-- <hr>是水平分割线，用来分隔内容 -->

<!-- 文字格式标签 -->
<strong>重要/加粗文字</strong>   <!-- 推荐使用，有语义含义（表示重要） -->
<b>普通加粗文字</b>              <!-- 只是视觉加粗，无语义 -->
<em>斜体/强调文字</em>           <!-- 推荐使用，有语义含义（表示强调） -->
<i>普通斜体文字</i>              <!-- 只是视觉斜体，无语义 -->
<mark>高亮标记文字</mark>        <!-- 背景色高亮，像荧光笔 -->
<small>小号文字</small>          <!-- 用于版权信息、注释等 -->
<del>删除线文字</del>            <!-- 表示被删除的内容 -->
<ins>下划线/插入文字</ins>       <!-- 表示新插入的内容 -->
普通文字<sub>下标</sub>          <!-- 化学式 H₂O 里的2 -->
普通文字<sup>上标</sup>          <!-- 数学公式 x² 里的2 -->

<!-- 示例 -->
<p>学习<strong>HTML</strong>需要<em>多加练习</em>。</p>
<p>原价<del>100元</del>，现价<ins>80元</ins>！</p>
<p>水的化学式是 H<sub>2</sub>O，数学公式 x<sup>2</sup> = 4</p>
```

---

## 三、链接

```html
<!-- 基本链接 -->
<a href="https://www.baidu.com">点击访问百度</a>
<!-- href="链接地址" → 点击文字跳转到指定网址 -->

<!-- 新标签页打开（推荐，避免覆盖当前页面） -->
<a href="https://www.google.com" target="_blank">新窗口打开谷歌</a>
<!-- target="_blank" → 在新标签页打开 -->

<!-- 锚点跳转（在同一页面内跳转） -->
<a href="#section1">跳转到第一节</a>     <!-- 点击后跳转到id="section1"的位置 -->
<a href="#section2">跳转到第二节</a>

<h2 id="section1">第一节</h2>            <!-- id是唯一标识符，不能重复 -->
<p>第一节的内容...</p>

<h2 id="section2">第二节</h2>
<p>第二节的内容...</p>

<!-- 返回顶部 -->
<a href="#">返回顶部</a>                 <!-- #表示页面顶部 -->

<!-- 发邮件和打电话 -->
<a href="mailto:yourname@example.com">发送邮件给我</a>
<!-- 点击会打开默认邮件程序 -->

<a href="tel:13800138000">拨打电话</a>
<!-- 点击在手机上会打开拨号界面 -->

<!-- 图片也可以作为链接 -->
<a href="https://example.com">
    <img src="logo.png" alt="网站Logo">
</a>
```

---

## 四、列表

### 无序列表
```html
<ul>                               <!-- ul = Unordered List -->
    <li>苹果</li>                  <!-- li = List Item -->
    <li>香蕉</li>
    <li>橙子</li>
</ul>
```
显示效果：
- 苹果
- 香蕉
- 橙子

### 有序列表
```html
<ol>                               <!-- ol = Ordered List -->
    <li>第一步：打开冰箱</li>
    <li>第二步：放进大象</li>
    <li>第三步：关上冰箱</li>
</ol>
```
显示效果：
1. 第一步：打开冰箱
2. 第二步：放进大象
3. 第三步：关上冰箱

### 嵌套列表
```html
<ul>
    <li>水果
        <ul>
            <li>苹果</li>
            <li>香蕉</li>
        </ul>
    </li>
    <li>蔬菜
        <ul>
            <li>白菜</li>
            <li>萝卜</li>
        </ul>
    </li>
</ul>
```

### 描述列表
```html
<dl>                               <!-- dl = Description List -->
    <dt>HTML</dt>                  <!-- dt = Description Term，术语 -->
    <dd>超文本标记语言，用来制作网页</dd>  <!-- dd = Description Description，描述 -->
    
    <dt>CSS</dt>
    <dd>层叠样式表，用来美化网页</dd>
    
    <dt>JavaScript</dt>
    <dd>编程语言，让网页有交互功能</dd>
</dl>
```

---

## 五、表格

### 基础表格
```html
<table border="1">                 <!-- border="1" 给表格加边框，便于观察 -->
    <!-- 表格头部 -->
    <thead>                        <!-- 可选，语义标签 -->
        <tr>
            <th>姓名</th>          <!-- th = Table Header，表头（自动加粗居中） -->
            <th>年龄</th>
            <th>城市</th>
        </tr>
    </thead>
    
    <!-- 表格主体 -->
    <tbody>                        <!-- 可选，语义标签 -->
        <tr>
            <td>小明</td>         <!-- td = Table Data，单元格 -->
            <td>18</td>
            <td>北京</td>
        </tr>
        <tr>
            <td>小红</td>
            <td>17</td>
            <td>上海</td>
        </tr>
    </tbody>
    
    <!-- 表格底部（可选） -->
    <tfoot>
        <tr>
            <td>总计</td>
            <td colspan="2">2人</td>  <!-- colspan="2" 合并2列 -->
        </tr>
    </tfoot>
</table>
```

### 合并单元格
```html
<table border="1">
    <tr>
        <th>项目</th>
        <th>金额</th>
    </tr>
    <tr>
        <td rowspan="2">食品</td>     <!-- rowspan="2" 合并2行 -->
        <td>100元</td>
    </tr>
    <tr>
        <td>50元</td>
    </tr>
</table>
```

---

## 六、图片与多媒体

### 图片
```html
<img src="图片.jpg" alt="图片描述">
<!-- 
    src = source，图片路径（必填）
    alt = alternative text，图片加载失败时显示的文字，也是盲人阅读器会读的内容（必填）
-->

<!-- 图片路径说明 -->
<img src="cat.jpg">                 <!-- 同一文件夹下的图片 -->
<img src="images/cat.jpg">          <!-- images文件夹下的图片 -->
<img src="../cat.jpg">              <!-- 上一级文件夹的图片 -->
<img src="https://example.com/cat.jpg"> <!-- 网络图片（URL） -->
```

### 响应式图片
```html
<picture>
    <!-- 手机屏幕宽度 ≤ 600px 时加载 small.jpg -->
    <source media="(max-width: 600px)" srcset="small.jpg">
    <!-- 平板宽度 ≤ 1200px 时加载 medium.jpg -->
    <source media="(max-width: 1200px)" srcset="medium.jpg">
    <!-- 其他情况加载 large.jpg -->
    <img src="large.jpg" alt="风景图">
</picture>
```

### 视频
```html
<!-- 基本视频 -->
<video src="video.mp4" controls width="600">
    您的浏览器不支持 video 标签。
</video>

<!-- 带多种格式 -->
<video controls width="600">
    <source src="video.mp4" type="video/mp4">
    <source src="video.webm" type="video/webm">
    <source src="video.ogv" type="video/ogg">
    您的浏览器不支持 video 标签。
</video>

<!-- 带属性的视频 -->
<video src="video.mp4" controls autoplay muted loop poster="封面图.jpg">
    <!-- autoplay：自动播放（通常需要配合muted） -->
    <!-- muted：静音 -->
    <!-- loop：循环播放 -->
    <!-- poster：设置视频封面 -->
</video>
```

### 音频
```html
<audio src="music.mp3" controls>
    您的浏览器不支持 audio 标签。
</audio>
```

### iframe 嵌入
```html
<iframe src="https://www.youtube.com/embed/视频ID" width="800" height="450">
    <!-- 常用于嵌入YouTube视频、Google地图 -->
</iframe>
```

---

## 七、容器与布局标签

### 基础容器
```html
<div>    <!-- 块级容器：独占一行，用来装一组内容 -->
<span>   <!-- 行内容器：不换行，用来包裹一小段文字或图标 -->
```

### HTML5 语义化布局标签
```html
<header>     <!-- 页眉：网站Logo、导航栏、搜索框等 -->
<nav>        <!-- 导航栏：菜单链接 -->
<main>       <!-- 主内容：页面最核心的内容，一个页面只有一个 -->
<section>    <!-- 章节：一组相关的内容 -->
<article>    <!-- 独立文章：博客文章、新闻等 -->
<aside>      <!-- 侧边栏：广告、相关链接 -->
<footer>     <!-- 页脚：版权信息、联系方式 -->
```

### 语义化布局示例
```html
<header>
    <h1>我的博客</h1>
    <nav>
        <a href="/">首页</a>
        <a href="/about">关于我</a>
    </nav>
</header>

<main>
    <article>
        <h2>第一篇文章</h2>
        <p>文章内容...</p>
    </article>
    <aside>
        <h3>广告位</h3>
        <p>联系我：xxx</p>
    </aside>
</main>

<footer>
    <p>&copy; 2024 我的博客</p>
</footer>
```

---

## 八、表单

```html
<form action="/submit" method="POST">
    <!-- 
        action：表单提交到哪里（后端接口地址）
        method：提交方式，GET（数据在URL）或 POST（数据在请求体，更安全）
    -->
    
    <!-- 1. 文本输入框 -->
    <label for="username">用户名：</label>
    <input type="text" id="username" name="username" placeholder="请输入用户名" required>
    
    <!-- 2. 密码输入框 -->
    <label for="password">密码：</label>
    <input type="password" id="password" name="password" placeholder="请输入密码">
    
    <!-- 3. 邮箱输入框 -->
    <label for="email">邮箱：</label>
    <input type="email" id="email" name="email" placeholder="example@email.com">
    
    <!-- 4. 数字输入框 -->
    <label for="age">年龄：</label>
    <input type="number" id="age" name="age" min="0" max="120" value="18">
    
    <!-- 5. 日期选择器 -->
    <label for="birthday">生日：</label>
    <input type="date" id="birthday" name="birthday">
    
    <!-- 6. 单选按钮 -->
    <label>性别：</label>
    <input type="radio" id="male" name="gender" value="男">
    <label for="male">男</label>
    <input type="radio" id="female" name="gender" value="女">
    <label for="female">女</label>
    
    <!-- 7. 复选框 -->
    <label>爱好：</label>
    <input type="checkbox" id="coding" name="hobby" value="编程">
    <label for="coding">编程</label>
    <input type="checkbox" id="reading" name="hobby" value="阅读">
    <label for="reading">阅读</label>
    
    <!-- 8. 下拉选择框 -->
    <label for="city">城市：</label>
    <select id="city" name="city">
        <option value="北京">北京</option>
        <option value="上海" selected>上海</option>
        <option value="广州">广州</option>
    </select>
    
    <!-- 9. 多行文本输入 -->
    <label for="bio">个人简介：</label>
    <textarea id="bio" name="bio" rows="5" cols="30" placeholder="介绍一下自己..."></textarea>
    
    <!-- 10. 文件上传 -->
    <label for="avatar">头像：</label>
    <input type="file" id="avatar" name="avatar" accept="image/*">
    
    <!-- 11. 隐藏字段 -->
    <input type="hidden" name="user_id" value="12345">
    
    <!-- 12. 按钮 -->
    <button type="submit">提交</button>
    <button type="reset">重置</button>
    <button type="button">普通按钮</button>
    
    <!-- input也可以做按钮 -->
    <input type="submit" value="提交">
    <input type="reset" value="重置">
</form>
```

---

## 九、全局属性

```html
<!-- id：唯一标识符（一个页面不能重复） -->
<div id="header">...</div>
<!-- 用途1：CSS通过 #header {} 来设置样式 -->
<!-- 用途2：JS通过 document.getElementById('header') 来操作 -->
<!-- 用途3：锚点跳转 <a href="#header">跳到头部</a> -->

<!-- class：类名（可以重复，一个标签可以有多个类名，空格分隔） -->
<div class="container main-box">...</div>
<!-- 用途：CSS通过 .container {} 来设置样式 -->

<!-- style：内联样式（直接写CSS，不推荐） -->
<p style="color: red; font-size: 20px;">红色大字</p>

<!-- data-*：自定义数据 -->
<div data-user-id="123" data-role="admin">...</div>

<!-- hidden：隐藏元素 -->
<p hidden>你看不到我</p>

<!-- title：鼠标悬停时显示的提示文字 -->
<abbr title="HyperText Markup Language">HTML</abbr>

<!-- lang：指定语言 -->
<p lang="en">Hello World</p>

<!-- tabindex：Tab键切换顺序 -->
<input type="text" tabindex="1">
<input type="text" tabindex="2">

<!-- disabled：禁用元素 -->
<button disabled>不可点击</button>
```

---

## 十、HTML 实体

| 显示 | 实体代码 | 说明 |
|------|----------|------|
| <    | `&lt;`   | 小于号 |
| >    | `&gt;`   | 大于号 |
| &    | `&amp;`  | 与符号 |
| "    | `&quot;` | 双引号 |
| '    | `&apos;` | 单引号 |
| ©    | `&copy;` | 版权符号 |
| ®    | `&reg;`  | 注册商标 |
| ™    | `&trade;`| 商标符号 |
| 空格 | `&nbsp;` | 不换行空格 |
| —    | `&mdash;`| 长破折号 |
| ·    | `&middot;`| 中间点 |

```html
<!-- 示例 -->
<p>使用 &lt;div&gt; 标签来创建容器</p>
<!-- 显示：使用 <div> 标签来创建容器 -->

<p>我&nbsp;&nbsp;&nbsp;有3个空格</p>
<!-- &nbsp;空格不会被浏览器合并 -->
```

---

## 十一、注释

```html
<!-- 这是HTML注释，不会显示在页面上 -->
<!-- 注释可以写多行
     用来解释代码的作用
     或者临时禁用某段代码 -->

<!-- 好注释示例 -->
<!-- 导航栏：包含首页、关于、联系三个链接 -->
<nav>
    <a href="/">首页</a>
    <a href="/about">关于</a>
    <a href="/contact">联系</a>
</nav>

<!-- 临时禁用某段代码 -->
<!--
<div class="debug">
    <p>这段代码暂时不用</p>
</div>
-->
```

---

## 十二、快速起步模板

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>我的第一个网页</title>
    <style>
        /* 这里写CSS样式 */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: system-ui, -apple-system, sans-serif;
            line-height: 1.6;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        p {
            color: #666;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <main>
        <h1>欢迎学习HTML！</h1>
        <p>这是我的第一个网页。</p>
        <p>HTML是网页的骨架，CSS是衣服，JavaScript是行为。</p>
    </main>
</body>
</html>
```

---

## 十三、语义化布局完整模板

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>我的个人网站</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: system-ui, sans-serif;
            line-height: 1.6;
            color: #333;
        }
        header {
            background: #2c3e50;
            color: white;
            padding: 20px;
            text-align: center;
        }
        nav {
            background: #34495e;
            padding: 10px;
            text-align: center;
        }
        nav a {
            color: white;
            margin: 0 15px;
            text-decoration: none;
        }
        nav a:hover {
            text-decoration: underline;
        }
        main {
            max-width: 1200px;
            margin: 20px auto;
            padding: 0 20px;
            display: flex;
            gap: 20px;
        }
        article {
            flex: 3;
            background: #fff;
            padding: 20px;
            border-radius: 8px;
        }
        aside {
            flex: 1;
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
        }
        footer {
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 20px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <header>
        <h1>我的个人网站</h1>
        <p>学习 | 成长 | 分享</p>
    </header>

    <nav>
        <a href="#">首页</a>
        <a href="#">关于我</a>
        <a href="#">博客文章</a>
        <a href="#">联系我</a>
    </nav>

    <main>
        <article>
            <h2>学习HTML的第一天</h2>
            <p>发布时间：<time datetime="2024-01-15">2024年1月15日</time></p>
            <p>HTML是网页开发的基础，它就像是盖房子时的地基和框架...</p>
            <h3>为什么要学HTML？</h3>
            <p>所有网页都是用HTML编写的，学好HTML是前端开发的起点。</p>
        </article>

        <aside>
            <h3>关于我</h3>
            <p>一个正在学习前端开发的小白。</p>
            <h3>热门文章</h3>
            <ul>
                <li><a href="#">CSS入门指南</a></li>
                <li><a href="#">JavaScript基础</a></li>
                <li><a href="#">响应式布局技巧</a></li>
            </ul>
        </aside>
    </main>

    <footer>
        <p>&copy; 2024 我的个人网站 | 学习笔记分享</p>
    </footer>
</body>
</html>
```

---

## 十四、速查小抄

### 编辑器快捷操作
- `! + Tab` → 快速生成HTML5模板（VSCode中）
- `Ctrl + /` → 注释/取消注释

### 最常用的10个标签
1. `<h1>` 标题
2. `<p>` 段落
3. `<a>` 链接
4. `<img>` 图片
5. `<div>` 容器
6. `<span>` 行内容器
7. `<ul>` + `<li>` 无序列表
8. `<table>` 表格
9. `<form>` + `<input>` 表单
10. `<button>` 按钮

### 核心套路速记
| 需求 | 用什么 |
|------|--------|
| 想换行 | `<br>` |
| 想加空行 | `<p>` |
| 想分块 | `<div>` |
| 想加样式 | `class` |
| 想定位 | `id` |
| 想跳转 | `<a>` |
| 想发数据 | `<form>` |

---

## ✨ 补充内容

### 补充一：HTML 版本历史

| 版本 | 年份 | 特点 |
|------|------|------|
| HTML 1.0 | 1991 | 最初的版本，只有基础标签 |
| HTML 2.0 | 1995 | 标准化表格、表单 |
| HTML 3.2 | 1997 | 引入数学公式、样式属性 |
| HTML 4.01 | 1999 | 引入CSS支持，语义化增强 |
| XHTML 1.0 | 2000 | 更严格的语法规范 |
| HTML5 | 2014 | 引入语义化标签、多媒体、Canvas等 |

### 补充二：常见的 `<meta>` 标签

```html
<!-- SEO 相关 -->
<meta name="description" content="页面描述，影响搜索结果">
<meta name="keywords" content="关键词1,关键词2,关键词3">
<meta name="author" content="作者名称">

<!-- 社交媒体分享（Open Graph） -->
<meta property="og:title" content="分享标题">
<meta property="og:description" content="分享描述">
<meta property="og:image" content="https://example.com/分享图片.jpg">
<meta property="og:url" content="https://example.com/页面链接">

<!-- 移动端相关 -->
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black">

<!-- 安全策略 -->
<meta http-equiv="Content-Security-Policy" content="default-src 'self'">
```

### 补充三：常见的 `<link>` 标签

```html
<!-- 引入 CSS -->
<link rel="stylesheet" href="style.css">

<!-- 网站图标（favicon） -->
<link rel="icon" href="favicon.ico" type="image/x-icon">

<!-- 预加载资源 -->
<link rel="preload" href="style.css" as="style">
<link rel="preload" href="font.woff2" as="font" type="font/woff2" crossorigin>

<!-- DNS 预解析 -->
<link rel="dns-prefetch" href="//example.com">

<!-- 预连接 -->
<link rel="preconnect" href="https://fonts.googleapis.com">

<!-- RSS 订阅 -->
<link rel="alternate" type="application/rss+xml" title="RSS" href="/feed.xml">

<!-- Canonical（规范链接，避免重复内容） -->
<link rel="canonical" href="https://example.com/page">
```

### 补充四：表单输入类型速查

| type 值 | 说明 |
|---------|------|
| `text` | 普通文本 |
| `password` | 密码（显示为点） |
| `email` | 邮箱（自动验证格式） |
| `number` | 数字（带增减按钮） |
| `tel` | 电话号码（手机上调出数字键盘） |
| `url` | 网址（自动验证格式） |
| `search` | 搜索框（带清除按钮） |
| `date` | 日期选择器 |
| `time` | 时间选择器 |
| `datetime-local` | 日期+时间 |
| `month` | 月份选择器 |
| `week` | 周选择器 |
| `color` | 颜色选择器 |
| `range` | 滑块 |
| `file` | 文件上传 |
| `hidden` | 隐藏字段 |
| `radio` | 单选按钮 |
| `checkbox` | 复选框 |
| `submit` | 提交按钮 |
| `reset` | 重置按钮 |
| `button` | 普通按钮 |
| `image` | 图片提交按钮 |

### 补充五：常用 `input` 属性

```html
<input 
    type="text"
    name="username"
    id="username"
    value="默认值"
    placeholder="提示文字"
    required          <!-- 必填 -->
    readonly          <!-- 只读 -->
    disabled          <!-- 禁用 -->
    autofocus         <!-- 自动聚焦 -->
    maxlength="20"    <!-- 最大字符数 -->
    minlength="3"     <!-- 最小字符数 -->
    pattern="[A-Za-z]+" <!-- 正则校验 -->
    autocomplete="off"  <!-- 关闭自动补全 -->
>
```

### 补充六：表格完整属性

```html
<table>
    <caption>表格标题</caption>  <!-- 表格标题，居中显示在表格上方 -->
    <colgroup>                   <!-- 列分组，用于统一设置列样式 -->
        <col style="width: 100px">
        <col style="width: 200px">
    </colgroup>
    <thead>...</thead>
    <tbody>...</tbody>
    <tfoot>...</tfoot>
</table>
```

### 补充七：iframe 常用属性

```html
<iframe 
    src="https://example.com"
    width="600"
    height="400"
    frameborder="0"           <!-- 边框宽度，0表示无边框 -->
    allowfullscreen           <!-- 允许全屏 -->
    loading="lazy"            <!-- 懒加载 -->
    sandbox="allow-scripts"   <!-- 安全沙箱，限制iframe中的操作 -->
    referrerpolicy="no-referrer"  <!-- 引用策略 -->
></iframe>
```

### 补充八：无障碍（Accessibility）常用属性

```html
<!-- aria-* 属性：帮助屏幕阅读器理解页面 -->
<button aria-label="关闭弹窗">×</button>
<button aria-labelledby="btn-label">保存</button>
<span id="btn-label" hidden>保存当前设置</span>

<div role="alert">这是警告信息</div>
<div role="dialog" aria-modal="true">弹窗内容</div>

<!-- 描述关系 -->
<input type="text" aria-describedby="help-text">
<span id="help-text">请输入您的用户名</span>

<!-- 状态 -->
<div aria-live="polite">动态更新的内容</div>  <!-- polite：等当前读完再读 -->
<div aria-live="assertive">重要通知</div>     <!-- assertive：立即打断阅读 -->

<!-- 隐藏（对屏幕阅读器也隐藏） -->
<div aria-hidden="true">纯装饰内容</div>
```

### 补充九：下载与媒体属性

```html
<!-- 下载链接（直接下载文件，而不是在浏览器中打开） -->
<a href="document.pdf" download>下载PDF文档</a>
<a href="document.pdf" download="新文件名.pdf">下载并重命名</a>

<!-- 图片懒加载 -->
<img src="image.jpg" alt="图片" loading="lazy">

<!-- 视频自动播放（静音） -->
<video src="video.mp4" autoplay muted playsinline>
<!-- playsinline：在移动端避免全屏播放 -->

<!-- 视频/音频预加载策略 -->
<video src="video.mp4" preload="metadata">
<!-- preload: none（不预加载）, metadata（只加载元数据）, auto（尽可能多加载） -->
```

### 补充十：HTML 最佳实践总结

1. **DOCTYPE 必须写**：第一行必须是 `<!DOCTYPE html>`
2. **字符编码必须有**：`<meta charset="UTF-8">` 要放在 `<head>` 最前面
3. **viewport 移动端适配**：不要忘记写
4. **语义化标签**：优先使用 `<header>、<nav>、<main>、<article>` 等，而不是全部用 `<div>`
5. **图片一定要写 alt**：有利于SEO和无障碍访问
6. **链接描述有意义**：不要用"点击这里"，用"查看产品详情"等
7. **使用正确的标题层级**：h1 → h2 → h3，不要跳级
8. **表单 label 要关联**：使用 `for` 属性关联 `id`
9. **避免内联样式**：用 class 代替 style
10. **及时关闭标签**：嵌套正确，保持结构清晰
11. **注释不要太少也不要太多**：关键部分写注释
12. **考虑性能**：不要嵌入过大的图片或视频，使用响应式图片

---
