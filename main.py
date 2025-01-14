import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def get_resource_path(relative_path):
    """获取资源文件的绝对路径"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包后的路径
        return os.path.join(sys._MEIPASS, relative_path)
    # 开发环境下的路径
    return os.path.join(os.path.abspath("."), relative_path)

def main():
    from PyQt6.QtWidgets import QApplication
    from src.gui.main_window import MainWindow

    app = QApplication(sys.argv)
    
    # 加载样式表
    try:
        style_path = get_resource_path(os.path.join('resources', 'style.qss'))
        with open(style_path, 'r', encoding='utf-8') as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("警告: 找不到样式表文件 style.qss")
    except Exception as e:
        print(f"错误: 加载样式表时出错: {str(e)}")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 