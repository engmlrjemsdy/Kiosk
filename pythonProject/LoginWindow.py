import mysql.connector
import re
import sys
import socket

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QLabel, QPushButton, QRadioButton, QMessageBox, \
    QMainWindow, QWidget, QApplication
from PyQt5.QtCore import QSize


class AdminWindow(QMainWindow):
    def __init__(self, order_number):
        super().__init__()
        self.order_number = order_number  # 초기 주문 번호 설정
        self.setWindowTitle("관리자 화면")
        self.setGeometry(480, 800)
        self.initUI()
        self.setup_socket()

    def initUI(self):
        self.order_number_label = QLabel(f"주문 번호: {self.order_number}", self)
        self.order_number_label.setStyleSheet("font-size: 20pt;")

        self.menu_label = QLabel("메뉴 : ", self)
        self.menu_label.setStyleSheet("font-size: 20pt;")

        self.counter_payment_label = QLabel("결제 방식: 카운터에서 결제", self)
        self.counter_payment_label.setStyleSheet("font-size: 20pt;")

        self.counter_payment_button = QPushButton("카운터에서 결제", self)
        self.counter_payment_button.setStyleSheet("font-size: 16pt;")
        self.counter_payment_button.clicked.connect(self.open_payment_screen)

        layout = QVBoxLayout()
        layout.addWidget(self.order_number_label)
        layout.addWidget(self.menu_label)
        layout.addWidget(self.counter_payment_label)
        layout.addWidget(self.counter_payment_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def open_payment_screen(self):
        from Voice_Payment import PaymentScreen
        self.payment_screen = PaymentScreen(order_number=self.order_number)  # 주문 번호를 인자로 전달하여 PaymentScreen 생성
        self.payment_screen.show()
        self.order_number += 1

    def setup_socket(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('localhost', 9999))  # 포트 번호를 일관성 있게 설정
        self.server_socket.listen(5)
        print("서버 대기 중...")

        self.client_socket, self.client_address = self.server_socket.accept()
        print(f"클라이언트 {self.client_address}가 연결되었습니다.")
        self.receive_order_info()

    def receive_order_info(self):
        while True:
            data = self.client_socket.recv(1024)
            if not data:
                break
            print("주문 정보 수신:", data.decode())

    def close_socket(self):
        self.client_socket.close()
        self.server_socket.close()

    def closeEvent(self, event):
        self.close_socket()
        event.accept()


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("로그인")
        self.setGeometry(100, 100, 280, 80)

        self.setupUi()

    def setupUi(self):
        layout = QVBoxLayout()

        self.username_label = QLabel("아이디:", self)
        layout.addWidget(self.username_label)
        self.username_edit = QLineEdit(self)
        layout.addWidget(self.username_edit)

        self.password_label = QLabel("비밀번호:", self)
        layout.addWidget(self.password_label)
        self.password_edit = QLineEdit(self)
        self.password_edit.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_edit)

        self.login_button = QPushButton("로그인", self)
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

        self.user_type_label = QLabel("사용자 유형:", self)
        layout.addWidget(self.user_type_label)

        self.user_type_admin = QRadioButton("관리자", self)
        self.user_type_kiosk = QRadioButton("키오스크", self)
        layout.addWidget(self.user_type_admin)
        layout.addWidget(self.user_type_kiosk)

        self.register_button = QPushButton("회원가입", self)
        self.register_button.clicked.connect(self.show_register_window)
        layout.addWidget(self.register_button)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def show_register_window(self):
        self.register_window = RegisterWindow()
        self.register_window.exec_()

    def login(self):
        username = self.username_edit.text()
        password = self.password_edit.text()

        if not self.user_type_admin.isChecked() and not self.user_type_kiosk.isChecked():
            QMessageBox.warning(self, "경고", "사용자 유형을 선택해주세요.")
            return

        if self.user_type_admin.isChecked():
            if login_user(username, password, "관리자"):
                self.open_admin_window()
        elif self.user_type_kiosk.isChecked():
            if login_user(username, password, "키오스크"):
                print("Login successful")
                self.open_kiosk_window()

    def open_admin_window(self):
        from adminwindow.Admin_Display import AdminDisplay
        admin_window = AdminDisplay(username=self.username_edit.text())
        admin_window.show()
        self.close()

    def open_kiosk_window(self):
        from MainWindow import MainWindow
        print("Opening kiosk window")
        self.close()
        self.kiosk_window = MainWindow()
        self.kiosk_window.show()



class RegisterWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("회원가입")
        self.setupUi()

    def setupUi(self):
        layout = QVBoxLayout()

        self.username_label = QLabel("아이디:", self)
        layout.addWidget(self.username_label)
        self.username_edit = QLineEdit(self)
        layout.addWidget(self.username_edit)

        self.check_button = QPushButton("중복 확인", self)
        self.check_button.clicked.connect(self.check_duplicate)
        layout.addWidget(self.check_button)

        self.password_label = QLabel("비밀번호:", self)
        layout.addWidget(self.password_label)
        self.password_edit = QLineEdit(self)
        self.password_edit.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_edit)

        self.confirm_password_label = QLabel("비밀번호 확인:", self)
        layout.addWidget(self.confirm_password_label)
        self.confirm_password_edit = QLineEdit(self)
        self.confirm_password_edit.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.confirm_password_edit)

        self.register_button = QPushButton("회원가입", self)
        self.register_button.clicked.connect(self.register)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

    def check_duplicate(self):
        username = self.username_edit.text()
        if not re.match("^(?=.*[a-zA-Z])(?=.*[0-9])[a-zA-Z0-9]{4,}$", username):
            QMessageBox.warning(self, "유효성 검사", "아이디는 영문자와 숫자의 조합으로 최소 4자 이상이어야 합니다.")
            return

        try:
            # MySQL 데이터베이스 연결
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="1234",
                database="kiosk"
            )

            # 커서 생성
            cursor = connection.cursor()

            # 사용자 정보 조회 쿼리
            select_query = "SELECT * FROM users WHERE username = %s"
            cursor.execute(select_query, (username,))
            user = cursor.fetchone()

            if user:
                QMessageBox.warning(self, "중복 확인", "이미 존재하는 아이디입니다.")
            else:
                QMessageBox.information(self, "중복 확인", "사용 가능한 아이디입니다.")

        except mysql.connector.Error as e:
            print("MySQL 오류:", e)

        finally:
            # 연결 종료
            if connection.is_connected():
                cursor.close()
                connection.close()

    def register(self):
        username = self.username_edit.text()
        password = self.password_edit.text()
        confirm_password = self.confirm_password_edit.text()

        if not self.validate_username(username) or not self.validate_password(password, confirm_password):
            return

        if register_user(username, password):
                self.close()

    def validate_username(self, username):
        if not re.match("^(?=.*[a-zA-Z])(?=.*[0-9])[a-zA-Z0-9]{4,}$", username):
            QMessageBox.warning(self, "유효성 검사", "아이디는 영문자와 숫자의 조합으로 최소 4자 이상이어야 합니다.")
            return False
        return True

    def validate_password(self, password, confirm_password):
        if password != confirm_password:
            QMessageBox.warning(self, "유효성 검사", "비밀번호와 비밀번호 확인이 일치하지 않습니다.")
            return False
        elif len(password) < 4:
            QMessageBox.warning(self, "유효성 검사", "비밀번호는 최소 4자 이상이어야 합니다.")
            return False
        return True

def register_user(username, password):
    try:
        # MySQL 데이터베이스 연결
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            database="kiosk"
        )

        # 커서 생성
        cursor = connection.cursor()

        # 사용자 정보 조회 쿼리
        select_query = "SELECT * FROM users WHERE username = %s"
        cursor.execute(select_query, (username,))
        user = cursor.fetchone()

        if user:
            QMessageBox.warning(None, "회원가입 실패", "이미 존재하는 아이디입니다.")
            return False

        # 사용자 정보를 INSERT 쿼리로 테이블에 저장
        insert_query = "INSERT INTO users (username, password) VALUES (%s, %s)"
        user_data = (username, password)
        cursor.execute(insert_query, user_data)

        # 변경사항을 커밋
        connection.commit()

        QMessageBox.information(None, "회원가입 성공", "회원가입이 완료되었습니다.")
        return True

    except mysql.connector.Error as e:
        print("MySQL 오류:", e)
        return False

    finally:
        # 연결 종료
        if connection.is_connected():
            cursor.close()
            connection.close()

def login_user(username, password, user_type):
    try:
        # MySQL 데이터베이스 연결
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            database="kiosk"
        )

        # 커서 생성
        cursor = connection.cursor()

        # 사용자 정보 조회 쿼리
        select_query = "SELECT * FROM users WHERE username = %s AND password = %s"
        user_data = (username, password)
        cursor.execute(select_query, user_data)
        user = cursor.fetchone()

        if user:
            QMessageBox.information(None, "로그인 성공", f"{user_type} 로그인 성공")
            return True

        else:
            QMessageBox.warning(None, "로그인 실패", "아이디 또는 비밀번호가 일치하지 않습니다.")
            return False

    except mysql.connector.Error as e:
        print("MySQL 오류:", e)
        return False

    finally:
        # 연결 종료
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())
