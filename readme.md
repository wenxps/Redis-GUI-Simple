# Redis GUI 可视化管理工具

## 项目简介

Redis GUI 是一个基于 PyQt6 开发的 Redis 数据库可视化管理工具。它提供了一个直观、用户友好的图形界面，让用户可以方便地管理和操作 Redis 数据库。这个工具适合开发人员、数据库管理员以及需要使用 Redis 的其他技术人员使用。

## 功能特性

1. 连接管理
   - 支持创建新的 Redis 连接
   - 可配置连接地址、端口、密码等参数
   - 支持保存和管理多个连接配置

2. 数据库操作
   - 支持切换不同的 Redis 数据库（DB0-DB15）
   - 显示当前数据库中的所有键
   - 支持按键名称进行搜索和过滤

3. 数据查看与编辑
   - 支持查看和编辑不同类型的 Redis 数据：
     - String（字符串）
     - List（列表）
     - Hash（哈希表）
     - Set（集合）
     - Sorted Set（有序集合）
   - 提供直观的数据编辑界面
   - 支持数据的添加、修改和删除操作

4. 界面特性
   - 现代化的用户界面设计
   - 支持暗色主题
   - 可调整的界面布局

## 开发环境搭建

### 系统要求
- Python 3.8 或更高版本
- Windows/Linux/MacOS 操作系统

### 安装步骤

1. 克隆项目代码
```bash
git clone [项目地址]
cd Redis-GUI-Project
```

2. 创建并激活虚拟环境（推荐）
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/MacOS
source venv/bin/activate
```

3. 安装依赖包
```bash
pip install -r requirements.txt
```

4. 运行开发版本
```bash
python main.py
```

## 打包说明

本项目使用 PyInstaller 进行打包，可以生成独立的可执行文件。

### 打包步骤

1. 安装 PyInstaller（如果尚未安装）
```bash
pip install pyinstaller
```

2. 执行打包命令
```bash
python build.py
```

打包完成后，可执行文件将生成在 `dist` 目录下。

## 使用说明

### 启动程序

1. 双击运行已打包的可执行文件 `Redis-GUI.exe`（Windows）或 `Redis-GUI`（Linux/MacOS）

### 基本操作流程

1. 创建连接
   - 点击左上角的"新建连接"按钮
   - 输入 Redis 服务器信息（地址、端口、密码等）
   - 点击"连接"按钮

2. 浏览数据
   - 在左侧面板选择数据库（DB0-DB15）
   - 使用搜索框查找特定的键
   - 在键列表中选择要查看的键

3. 编辑数据
   - 双击值区域进行编辑
   - 使用工具栏按钮进行添加、删除操作
   - 编辑完成后点击保存

4. 管理连接
   - 可以保存多个连接配置
   - 通过连接管理器切换不同的连接

### 注意事项

- 首次使用时需要配置正确的 Redis 连接信息
- 建议在进行重要操作前备份数据
- 部分功能可能需要相应的 Redis 服务器权限

## 问题反馈

如果您在使用过程中遇到任何问题，或有任何建议，请通过以下方式反馈：
1. 在项目 GitHub 页面提交 Issue
2. 发送邮件至项目维护者

## 开发计划

未来版本计划添加的功能：
1. 支持 Redis 集群管理
2. 性能监控功能
3. 数据导入导出功能
4. 命令行界面的集成
