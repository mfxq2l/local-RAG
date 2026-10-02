以下是在原《C / Python 打包命令速查》基础上，加入 **Java** 与 **Rust** 打包方式的完整版。

---

# C / Python / Java / Rust 打包命令速查

## 一、C 语言编译（gcc）

### 基础编译

```cmd
gcc -o 输出.exe 源文件.c
```

### 常用编译选项

```cmd
gcc -O2 -o 输出.exe 源文件.c -mwindows
```

| 选项 | 说明 |
|------|------|
| `-O2` | 二级优化，提升运行速度 |
| `-O3` | 三级优化，极致速度（体积变大） |
| `-Os` | 优化体积 |
| `-mwindows` | 不显示命令行黑窗 |
| `-static` | 静态链接，不依赖 DLL |
| `-lwinmm` | 链接多媒体库 |
| `-lcomctl32` | 链接通用控件库 |
| `-lgdi32` | 链接图形库 |
| `-luser32` | 链接窗口库 |
| `-Wall` | 显示所有警告 |
| `-g` | 生成调试信息 |
| `-s` | 剥离符号表（减小体积） |

### 体积精简进阶选项

| 选项 | 说明 |
|------|------|
| `-ffunction-sections` | 将每个函数放在单独的 section 中 |
| `-fdata-sections` | 将每个数据项放在单独的 section 中 |
| `-Wl,--gc-sections` | 链接时回收未使用的 section，删除无用代码 |

完整最小体积命令：

```cmd
gcc -Os -ffunction-sections -fdata-sections -Wl,--gc-sections -static -s -o out.exe in.c -mwindows
```

> 注意：`-fdata-sections` 在某些 MinGW 版本下可能因额外 `.data` section 反而增大体积，建议实际测试后再决定。

### 完整示例

```cmd
gcc -O2 -static -s -o myapp.exe main.c -mwindows -lwinmm -lcomctl32
```

---

## 二、Python 打包（PyInstaller）

### 安装

```cmd
pip install pyinstaller
```

### 基础打包

```cmd
pyinstaller --onefile 脚本.py
```

### 常用选项

```cmd
pyinstaller --onefile --noconsole --icon=图标.ico 脚本.py
```

| 选项 | 说明 |
|------|------|
| `--onefile` | 打包成单个 exe 文件 |
| `--noconsole` | 不显示命令行窗口 |
| `--console` | 显示命令行窗口（调试用） |
| `--icon=file.ico` | 设置 exe 图标 |
| `--name=名称` | 指定输出文件名 |
| `--add-data=源;目标` | 添加额外文件 |
| `--hidden-import=模块名` | 强制包含隐藏依赖 |
| `--exclude-module=模块名` | 排除不需要的模块 |
| `--upx-dir=路径` | 使用 UPX 压缩 |
| `--noupx` | 不使用压缩 |
| `--clean` | 清理临时文件 |
| `--log-level=ERROR` | 只显示错误信息 |

### 高级选项

| 选项 | 说明 |
|------|------|
| `--onedir` | 生成文件夹而非单文件，启动更快，AV 误报更低 |
| `--collect-submodules=包名` | 收集某包的所有子模块，解决动态导入问题 |
| `--collect-data=包名` | 收集某包的数据文件 |
| `--collect-all=包名` | 收集包的所有内容（最完整） |
| `--runtime-hook=脚本.py` | 程序启动前执行的钩子脚本 |
| `--splash=图片.png` | 显示启动画面（PyInstaller 4.1+） |
| `--upx-exclude=文件` | 排除某些 DLL 不被 UPX 压缩 |
| `-O` / `-OO` | Python 优化级别（移除断言/文档字符串） |
| `--strip` | 剥离调试符号（Linux/macOS） |
| `--key=密钥` | 字节码加密（⚠️ 非强加密） |
| `--version-file=文件` | Windows 版本信息文件 |
| `--manifest=文件` | Windows 应用清单文件 |
| `--uac-admin` | 要求管理员权限运行 |

### 输出位置

- 打包成功后在 `dist\` 文件夹找到 exe
- 临时文件在 `build\` 文件夹
- 配置文件在 `*.spec` 文件

### 使用 spec 文件自定义打包

```cmd
pyi-makespec 脚本.py
```

生成 spec 后，直接运行：

```cmd
pyinstaller 脚本.spec
```

---

## 三、Python 打包工具横向对比

| 工具 | 编译机制 | 运行速度 | 启动速度 | 打包速度 | 体积 | 安全/反编译 | 适用场景 |
|------|----------|----------|----------|----------|------|------------|----------|
| **PyInstaller** | 打包解释器 | 与 CPython 相同 | 较慢（onefile） | 快（1-3 分钟） | 大 | 弱 | 快速部署、日常使用 |
| **Nuitka** | Python→C++→二进制 | 提升 2-4 倍 | 快（无解包） | 慢（10-30 分钟） | 中 | 强 | 性能敏感、代码保护 |
| **cx_Freeze** | 冻结为可执行文件 | 正常 | 较快 | 较快 | 中 | 中 | 精细控制依赖、跨平台 |
| **PyOxidizer** | 嵌入 Python 解释器 | 正常 | 较快 | 中 | 中 | 中 | Rust 生态、嵌入式场景 |
| **Briefcase** | 打包为原生应用 | 正常 | 快 | 中 | 中 | 中 | 跨平台 GUI、MSI/AppImage |

### Nuitka 详细使用

```cmd
pip install nuitka

# 独立文件夹模式（推荐）
python -m nuitka --standalone myapp.py

# 单文件模式
python -m nuitka --onefile myapp.py

# GUI 程序（无控制台）
python -m nuitka --onefile --windows-disable-console myapp.py
```

| 选项 | 说明 |
|------|------|
| `--standalone` | 生成独立文件夹（含所有依赖） |
| `--onefile` | 生成单个 exe |
| `--windows-disable-console` | 隐藏控制台窗口 |
| `--windows-icon=icon.ico` | 设置 exe 图标 |
| `--include-data-file=源=目标` | 包含数据文件 |
| `--enable-plugin=插件名` | 启用插件（如 numpy、PyQt5） |
| `--follow-imports` | 跟踪导入的模块 |
| `--lto=yes` | 启用链接时优化，加速打包 |
| `--jobs=N` | 并行 C 编译任务数 |
| `--output-dir=dist` | 指定输出目录 |

### cx_Freeze 快速上手

```python
from cx_Freeze import setup, Executable

setup(
    name="MyApp",
    version="1.0",
    executables=[Executable("main.py", base="Win32GUI", icon="icon.ico")],
    options={
        "build_exe": {
            "packages": ["requests"],
            "excludes": ["tkinter", "unittest"],
            "include_files": ["data/"],
        }
    },
)
```

```cmd
python setup.py build
```

---

## 四、Java 打包为 EXE

Java 默认编译为字节码（`.class`）并由 JVM 运行。要生成 `.exe`，主要有四种方式。

### 4.1 Java 打包方案总览

| 方案 | 原理 | 需要 JRE | 启动速度 | 体积 | 适合场景 |
|------|------|----------|----------|------|----------|
| **jpackage** | 捆绑 JRE 的启动器 | 否（自带） | 正常 JVM 速度 | 较大 | 现代 Java 项目，官方支持 |
| **GraalVM Native Image** | AOT 编译为原生码 | **否** | **极快** | 中等 | 性能敏感、无 JRE 环境 |
| **Launch4j / exe4j** | 包装 JAR 为 EXE | 是/可捆绑 | 正常 JVM 速度 | 小（不捆绑）/ 极大（捆绑） | 轻量工具，快速分发 |
| **手动捆绑 JRE** | 自带 JRE + 启动脚本 | 否 | 正常 JVM 速度 | 大 | 完全可控，兼容旧项目 |

---

### 4.2 jpackage（官方推荐，最省心）

`jpackage` 是 JDK 14+ 自带的打包工具。它本身不编译 Java，而是把 JAR 和一个精简版 JRE 打包成一个自包含的 `.exe` 或安装程序。

#### 先用 jlink 生成精简运行时

```cmd
jlink --add-modules java.base,java.desktop --output runtime --strip-debug --no-header-files --no-man-pages --compress=2
```

> 新版 JDK 中 `--compress=2` 可改为 `--compress=zip-6`。

#### 生成 app-image（文件夹形式，内含 exe 启动器）

```cmd
jpackage --type app-image --input . --main-jar myapp.jar --runtime-image runtime --name MyApp --dest dist
```

生成的 `dist\MyApp\MyApp.exe` 就是可执行文件，同目录下自带运行时。

#### 生成 exe 安装程序

```cmd
jpackage --type exe --input . --main-jar myapp.jar --runtime-image runtime --name MyApp --dest dist --win-dir-chooser --win-menu --win-shortcut --icon app.ico
```

常用参数：

| 参数 | 说明 |
|------|------|
| `--type exe` | 生成 Windows 安装程序 |
| `--type app-image` | 生成免安装文件夹 |
| `--input` | 包含 jar 的目录 |
| `--main-jar` | 主 jar 文件名 |
| `--main-class` | 主类（jar 中无 Main-Class 时指定） |
| `--runtime-image` | 指定 jlink 生成的运行时 |
| `--name` | 应用名称 |
| `--dest` | 输出目录 |
| `--icon` | 图标（.ico） |
| `--win-dir-chooser` | 允许用户选择安装目录 |
| `--win-menu` | 添加到开始菜单 |
| `--win-shortcut` | 创建桌面快捷方式 |
| `--win-console` | 显示控制台窗口 |

---

### 4.3 GraalVM Native Image（真·编译为原生 EXE）

GraalVM 的 `native-image` 在构建时进行提前编译（AOT），把 Java 字节码直接编译成独立的原生机器码，生成真正的 `.exe`，**不需要任何 JRE**，启动速度极快。

#### 安装与准备

- 安装 GraalVM（含 `native-image`）
- Windows 下需安装 **Visual Studio 2022 生成工具**（提供 C 编译器）

#### 基础命令

```cmd
native-image -jar myapp.jar
```

或指定主类：

```cmd
native-image -cp target/classes com.example.Main
```

#### Maven 项目

```cmd
mvn -Pnative package
```

需在 `pom.xml` 中配置 `native-maven-plugin`。

#### 处理反射、动态代理、JNI

GraalVM 需要额外配置。可用 agent 自动生成配置：

```cmd
java -agentlib:native-image-agent=config-output-dir=src/main/resources/META-INF/native-image -jar myapp.jar
```

然后重新构建：

```cmd
native-image --no-fallback -jar myapp.jar
```

#### 优缺点

**优点**：启动毫秒级，内存占用低，无 JRE 依赖。
**代价**：构建耗时；反射/动态代理需配置；Windows 下依赖 VS 生成工具；调试较困难。

---

### 4.4 Launch4j / exe4j（包装启动器）

这类工具把 JAR 包装成一个 `.exe` 启动器，运行时仍需要系统有 JRE，或者手动捆绑一个 JRE 目录。

**Launch4j 特点**：
- 开源免费，图形界面配置简单
- 可设置最小/最大 Java 版本
- 找不到 JRE 时可引导用户下载
- 如果捆绑 JRE，体积会急剧膨胀

**exe4j**：商业软件，功能更丰富，适合企业发布。

---

### 4.5 手动捆绑 JRE

用 `jlink` 生成精简 JRE，然后与 JAR 一起分发，并写一个启动脚本或使用 Launch4j 包装。

```cmd
jlink --add-modules java.base --output jre --strip-debug --no-header-files --no-man-pages --compress=2
```

目录结构：

```
MyApp\
  app.jar
  jre\
  MyApp.exe（Launch4j 生成，指向 jre\bin\java.exe）
```

---

## 五、Rust 编译为 EXE

Rust 本身就是编译型语言，默认就生成 `.exe`，不需要任何“打包”工具。

### 5.1 直接编译

```cmd
rustc main.rs          # 生成 main.exe
cargo build --release  # 生成 target\release\你的程序.exe
```

Rust 在 Windows 上默认使用 **MSVC 工具链**（`x86_64-pc-windows-msvc`），需要安装 **Visual Studio C++ 生成工具**来提供链接器和系统库。

---

### 5.2 交叉编译到 Windows

从 Linux/macOS 生成 Windows `.exe`：

```bash
rustup target add x86_64-pc-windows-gnu

# Debian/Ubuntu 安装 MinGW-w64
sudo apt install mingw-w64

cargo build --release --target x86_64-pc-windows-gnu
```

生成的 EXE 在 `target/x86_64-pc-windows-gnu/release/` 下。

也可使用 **cargo-xwin** 简化 MSVC 目标的交叉编译：

```bash
cargo install cargo-xwin
cargo xwin build --release --target x86_64-pc-windows-msvc
```

---

### 5.3 静态链接与体积优化

在 `Cargo.toml` 中加入：

```toml
[profile.release]
opt-level = "z"      # 优化体积
lto = true           # 链接时优化
codegen-units = 1    # 减少并行，提升优化
panic = "abort"      # 移除 panic 展开
strip = true         # 剥离符号
```

要完全静态链接（不依赖 MSVC 运行时 DLL），在 `.cargo/config.toml` 中配置：

```toml
[target.x86_64-pc-windows-msvc]
rustflags = ["-C", "target-feature=+crt-static"]
```

或命令行：

```cmd
set RUSTFLAGS=-C target-feature=+crt-static
cargo build --release
```

---

### 5.4 生成安装包

| 工具 | 说明 |
|------|------|
| **cargo-wix** | 生成 WiX MSI 安装包 |
| **cargo-bundle** | 主要面向 macOS，也可用于其他平台 |
| **cargo-packager** | 跨平台打包工具，支持 exe、msi、dmg 等 |
| **Inno Setup** | 手动编写脚本，生成 Windows 安装程序 |

cargo-wix 示例：

```cmd
cargo install cargo-wix
cargo wix init
cargo wix
```

---

### 5.5 Rust 常见问题

| 问题 | 解决方法 |
|------|----------|
| 缺少 `link.exe` | 安装 Visual Studio C++ 生成工具 |
| 交叉编译缺少 `x86_64-w64-mingw32-gcc` | 安装 `mingw-w64` |
| 体积过大 | 使用 `opt-level="z"`、`lto`、`strip`、UPX |
| 运行提示缺少 `VCRUNTIME140.dll` | 启用 `+crt-static` 静态链接 |
| 杀毒误报 | 添加图标、版本信息、代码签名 |

---

## 六、批量打包脚本

保存为 `pack.bat`，把文件拖进去自动处理：

```batch
@echo off
chcp 65001 >nul
if "%~1"=="" (echo 拖入文件&pause&exit/b)

if /i "%~x1"==".c" (
    gcc -O2 -static -s "%~f1" -o "%~dp1%~n1.exe" -mwindows
    if %errorlevel%==0 (echo 成功: %~dp1%~n1.exe) else (echo 编译失败)
)

if /i "%~x1"==".py" (
    pyinstaller --onefile --noconsole --clean "%~f1"
    if %errorlevel%==0 (echo 成功: %~dp1dist\%~n1.exe) else (echo 打包失败)
)

if /i "%~x1"==".rs" (
    rustc -O "%~f1" -o "%~dp1%~n1.exe"
    if %errorlevel%==0 (echo 成功: %~dp1%~n1.exe) else (echo 编译失败)
)

pause
```

> Java 不建议用拖拽脚本直接打包，推荐使用 Maven / Gradle 构建 JAR 后，再用 `jpackage` 或 `native-image` 处理。

---

## 七、UPX 压缩（减小体积）

### 下载

https://github.com/upx/upx/releases

### 使用

```cmd
# 单独压缩
upx --best --ultra-brute 程序.exe

# PyInstaller 集成
pyinstaller --onefile --upx-dir=C:\upx 脚本.py

# C 语言先编译再压缩
gcc -O2 -o app.exe app.c
upx --best --ultra-brute app.exe

# Rust 编译后压缩
cargo build --release
upx --best --lzma target\release\app.exe
```

| UPX 选项 | 说明 |
|----------|------|
| `--best` | 最好压缩比 |
| `--ultra-brute` | 极端压缩（慢） |
| `--lzma` | LZMA 算法（体积最小） |
| `--no-compress` | 不压缩 |

> Java 的 jpackage 启动器可压缩；GraalVM 原生 exe 也可压缩。注意排除关键 DLL。

---

## 八、资源文件嵌入（C 语言）

### 创建资源文件 `resource.rc`

```rc
1 ICON "icon.ico"

1 VERSIONINFO
FILEVERSION 1,0,0,0
PRODUCTVERSION 1,0,0,0
FILEOS 0x40004L
FILETYPE 0x1L
BEGIN
    BLOCK "StringFileInfo"
    BEGIN
        BLOCK "040904b0"
        BEGIN
            VALUE "CompanyName", "My Company"
            VALUE "FileDescription", "My Application"
            VALUE "FileVersion", "1.0.0.0"
            VALUE "ProductName", "My Product"
            VALUE "OriginalFilename", "app.exe"
        END
    END
    BLOCK "VarFileInfo"
    BEGIN
        VALUE "Translation", 0x409, 1200
    END
END
```

### 编译资源

```cmd
windres resource.rc -o resource.o
```

### 链接资源

```cmd
gcc -o app.exe main.c resource.o -mwindows
```

---

## 九、代码签名与杀毒软件误报

### 为什么会被误报

PyInstaller 打包的 exe、UPX 压缩的程序、部分 Java 启动器经常被杀毒软件误报，主要原因：

1. PyInstaller 的 bootloader 结构类似某些恶意软件的自解压行为
2. UPX 的压缩壳被大量恶意软件使用
3. 单文件模式在运行时解压到临时目录，行为类似释放器

### 降低误报的方法

| 方法 | 效果 |
|------|------|
| 使用 `--onedir` 替代 `--onefile` | 避免内存解压行为，显著降低误报 |
| 禁用 UPX（`--noupx`） | UPX 压缩壳是杀软重点检测对象 |
| 添加图标和版本信息 | 使 exe 更像正规软件 |
| 申请代码签名证书并签名 | 最有效的方法，显著提升信任度 |
| 向微软提交应用获取信誉 | 逐步积累 SmartScreen 信誉 |
| 避免使用 `--key` 加密 | 加密后的二进制更容易触发启发式检测 |

### 代码签名命令

```cmd
signtool sign /fd SHA256 /a /tr http://timestamp.digicert.com /td SHA256 "C:\path\to\yourfile.exe"
```

| 参数 | 说明 |
|------|------|
| `/fd SHA256` | 文件摘要算法 |
| `/a` | 自动选择最佳证书 |
| `/tr URL` | 时间戳服务器地址 |
| `/td SHA256` | 时间戳摘要算法 |
| `/f 证书.pfx` | 指定证书文件 |
| `/p 密码` | 证书密码 |

验证签名：

```cmd
signtool verify /v /pa "C:\path\to\yourfile.exe"
```

> Java 的 jpackage 生成的 exe、Rust 生成的 exe 均可使用同一命令签名。

---

## 十、二进制依赖与 DLL 排查

### 查看 exe 依赖的 DLL

```cmd
dumpbin /DEPENDENTS 程序.exe
```

或使用开源的 Dependencies 工具图形化查看。

### 常见缺少 DLL 的原因

| 现象 | 原因 | 解决方法 |
|------|------|----------|
| 缺少 `VCRUNTIME140.dll` | 目标机器未安装 VC++ 运行库 | C 程序加 `-static`；Rust 启用 `+crt-static`；Python 建议让用户安装 VC++ Redistributable |
| 缺少 `python3xx.dll` | Python 解释器未打包完整 | 使用 `--hidden-import` 或 `--collect-all` 强制包含 |
| 缺少 Qt 相关 DLL | PyQt/PySide 插件未收集 | 使用 `--collect-all PyQt5` 或 `--collect-all PySide6` |
| 缺少 JRE | Java 程序未捆绑运行时 | 使用 jpackage 捆绑 JRE，或 GraalVM 原生编译 |
| 报错 `0x8007007E` | DLL 模块找不到或架构不匹配 | 检查 32/64 位一致性 |

---

## 十一、常见问题

| 问题 | 解决方法 |
|------|----------|
| `gcc` 不是内部命令 | 安装 MinGW 并添加到 PATH |
| `pyinstaller` 不是内部命令 | `pip install pyinstaller` |
| 打包后闪退 | 去掉 `--noconsole` 看错误信息 |
| 文件太大 | 用虚拟环境+排除模块+UPX 压缩，或换 C / Nuitka / Rust |
| 缺少 DLL | C 加 `-static`；Rust 加 `+crt-static` |
| Python 打包慢 | 加 `--clean`；Nuitka 可用 `--lto=yes` |
| 杀毒软件报毒 | 使用 `--onedir`、禁用 UPX、添加数字签名 |
| 图标不显示 | 使用 `.ico` 格式，不能用 `.png` |
| 中文路径报错 | 把文件移到英文路径 |
| 启动速度慢 | Python 用 `--onedir`；Java 用 GraalVM；Rust 天然快 |
| 动态导入的模块找不到 | `--hidden-import` 或 `--collect-submodules` |
| `ModuleNotFoundError` | `--hidden-import=模块名` |
| 资源文件找不到 | 使用 `sys._MEIPASS` 获取临时解压路径 |
| Java 打包后提示找不到 JRE | 使用 jpackage 捆绑 JRE，或 GraalVM 原生编译 |
| GraalVM 反射报错 | 配置 `reflect-config.json` 或使用 agent 生成 |
| Rust 编译缺少 `link.exe` | 安装 Visual Studio C++ 生成工具 |
| Rust 交叉编译失败 | 安装 `mingw-w64` 或使用 `cargo-xwin` |

---

## 十二、快速参考卡片

### C 语言（最小体积）

```cmd
gcc -Os -ffunction-sections -fdata-sections -Wl,--gc-sections -static -s -o out.exe in.c -mwindows
```

### C 语言（最快速度）

```cmd
gcc -O3 -static -o out.exe in.c -mwindows
```

### Python（最小体积）

```cmd
pyinstaller --onefile --noconsole --exclude-module=tkinter --exclude-module=matplotlib --strip -O in.py
```

### Python（最快打包）

```cmd
pyinstaller --onefile --noconsole --clean --log-level=ERROR in.py
```

### Python（最佳运行性能，推荐 Nuitka）

```cmd
nuitka --onefile --windows-disable-console --lto=yes --enable-plugin=numpy app.py
```

### Python（最佳兼容性，推荐 onedir）

```cmd
pyinstaller --onedir --noconsole --clean 脚本.py
```

### Java（官方 jpackage）

```cmd
jlink --add-modules java.base,java.desktop --output runtime --strip-debug --no-header-files --no-man-pages --compress=2

jpackage --type exe --input . --main-jar app.jar --runtime-image runtime --name MyApp --win-dir-chooser --win-menu --win-shortcut --icon app.ico
```

### Java（GraalVM 原生编译）

```cmd
native-image -jar app.jar
```

### Rust（直接编译）

```cmd
cargo build --release
```

### Rust（交叉编译到 Windows）

```cmd
rustup target add x86_64-pc-windows-gnu
cargo build --release --target x86_64-pc-windows-gnu
```

### Rust（静态链接 + 体积优化）

```cmd
set RUSTFLAGS=-C target-feature=+crt-static
cargo build --release
```

### 代码签名

```cmd
signtool sign /fd SHA256 /a /tr http://timestamp.digicert.com /td SHA256 程序.exe
```