from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import QMovie  # 确保导入 QMovie
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QSizePolicy  # 确保导入QSizePolicy
import json
import sys
from PyQt6.QtCore import QTimer

class LoadingDialog(QDialog):
    """自定义加载对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("加载中...")
        self.setModal(True)
        self.setFixedSize(200, 100)
        
        layout = QVBoxLayout(self)
        self.label = QLabel("正在加载，请稍候...")
        layout.addWidget(self.label)

        # 添加加载动画
        self.movie = QMovie("resources/loading.gif")  # 请替换为实际的加载动画路径
        self.loading_label = QLabel()
        self.loading_label.setMovie(self.movie)
        self.loading_label.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding))  # 设置大小策略
        layout.addWidget(self.loading_label)

        self.movie.start()

class DataViewer(QWidget):
    def __init__(self, redis_client, main_window):
        super().__init__()
        self.redis_client = redis_client
        self.main_window = main_window  # 保存MainWindow的引用
        self.current_key = None  # 当前键
        self.current_type = None  # 当前数据类型
        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)

        # 工具栏
        self.toolbar = QHBoxLayout()
        
        # 数据类型显示
        self.type_label = QLabel("类型: -")
        self.toolbar.addWidget(self.type_label)
        
        self.toolbar.addStretch()  # 添加弹性空间
        
        # TTL设置
        self.ttl_label = QLabel("TTL:")
        self.ttl_input = QSpinBox()
        self.ttl_input.setRange(-1, 2147483647)
        self.ttl_input.setValue(-1)
        self.ttl_input.setMinimumHeight(30)
        self.ttl_input.setMinimumWidth(100)
        self.toolbar.addWidget(self.ttl_label)
        self.toolbar.addWidget(self.ttl_input)
        
        # 操作按钮
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.setMinimumHeight(30)
        self.refresh_btn.clicked.connect(self.refresh_data)
        self.toolbar.addWidget(self.refresh_btn)
        
        self.add_btn = QPushButton("添加键")
        self.add_btn.setMinimumHeight(30)
        self.add_btn.clicked.connect(self.show_add_key_dialog)
        self.toolbar.addWidget(self.add_btn)

        self.save_btn = QPushButton("保存")
        self.save_btn.setMinimumHeight(30)
        self.save_btn.clicked.connect(self.save_data)
        self.toolbar.addWidget(self.save_btn)

        self.delete_btn = QPushButton("删除键")
        self.delete_btn.setMinimumHeight(30)
        self.delete_btn.clicked.connect(self.delete_key)
        self.toolbar.addWidget(self.delete_btn)
        
        self.layout.addLayout(self.toolbar)

        # 数据显示区域
        self.data_area = QStackedWidget()  # 使用堆叠窗口管理不同类型的UI
        self.layout.addWidget(self.data_area)

        # 创建不同类型的输入区域
        self.create_string_input()
        self.create_hash_input()
        self.create_list_input()
        self.create_set_input()
        self.create_zset_input()

        # 应用样式
        self.apply_styles()

    def create_string_input(self):
        """创建字符串输入区域"""
        self.string_widget = QWidget()
        string_layout = QVBoxLayout(self.string_widget)
        self.string_text = QTextEdit()
        string_layout.addWidget(self.string_text)
        self.data_area.addWidget(self.string_widget)

    def create_hash_input(self):
        """创建哈希输入区域"""
        self.hash_widget = QWidget()
        hash_layout = QVBoxLayout(self.hash_widget)
        self.hash_text = QTextEdit()
        hash_layout.addWidget(self.hash_text)
        self.data_area.addWidget(self.hash_widget)

    def create_list_input(self):
        """创建列表输入区域"""
        self.list_widget = QWidget()
        list_layout = QVBoxLayout(self.list_widget)
        self.list_text = QTextEdit()
        list_layout.addWidget(self.list_text)
        self.data_area.addWidget(self.list_widget)

    def create_set_input(self):
        """创建集合输入区域"""
        self.set_widget = QWidget()
        set_layout = QVBoxLayout(self.set_widget)
        self.set_text = QTextEdit()
        set_layout.addWidget(self.set_text)
        self.data_area.addWidget(self.set_widget)

    def create_zset_input(self):
        """创建有序集合输入区域"""
        self.zset_widget = QWidget()
        zset_layout = QVBoxLayout(self.zset_widget)
        self.zset_text = QTextEdit()
        zset_layout.addWidget(self.zset_text)
        self.data_area.addWidget(self.zset_widget)

    def show_key_data(self, key):
        """显示指定键的数据"""
        if not key:
            self.show_error("键名为空")
            return
            
        self.current_key = key
        
        # 先清空当前显示
        self.clear_current_display()
        
        # 显示加载对话框
        loading_dialog = LoadingDialog(self)
        loading_dialog.show()
        QApplication.processEvents()  # 确保加载对话框显示出来
    
        try:
            # 获取数据类型
            self.current_type = self.redis_client.get_type(key)
            if not self.current_type:
                raise Exception(f"无法获取键 {key} 的数据类型")
            
            # 更新类型显示
            self.type_label.setText(f"类型: {self.current_type}")
            QApplication.processEvents()
            
            # 获取TTL
            ttl = self.redis_client.get_ttl(key)
            self.ttl_input.setValue(ttl if ttl is not None else -1)
            
            # 切换到正确的显示界面
            type_index = self.get_type_index(self.current_type)
            self.data_area.setCurrentIndex(type_index)
            QApplication.processEvents()
            
            # 获取值
            value = self.redis_client.get_value(key)
            if value is None:
                raise Exception(f"无法获取键 {key} 的值")
            
            # 根据数据类型显示数据
            self.display_value(value)
            
        except Exception as e:
            error_msg = f"错误: {str(e)}"
            print(f"显示键 {key} 的数据时出错: {str(e)}")  # 添加控制台输出
            self.show_error(error_msg)
        finally:
            loading_dialog.close()
            QApplication.processEvents()  # 确保界面更新
    
    def clear_current_display(self):
        """清空当前显示"""
        self.string_text.clear()
        self.hash_text.clear()
        self.list_text.clear()
        self.set_text.clear()
        self.zset_text.clear()
        self.type_label.setText("类型: -")
        self.ttl_input.setValue(-1)
    
    def display_value(self, value):
        """显示数据值"""
        try:
            if self.current_type == 'string':
                self.string_text.setText(str(value))
                
            elif self.current_type == 'hash':
                formatted_value = json.dumps(value, indent=2, ensure_ascii=False)
                self.hash_text.setText(formatted_value)
                
            elif self.current_type == 'list':
                formatted_value = json.dumps(value, indent=2, ensure_ascii=False)
                self.list_text.setText(formatted_value)
                
            elif self.current_type == 'set':
                formatted_value = json.dumps(list(value), indent=2, ensure_ascii=False)
                self.set_text.setText(formatted_value)
                
            elif self.current_type == 'zset':
                formatted_value = json.dumps(value, indent=2, ensure_ascii=False)
                self.zset_text.setText(formatted_value)
                
            QApplication.processEvents()  # 确保数据显示更新
            
        except Exception as e:
            raise Exception(f"格式化数据时出错: {str(e)}")
    
    def show_error(self, error_msg):
        """显示错误信息"""
        self.type_label.setText("类型: 错误")
        self.data_area.setCurrentIndex(0)  # 切换到字符串显示
        self.string_text.setText(error_msg)
        QApplication.processEvents()
    def get_type_index(self, data_type):
        """根据数据类型返回对应的索引"""
        if data_type == 'string':
            return 0
        elif data_type == 'hash':
            return 1
        elif data_type == 'list':
            return 2
        elif data_type == 'set':
            return 3
        elif data_type == 'zset':
            return 4
        return 0  # 默认返回字符串索引

    def show_save_dialog(self):
        """显示保存对话框"""
        save_dialog = QDialog(self)
        save_dialog.setWindowTitle("保存数据")
        layout = QVBoxLayout(save_dialog)

        # 数据类型选择
        self.save_type_combo = QComboBox()
        self.save_type_combo.addItems(['字符串', '哈希', '列表', '集合', '有序集合'])
        layout.addWidget(self.save_type_combo)

        # 确认按钮
        save_button = QPushButton("保存")
        save_button.clicked.connect(self.save_data)
        layout.addWidget(save_button)

        save_dialog.exec()

    def show_add_key_dialog(self):
        """显示添加键的对话框"""
        self.add_dialog = QDialog(self)  # 保存对话框引用
        self.add_dialog.setWindowTitle("添加键")
        layout = QVBoxLayout(self.add_dialog)
    
        # 输入框
        self.new_key_input = QLineEdit()
        self.new_key_input.setPlaceholderText("键名")
        layout.addWidget(self.new_key_input)
    
        self.new_value_input = QTextEdit()
        self.new_value_input.setPlaceholderText("值（根据类型格式）")
        layout.addWidget(self.new_value_input)
    
        # 数据类型选择
        self.new_type_combo = QComboBox()
        self.new_type_combo.addItems(['字符串', '哈希', '列表', '集合', '有序集合'])
        layout.addWidget(self.new_type_combo)
    
        # 确认按钮
        add_button = QPushButton("添加")
        add_button.clicked.connect(self.add_key)
        layout.addWidget(add_button)
    
        # 根据选择的类型更新输入格式
        self.new_type_combo.currentIndexChanged.connect(self.update_input_format)
        self.update_input_format()  # 初始化时更新格式
    
        self.add_dialog.exec()

    def update_input_format(self):
        """根据选择的类型更新输入格式"""
        selected_type = self.new_type_combo.currentText()
        if selected_type == '字符串':
            self.new_value_input.setPlaceholderText("值（字符串）")
        elif selected_type == '哈希':
            self.new_value_input.setPlaceholderText("值（JSON格式，例如: {\"field1\": \"value1\"}）")
        elif selected_type == '列表':
            self.new_value_input.setPlaceholderText("值（JSON数组，例如: [\"item1\", \"item2\"]）")
        elif selected_type == '集合':
            self.new_value_input.setPlaceholderText("值（JSON数组，例如: [\"member1\", \"member2\"]）")
        elif selected_type == '有序集合':
            self.new_value_input.setPlaceholderText("值（JSON数组，例如: [[\"member1\", score1], [\"member2\", score2]]）")

    def add_key(self):
        """添加新键"""
        key = self.new_key_input.text().strip()
        value_text = self.new_value_input.toPlainText().strip()
        data_type = self.new_type_combo.currentText()
    
        if not key:
            QMessageBox.warning(self, "错误", "键名不能为空")
            return
    
        loading_dialog = LoadingDialog(self)  # 显示加载对话框
        loading_dialog.show()
    
        try:
            if data_type == '字符串':
                success = self.redis_client.set_string(key, value_text)
            elif data_type == '哈希':
                value = json.loads(value_text)  # 确保解析为字典
                success = self.redis_client.set_hash(key, value)
            elif data_type == '列表':
                value = json.loads(value_text)  # 确保解析为列表
                success = self.redis_client.set_list(key, value)
            elif data_type == '集合':
                value = json.loads(value_text)  # 确保解析为列表
                success = self.redis_client.set_set(key, value)
            elif data_type == '有序集合':
                value = json.loads(value_text)  # 确保解析为列表
                success = self.redis_client.set_zset(key, value)
            else:
                QMessageBox.warning(self, "错误", f"不支持的数据类型: {data_type}")
                return
    
            if success:
                QMessageBox.information(self, "成功", "键添加成功")
                self.refresh_data()  # 刷新显示
                self.refresh_key_list()  # 刷新当前库的键列表
                self.new_key_input.clear()
                self.new_value_input.clear()
                self.new_type_combo.setCurrentIndex(0)
                self.add_dialog.accept()  # 正确关闭添加键对话框
            else:
                QMessageBox.warning(self, "错误", "键添加失败")
                
        except json.JSONDecodeError:
            QMessageBox.warning(self, "错误", "无效的JSON格式")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"添加键时出错: {str(e)}")
        finally:
            loading_dialog.close()  # 关闭加载对话框
   
    def save_data(self):
        """保存数据"""
        if not self.current_key:
            QMessageBox.warning(self, "错误", "没有选中的键")
            return
            
        # 显示加载对话框
        loading_dialog = LoadingDialog(self)
        loading_dialog.show()

        # 使用 QTimer 来模拟耗时操作
        QTimer.singleShot(0, lambda: self.perform_save(loading_dialog))

    def perform_save(self, loading_dialog):
        """执行保存操作"""
        try:
            # 获取当前文本
            text = ''
            if self.current_type == 'string':
                text = self.string_text.toPlainText().strip()
                success = self.redis_client.set_string(self.current_key, text)
            elif self.current_type == 'hash':
                text = self.hash_text.toPlainText().strip()
                data = json.loads(text)
                success = self.redis_client.set_hash(self.current_key, data)
            elif self.current_type == 'list':
                text = self.list_text.toPlainText().strip()
                data = json.loads(text)
                success = self.redis_client.set_list(self.current_key, data)
            elif self.current_type == 'set':
                text = self.set_text.toPlainText().strip()
                data = json.loads(text)
                success = self.redis_client.set_set(self.current_key, data)
            elif self.current_type == 'zset':
                text = self.zset_text.toPlainText().strip()
                data = json.loads(text)
                success = self.redis_client.set_zset(self.current_key, data)
            else:
                QMessageBox.warning(self, "错误", f"不支持的数据类型: {self.current_type}")
                return
            
            # 设置TTL
            ttl = self.ttl_input.value()
            if ttl >= 0:
                self.redis_client.set_ttl(self.current_key, ttl)

            loading_dialog.close()  # 关闭加载对话框

            if success:
                QMessageBox.information(self, "成功", "数据保存成功")
                self.refresh_data()  # 刷新显示
            else:
                QMessageBox.warning(self, "错误", "数据保存失败")
                
        except Exception as e:
            loading_dialog.close()  # 关闭加载对话框
            QMessageBox.warning(self, "错误", f"保存数据时出错: {str(e)}")

    def refresh_data(self):
        """刷新当前数据"""
        loading_dialog = LoadingDialog(self)  # 显示加载对话框
        loading_dialog.show()

        # 使用 QTimer 来模拟耗时操作
        QTimer.singleShot(0, lambda: self.perform_refresh(loading_dialog))

    def perform_refresh(self, loading_dialog):
        """执行刷新操作"""
        if self.current_key:
            self.show_key_data(self.current_key)
        loading_dialog.close()  # 关闭加载对话框

    def delete_key(self):
        """删除当前键"""
        if not self.current_key:
            QMessageBox.warning(self, "错误", "没有选中的键")
            return

        loading_dialog = LoadingDialog(self)  # 显示加载对话框
        loading_dialog.show()

        # 使用 QTimer 来模拟耗时操作
        QTimer.singleShot(0, lambda: self.perform_delete(loading_dialog))

    def perform_delete(self, loading_dialog):
        """执行删除操作"""
        try:
            success = self.redis_client.delete_key(self.current_key)
            if success:
                QMessageBox.information(self, "成功", "键删除成功")
                self.clear_data()  # 清空数据显示
                self.refresh_key_list()  # 刷新键列表
            else:
                QMessageBox.warning(self, "错误", "键删除失败")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"删除键时出错: {str(e)}")
        finally:
            loading_dialog.close()  # 关闭加载对话框

    def clear_data(self):
        """清空数据显示"""
        self.current_key = None
        self.current_type = None
        self.type_label.setText("类型: -")
        self.data_area.setCurrentIndex(0)  # 默认显示字符串输入区域
        self.string_text.clear()
        self.hash_text.clear()
        self.list_text.clear()
        self.set_text.clear()
        self.zset_text.clear()
        self.ttl_input.setValue(-1)

    def apply_styles(self):
        """应用样式"""
        # 这里可以添加样式设置
        pass 

    def refresh_key_list(self):
        """刷新当前库的键列表"""
        try:
            # 获取当前选中的数据库索引
            current_db_item = self.main_window.db_list.currentItem()
            if not current_db_item:
                return
            
            # 更新UI显示
            self.main_window.refresh_key_list()  # 调用MainWindow的refresh_key_list方法
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"刷新键列表时出错: {str(e)}")

    def display_key(self, key):
        """显示键"""
        # 这里需要实现显示键的逻辑
        pass