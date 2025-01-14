from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import sys
import os
from collections import defaultdict

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, current_dir)

# 导入其他模块
from src.redis_client import RedisClient
from src.gui.connection_dialog import ConnectionDialog
from src.gui.data_viewer import DataViewer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Redis GUI")
        self.setMinimumSize(1200, 800)
        self.redis_client = RedisClient()
        self.setup_ui()

    def setup_ui(self):
        # 创建主窗口布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # 创建左侧面板
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 10, 10, 10)  # 设置边距
        left_layout.setSpacing(10)  # 设置组件间距
        
        # 连接按钮
        self.connect_btn = QPushButton("新建连接")
        self.connect_btn.setMinimumHeight(30)  # 设置按钮高度
        self.connect_btn.clicked.connect(self.show_connection_dialog)
        left_layout.addWidget(self.connect_btn)

        # 数据库选择器
        db_group = QGroupBox("数据库")
        db_layout = QVBoxLayout(db_group)
        self.db_list = QListWidget()
        self.db_list.setMinimumHeight(200)  # 设置最小高度
        self.db_list.itemClicked.connect(self.on_db_selected)
        db_layout.addWidget(self.db_list)
        left_layout.addWidget(db_group)

        # 键列表组
        keys_group = QGroupBox("键列表")
        keys_layout = QVBoxLayout(keys_group)
        
        # 工具栏
        tools_layout = QHBoxLayout()
        
        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索键...")
        self.search_input.textChanged.connect(self.filter_keys)
        self.search_input.setMinimumHeight(30)
        tools_layout.addWidget(self.search_input)
        
        # 删除按钮
        delete_btn = QPushButton("删除选中")
        delete_btn.setMinimumHeight(30)
        delete_btn.clicked.connect(self.delete_selected)
        tools_layout.addWidget(delete_btn)
        
        keys_layout.addLayout(tools_layout)
        
        # 树形键列表
        self.key_tree = QTreeWidget()
        self.key_tree.setHeaderLabel("键列表")
        self.key_tree.setMinimumHeight(400)
        self.key_tree.setSelectionMode(QTreeWidget.SelectionMode.ExtendedSelection)
        self.key_tree.itemClicked.connect(self.on_tree_item_selected)
        self.key_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.key_tree.customContextMenuRequested.connect(self.show_context_menu)
        keys_layout.addWidget(self.key_tree)
        
        left_layout.addWidget(keys_group)

        # 设置左侧面板的固定宽度
        left_panel.setFixedWidth(300)
        layout.addWidget(left_panel)

        # 创建右侧数据显示区
        self.data_viewer = DataViewer(self.redis_client, self)  # 传递MainWindow的实例
        layout.addWidget(self.data_viewer)

        # 创建菜单栏
        self.create_menu_bar()
        
        # 设置样式
        self.apply_styles()

    def apply_styles(self):
        # 设置列表样式
        list_style = """
        QListWidget {
            background-color: white;
            border: 1px solid #cccccc;
            border-radius: 4px;
            padding: 5px;
        }
        QListWidget::item {
            padding: 5px;
            border-bottom: 1px solid #eeeeee;
        }
        QListWidget::item:selected {
            background-color: #0078d7;
            color: white;
        }
        QListWidget::item:hover {
            background-color: #e5f3ff;
        }
        """
        self.db_list.setStyleSheet(list_style)
        self.key_tree.setStyleSheet(list_style)

        # 设置按钮样式
        button_style = """
        QPushButton {
            background-color: #0078d7;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #1984d8;
        }
        QPushButton:pressed {
            background-color: #006cc1;
        }
        """
        self.connect_btn.setStyleSheet(button_style)

    def filter_keys(self, text):
        """过滤键列表"""
        def filter_items(item):
            # 如果是文件夹，检查所有子项
            if item.childCount() > 0:
                show_children = False
                for i in range(item.childCount()):
                    if filter_items(item.child(i)):
                        show_children = True
                item.setHidden(not show_children)
                return show_children
            else:
                # 如果是键，检查是否匹配
                matches = text.lower() in self._get_full_key(item).lower()
                item.setHidden(not matches)
                return matches

        # 从根节点开始过滤
        for i in range(self.key_tree.topLevelItemCount()):
            filter_items(self.key_tree.topLevelItem(i))

    def show_connection_dialog(self):
        dialog = ConnectionDialog(self)
        if dialog.exec():
            # 获取连接信息并尝试连接
            conn_info = dialog.get_connection_info()
            if self.redis_client.connect(**conn_info):  # 使用解包操作符传递参数
                self.refresh_db_list()  # 只在连接成功后刷新
                QMessageBox.information(self, "成功", "Redis连接成功！")
            else:
                QMessageBox.warning(self, "错误", "无法连接到Redis服务器，请检查连接信息。")

    def refresh_db_list(self):
        if not self.redis_client.client:  # 检查是否已连接
            return
        
        self.db_list.clear()
        for i in range(16):  # Redis默认16个数据库
            item = QListWidgetItem(f"db{i}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.db_list.addItem(item)

    def on_db_selected(self, item):
        if not self.redis_client.client:  # 检查是否已连接
            QMessageBox.warning(self, "错误", "请先连接到Redis服务器")
            return
        
        db_num = int(item.text().replace("db", ""))
        if self.redis_client.select_db(db_num):  # 检查数据库选择是否成功
            self.refresh_key_list()
        else:
            QMessageBox.warning(self, "错误", f"无法切换到数据库 {db_num}")

    def refresh_key_list(self):
        """刷新键列表为树形结构"""
        self.key_tree.clear()
        keys = self.redis_client.get_all_keys()
        
        # 创建树形结构
        tree = defaultdict(dict)
        for key in sorted(keys):
            parts = key.split(':')
            current = tree
            for i, part in enumerate(parts):
                if i == len(parts) - 1:
                    current[part] = None  # 叶子节点
                else:
                    if part not in current:
                        current[part] = defaultdict(dict)
                    current = current[part]
        
        # 递归构建树形界面
        self._build_tree(tree, self.key_tree)
        self.key_tree.expandAll()  # 展开所有节点

    def _build_tree(self, tree_dict, parent_item):
        """递归构建树形结构"""
        for key, value in tree_dict.items():
            if value is None:  # 叶子节点（实际的键）
                item = QTreeWidgetItem(parent_item)
                item.setText(0, key)
                item.setData(0, Qt.ItemDataRole.UserRole, self._get_full_key(item))
            else:  # 文件夹节点
                folder = QTreeWidgetItem(parent_item)
                folder.setText(0, key)
                folder.setIcon(0, self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon))
                self._build_tree(value, folder)

    def _get_full_key(self, item):
        """获取完整的键名"""
        parts = []
        while item is not None:
            parts.insert(0, item.text(0))
            item = item.parent()
        return ':'.join(parts)

    def on_tree_item_selected(self, item, column):
        """处理树节点选择"""
        if not item.childCount():  # 只处理叶子节点
            full_key = self._get_full_key(item)
            self.data_viewer.show_key_data(full_key)

    def show_context_menu(self, position):
        """显示右键菜单"""
        items = self.key_tree.selectedItems()
        if not items:
            return

        menu = QMenu()
        delete_action = menu.addAction("删除")
        delete_action.triggered.connect(self.delete_selected)
        
        if len(items) == 1 and items[0].childCount() > 0:
            # 如果选中的是文件夹，添加展开/折叠选项
            expand_action = menu.addAction("展开所有")
            expand_action.triggered.connect(lambda: self._expand_folder(items[0], True))
            collapse_action = menu.addAction("折叠所有")
            collapse_action.triggered.connect(lambda: self._expand_folder(items[0], False))

        menu.exec(self.key_tree.viewport().mapToGlobal(position))

    def _expand_folder(self, item, expand=True):
        """展开或折叠文件夹"""
        item.setExpanded(expand)
        for i in range(item.childCount()):
            self._expand_folder(item.child(i), expand)

    def delete_selected(self):
        """删除选中的键或文件夹"""
        items = self.key_tree.selectedItems()
        if not items:
            return

        keys_to_delete = []
        for item in items:
            if item.childCount() > 0:  # 文件夹
                keys_to_delete.extend(self._get_folder_keys(item))
            else:  # 单个键
                keys_to_delete.append(self._get_full_key(item))

        if not keys_to_delete:
            return

        msg = f"确定要删除以下 {len(keys_to_delete)} 个键吗？\n" + "\n".join(keys_to_delete[:10])
        if len(keys_to_delete) > 10:
            msg += f"\n... 等 {len(keys_to_delete)} 个键"

        reply = QMessageBox.question(
            self,
            "确认删除",
            msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            success_count = 0
            for key in keys_to_delete:
                if self.redis_client.delete_key(key):
                    success_count += 1

            # 清空右侧数据显示
            self.data_viewer.clear_data()
            
            # 刷新键列表
            self.refresh_key_list()
            
            QMessageBox.information(
                self,
                "删除完成",
                f"成功删除 {success_count} 个键，失败 {len(keys_to_delete) - success_count} 个"
            )

    def _get_folder_keys(self, folder_item):
        """获取文件夹中所有键"""
        keys = []
        for i in range(folder_item.childCount()):
            child = folder_item.child(i)
            if child.childCount() > 0:  # 子文件夹
                keys.extend(self._get_folder_keys(child))
            else:  # 叶子节点
                keys.append(self._get_full_key(child))
        return keys

    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件")
        
        new_conn_action = QAction("新建连接", self)
        new_conn_action.triggered.connect(self.show_connection_dialog)
        file_menu.addAction(new_conn_action)
        
        # 添加数据库操作菜单
        db_menu = menubar.addMenu("数据库")
        
        flush_db_action = QAction("清空当前库", self)
        flush_db_action.triggered.connect(self.flush_current_db)
        db_menu.addAction(flush_db_action)
        
        flush_all_action = QAction("清空所有库", self)
        flush_all_action.triggered.connect(self.flush_all_dbs)
        db_menu.addAction(flush_all_action)
        
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def flush_current_db(self):
        """清空当前数据库"""
        reply = QMessageBox.question(
            self,
            "确认清空",
            "确定要清空当前数据库吗？此操作不可恢复！",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.redis_client.flush_db():
                # 清空右侧数据显示
                self.data_viewer.clear_data()
                # 刷新键列表
                self.refresh_key_list()
                QMessageBox.information(self, "成功", "当前数据库已清空")
            else:
                QMessageBox.warning(self, "错误", "清空数据库失败")

    def flush_all_dbs(self):
        """清空所有数据库"""
        reply = QMessageBox.question(
            self,
            "确认清空",
            "确定要清空所有数据库吗？此操作不可恢复！",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.redis_client.flush_all():
                # 清空右侧数据显示
                self.data_viewer.clear_data()
                # 刷新键列表
                self.refresh_key_list()
                QMessageBox.information(self, "成功", "所有数据库已清空")
            else:
                QMessageBox.warning(self, "错误", "清空数据库失败")

    def show_monitor(self):
        # 实现监控面板（将在后续代码中添加）
        pass