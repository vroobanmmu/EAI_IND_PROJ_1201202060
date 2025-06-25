import sys
import webbrowser
import requests
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QHBoxLayout, QMessageBox, QSystemTrayIcon, QMenu, QAction, QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QTextEdit, QLineEdit, QInputDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap

class SoyJoyDesktop(QWidget):
    def __init__(self):
        super().__init__()
        icon_path = os.path.join(os.path.dirname(__file__), 'static', 'images', 'soy_icon.png')
        icon_pixmap = QPixmap(icon_path).scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setWindowIcon(QIcon(icon_pixmap))
        self.setWindowTitle('Soy Joy Admin Desktop')
        self.setGeometry(100, 100, 1000, 700)
        self.setStyleSheet('background:#ece6df; font-family:Montserrat,Arial,sans-serif;')
        self.api_base = 'http://127.0.0.1:5000'
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 30, 0, 30)

        # Card-like container
        card = QFrame()
        card.setStyleSheet('background:#fffbe7; border-radius:18px;')
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 30, 40, 30)
        card_layout.setSpacing(24)

        # Logo and title (centered at the top)
        logo_title_layout = QVBoxLayout()
        logo_title_layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        logo = QLabel()
        logo.setPixmap(QPixmap(icon_path).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo.setAlignment(Qt.AlignHCenter)
        logo_title_layout.addWidget(logo)
        title = QLabel('<b>Soy Joy Admin Desktop</b>')
        title.setAlignment(Qt.AlignHCenter)
        title.setStyleSheet('font-size:36px; color:#6d4c41; margin-top:8px; margin-bottom:18px;')
        logo_title_layout.addWidget(title)
        card_layout.addLayout(logo_title_layout)

        # Admin login form
        self.login_layout = QHBoxLayout()
        self.admin_user_input = QLineEdit()
        self.admin_user_input.setPlaceholderText('Admin username')
        self.admin_user_input.setStyleSheet('font-size:20px; padding:12px;')
        self.admin_pass_input = QLineEdit()
        self.admin_pass_input.setPlaceholderText('Password')
        self.admin_pass_input.setEchoMode(QLineEdit.Password)
        self.admin_pass_input.setStyleSheet('font-size:20px; padding:12px;')
        # Add show/hide password button
        self.toggle_pass_btn = QPushButton('Show')
        self.toggle_pass_btn.setCheckable(True)
        self.toggle_pass_btn.setStyleSheet('font-size:16px; padding:8px 16px;')
        self.toggle_pass_btn.toggled.connect(self.toggle_password_visibility)
        self.login_btn = QPushButton('Login')
        self.login_btn.setStyleSheet(self.btn_style('#388e3c', '#fff', font_size=22, min_width=180))
        self.login_btn.clicked.connect(self.admin_login)
        self.login_layout.addStretch()
        self.login_layout.addWidget(self.admin_user_input)
        self.login_layout.addWidget(self.admin_pass_input)
        self.login_layout.addWidget(self.toggle_pass_btn)
        self.login_layout.addWidget(self.login_btn)
        self.login_layout.addStretch()
        card_layout.addLayout(self.login_layout)

        # Admin function buttons (centered, hidden until login)
        self.btn_layout = QHBoxLayout()
        self.btn_layout.addStretch()
        self.dashboard_btn = QPushButton('Dashboard')
        self.dashboard_btn.setStyleSheet(self.btn_style('#ffd600', '#6d4c41', font_size=20, min_width=160))
        self.dashboard_btn.clicked.connect(self.show_dashboard)
        self.orders_btn = QPushButton('Orders')
        self.orders_btn.setStyleSheet(self.btn_style('#ffd600', '#6d4c41', font_size=20, min_width=160))
        self.orders_btn.clicked.connect(self.show_orders)
        self.inventory_btn = QPushButton('Inventory')
        self.inventory_btn.setStyleSheet(self.btn_style('#ffd600', '#6d4c41', font_size=20, min_width=160))
        self.inventory_btn.clicked.connect(self.show_inventory)
        self.activity_btn = QPushButton('User Activity')
        self.activity_btn.setStyleSheet(self.btn_style('#ffd600', '#6d4c41', font_size=20, min_width=160))
        self.activity_btn.clicked.connect(self.show_activity)
        self.open_landing_btn = QPushButton('Open in Web')
        self.open_landing_btn.setStyleSheet(self.btn_style('#6d4c41', '#fff', font_size=20, min_width=180))
        self.open_landing_btn.clicked.connect(lambda: webbrowser.open(f'{self.api_base}/'))
        self.open_landing_btn.setVisible(False)
        for btn in [self.dashboard_btn, self.orders_btn, self.inventory_btn, self.activity_btn, self.open_landing_btn]:
            btn.setVisible(False)
            self.btn_layout.addWidget(btn)
        self.btn_layout.addStretch()
        # Move button layout just below the logo/title
        card_layout.addLayout(self.btn_layout)

        # Logout button (hidden until login)
        self.logout_btn = QPushButton('Logout')
        self.logout_btn.setStyleSheet(self.btn_style('#fc8181', '#fff', font_size=18, min_width=120))
        self.logout_btn.clicked.connect(self.logout_admin)
        self.logout_btn.setVisible(False)
        # Place logout button at top right
        logout_layout = QHBoxLayout()
        logout_layout.addStretch()
        logout_layout.addWidget(self.logout_btn)
        card_layout.addLayout(logout_layout)

        # Main content area
        self.content_area = QVBoxLayout()
        card_layout.addLayout(self.content_area)

        outer.addWidget(card)

        # System tray icon for notifications
        tray_icon = QIcon(icon_path)
        self.tray_icon = QSystemTrayIcon(tray_icon, self)
        self.tray_icon.setToolTip('Soy Joy Admin Desktop')
        tray_menu = QMenu()
        quit_action = QAction('Quit', self)
        quit_action.triggered.connect(QApplication.instance().quit)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        # Session for requests
        self.session = requests.Session()

    def btn_style(self, bg, fg, font_size=18, min_width=140):
        return (
            f"QPushButton {{ background: {bg}; color: {fg}; font-weight: 700; border: none; border-radius: 10px; "
            f"padding: 16px 36px; min-width: {min_width}px; font-size: {font_size}px; text-align: center; }} "
            f"QPushButton:hover {{ background: #bdbdbd; color: #4e342e; }}"
        )

    def admin_login(self):
        username = self.admin_user_input.text().strip()
        password = self.admin_pass_input.text().strip()
        if not username or not password:
            QMessageBox.warning(self, 'Login Error', 'Please enter both username and password.')
            return
        # Only allow a01/a01@1234
        if username == 'a01' and password == 'a01@1234':
            self.session = requests.Session()
            try:
                resp = self.session.post(f'{self.api_base}/admin/login', data={'admin_username': username, 'admin_password': password})
                if resp.status_code == 200 and ('dashboard' in resp.url or resp.url.endswith('/admin-dashboard')):
                    for btn in [self.dashboard_btn, self.orders_btn, self.inventory_btn, self.activity_btn, self.open_landing_btn]:
                        btn.setEnabled(True)
                        btn.setVisible(True)
                    self.login_btn.setVisible(False)
                    self.admin_user_input.setVisible(False)
                    self.admin_pass_input.setVisible(False)
                    self.toggle_pass_btn.setVisible(False)
                    self.logout_btn.setVisible(True)
                    self.login_layout.setEnabled(False)
                    self.show_notification('Login', 'Admin login successful!')
                    self.show_dashboard()
                else:
                    QMessageBox.warning(self, 'Login Failed', 'Invalid admin credentials.')
            except Exception as e:
                QMessageBox.critical(self, 'Login Error', f'Error: {e}')
        else:
            QMessageBox.warning(self, 'Login Failed', 'Invalid admin credentials.')

    def clear_content(self):
        while self.content_area.count():
            item = self.content_area.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def show_dashboard(self):
        self.clear_content()
        label = QLabel('Admin Dashboard')
        label.setStyleSheet('font-size:28px; font-weight:bold; color:#6d4c41; margin-bottom:18px;')
        self.content_area.addWidget(label)
        # Show admin logins and admin activities from backend
        try:
            resp = self.session.get(f'{self.api_base}/api/admin/dashboard')
            if resp.status_code == 200 and resp.headers.get('Content-Type','').startswith('application/json'):
                data = resp.json()
                admin_logs = data.get('admin_logs', [])
                admin_activities = data.get('admin_activities', [])
                admin_label = QLabel('Admin Logins:')
                admin_label.setStyleSheet('font-size:22px; font-weight:bold; color:#388e3c; margin-top:12px;')
                self.content_area.addWidget(admin_label)
                for log in admin_logs:
                    self.content_area.addWidget(QLabel(f"{log['username']} - {log['login_time']}"))
                activity_label = QLabel('Admin Activities:')
                activity_label.setStyleSheet('font-size:22px; font-weight:bold; color:#6d4c41; margin-top:18px;')
                self.content_area.addWidget(activity_label)
                for log in admin_activities:
                    self.content_area.addWidget(QLabel(f"{log['login_time']} - {log['username']}: {log.get('action','')} - {log.get('detail','')}"))
            else:
                self.content_area.addWidget(QLabel('Failed to load dashboard logs.'))
        except Exception as e:
            self.content_area.addWidget(QLabel(f'Error: {e}'))

    def show_orders(self):
        self.last_panel = 'show_orders'
        self.clear_content()
        label = QLabel('Orders')
        label.setStyleSheet('font-size:28px; font-weight:bold; color:#6d4c41; margin-bottom:18px;')
        self.content_area.addWidget(label)
        table = QTableWidget()
        table.setStyleSheet('font-size:20px;')
        table.verticalHeader().setDefaultSectionSize(40)
        table.horizontalHeader().setStyleSheet('font-size:22px; font-weight:bold;')
        table.setMinimumHeight(400)
        try:
            resp = self.session.get(f'{self.api_base}/api/admin/orders')
            if resp.status_code == 200 and resp.headers.get('Content-Type','').startswith('application/json'):
                orders = resp.json().get('orders', [])
                table.setColumnCount(6)
                table.setHorizontalHeaderLabels(['Username', 'Product ID', 'Name', 'Quantity', 'Price', 'Date'])
                table.setRowCount(len(orders))
                for row, order in enumerate(orders):
                    table.setItem(row, 0, QTableWidgetItem(order['username']))
                    table.setItem(row, 1, QTableWidgetItem(order['product_id']))
                    table.setItem(row, 2, QTableWidgetItem(order['name']))
                    table.setItem(row, 3, QTableWidgetItem(str(order['quantity'])))
                    table.setItem(row, 4, QTableWidgetItem(str(order['price'])))
                    table.setItem(row, 5, QTableWidgetItem(order.get('date','')))
                table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                self.content_area.addWidget(table)
            else:
                self.content_area.addWidget(QLabel('Failed to load orders.'))
        except Exception as e:
            self.content_area.addWidget(QLabel(f'Error: {e}'))

    def show_inventory(self):
        self.clear_content()
        label = QLabel('Inventory')
        label.setStyleSheet('font-size:28px; font-weight:bold; color:#6d4c41; margin-bottom:18px;')
        self.content_area.addWidget(label)
        try:
            resp = self.session.get(f'{self.api_base}/api/admin/inventory')
            if resp.status_code == 200:
                products = resp.json().get('products', [])
                table = QTableWidget()
                table.setStyleSheet('font-size:20px;')
                table.verticalHeader().setDefaultSectionSize(40)
                table.horizontalHeader().setStyleSheet('font-size:22px; font-weight:bold;')
                table.setMinimumHeight(400)
                table.setColumnCount(5)
                table.setHorizontalHeaderLabels(['ID', 'Name', 'Price', 'Stock', 'Image'])
                table.setRowCount(len(products))
                for row, prod in enumerate(products):
                    table.setItem(row, 0, QTableWidgetItem(prod['id']))
                    table.setItem(row, 1, QTableWidgetItem(prod['name']))
                    table.setItem(row, 2, QTableWidgetItem(str(prod['price'])))
                    table.setItem(row, 3, QTableWidgetItem(str(prod.get('stock',''))))
                    table.setItem(row, 4, QTableWidgetItem(prod.get('image','')))
                table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                self.content_area.addWidget(table)
                # Add edit functionality (double click to edit stock)
                table.itemDoubleClicked.connect(lambda item: self.edit_inventory_item(table, item))
            else:
                self.content_area.addWidget(QLabel('Failed to load inventory.'))
        except Exception as e:
            self.content_area.addWidget(QLabel(f'Error: {e}'))

    def show_activity(self):
        self.last_panel = 'show_activity'
        self.clear_content()
        label = QLabel('User Activity')
        label.setStyleSheet('font-size:28px; font-weight:bold; color:#6d4c41; margin-bottom:18px;')
        self.content_area.addWidget(label)
        try:
            resp = self.session.get(f'{self.api_base}/api/admin/user-activity')
            if resp.status_code == 200 and resp.headers.get('Content-Type','').startswith('application/json'):
                activities = resp.json().get('activities', [])
                text = '\n'.join([f"{a['date']} - {a['username']}: {a['detail']}" for a in activities])
                text_edit = QTextEdit()
                text_edit.setReadOnly(True)
                text_edit.setText(text)
                self.content_area.addWidget(text_edit)
            else:
                self.content_area.addWidget(QLabel('Failed to load user activity.'))
        except Exception as e:
            self.content_area.addWidget(QLabel(f'Error: {e}'))

    def edit_inventory_item(self, table, item):
        row = item.row()
        col = item.column()
        if col not in [1,2,3,4]:
            return
        product_id = table.item(row, 0).text()
        old_value = table.item(row, col).text()
        new_value, ok = QInputDialog.getText(self, 'Edit Value', f'Edit value for {table.horizontalHeaderItem(col).text()}:', text=old_value)
        if ok and new_value != old_value:
            # Prepare data for update
            data = {
                'name': table.item(row, 1).text(),
                'price': table.item(row, 2).text(),
                'stock': table.item(row, 3).text(),
                'image': table.item(row, 4).text()
            }
            data[table.horizontalHeaderItem(col).text().lower()] = new_value
            try:
                resp = self.session.post(f'{self.api_base}/api/admin/inventory/edit/{product_id}', json=data)
                if resp.status_code == 200:
                    QMessageBox.information(self, 'Success', 'Product updated successfully!')
                    self.show_inventory()
                else:
                    QMessageBox.warning(self, 'Error', 'Failed to update product.')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Error: {e}')

    def toggle_password_visibility(self, checked):
        if checked:
            self.admin_pass_input.setEchoMode(QLineEdit.Normal)
            self.toggle_pass_btn.setText('Hide')
        else:
            self.admin_pass_input.setEchoMode(QLineEdit.Password)
            self.toggle_pass_btn.setText('Show')

    def show_notification(self, title, message):
        if self.tray_icon.isVisible():
            self.tray_icon.showMessage(title, message, QSystemTrayIcon.Information, 4000)

    def logout_admin(self):
        # Reset UI to login state
        self.session = None
        self.logout_btn.setVisible(False)
        for btn in [self.dashboard_btn, self.orders_btn, self.inventory_btn, self.activity_btn, self.open_landing_btn]:
            btn.setEnabled(False)
            btn.setVisible(False)
        for i in range(self.login_layout.count()):
            widget = self.login_layout.itemAt(i).widget()
            if widget:
                widget.setVisible(True)
        self.login_layout.setEnabled(True)
        self.clear_content()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SoyJoyDesktop()
    window.show()
    sys.exit(app.exec_())
