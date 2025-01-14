import PyInstaller.__main__
import os
import shutil

# 确保resources目录存在
if not os.path.exists('resources'):
    os.makedirs('resources')

# 创建临时目录用于打包
temp_dir = 'temp_build'
if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)

# 复制所有源文件到临时目录
shutil.copytree('src', os.path.join(temp_dir, 'src'), dirs_exist_ok=True)
shutil.copytree('resources', os.path.join(temp_dir, 'resources'), dirs_exist_ok=True)
shutil.copy('main.py', os.path.join(temp_dir, 'main.py'))

# 切换到临时目录
os.chdir(temp_dir)

PyInstaller.__main__.run([
    'main.py',
    '--name=Redis-GUI',
    '--windowed',
    '--onefile',
    '--add-data=resources;resources',  # 修改分隔符
    '--icon=resources/icon.png',
    '--clean',
    '--noconfirm',
    '--hidden-import=redis',
    '--hidden-import=src',
    '--hidden-import=src.gui',
    '--hidden-import=src.redis_client',
    '--hidden-import=src.config_manager',
    '--paths=.',
    '--collect-all=src',
    '--distpath=../dist',  # 输出到上级目录的dist文件夹
    '--workpath=../build'  # 工作目录设置到上级目录的build文件夹
])

# 清理临时目录
os.chdir('..')
shutil.rmtree(temp_dir) 