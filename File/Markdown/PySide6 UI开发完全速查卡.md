
# 🎨 PySide6 UI开发完全速查卡

## 📖 目录
1. [环境搭建](#1-环境搭建)
2. [核心概念](#2-核心概念)
3. [基础控件](#3-基础控件)
4. [布局管理器](#4-布局管理器)
5. [高级控件](#5-高级控件)
6. [QSS样式表](#6-qss样式表)
7. [信号与槽](#7-信号与槽)
8. [多线程](#8-多线程)
9. [事件处理](#9-事件处理)
10. [窗口美化](#10-窗口美化)
11. [打包发布](#11-打包发布)
12. [常见问题](#12-常见问题)

---

## 1. 环境搭建

### 安装
```bash
# 安装PySide6
pip install PySide6

# 安装打包工具
pip install pyinstaller

# 安装其他常用库
pip install mutagen pygame pillow
```

### 基础模板
```python
import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        # 窗口设置
        self.setWindowTitle("我的应用")
        self.setGeometry(100, 100, 800, 600)  # x, y, width, height
        # 或者
        self.resize(800, 600)  # 只设置大小
        self.move(100, 100)    # 只设置位置
        
        # 中央控件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 布局
        layout = QVBoxLayout(central_widget)
        
        # 添加控件
        label = QLabel("Hello World!")
        layout.addWidget(label)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
```

---

## 2. 核心概念

### 2.1 继承关系
```
QObject (所有对象的基类)
    └── QWidget (所有UI组件的基类)
        ├── QMainWindow (主窗口)
        ├── QDialog (对话框)
        ├── QLabel (标签)
        ├── QPushButton (按钮)
        ├── QLineEdit (输入框)
        └── ... (所有其他控件)
```

### 2.2 三种窗口类型
```python
# 1. QMainWindow - 主窗口（带菜单栏、工具栏、状态栏）
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # 菜单栏
        menubar = self.menuBar()
        file_menu = menubar.addMenu("文件")
        # 工具栏
        toolbar = self.addToolBar("工具栏")
        # 状态栏
        statusbar = self.statusBar()
        statusbar.showMessage("就绪")

# 2. QWidget - 独立的窗口或控件
class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        # 直接用

# 3. QDialog - 对话框（有确定/取消按钮）
class MyDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setModal(True)  # 模态对话框
```

### 2.3 窗口标志
```python
# 常用窗口标志
self.setWindowFlags(
    Qt.FramelessWindowHint |      # 无边框
    Qt.WindowStaysOnTopHint |      # 置顶
    Qt.WindowCloseButtonHint |     # 有关闭按钮
    Qt.WindowMinimizeButtonHint |  # 有最小化按钮
    Qt.WindowMaximizeButtonHint    # 有最大化按钮
)

# 透明背景
self.setAttribute(Qt.WA_TranslucentBackground)

# 窗口透明度
self.setWindowOpacity(0.9)  # 0.0-1.0
```

---

## 3. 基础控件

### 3.1 QLabel - 标签
```python
label = QLabel("文本内容")

# 常用方法
label.setText("新文本")
label.text()                    # 获取文本
label.setAlignment(Qt.AlignCenter)  # 居中
label.setWordWrap(True)         # 自动换行
label.setPixmap(QPixmap("image.png"))  # 显示图片
label.setScaledContents(True)   # 图片自适应
label.setStyleSheet("color: red; font-size: 20px;")

# 对齐方式
Qt.AlignLeft | Qt.AlignRight | Qt.AlignCenter
Qt.AlignTop | Qt.AlignBottom | Qt.AlignVCenter
Qt.AlignJustify  # 两端对齐
```

### 3.2 QPushButton - 按钮
```python
btn = QPushButton("点击我")

# 常用方法
btn.setText("新文本")
btn.setEnabled(False)           # 禁用
btn.setCheckable(True)          # 可切换状态
btn.setChecked(True)            # 选中状态
btn.isChecked()                 # 是否选中
btn.setIcon(QIcon("icon.png"))  # 设置图标
btn.setShortcut("Ctrl+S")       # 快捷键
btn.clicked.connect(on_click)   # 点击信号
btn.pressed.connect(on_press)   # 按下信号
btn.released.connect(on_release)# 释放信号
btn.toggled.connect(on_toggle)  # 切换信号（checkable时）
```

### 3.3 QLineEdit - 单行输入框
```python
line = QLineEdit()

# 常用方法
line.setText("默认文本")
line.text()                     # 获取文本
line.setPlaceholderText("请输入...")  # 占位符
line.setEchoMode(QLineEdit.Password)  # 密码模式
line.setMaxLength(50)           # 最大长度
line.setReadOnly(True)          # 只读
line.setClearButtonEnabled(True) # 显示清除按钮
line.textChanged.connect(on_change)  # 文本改变信号
line.returnPressed.connect(on_enter) # 回车信号

# Echo模式
QLineEdit.Normal    # 正常显示
QLineEdit.Password  # 密码模式
QLineEdit.NoEcho    # 不显示
QLineEdit.PasswordEchoOnEdit  # 编辑时显示
```

### 3.4 QTextEdit - 多行文本框
```python
text = QTextEdit()

# 常用方法
text.setPlainText("纯文本")
text.setHtml("<h1>HTML内容</h1>")
text.toPlainText()              # 获取纯文本
text.toHtml()                   # 获取HTML
text.clear()
text.setReadOnly(True)
text.textChanged.connect(on_change)

# 常用操作
text.append("追加文本")
text.insertPlainText("插入")
text.undo()                     # 撤销
text.redo()                     # 重做
text.selectAll()
text.copy()
text.paste()
```

### 3.5 QComboBox - 下拉框
```python
combo = QComboBox()

# 添加选项
combo.addItem("选项1")
combo.addItems(["选项2", "选项3"])
combo.insertItem(0, "选项0")   # 指定位置插入

# 常用方法
combo.currentText()             # 当前文本
combo.currentIndex()            # 当前索引
combo.setCurrentIndex(1)        # 设置选中
combo.clear()
combo.count()                   # 选项数量
combo.itemText(0)               # 获取指定选项文本
combo.currentTextChanged.connect(on_change)  # 文本改变信号
combo.activated.connect(on_activate)         # 激活信号
```

### 3.6 QCheckBox - 复选框
```python
check = QCheckBox("选项")

# 常用方法
check.setChecked(True)          # 选中
check.isChecked()               # 是否选中
check.setTristate(True)         # 三态模式（部分选中）
check.setCheckState(Qt.Checked) # 设置状态
check.stateChanged.connect(on_change)  # 状态改变信号

# 状态常量
Qt.Unchecked    # 0 - 未选中
Qt.PartiallyChecked  # 1 - 部分选中
Qt.Checked      # 2 - 选中
```

### 3.7 QRadioButton - 单选按钮
```python
# 需要放在按钮组中实现互斥
radio1 = QRadioButton("选项1")
radio2 = QRadioButton("选项2")

# 按钮组
group = QButtonGroup()
group.addButton(radio1, 1)  # 第二个参数是ID
group.addButton(radio2, 2)
group.buttonClicked.connect(on_click)  # 按钮点击信号
group.checkedId()  # 获取选中的ID

# 常用方法
radio1.isChecked()
radio1.setChecked(True)
radio1.toggled.connect(on_toggle)  # 切换信号
```

### 3.8 QSlider - 滑块
```python
slider = QSlider(Qt.Horizontal)  # 水平滑块
slider = QSlider(Qt.Vertical)    # 垂直滑块

# 常用方法
slider.setMinimum(0)
slider.setMaximum(100)
slider.setValue(50)
slider.value()                  # 获取值
slider.setTickInterval(10)      # 刻度间隔
slider.setTickPosition(QSlider.TicksBelow)  # 刻度位置
slider.setPageStep(10)          # 翻页步长
slider.setSingleStep(1)         # 单步步长
slider.valueChanged.connect(on_change)  # 值改变信号
slider.sliderMoved.connect(on_move)     # 拖动信号
```

### 3.9 QProgressBar - 进度条
```python
progress = QProgressBar()

# 常用方法
progress.setRange(0, 100)       # 设置范围
progress.setValue(50)           # 设置值
progress.value()                # 获取值
progress.reset()                # 重置
progress.setMinimum(0)
progress.setMaximum(100)
progress.setTextVisible(True)   # 显示文本
progress.setFormat("%p%")       # 显示格式
# %p - 百分比, %v - 当前值, %m - 最大值

progress.setStyleSheet("""
    QProgressBar::chunk {
        background: red;
        border-radius: 5px;
    }
""")
```

---

## 4. 布局管理器

### 4.1 QVBoxLayout - 垂直布局
```python
layout = QVBoxLayout()

# 常用方法
layout.addWidget(widget)        # 添加控件
layout.addLayout(other_layout)  # 添加子布局
layout.addStretch()             # 添加弹性空间（弹簧）
layout.setSpacing(10)           # 间距
layout.setContentsMargins(10, 10, 10, 10)  # 边距
layout.insertWidget(0, widget)  # 插入到指定位置

# 添加参数
layout.addWidget(widget, stretch=1)  # stretch=1 表示拉伸比例
layout.addWidget(widget, alignment=Qt.AlignCenter)  # 对齐方式
```

### 4.2 QHBoxLayout - 水平布局
```python
layout = QHBoxLayout()
# 方法同 QVBoxLayout
layout.addStretch()
```

### 4.3 QGridLayout - 网格布局
```python
layout = QGridLayout()

# 添加控件 (row, column, rowspan, colspan)
layout.addWidget(widget, 0, 0)           # 第0行第0列
layout.addWidget(widget, 0, 1)           # 第0行第1列
layout.addWidget(widget, 0, 0, 1, 2)     # 跨2列
layout.addWidget(widget, 0, 0, 2, 1)     # 跨2行

# 设置行列比例
layout.setRowStretch(0, 1)               # 第0行拉伸比例
layout.setColumnStretch(0, 1)            # 第0列拉伸比例
```

### 4.4 QFormLayout - 表单布局
```python
layout = QFormLayout()

# 添加行
layout.addRow("名称:", QLineEdit())
layout.addRow("年龄:", QSpinBox())
layout.addRow(QLabel("备注:"), QTextEdit())

# 插入行
layout.insertRow(0, "ID:", QLineEdit())

# 获取行数
layout.rowCount()
```

### 4.5 布局嵌套示例
```python
# 复杂布局
main_layout = QVBoxLayout()

# 顶部
header = QHBoxLayout()
header.addWidget(QLabel("标题"))
header.addStretch()
header.addWidget(QPushButton("按钮"))

# 中间
content = QGridLayout()
content.addWidget(QLabel("内容"), 0, 0, 1, 2)

# 底部
footer = QHBoxLayout()
footer.addWidget(QPushButton("确定"))
footer.addWidget(QPushButton("取消"))

main_layout.addLayout(header)
main_layout.addLayout(content)
main_layout.addLayout(footer)

# 也可以设置拉伸因子
main_layout.addLayout(header, stretch=0)   # 不拉伸
main_layout.addLayout(content, stretch=1)  # 拉伸
main_layout.addLayout(footer, stretch=0)   # 不拉伸
```

---

## 5. 高级控件

### 5.1 QTableWidget - 表格
```python
table = QTableWidget()

# 设置行列数
table.setRowCount(10)
table.setColumnCount(5)

# 设置表头
table.setHorizontalHeaderLabels(["列1", "列2", "列3", "列4", "列5"])
table.setVerticalHeaderLabels(["行1", "行2", "行3", ...])

# 添加数据
item = QTableWidgetItem("内容")
table.setItem(row, col, item)

# 常用方法
table.currentItem()              # 当前选中的项
table.currentRow()               # 当前行
table.currentColumn()            # 当前列
table.sortItems(0, Qt.AscendingOrder)  # 排序
table.clearContents()            # 清空内容
table.clear()                    # 清空全部

# 设置选择模式
table.setSelectionBehavior(QAbstractItemView.SelectRows)  # 选择整行
table.setSelectionMode(QAbstractItemView.MultiSelection)  # 多选

# 自动调整
table.resizeColumnsToContents()
table.resizeRowsToContents()

# 右键菜单
table.setContextMenuPolicy(Qt.CustomContextMenu)
table.customContextMenuRequested.connect(self.show_menu)

def show_menu(self, pos):
    menu = QMenu()
    menu.addAction("操作1")
    menu.addAction("操作2")
    menu.exec(self.table.mapToGlobal(pos))
```

### 5.2 QListWidget - 列表
```python
list_widget = QListWidget()

# 添加项目
list_widget.addItem("项目1")
list_widget.addItems(["项目2", "项目3"])

# 自定义项目
item = QListWidgetItem("自定义项目")
item.setForeground(QColor(255, 0, 0))  # 文字颜色
item.setBackground(QColor(0, 0, 0))    # 背景颜色
item.setCheckState(Qt.Checked)         # 复选框
list_widget.addItem(item)

# 常用方法
list_widget.currentItem()           # 当前项
list_widget.currentRow()            # 当前行号
list_widget.count()                 # 项目数量
list_widget.takeItem(row)           # 移除项目
list_widget.clear()
list_widget.itemClicked.connect(on_click)
list_widget.currentTextChanged.connect(on_change)

# 模式
list_widget.setSelectionMode(QAbstractItemView.MultiSelection)
```

### 5.3 QTreeWidget - 树形
```python
tree = QTreeWidget()

# 设置列
tree.setColumnCount(2)
tree.setHeaderLabels(["名称", "值"])

# 添加根节点
root = QTreeWidgetItem(tree)
root.setText(0, "根节点")

# 添加子节点
child = QTreeWidgetItem(root)
child.setText(0, "子节点1")
child.setText(1, "值1")

# 常用方法
tree.currentItem()
tree.topLevelItemCount()
tree.clear()
tree.itemClicked.connect(on_click)

# 展开/折叠
root.setExpanded(True)
```

### 5.4 QTabWidget - 标签页
```python
tabs = QTabWidget()

# 添加页面
page1 = QWidget()
page2 = QWidget()
tabs.addTab(page1, "标签1")
tabs.addTab(page2, "标签2")

# 插入页面
tabs.insertTab(0, page, "新标签")

# 常用方法
tabs.currentIndex()             # 当前页索引
tabs.currentWidget()            # 当前页控件
tabs.setCurrentIndex(0)
tabs.setCurrentWidget(page1)
tabs.removeTab(0)
tabs.clear()
tabs.currentChanged.connect(on_change)

# 设置样式
tabs.setTabsClosable(True)      # 可关闭
tabs.setMovable(True)           # 可移动
tabs.setDocumentMode(True)      # 文档模式
```

### 5.5 QScrollArea - 滚动区域
```python
scroll = QScrollArea()

# 设置内容
content = QWidget()
layout = QVBoxLayout(content)
# ... 添加大量内容
scroll.setWidget(content)
scroll.setWidgetResizable(True)  # 内容自适应

# 滚动条策略
scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
```

### 5.6 QDockWidget - 停靠窗口
```python
dock = QDockWidget("标题")

# 添加内容
content = QListWidget()
dock.setWidget(content)

# 添加到主窗口
self.addDockWidget(Qt.LeftDockWidgetArea, dock)

# 可停靠区域
dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

# 可浮动
dock.setFloating(True)
dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable)
```

### 5.7 QMenu / QMenuBar - 菜单
```python
# 菜单栏
menubar = self.menuBar()

# 添加菜单
file_menu = menubar.addMenu("文件")
edit_menu = menubar.addMenu("编辑")

# 添加动作
open_action = QAction("打开", self)
open_action.setShortcut("Ctrl+O")
open_action.triggered.connect(self.open_file)
file_menu.addAction(open_action)

# 添加分隔线
file_menu.addSeparator()

# 子菜单
sub_menu = QMenu("子菜单")
sub_menu.addAction("选项1")
file_menu.addMenu(sub_menu)

# 右键菜单
def contextMenuEvent(self, event):
    menu = QMenu(self)
    menu.addAction("操作1")
    menu.addAction("操作2")
    menu.exec(event.globalPos())
```

### 5.8 QMessageBox - 消息框
```python
# 信息框
QMessageBox.information(self, "标题", "消息内容")

# 警告框
QMessageBox.warning(self, "警告", "警告内容")

# 错误框
QMessageBox.critical(self, "错误", "错误内容")

# 询问框
reply = QMessageBox.question(self, "确认", "确定要删除吗？",
                              QMessageBox.Yes | QMessageBox.No)
if reply == QMessageBox.Yes:
    # 执行操作

# 自定义按钮
msg_box = QMessageBox()
msg_box.setWindowTitle("标题")
msg_box.setText("内容")
msg_box.setIcon(QMessageBox.Information)
msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
msg_box.setDefaultButton(QMessageBox.Ok)
reply = msg_box.exec()
```

### 5.9 QFileDialog - 文件对话框
```python
# 选择文件
file_path, _ = QFileDialog.getOpenFileName(
    self, "选择文件", 
    os.path.expanduser("~"),  # 起始目录
    "文本文件 (*.txt);;所有文件 (*.*)"
)

# 选择多个文件
file_paths, _ = QFileDialog.getOpenFileNames(
    self, "选择文件", 
    os.path.expanduser("~"),
    "图片文件 (*.png *.jpg);;所有文件 (*.*)"
)

# 选择目录
dir_path = QFileDialog.getExistingDirectory(
    self, "选择目录",
    os.path.expanduser("~")
)

# 保存文件
file_path, _ = QFileDialog.getSaveFileName(
    self, "保存文件",
    os.path.join(os.path.expanduser("~"), "未命名.txt"),
    "文本文件 (*.txt)"
)
```

### 5.10 QDialog - 自定义对话框
```python
class MyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle("自定义对话框")
        self.resize(400, 300)
        
        layout = QVBoxLayout()
        
        # 内容
        layout.addWidget(QLabel("输入内容:"))
        self.input = QLineEdit()
        layout.addWidget(self.input)
        
        # 按钮
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def get_value(self):
        return self.input.text()

# 使用
dialog = MyDialog(self)
if dialog.exec() == QDialog.Accepted:
    value = dialog.get_value()
    print(value)
```

---

## 6. QSS样式表

### 6.1 基本语法
```css
/* 选择器 { 属性: 值; } */

/* 类选择器（推荐） */
QPushButton {
    background-color: red;
    color: white;
    border-radius: 5px;
}

/* ID选择器 */
#myButton {
    background-color: blue;
}

/* 伪状态 */
QPushButton:hover {
    background-color: darkred;
}
QPushButton:pressed {
    background-color: #800000;
}
QPushButton:disabled {
    background-color: #cccccc;
}
```

### 6.2 常用属性
```css
/* 背景 */
background-color: red;
background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #ff0000, stop:1 #00ff00);
background: qradialgradient(cx:0.5,cy:0.5,radius:0.5, stop:0 #ff0000, stop:1 #0000ff);
background: qconicalgradient(cx:0.5,cy:0.5, angle:0, stop:0 #ff0000, stop:1 #0000ff);
background-image: url(:/images/logo.png);
background-repeat: no-repeat;

/* 颜色 */
color: #ffffff;
color: rgba(255, 255, 255, 0.5);

/* 字体 */
font-family: "Microsoft YaHei";
font-size: 14px;
font-weight: bold;
font-style: italic;

/* 边框 */
border: 1px solid #333333;
border-radius: 5px;
border-top-left-radius: 5px;
border-color: red;
border-width: 2px;

/* 边距 */
padding: 5px 10px 5px 10px;
margin: 5px;

/* 大小 */
width: 100px;
height: 30px;
max-width: 200px;
min-height: 20px;

/* 其他 */
opacity: 0.8;
text-align: center;
text-decoration: underline;
```

### 6.3 常用控件样式

```css
/* 主窗口 */
QMainWindow {
    background-color: #1a1a1a;
}

/* 按钮 */
QPushButton {
    background-color: #ec4141;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #d63a3a;
}
QPushButton:pressed {
    background-color: #b33030;
}
QPushButton:disabled {
    background-color: #553333;
    color: #888888;
}

/* 输入框 */
QLineEdit {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    padding: 6px 10px;
    color: white;
}
QLineEdit:focus {
    border-color: #ec4141;
}

/* 文本编辑框 */
QTextEdit {
    background-color: #1a1a1a;
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    color: white;
    padding: 8px;
}

/* 下拉框 */
QComboBox {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    padding: 6px 10px;
    color: white;
}
QComboBox::drop-down {
    border: none;
}
QComboBox::down-arrow {
    image: url(arrow.png);
}
QComboBox QAbstractItemView {
    background-color: #2d2d2d;
    color: white;
    selection-background-color: #ec4141;
}

/* 表格 */
QTableWidget {
    background-color: #141414;
    gridline-color: #1e1e1e;
}
QTableWidget::item {
    padding: 6px;
    color: #dddddd;
}
QTableWidget::item:selected {
    background-color: #3a1a1a;
}
QHeaderView::section {
    background-color: #1a1a1a;
    color: #aaaaaa;
    padding: 6px;
    border: none;
    border-bottom: 1px solid #2a2a2a;
}

/* 滚动条 */
QScrollBar:vertical {
    background: #1a1a1a;
    width: 12px;
    border-radius: 6px;
}
QScrollBar::handle:vertical {
    background: #3a3a3a;
    border-radius: 6px;
}
QScrollBar::handle:vertical:hover {
    background: #5a5a5a;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* 进度条 */
QProgressBar {
    background-color: #1e1e1e;
    border-radius: 4px;
    height: 20px;
    text-align: center;
    color: white;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #ec4141, stop:1 #ff6b6b);
    border-radius: 4px;
}

/* 标签页 */
QTabWidget::pane {
    border: 1px solid #2a2a2a;
    border-radius: 4px;
    background: #141414;
}
QTabBar::tab {
    background: #1a1a1a;
    color: #888888;
    padding: 8px 16px;
    border: 1px solid #2a2a2a;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}
QTabBar::tab:selected {
    background: #141414;
    color: white;
}
QTabBar::tab:hover:!selected {
    background: #2a2a2a;
}

/* 滑块 */
QSlider::groove:horizontal {
    height: 4px;
    background: #2d2d2d;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #ec4141;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}
QSlider::handle:horizontal:hover {
    background: #ff6b6b;
}
QSlider::sub-page:horizontal {
    background: #ec4141;
    border-radius: 2px;
}

/* 菜单 */
QMenu {
    background-color: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 4px;
    padding: 4px;
}
QMenu::item {
    padding: 6px 20px;
    color: white;
}
QMenu::item:selected {
    background-color: #ec4141;
}
```

### 6.4 加载样式表
```python
# 方式1：直接字符串
self.setStyleSheet("QPushButton { background: red; }")

# 方式2：从文件加载
def load_stylesheet(app):
    with open("style.qss", "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())

# 方式3：资源文件
# 先创建资源文件 resource.qrc
<RCC>
    <qresource prefix="/">
        <file>style.qss</file>
    </qresource>
</RCC>
# 编译: pyrcc6 resource.qrc -o resource_rc.py
# 使用: 
import resource_rc
self.setStyleSheet("""
    QPushButton { background: red; }
""")
```

---

## 7. 信号与槽

### 7.1 基本用法
```python
# 内置信号
btn = QPushButton("点击")
btn.clicked.connect(self.on_click)

def on_click(self):
    print("按钮被点击")

# 带参数的信号
line = QLineEdit()
line.textChanged.connect(self.on_text_changed)

def on_text_changed(self, text):
    print(f"文本变为: {text}")

# 多个信号连接同一个槽
btn1.clicked.connect(self.on_any_click)
btn2.clicked.connect(self.on_any_click)

def on_any_click(self):
    sender = self.sender()  # 获取发送信号的控件
    print(f"{sender.text()} 被点击")
```

### 7.2 自定义信号
```python
from PySide6.QtCore import Signal

class MyWidget(QWidget):
    # 定义信号
    my_signal = Signal()  # 无参数
    value_changed = Signal(int)  # 带参数
    data_ready = Signal(str, int)  # 多参数
    
    def __init__(self):
        super().__init__()
        self.btn = QPushButton("发送信号")
        self.btn.clicked.connect(self.emit_signal)
    
    def emit_signal(self):
        self.my_signal.emit()
        self.value_changed.emit(100)
        self.data_ready.emit("数据", 200)

# 使用
widget = MyWidget()
widget.my_signal.connect(lambda: print("收到信号"))
widget.value_changed.connect(lambda v: print(f"值: {v}"))
widget.data_ready.connect(lambda s, i: print(f"{s}: {i}"))
```

### 7.3 信号槽高级用法
```python
# 断开连接
widget.my_signal.disconnect()

# 检查是否连接
widget.my_signal.isConnected()

# 阻塞信号（临时禁用信号）
widget.blockSignals(True)
widget.setValue(100)  # 不会触发信号
widget.blockSignals(False)

# 信号列表
receivers = widget.receivers(SIGNAL("my_signal()"))

# 多线程信号
class Worker(QThread):
    progress = Signal(int)
    
    def run(self):
        for i in range(100):
            self.progress.emit(i)
            self.msleep(100)
```

---

## 8. 多线程

### 8.1 QThread 基本用法
```python
class Worker(QThread):
    finished = Signal()
    progress = Signal(int)
    error = Signal(str)
    
    def __init__(self, data):
        super().__init__()
        self.data = data
    
    def run(self):
        try:
            for i in range(len(self.data)):
                # 耗时操作
                self.msleep(100)  # 模拟工作
                self.progress.emit(int((i+1)/len(self.data)*100))
            
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

# 使用
worker = Worker(data)
worker.progress.connect(self.update_progress)
worker.finished.connect(self.on_finished)
worker.error.connect(self.on_error)
worker.start()

# 清理
worker.quit()
worker.wait()
```

### 8.2 QThread + QObject 方式（推荐）
```python
class Worker(QObject):
    finished = Signal()
    progress = Signal(int)
    
    @Slot()
    def do_work(self):
        for i in range(100):
            self.progress.emit(i)
            QThread.msleep(50)
        self.finished.emit()

# 使用
thread = QThread()
worker = Worker()
worker.moveToThread(thread)

thread.started.connect(worker.do_work)
worker.finished.connect(thread.quit)
worker.finished.connect(worker.deleteLater)
thread.finished.connect(thread.deleteLater)

thread.start()
```

### 8.3 线程安全的数据传递
```python
# 使用信号传递数据（安全）
class Worker(QThread):
    result = Signal(dict)
    
    def run(self):
        data = {"key": "value"}
        self.result.emit(data)

# 使用队列
from queue import Queue

class Worker(QThread):
    def __init__(self, queue):
        super().__init__()
        self.queue = queue
    
    def run(self):
        self.queue.put("data")
```

---

## 9. 事件处理

### 9.1 常用事件
```python
class MyWidget(QWidget):
    # 鼠标事件
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            print(f"左键按下: {event.pos()}")
        elif event.button() == Qt.RightButton:
            print("右键按下")
    
    def mouseReleaseEvent(self, event):
        print(f"鼠标释放: {event.pos()}")
    
    def mouseDoubleClickEvent(self, event):
        print("双击")
    
    def mouseMoveEvent(self, event):
        print(f"鼠标移动: {event.pos()}")
        # 需要开启鼠标追踪
        # self.setMouseTracking(True)
    
    # 键盘事件
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.modifiers() & Qt.ControlModifier:
            if event.key() == Qt.Key_S:
                print("Ctrl+S 按下")
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            print("回车键按下")
    
    # 拖放事件
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            print(f"拖入: {path}")
    
    # 窗口事件
    def showEvent(self, event):
        print("窗口显示")
    
    def hideEvent(self, event):
        print("窗口隐藏")
    
    def closeEvent(self, event):
        reply = QMessageBox.question(self, "确认", "确定退出吗？",
                                      QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
    
    def resizeEvent(self, event):
        print(f"窗口大小改变: {event.size()}")
    
    def moveEvent(self, event):
        print(f"窗口移动: {event.pos()}")
```

### 9.2 事件过滤器
```python
class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.btn = QPushButton("按钮")
        self.btn.installEventFilter(self)  # 安装事件过滤器
    
    def eventFilter(self, obj, event):
        if obj is self.btn:
            if event.type() == QEvent.Enter:
                print("鼠标进入按钮")
                return True  # 事件被处理
        return super().eventFilter(obj, event)
```

---

## 10. 窗口美化

### 10.1 无边框窗口
```python
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # 无边框
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 创建标题栏
        self.title_bar = QWidget()
        self.title_bar.setFixedHeight(35)
        
        # 窗口拖拽
        self.drag_pos = None
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if event.pos().y() <= 35:  # 只在标题栏区域拖拽
                self.drag_pos = event.globalPos()
    
    def mouseMoveEvent(self, event):
        if self.drag_pos:
            delta = event.globalPos() - self.drag_pos
            self.move(self.pos() + delta)
            self.drag_pos = event.globalPos()
    
    def mouseReleaseEvent(self, event):
        self.drag_pos = None
```

### 10.2 窗口阴影
```python
from PySide6.QtWidgets import QGraphicsDropShadowEffect

# 给控件添加阴影
shadow = QGraphicsDropShadowEffect()
shadow.setBlurRadius(15)
shadow.setColor(QColor(0, 0, 0, 150))
shadow.setOffset(0, 2)
widget.setGraphicsEffect(shadow)

# 多个阴影叠加
class ShadowWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 主容器
        container = QWidget(self)
        container.setObjectName("container")
        container.setStyleSheet("""
            #container {
                background: #1a1a1a;
                border-radius: 10px;
            }
        """)
        
        # 阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 5)
        container.setGraphicsEffect(shadow)
```

### 10.3 毛玻璃效果（Windows 11）
```python
import ctypes

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Windows 11 毛玻璃
        self.setStyleSheet("background: rgba(26, 26, 26, 200);")
        
        # 启用毛玻璃（仅Windows 11）
        try:
            from ctypes import wintypes
            # 设置窗口为透明
            hwnd = int(self.winId())
            ctypes.windll.user32.SetWindowCompositionAttribute(
                hwnd, 
                self.get_blur_attr()
            )
        except:
            pass
    
    def get_blur_attr(self):
        # Windows 11 毛玻璃效果
        class WINDOWCOMPOSITIONATTRIBDATA(ctypes.Structure):
            _fields_ = [
                ("Attribute", ctypes.c_int),
                ("Data", ctypes.POINTER(ctypes.c_int)),
                ("Size", ctypes.c_size_t)
            ]
        
        attr = 19  # WCA_ACCENT_POLICY
        accent = 4  # ACCENT_ENABLE_BLURBEHIND
        data = ctypes.c_int(accent)
        return WINDOWCOMPOSITIONATTRIBDATA(attr, ctypes.pointer(data), ctypes.sizeof(data))
```

### 10.4 动画效果
```python
from PySide6.QtCore import QPropertyAnimation, QEasingCurve

# 淡入淡出
animation = QPropertyAnimation(widget, b"windowOpacity")
animation.setDuration(1000)  # 1秒
animation.setStartValue(0)
animation.setEndValue(1)
animation.setEasingCurve(QEasingCurve.InOutQuad)
animation.start()

# 移动动画
animation = QPropertyAnimation(widget, b"pos")
animation.setDuration(500)
animation.setStartValue(QPoint(0, 0))
animation.setEndValue(QPoint(100, 100))
animation.start()

# 大小动画
animation = QPropertyAnimation(widget, b"size")
animation.setDuration(300)
animation.setStartValue(QSize(100, 100))
animation.setEndValue(QSize(200, 200))
animation.start()

# 组合动画
from PySide6.QtCore import QParallelAnimationGroup

group = QParallelAnimationGroup()
group.addAnimation(animation1)
group.addAnimation(animation2)
group.start()
```

---

## 11. 打包发布

### 11.1 PyInstaller 基本命令
```bash
# 基础打包
pyinstaller --onefile --windowed --name "MyApp" main.py

# 带数据文件
pyinstaller --onefile --windowed --add-data "style.qss;." --name "MyApp" main.py

# 带图标
pyinstaller --onefile --windowed --icon "app.ico" --name "MyApp" main.py

# 带多数据文件
pyinstaller --onefile --windowed --add-data "images;images" --add-data "data;data" --name "MyApp" main.py

# 指定工作目录
pyinstaller --distpath "./dist" --workpath "./build" --name "MyApp" main.py
```

### 11.2 常见打包参数
```bash
-F, --onefile           # 打包成单文件
-D, --onedir            # 打包成文件夹（默认）
-w, --windowed          # 不显示控制台
-c, --console           # 显示控制台（默认）
-i, --icon              # 设置图标
-n, --name              # 设置名称
--add-data              # 添加数据文件 (源:目标)
--add-binary            # 添加二进制文件
-p, --paths             # 添加搜索路径
--hidden-import         # 添加隐藏导入
--collect-all           # 收集所有子模块
--exclude-module        # 排除模块
--debug                 # 调试模式
--clean                 # 清理缓存
-y, --noconfirm         # 覆盖输出目录
```

### 11.3 spec 文件配置
```python
# main.spec
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('style.qss', '.')],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyd = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyd,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MyApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app.ico'
)

# 使用 spec 文件打包
# pyinstaller main.spec
```

### 11.4 打包常见问题解决
```bash
# 1. 缺少模块
pyinstaller --hidden-import=mutagen --hidden-import=PySide6 main.py

# 2. 打包太大
pyinstaller --onefile --exclude-module=matplotlib --exclude-module=numpy main.py

# 3. 资源文件访问
# 在代码中：
import sys
import os

def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# 使用
style_path = get_resource_path("style.qss")
with open(style_path, "r") as f:
    self.setStyleSheet(f.read())

# 4. 打包后闪退
# 用命令行运行exe查看错误
# 或在代码中加入日志
import logging
logging.basicConfig(filename='app.log', level=logging.DEBUG)
```

---

## 12. 常见问题

### 12.1 布局问题
```python
# Q: 控件不显示或显示不全？
# A: 检查是否设置了布局，是否将控件添加到了布局中

# Q: 窗口大小变化时布局混乱？
# A: 使用 sizePolicy 设置大小策略
widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
# 或设置拉伸因子
layout.addWidget(widget, stretch=1)

# Q: 控件无法自适应？
# A: 设置 sizePolicy
widget.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
```

### 12.2 信号问题
```python
# Q: 信号不触发？
# A: 检查控件是否被禁用、信号是否正确连接

# Q: 多线程信号不响应？
# A: 确保信号在QThread中发送，不是在工作线程中直接调用

# Q: 循环引用导致内存泄漏？
# A: 使用 weakref 或断开信号连接
widget.deleteLater()  # 安全删除
```

### 12.3 性能问题
```python
# Q: 大量数据时界面卡顿？
# A: 使用 setUpdatesEnabled(False) 批量更新
table.setUpdatesEnabled(False)
for i in range(1000):
    table.setItem(i, 0, QTableWidgetItem("数据"))
table.setUpdatesEnabled(True)

# Q: 频繁重绘导致性能差？
# A: 使用 QTimer 延迟更新
self.timer = QTimer()
self.timer.setSingleShot(True)
self.timer.timeout.connect(self.update_ui)
self.timer.start(100)  # 100ms后更新

# Q: 内存占用太大？
# A: 及时清理不用的控件
widget.deleteLater()
```

### 12.4 中文乱码
```python
# 在代码文件第一行添加编码声明
# -*- coding: utf-8 -*-

# 或者在读取文件时指定编码
with open('file.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# 或者全局设置
import sys
sys.setdefaultencoding('utf-8')  # Python 2
```

---

## 📚 学习资源

### 官方文档
- [Qt for Python 官方文档](https://doc.qt.io/qtforpython/)
- [Qt 5 文档](https://doc.qt.io/qt-5/)

### 速查网站
- [PySide6 控件示例](https://doc.qt.io/qtforpython/examples/index.html)
- [QSS 样式大全](https://doc.qt.io/qt-5/stylesheet-examples.html)

### 图标资源
- [Font Awesome](https://fontawesome.com/)
- [Feather Icons](https://feathericons.com/)
- [Material Icons](https://material.io/icons/)

### 配色工具
- [Coolors](https://coolors.co/)
- [Adobe Color](https://color.adobe.com/)

---

## 🎯 实战模板

### 完整应用模板
```python
import sys
import os
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("我的应用")
        self.resize(900, 650)
        
        # 设置样式
        self.setup_style()
        
        # 创建UI
        self.setup_ui()
        
        # 连接信号
        self.connect_signals()
    
    def setup_style(self):
        """设置全局样式"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a1a;
            }
            QPushButton {
                background-color: #ec4141;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d63a3a;
            }
        """)
    
    def setup_ui(self):
        """创建UI"""
        # 中央控件
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        
        # 标题
        title = QLabel("🎵 我的应用")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #ec4141;")
        main_layout.addWidget(title)
        
        # 内容区域
        content = QHBoxLayout()
        
        # 左侧
        left = QVBoxLayout()
        left.addWidget(QLabel("左侧"))
        content.addLayout(left)
        
        # 右侧
        right = QVBoxLayout()
        right.addWidget(QLabel("右侧"))
        content.addLayout(right)
        
        main_layout.addLayout(content)
        
        # 底部按钮
        bottom = QHBoxLayout()
        bottom.addStretch()
        bottom.addWidget(QPushButton("确定"))
        bottom.addWidget(QPushButton("取消"))
        main_layout.addLayout(bottom)
    
    def connect_signals(self):
        """连接信号"""
        pass

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
```

---

## ✨ 最后的小贴士

1. **多看官方示例** - Qt官方提供了大量示例代码
2. **用 QSS 美化** - 不用写复杂的绘图代码
3. **善用 Signal** - 让代码解耦，更清晰
4. **多线程处理** - 别让界面卡死
5. **打包前测试** - 在开发环境测试好再打包

