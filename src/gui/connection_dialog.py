from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

class ConnectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Redis连接")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)  # 设置垂直间距
        layout.setContentsMargins(20, 20, 20, 20)  # 设置边距

        form_layout = QFormLayout()
        form_layout.setSpacing(15)  # 设置表单项之间的间距
        form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)  # 允许字段扩展

        # 主机
        self.host_input = QLineEdit()
        self.host_input.setText("localhost")
        self.host_input.setMinimumHeight(35)  # 增加高度
        form_layout.addRow("主机:", self.host_input)

        # 端口
        port_container = QWidget()
        port_layout = QHBoxLayout(port_container)
        port_layout.setContentsMargins(0, 0, 0, 0)
        
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(6379)
        self.port_input.setMinimumHeight(35)  # 增加高度
        self.port_input.setMinimumWidth(200)  # 增加宽度
        self.port_input.setFixedHeight(35)    # 固定高度
        port_layout.addWidget(self.port_input)
        port_layout.addStretch()
        
        form_layout.addRow("端口:", port_container)

        # 密码
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(35)  # 增加高度
        form_layout.addRow("密码:", self.password_input)

        # 数据库
        self.db_input = QSpinBox()
        self.db_input.setRange(0, 15)
        self.db_input.setMinimumHeight(35)  # 增加高度
        self.db_input.setMinimumWidth(200)  # 增加宽度
        self.db_input.setFixedHeight(35)    # 固定高度
        form_layout.addRow("数据库:", self.db_input)

        layout.addLayout(form_layout)

        # 按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        # 设置按钮样式和大小
        for button in button_box.buttons():
            button.setMinimumHeight(35)  # 增加按钮高度
            button.setMinimumWidth(100)  # 增加按钮宽度
        
        layout.addSpacing(20)  # 添加一些垂直空间
        layout.addWidget(button_box)

        # 设置窗口最小大小
        self.setMinimumWidth(400)
        self.setMinimumHeight(300)  # 设置最小高度
        
        # 应用样式
        self.apply_styles()

    def apply_styles(self):
        # 输入框样式
        input_style = """
        QLineEdit, QSpinBox {
            padding: 5px 10px;
            border: 1px solid #cccccc;
            border-radius: 4px;
            background-color: white;
            selection-background-color: #0078d7;
            font-size: 14px;
        }
        QLineEdit:focus, QSpinBox:focus {
            border: 1px solid #0078d7;
        }
        QSpinBox::up-button {
            width: 25px;
            border-left: 1px solid #cccccc;
            border-bottom: 1px solid #cccccc;
            border-top-right-radius: 4px;
            background: #f5f5f5;
        }
        QSpinBox::down-button {
            width: 25px;
            border-left: 1px solid #cccccc;
            border-top-right-radius: 0px;
            border-bottom-right-radius: 4px;
            background: #f5f5f5;
        }
        QSpinBox::up-button:hover, QSpinBox::down-button:hover {
            background: #e0e0e0;
        }
        QSpinBox::up-arrow {
            image: url(up_arrow.png);
            width: 12px;
            height: 12px;
        }
        QSpinBox::down-arrow {
            image: url(down_arrow.png);
            width: 12px;
            height: 12px;
        }
        """
        
        # 按钮样式
        button_style = """
        QPushButton {
            background-color: #0078d7;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 4px;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #1984d8;
        }
        QPushButton:pressed {
            background-color: #006cc1;
        }
        """
        
        self.setStyleSheet(input_style)
        
        # 应用按钮样式
        for button in self.findChildren(QPushButton):
            button.setStyleSheet(button_style)

    def get_connection_info(self):
        return {
            'host': self.host_input.text(),
            'port': self.port_input.value(),
            'password': self.password_input.text(),
            'db': self.db_input.value()
        } 