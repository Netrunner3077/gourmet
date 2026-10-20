import os
import sys
import PyQt5
import sqlite3

_qt_plugin_path = os.path.join(os.path.dirname(PyQt5.__file__), "Qt5", "plugins")
os.environ["QT_PLUGIN_PATH"] = _qt_plugin_path
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = os.path.join(_qt_plugin_path, "platforms")

from PyQt5.QtGui import *
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QDialog, QTextEdit
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class Login_and_registration(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.ch_btn = ''

    def initUI(self):
        self.setGeometry(800, 450, 300, 300)
        self.setWindowTitle('Регистрация и вход')
        self.setStyleSheet("color: #FF00FF; background-color:#00008B")

        self.login_text = QLabel('Логин...', self)
        self.login_text.setGeometry(120, 25 ,150, 30)
        self.login_text.setFont(QFont('Arial', 10))

        self.login_add = QLineEdit(self)
        self.login_add.setGeometry(80, 70, 150,20)
        self.login_add.setFont(QFont('Arial', 10))

        self.password_text = QLabel('Пароль...',self)
        self.password_text.setGeometry(120, 95, 170, 30)
        self.password_text.setFont(QFont('Arial', 10))

        self.password_add = QLineEdit(self)
        self.password_add.setEchoMode(QLineEdit.Password)
        self.password_add.setGeometry(80, 130, 150,20)
        self.password_add.setFont(QFont('Arial', 10))

        self.btn_star = QPushButton('*', self)
        self.btn_star.setGeometry(50, 130, 20, 20)
        self.btn_star.clicked.connect(self.star_)

        self.btn_sing_up = QPushButton('Войти', self)
        self.btn_sing_up.setGeometry(90, 160, 120,40)
        self.btn_sing_up.setFont(QFont('Arial', 10))
        self.btn_sing_up.clicked.connect(self.registration_and_log_in)

        self.btn_reg = QPushButton('Регистрация', self)
        self.btn_reg.setGeometry(90, 210, 120, 40)
        self.btn_reg.setFont(QFont('Arial', 10))
        self.btn_reg.clicked.connect(self.registration_and_log_in)

        self.ch_login_and_password = QLabel('', self)
        self.ch_login_and_password.setGeometry(10, 300, 400, 40)


    def star_(self):
        if self.password_add.echoMode() == QLineEdit.Normal:
            self.password_add.setEchoMode(QLineEdit.Password)
        else:
            self.password_add.setEchoMode(QLineEdit.Normal)

    def registration_and_log_in(self):
        self.login= self.login_add.text()
        lg = []
        self.password = self.password_add.text()
        self.ch_btn = self.sender().text()
        if self.ch_btn == 'Регистрация':
            self.password_text.setText('Новый пароль')
            self.password_text.setGeometry(90, 95, 170, 30)
            self.login_text.setText('Новый логин')
            self.login_text.setGeometry(100, 25 ,150, 30)

        conn = sqlite3.connect('base.db')
        cursor = conn.cursor()
        quer = "SELECT * FROM user"
        cursor.execute(quer)
        result = cursor.fetchall()
        cnd=0
        for i in range(len(result)):
            result[i] = list(result[i])
            lg += result[i]

        while cnd<len(result):


            if self.login in lg[::2]:
                self.ch_login_and_password.setText('Пользователь уже зарегистрирован')
                self.ch_login_and_password.setGeometry(15, 240, 300, 40)
                break

            else:
                if self.login not in lg and (len(self.login) < 4 or len(self.password) < 4 or (len(self.login) < 4 and len(self.password) < 4)):
                        self.ch_login_and_password.setText('Логин и пароль должен быть неменее 5\n                      символов')
                        self.ch_login_and_password.setGeometry(0, 255, 300, 40)
                        break
                else:
                    self.ch_login_and_password.setText('Логин и пароль сохранены')
                    self.ch_login_and_password.setGeometry(50, 240, 300, 40)
                    query = f"INSERT INTO user (login, password) VALUES ('{self.login}', '{self.password}')"
                    cursor.execute(query)
                    conn.commit()
                    break

            cnd += 1

        index = 0
        if self.ch_btn == 'Войти':
            while index < len(result):
                if (self.password not in result[index] and self.login in result[index]) or (self.password in result[index] and self.login not in result[index]):
                    self.ch_login_and_password.setText('Пароль или логин введены неправильно\n                 попробуйте снова')
                    self.ch_login_and_password.setGeometry(0, 250, 300, 40)
                    break

                elif self.password in result[index] and self.login in result[index]:
                    self.close()
                    self.window = Profile_user_chose_categories()
                    self.window.show()
                    break

                index += 1
        cursor.close()
        conn.close()

class Profile_user_chose_categories(QWidget):
    
    def __init__(self):
        super().__init__()
        self.initUI()
        self.ch_btn = ''

    def initUI(self):
        self.setGeometry(600, 100, 700, 700)
        self.setWindowTitle('Гурман')
        self.setStyleSheet("color: #FF00FF; background-color:#00008B")

        self.category = QLabel(self)
        self.category.setText('Выберете категорию:')
        self.category.setGeometry(280, 50, 190, 30)
        self.category.setFont(QFont('Arial', 10))

        self.btn_milk_food = QPushButton('Молочные изделия', self)
        self.btn_milk_food.setGeometry(230, 100, 300, 70)
        self.btn_milk_food.clicked.connect(self.transitions_milk_food)
        self.btn_milk_food.setFont(QFont('Arial', 10))
        self.btn_milk_food.setStyleSheet("color: yellow;")

        self.btn_meet_food = QPushButton('Мясные изделия', self)
        self.btn_meet_food.setGeometry(230, 200, 300, 70)
        self.btn_meet_food.clicked.connect(self.transitions_meet_food)
        self.btn_meet_food.setFont(QFont('Arial', 10))
        self.btn_meet_food.setStyleSheet("color: yellow;")

        self.btn_drinks = QPushButton('Газированные напитки', self)
        self.btn_drinks.setGeometry(230, 300, 300, 70)
        self.btn_drinks.clicked.connect(self.transitions_drinks)
        self.btn_drinks.setFont(QFont('Arial', 10))
        self.btn_drinks.setStyleSheet("color: yellow;")

        self.btn_log_out_account = QPushButton('Сменить аккаунт', self)
        self.btn_log_out_account.setGeometry(10, 640, 200, 50)
        self.btn_log_out_account.clicked.connect(self.transitions_exit_account)
        self.btn_log_out_account.setFont(QFont('Arial', 10))

        self.btn_exit_application = QPushButton('Закрыть приложение', self)
        self.btn_exit_application.setGeometry(490, 640, 200, 50)
        self.btn_exit_application.clicked.connect(self.transitions_exit)
        self.btn_exit_application.setFont(QFont('Arial', 10))

    def transitions_exit(self):
        self.close()
        
    def transitions_exit_account(self):
        self.close()
        self.window = Login_and_registration()
        self.window.show()

    def transitions_milk_food(self):
        self.close()
        self.window = Main_Milk_Food_Window()
        self.window.show()

    def transitions_meet_food(self):
        self.close()
        self.window = Main_Meet_Food_Window()
        self.window.show()

    def transitions_drinks(self):
        self.close()
        self.window = Main_Drinks_Window()
        self.window.show()
    
class Main_Milk_Food_Window(QWidget):
    
    def __init__(self):
        super().__init__()
        self.initUI()
        self.ch_btn = ''

    def initUI(self):
        self.setGeometry(600, 80, 800, 900)
        self.setWindowTitle('Гурман')
        self.setStyleSheet("color: #FF00FF; background-color:#00008B")
        
        self.label1 = QLabel(self)
        self.label1.setGeometry(50, 50, 200, 200)
        image_Milk = QPixmap("Milk.jpg")
        self.label1.setPixmap(image_Milk)
        self.label1.setCursor(Qt.PointingHandCursor)
        self.label1.setObjectName("milk")
        self.findChild(QLabel, "milk").mousePressEvent = self.on_milk_click

        self.label2 = QLabel(self)
        self.label2.setGeometry(300, 50, 200, 200)
        image_Cheese = QPixmap("Cheese.jpg")
        self.label2.setPixmap(image_Cheese)
        self.label2.setCursor(Qt.PointingHandCursor)
        self.label2.setObjectName("cheese")
        self.findChild(QLabel, "cheese").mousePressEvent = self.on_cheese_click

        self.label3 = QLabel(self)
        self.label3.setGeometry(550, 50, 200, 200)
        image_Cottage_cheese = QPixmap("Cottage cheese.jpg")
        self.label3.setPixmap(image_Cottage_cheese)
        self.label3.setCursor(Qt.PointingHandCursor)
        self.label3.setObjectName("cottage_cheese")
        self.findChild(QLabel, "cottage_cheese").mousePressEvent = self.on_cottage_cheese_click

        self.btn_log_out = QPushButton('Выйти из аккаунта', self)
        self.btn_log_out.setGeometry(570, 800, 200, 40)
        self.btn_log_out.clicked.connect(self.transition_log_in)
        self.btn_log_out.setFont(QFont('Arial', 10))

        self.btn_exit = QPushButton('Закрыть приложение', self)
        self.btn_exit.setGeometry(570, 850, 200, 40)
        self.btn_exit.clicked.connect(self.transition_exit_app)
        self.btn_exit.setFont(QFont('Arial', 10))

        self.btn_back = QPushButton('Назад', self)
        self.btn_back.setGeometry(300, 850, 130, 40)
        self.btn_back.clicked.connect(self.back_)
        self.btn_back.setFont(QFont('Arial', 10))

    def on_milk_click(self, event):
        self.close()
        self.window = Milk_Window()
        self.window.show()

    def on_cheese_click(self, event):
        self.close()
        self.window = Cheese_Window()
        self.window.show()

    def on_cottage_cheese_click(self, event):
        self.close()
        self.window = Cottage_Cheese_Window()
        self.window.show()

    def back_(self):
        self.close()
        self.window = Profile_user_chose_categories()
        self.window.show()

    def transition_exit_app(self):
        self.close()
        
    def transition_log_in(self):
        self.close()
        self.window = Login_and_registration()
        self.window.show()

class Milk_Window(QWidget):
    def __init__(self):
        super().__init__()
        self.index = 0
        self.setGeometry(600, 80, 800, 900)
        self.setWindowTitle('Молоко - Коровка из Кореновки - 2,5%')
        self.setStyleSheet("color: #FF00FF; background-color:#00008B")
        self.send_review = ''
        self.check_review = ''

        self.btn_back = QPushButton('Назад', self)
        self.btn_back.setGeometry(300, 850, 130, 40)
        self.btn_back.clicked.connect(self.back)
        self.btn_back.setFont(QFont('Arial', 10))

        self.btn_conclusion = QPushButton('Показать состав', self)
        self.btn_conclusion.setGeometry(530, 640, 250, 50)
        self.btn_conclusion.setFont(QFont('Arial', 10))
        self.btn_conclusion.clicked.connect(self.conclusion)

        self.btn_all_reviews = QPushButton('Показать отзывы', self)
        self.btn_all_reviews.setGeometry(530, 570, 250, 50)
        self.btn_all_reviews.setFont(QFont('Arial', 10))
        self.btn_all_reviews.clicked.connect(self.all_reviews)

        self.btn_delete = QPushButton('Очистить', self)
        self.btn_delete.setGeometry(530, 710, 250, 50)
        self.btn_delete.clicked.connect(self.delete_)
        self.btn_delete.setFont(QFont('Arial', 10))

        self.result = QLabel("Состав: ",self)
        self.result.setGeometry(10, 90, 500, 80)

        self.review_result = QLabel("Отзывы: ",self)
        self.review_result.setGeometry(10, 200, 500, 80)

        self.review = QTextEdit(self)
        self.review.setGeometry(20, 500, 500, 300)
        self.btn_review = QPushButton('Оставить отзыв', self)
        self.btn_review.setGeometry(530, 500, 250, 50)
        self.btn_review.clicked.connect(self.send_reviews)
        self.btn_review.setFont(QFont('Arial', 10))

    def send_reviews(self):
        self.send_review = self.sender().text()
        self.check_review = self.review.toPlainText()
        conn = sqlite3.connect('base.db')
        cursor = conn.cursor()
        quer = "SELECT milk_review FROM reviews"
        cursor.execute(quer)
        result = cursor.fetchall()
        if self.send_review == 'Оставить отзыв':
            query = f"INSERT INTO reviews (milk_review) VALUES ('{self.check_review}')"
            cursor.execute(query)
            conn.commit()
        cursor.close()
        conn.close()

    def back(self):
        self.close()
        self.window = Main_Milk_Food_Window()
        self.window.show()

    def delete_(self):
        self.result.setText('')
        self.review_result.setText('')

    def conclusion(self):
        conn = sqlite3.connect('base.db')
        cursor = conn.cursor()
        cursor.execute("SELECT info FROM milk_food WHERE name=?", ('Молоко - Коровка из Кореновки - 2,5%',))
        info = cursor.fetchone()
        cursor.close()
        conn.close()
        if info:
            self.result.setText(info[0])
            self.result.show()
        else:
            self.result.setText("Данные не найдены")
            self.result.show()

    def all_reviews(self):
        conn = sqlite3.connect('base.db')
        cursor = conn.cursor()
        cursor.execute("SELECT milk_review FROM reviews")
        milk_review = cursor.fetchall()
        cursor.close()
        conn.close()
        if milk_review:
            milk_review_text = "\n".join([str(row[0]) for row in milk_review])
            self.review_result.setText(milk_review_text)
            self.review_result.show()
        else:
            self.review_result.setText("Отзывов ещё нет")
            self.review_result.show() 
            
class Cheese_Window(QWidget):
    def __init__(self):
        super().__init__()
        self.index = 0
        self.send_review = ''
        self.check_review = ''
        self.setGeometry(600, 80, 800, 900)
        self.setWindowTitle('Сыр - Российский')
        self.setStyleSheet("color: #FF00FF; background-color:#00008B")

        self.btn_back = QPushButton('Назад', self)
        self.btn_back.setGeometry(300, 850, 130, 40)
        self.btn_back.clicked.connect(self.back)
        self.btn_back.setFont(QFont('Arial', 10))

        self.btn_conclusion = QPushButton('Показать состав', self)
        self.btn_conclusion.setGeometry(530, 640, 250, 50)
        self.btn_conclusion.setFont(QFont('Arial', 10))
        self.btn_conclusion.clicked.connect(self.conclusion)

        self.btn_delete = QPushButton('Очистить', self)
        self.btn_delete.setGeometry(530, 710, 250, 50)
        self.btn_delete.clicked.connect(self.delete_)
        self.btn_delete.setFont(QFont('Arial', 10))

        self.result = QLabel("Состав: ",self)
        self.result.setGeometry(10, 90, 500, 80)

        self.review = QTextEdit(self)
        self.review.setGeometry(20, 500, 500, 300)
        self.btn_review = QPushButton('Оставить отзыв', self)
        self.btn_review.setGeometry(530, 500, 250, 50)
        self.btn_review.clicked.connect(self.send_reviews)
        self.btn_review.setFont(QFont('Arial', 10))

        self.btn_all_reviews = QPushButton('Показать отзывы', self)
        self.btn_all_reviews.setGeometry(530, 570, 250, 50)
        self.btn_all_reviews.setFont(QFont('Arial', 10))
        self.btn_all_reviews.clicked.connect(self.all_reviews)

        self.review_result = QLabel("Отзывы: ",self)
        self.review_result.setGeometry(10, 200, 500, 80)

    def all_reviews(self):
        conn = sqlite3.connect('base.db')
        cursor = conn.cursor()
        cursor.execute("SELECT cheese_review FROM reviews")
        milk_review = cursor.fetchall()
        cursor.close()
        conn.close()
        if milk_review:
            milk_review_text = "\n".join([str(row[0]) for row in milk_review])
            self.review_result.setText(milk_review_text)
            self.review_result.show()
        else:
            self.review_result.setText("Отзывов ещё нет")
            self.review_result.show()

    def send_reviews(self):
        self.send_review = self.sender().text()
        self.check_review = self.review.toPlainText()
        conn = sqlite3.connect('base.db')
        cursor = conn.cursor()
        quer = "SELECT cheese_review FROM reviews"
        cursor.execute(quer)
        result = cursor.fetchall()
        if self.send_review == 'Оставить отзыв':
            query = f"INSERT INTO reviews (cheese_review) VALUES ('{self.check_review}')"
            cursor.execute(query)
            conn.commit()
        cursor.close()
        conn.close()

    def back(self):
        self.close()
        self.window = Main_Milk_Food_Window()
        self.window.show()

    def delete_(self):
        self.result.setText('')
        self.review_result.setText('')

    def conclusion(self):
        conn = sqlite3.connect('base.db')
        cursor = conn.cursor()
        cursor.execute("SELECT info FROM milk_food WHERE name='Сыр'")
        info = cursor.fetchone()
        cursor.close()
        conn.close()
        if info:
            self.result.setText(info[0])
            self.result.show()
        else:
            self.result.setText("Данные не найдены")
            self.result.show()

class Cottage_Cheese_Window(QWidget):
    def __init__(self):
        super().__init__()
        self.index = 0
        self.send_review = ''
        self.check_review = ''
        self.setGeometry(600, 80, 800, 900)
        self.setWindowTitle('Творог - Простоквашино - 9%')
        self.setStyleSheet("color: #FF00FF; background-color:#00008B")

        self.btn_back = QPushButton('Назад', self)
        self.btn_back.setGeometry(300, 850, 130, 40)
        self.btn_back.clicked.connect(self.back)
        self.btn_back.setFont(QFont('Arial', 10))

        self.btn_conclusion = QPushButton('Показать состав', self)
        self.btn_conclusion.setGeometry(530, 640, 250, 50)
        self.btn_conclusion.setFont(QFont('Arial', 10))
        self.btn_conclusion.clicked.connect(self.conclusion)

        self.btn_delete = QPushButton('Очистить', self)
        self.btn_delete.setGeometry(530, 710, 250, 50)
        self.btn_delete.clicked.connect(self.delete_)
        self.btn_delete.setFont(QFont('Arial', 10))

        self.result = QLabel("Состав: ",self)
        self.result.setGeometry(10, 90, 500, 80)

        self.review = QTextEdit(self)
        self.review.setGeometry(20, 500, 500, 300)
        self.btn_review = QPushButton('Оставить отзыв', self)
        self.btn_review.setGeometry(530, 500, 250, 50)
        self.btn_review.clicked.connect(self.send_reviews)
        self.btn_review.setFont(QFont('Arial', 10))

        self.btn_all_reviews = QPushButton('Показать отзывы', self)
        self.btn_all_reviews.setGeometry(530, 570, 250, 50)
        self.btn_all_reviews.setFont(QFont('Arial', 10))
        self.btn_all_reviews.clicked.connect(self.all_reviews)

        self.review_result = QLabel("Отзывы: ",self)
        self.review_result.setGeometry(10, 200, 500, 80)

    def all_reviews(self):
        conn = sqlite3.connect('base.db')
        cursor = conn.cursor()
        cursor.execute("SELECT cottage_cheese_review FROM reviews")
        milk_review = cursor.fetchall()
        cursor.close()
        conn.close()
        if milk_review:
            milk_review_text = "\n".join([str(row[0]) for row in milk_review])
            self.review_result.setText(milk_review_text)
            self.review_result.show()
        else:
            self.review_result.setText("Отзывов ещё нет")
            self.review_result.show()

    def send_reviews(self):
        self.send_review = self.sender().text()
        self.check_review = self.review.toPlainText()
        conn = sqlite3.connect('base.db')
        cursor = conn.cursor()
        quer = "SELECT cottage_cheese_review FROM reviews"
        cursor.execute(quer)
        result = cursor.fetchall()
        if self.send_review == 'Оставить отзыв':
            query = f"INSERT INTO reviews (cottage_cheese_review) VALUES ('{self.check_review}')"
            cursor.execute(query)
            conn.commit()
        cursor.close()
        conn.close()

    def back(self):
        self.close()
        self.window = Main_Milk_Food_Window()
        self.window.show()

    def delete_(self):
        self.result.setText('')
        self.review_result.setText('')

    def conclusion(self):
        conn = sqlite3.connect('base.db')
        cursor = conn.cursor()
        cursor.execute("SELECT info FROM milk_food WHERE name='Творог'")
        info = cursor.fetchone()
        cursor.close()
        conn.close()
        if info:
            self.result.setText(info[0])
            self.result.show()
        else:
            self.result.setText("Данные не найдены")
            self.result.show()

class Main_Meet_Food_Window(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.ch_btn = ''

    def initUI(self):
        self.setGeometry(600, 80, 800, 900)
        self.setWindowTitle('Гурман')
        self.setStyleSheet("color: #FF00FF; background-color:#00008B")
        
        self.label4 = QLabel(self)
        self.label4.setGeometry(50, 50, 200, 200)
        image_Sausage = QPixmap("Sausage.jpg")
        self.label4.setPixmap(image_Sausage)
        self.label4.setCursor(Qt.PointingHandCursor)
        self.label4.setObjectName("sausage")
        self.findChild(QLabel, "sausage").mousePressEvent = self.on_sausage_click

        self.label5 = QLabel(self)
        self.label5.setGeometry(300, 50, 200, 200)
        image_Schnitzel = QPixmap("Schnitzel.jpg")
        self.label5.setPixmap(image_Schnitzel)
        self.label5.setCursor(Qt.PointingHandCursor)
        self.label5.setObjectName("schnitzel")
        self.findChild(QLabel, "schnitzel").mousePressEvent = self.on_schnitzel_click

        self.label6 = QLabel(self)
        self.label6.setGeometry(550, 50, 200, 200)
        image_Chicken = QPixmap("Chicken.jpg")
        self.label6.setPixmap(image_Chicken)
        self.label6.setCursor(Qt.PointingHandCursor)
        self.label6.setObjectName("chicken")
        self.findChild(QLabel, "chicken").mousePressEvent = self.on_chicken_click

        self.btn_log_out = QPushButton('Выйти из аккаунта', self)
        self.btn_log_out.setGeometry(570, 800, 200, 40)
        self.btn_log_out.clicked.connect(self.transition_log_in)
        self.btn_log_out.setFont(QFont('Arial', 10))

        self.btn_exit = QPushButton('Закрыть приложение', self)
        self.btn_exit.setGeometry(570, 850, 200, 40)
        self.btn_exit.clicked.connect(self.transition_exit_app)
        self.btn_exit.setFont(QFont('Arial', 10))

        self.btn_back = QPushButton('Назад', self)
        self.btn_back.setGeometry(300, 850, 130, 40)
        self.btn_back.clicked.connect(self.back_)
        self.btn_back.setFont(QFont('Arial', 10))

    def on_sausage_click(self, event):
        self.close()
        self.window = Sausage_Window()
        self.window.show()

    def on_schnitzel_click(self, event):
        self.close()
        self.window = Schnitzel_Window()
        self.window.show()

    def on_chicken_click(self, event):
        self.close()
        self.window = Chicken_Window()
        self.window.show()

    def back_(self):
        self.close()
        self.window = Profile_user_chose_categories()
        self.window.show()

    def transition_exit_app(self):
        self.close()
        
    def transition_log_in(self):
        self.close()
        self.window = Login_and_registration()
        self.window.show()

class Sausage_Window(QWidget):
    def __init__(self):
        super().__init__()
        self.index = 0
        self.send_review = ''
        self.check_review = ''
        self.setGeometry(600, 80, 800, 900)
        self.setWindowTitle('Докторская колбаса')
        self.setStyleSheet("color: #FF00FF; background-color:#00008B")

        self.btn_back = QPushButton('Назад', self)
        self.btn_back.setGeometry(300, 850, 130, 40)
        self.btn_back.clicked.connect(self.back)
        self.btn_back.setFont(QFont('Arial', 10))

        self.btn_conclusion = QPushButton('Показать состав', self)
        self.btn_conclusion.setGeometry(530, 640, 250, 50)
        self.btn_conclusion.setFont(QFont('Arial', 10))
        self.btn_conclusion.clicked.connect(self.conclusion)

        self.btn_delete = QPushButton('Очистить', self)
        self.btn_delete.setGeometry(530, 710, 250, 50)
        self.btn_delete.clicked.connect(self.delete_)
        self.btn_delete.setFont(QFont('Arial', 10))

        self.result = QLabel("Состав: ",self)
        self.result.setGeometry(10, 90, 500, 80)

        self.review = QTextEdit(self)
        self.review.setGeometry(20, 500, 500, 300)
        self.btn_review = QPushButton('Оставить отзыв', self)
        self.btn_review.setGeometry(530, 500, 250, 50)
        self.btn_review.clicked.connect(self.send_reviews)
        self.btn_review.setFont(QFont('Arial', 10))

        self.btn_all_reviews = QPushButton('Показать отзывы', self)
        self.btn_all_reviews.setGeometry(530, 570, 250, 50)
        self.btn_all_reviews.setFont(QFont('Arial', 10))
        self.btn_all_reviews.clicked.connect(self.all_reviews)

        self.review_result = QLabel("Отзывы: ",self)
        self.review_result.setGeometry(10, 200, 500, 80)

    def all_reviews(self):
        conn = sqlite3.connect('base.db')
        cursor = conn.cursor()
        cursor.execute("SELECT sausage_review FROM reviews")
        milk_review = cursor.fetchall()
        cursor.close()
        conn.close()
        if milk_review:
            milk_review_text = "\n".join([str(row[0]) for row in milk_review])
            self.review_result.setText(milk_review_text)
            self.review_result.show()
        else:
            self.review_result.setText("Отзывов ещё нет")
            self.review_result.show()

    def send_reviews(self):
        self.send_review = self.sender().text()
        self.check_review = self.review.toPlainText()
        conn = sqlite3.connect('base.db')
        cursor = conn.cursor()
        quer = "SELECT sausage_review FROM reviews"
        cursor.execute(quer)
        result = cursor.fetchall()
        if self.send_review == 'Оставить отзыв':
            query = f"INSERT INTO reviews (sausage_review) VALUES ('{self.check_review}')"
            cursor.execute(query)
            conn.commit()
        cursor.close()
        conn.close()

    def delete_(self):
        self.result.setText('')
        self.review_result.setText('')

    def conclusion(self):
        conn = sqlite3.connect('base.db')
        cursor = conn.cursor()
        cursor.execute("SELECT info FROM meet_food WHERE name='Колбаса докторская (варёная) - Тавр'")
        info = cursor.fetchone()
        cursor.close()
        conn.close()
        if info:
            self.result.setText(info[0])
            self.result.show()
        else:
            self.result.setText("Данные не найдены")
            self.result.show()

    def back(self):
        self.close()
        self.window = Main_Meet_Food_Window()
        self.window.show()

class Schnitzel_Window(QWidget):
    def __init__(self):
        super().__init__()
        self.send_review = ''
        self.check_review = ''
        self.index = 0
        self.setGeometry(600, 80, 800, 900)
        self.setWindowTitle('Шницель')
        self.setStyleSheet("color: #FF00FF; background-color:#00008B")

        self.btn_back = QPushButton('Назад', self)
        self.btn_back.setGeometry(300, 850, 130, 40)
        self.btn_back.clicked.connect(self.back)
        self.btn_back.setFont(QFont('Arial', 10))

        self.btn_conclusion = QPushButton('Показать состав', self)
        self.btn_conclusion.setGeometry(530, 640, 250, 50)
        self.btn_conclusion.setFont(QFont('Arial', 10))
        self.btn_conclusion.clicked.connect(self.conclusion)

        self.btn_delete = QPushButton('Очистить', self)
        self.btn_delete.setGeometry(530, 710, 250, 50)
        self.btn_delete.clicked.connect(self.delete_)
        self.btn_delete.setFont(QFont('Arial', 10))

        self.result = QLabel("Состав: ",self)
        self.result.setGeometry(10, 90, 500, 80)

        self.review = QTextEdit(self)
        self.review.setGeometry(20, 500, 500, 300)
        self.btn_review = QPushButton('Оставить отзыв', self)
        self.btn_review.setGeometry(530, 500, 250, 50)
        self.btn_review.clicked.connect(self.send_reviews)
        self.btn_review.setFont(QFont('Arial', 10))

        self.btn_all_reviews = QPushButton('Показать отзывы', self)
        self.btn_all_reviews.setGeometry(530, 570, 250, 50)
        self.btn_all_reviews.setFont(QFont('Arial', 10))
        self.btn_all_reviews.clicked.connect(self.all_reviews)

        self.review_result = QLabel("Отзывы: ",self)
        self.review_result.setGeometry(10, 200, 500, 80)

    def all_reviews(self):
        conn = sqlite3.connect('base.db')
        cursor = conn.cursor()
        cursor.execute("SELECT schnitzel_review FROM reviews")
        milk_review = cursor.fetchall()
        cursor.close()
        conn.close()
        if milk_review:
            milk_review_text = "\n".join([str(row[0]) for row in milk_review])
            self.review_result.setText(milk_review_text)
            self.review_result.show()
        else:
            self.review_result.setText("Отзывов ещё нет")
            self.review_result.show()

    def send_reviews(self):
        self.send_review = self.sender().text()
        self.check_review = self.review.toPlainText()
        conn = sqlite3.connect('base.db')
        cursor = conn.cursor()
        quer = "SELECT schnitzel_review FROM reviews"
        cursor.execute(quer)
        result = cursor.fetchall()
        if self.send_review == 'Оставить отзыв':
            query = f"INSERT INTO reviews (schnitzel_review) VALUES ('{self.check_review}')"
            cursor.execute(query)
            conn.commit()
        cursor.close()
        conn.close()

    def delete_(self):
        self.result.setText('')
        self.review_result.setText('')

    def conclusion(self):
        conn = sqlite3.connect('base.db')
        cursor = conn.cursor()
        cursor.execute("SELECT info FROM meet_food WHERE name='Шницель из свинины - ДАльние ДАли'")
        info = cursor.fetchone()
        cursor.close()
        conn.close()
        if info:
            self.result.setText(info[0])
            self.result.show()
        else:
            self.result.setText("Данные не найдены")
            self.result.show()

    def back(self):
        self.close()
        self.window = Main_Meet_Food_Window()
        self.window.show()

class Chicken_Window(QWidget):
    def __init__(self):
        super().__init__()
        self.index = 0
        self.send_review = ''
        self.check_review = ''
        self.setGeometry(600, 80, 800, 900)
        self.setWindowTitle('Курица')
        self.setStyleSheet("color: #FF00FF; background-color:#00008B")

        self.btn_back = QPushButton('Назад', self)
        self.btn_back.setGeometry(300, 850, 130, 40)
        self.btn_back.clicked.connect(self.back)
        self.btn_back.setFont(QFont('Arial', 10))

        self.btn_conclusion = QPushButton('Показать состав', self)
        self.btn_conclusion.setGeometry(530, 640, 250, 50)
        self.btn_conclusion.setFont(QFont('Arial', 10))
        self.btn_conclusion.clicked.connect(self.conclusion)

        self.btn_delete = QPushButton('Очистить', self)
        self.btn_delete.setGeometry(530, 710, 250, 50)
        self.btn_delete.clicked.connect(self.delete_)
        self.btn_delete.setFont(QFont('Arial', 10))

        self.result = QLabel("Состав: ",self)
        self.result.setGeometry(10, 90, 500, 80)

        self.review = QTextEdit(self)
        self.review.setGeometry(20, 500, 500, 300)
        self.btn_review = QPushButton('Оставить отзыв', self)
        self.btn_review.setGeometry(530, 500, 250, 50)
        self.btn_review.clicked.connect(self.send_reviews)
        self.btn_review.setFont(QFont('Arial', 10))

        self.btn_all_reviews = QPushButton('Показать отзывы', self)
        self.btn_all_reviews.setGeometry(530, 570, 250, 50)
        self.btn_all_reviews.setFont(QFont('Arial', 10))
        self.btn_all_reviews.clicked.connect(self.all_reviews)

        self.review_result = QLabel("Отзывы: ",self)
        self.review_result.setGeometry(10, 200, 500, 80)

    def all_reviews(self):
        conn = sqlite3.connect('base.db')
        cursor = conn.cursor()
        cursor.execute("SELECT chicken_review FROM reviews")
        milk_review = cursor.fetchall()
        cursor.close()
        conn.close()
        if milk_review:
            milk_review_text = "\n".join([str(row[0]) for row in milk_review])
            self.review_result.setText(milk_review_text)
            self.review_result.show()
        else:
            self.review_result.setText("Отзывов ещё нет")
            self.review_result.show()

    def send_reviews(self):
        self.send_review = self.sender().text()
        self.check_review = self.review.toPlainText()
        conn = sqlite3.connect('base.db')
        cursor = conn.cursor()
        quer = "SELECT chicken_review FROM reviews"
        cursor.execute(quer)
        result = cursor.fetchall()
        if self.send_review == 'Оставить отзыв':
            query = f"INSERT INTO reviews (chicken_review) VALUES ('{self.check_review}')"
            cursor.execute(query)
            conn.commit()
        cursor.close()
        conn.close()

    def delete_(self):
        self.result.setText('')
        self.review_result.setText('')

    def conclusion(self):
        conn = sqlite3.connect('base.db')
        cursor = conn.cursor()
        cursor.execute("SELECT info FROM meet_food WHERE name='Курица - Цыплёнок-бройлер - Белая Птица'")
        info = cursor.fetchone()
        cursor.close()
        conn.close()
        if info:
            self.result.setText(info[0])
            self.result.show()
        else:
            self.result.setText("Данные не найдены")
            self.result.show()

    def back(self):
        self.close()
        self.window = Main_Meet_Food_Window()
        self.window.show()

class Main_Drinks_Window(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.ch_btn = ''

    def initUI(self):
        self.setGeometry(600, 80, 800, 900)
        self.setWindowTitle('Гурман')
        self.setStyleSheet("color: #FF00FF; background-color:#00008B")
        
        self.label7 = QLabel(self)
        self.label7.setGeometry(50, 50, 200, 200)
        image_Good_kola = QPixmap("Good_kola.jpg")
        self.label7.setPixmap(image_Good_kola)
        self.label7.setCursor(Qt.PointingHandCursor)
        self.label7.setObjectName("good_kola")
        self.findChild(QLabel, "good_kola").mousePressEvent = self.on_good_kola_click

        self.label8 = QLabel(self)
        self.label8.setGeometry(300, 50, 200, 200)
        image_Bitter = QPixmap("Bitter.jpg")
        self.label8.setPixmap(image_Bitter)
        self.label8.setCursor(Qt.PointingHandCursor)
        self.label8.setObjectName("bitter")
        self.findChild(QLabel, "bitter").mousePressEvent = self.on_bitter_click

        self.label9 = QLabel(self)
        self.label9.setGeometry(550, 50, 200, 200)
        image_Kvas = QPixmap("Kvas.jpg")
        self.label9.setPixmap(image_Kvas)
        self.label9.setCursor(Qt.PointingHandCursor)
        self.label9.setObjectName("kvas")
        self.findChild(QLabel, "kvas").mousePressEvent = self.on_kvas_click

        self.btn_log_out = QPushButton('Выйти из аккаунта', self)
        self.btn_log_out.setGeometry(570, 800, 200, 40)
        self.btn_log_out.clicked.connect(self.transition_log_in)
        self.btn_log_out.setFont(QFont('Arial', 10))

        self.btn_exit = QPushButton('Закрыть приложение', self)
        self.btn_exit.setGeometry(570, 850, 200, 40)
        self.btn_exit.clicked.connect(self.transition_exit_app)
        self.btn_exit.setFont(QFont('Arial', 10))

        self.btn_back = QPushButton('Назад', self)
        self.btn_back.setGeometry(300, 850, 130, 40)
        self.btn_back.clicked.connect(self.back_)
        self.btn_back.setFont(QFont('Arial', 10))

    def on_good_kola_click(self, event):
        self.close()
        self.window = Good_kola_Window()
        self.window.show()

    def on_bitter_click(self, event):
        self.close()
        self.window = Bitter_Window()
        self.window.show()

    def on_kvas_click(self, event):
        self.close()
        self.window = Kvas_Window()
        self.window.show()

    def back_(self):
        self.close()
        self.window = Profile_user_chose_categories()
        self.window.show()

    def transition_exit_app(self):
        self.close()
        
    def transition_log_in(self):
        self.close()
        self.window = Login_and_registration()
        self.window.show()

class Good_kola_Window(QWidget):
    def __init__(self):
        super().__init__()
        self.index = 0
        self.send_review = ''
        self.check_review = ''
        self.setGeometry(600, 80, 800, 900)
        self.setWindowTitle('Добрый Кола')
        self.setStyleSheet("color: #FF00FF; background-color:#00008B")

        self.btn_back = QPushButton('Назад', self)
        self.btn_back.setGeometry(300, 850, 130, 40)
        self.btn_back.clicked.connect(self.back)
        self.btn_back.setFont(QFont('Arial', 10))

        self.btn_conclusion = QPushButton('Показать состав', self)
        self.btn_conclusion.setGeometry(530, 640, 250, 50)
        self.btn_conclusion.setFont(QFont('Arial', 10))
        self.btn_conclusion.clicked.connect(self.conclusion)

        self.btn_delete = QPushButton('Очистить', self)
        self.btn_delete.setGeometry(530, 710, 250, 50)
        self.btn_delete.clicked.connect(self.delete_)
        self.btn_delete.setFont(QFont('Arial', 10))

        self.result = QLabel("Состав: ",self)
        self.result.setGeometry(10, 90, 500, 80)

        self.review = QTextEdit(self)
        self.review.setGeometry(20, 500, 500, 300)
        self.btn_review = QPushButton('Оставить отзыв', self)
        self.btn_review.setGeometry(530, 500, 250, 50)
        self.btn_review.clicked.connect(self.send_reviews)
        self.btn_review.setFont(QFont('Arial', 10))

        self.btn_all_reviews = QPushButton('Показать отзывы', self)
        self.btn_all_reviews.setGeometry(530, 570, 250, 50)
        self.btn_all_reviews.setFont(QFont('Arial', 10))
        self.btn_all_reviews.clicked.connect(self.all_reviews)

        self.review_result = QLabel("Отзывы: ",self)
        self.review_result.setGeometry(10, 200, 500, 80)

    def all_reviews(self):
        conn = sqlite3.connect('base.db')
        cursor = conn.cursor()
        cursor.execute("SELECT kola_review FROM reviews")
        milk_review = cursor.fetchall()
        cursor.close()
        conn.close()
        if milk_review:
            milk_review_text = "\n".join([str(row[0]) for row in milk_review])
            self.review_result.setText(milk_review_text)
            self.review_result.show()
        else:
            self.review_result.setText("Отзывов ещё нет")
            self.review_result.show()

    def send_reviews(self):
        self.send_review = self.sender().text()
        self.check_review = self.review.toPlainText()
        conn = sqlite3.connect('base.db')
        cursor = conn.cursor()
        quer = "SELECT kola_review FROM reviews"
        cursor.execute(quer)
        result = cursor.fetchall()
        if self.send_review == 'Оставить отзыв':
            query = f"INSERT INTO reviews (kola_review) VALUES ('{self.check_review}')"
            cursor.execute(query)
            conn.commit()
        cursor.close()
        conn.close()

    def delete_(self):
        self.result.setText('')
        self.review_result.setText('')

    def conclusion(self):
        conn = sqlite3.connect('base.db')
        cursor = conn.cursor()
        cursor.execute("SELECT info FROM drinks_food WHERE name='Добрый кола'")
        info = cursor.fetchone()
        cursor.close()
        conn.close()
        if info:
            self.result.setText(info[0])
            self.result.show()
        else:
            self.result.setText("Данные не найдены")
            self.result.show()

    def back(self):
        self.close()
        self.window = Main_Drinks_Window()
        self.window.show()

class Bitter_Window(QWidget):
    def __init__(self):
        super().__init__()
        self.index = 0
        self.send_review = ''
        self.check_review = ''
        self.setGeometry(600, 80, 800, 900)
        self.setWindowTitle('Bitter')
        self.setStyleSheet("color: #FF00FF; background-color:#00008B")

        self.btn_back = QPushButton('Назад', self)
        self.btn_back.setGeometry(300, 850, 130, 40)
        self.btn_back.clicked.connect(self.back)
        self.btn_back.setFont(QFont('Arial', 10))

        self.btn_conclusion = QPushButton('Показать состав', self)
        self.btn_conclusion.setGeometry(530, 640, 250, 50)
        self.btn_conclusion.setFont(QFont('Arial', 10))
        self.btn_conclusion.clicked.connect(self.conclusion)

        self.btn_delete = QPushButton('Очистить', self)
        self.btn_delete.setGeometry(530, 710, 250, 50)
        self.btn_delete.clicked.connect(self.delete_)
        self.btn_delete.setFont(QFont('Arial', 10))

        self.result = QLabel("Состав: ",self)
        self.result.setGeometry(10, 90, 500, 80)

        self.review = QTextEdit(self)
        self.review.setGeometry(20, 500, 500, 300)
        self.btn_review = QPushButton('Оставить отзыв', self)
        self.btn_review.setGeometry(530, 500, 250, 50)
        self.btn_review.clicked.connect(self.send_reviews)
        self.btn_review.setFont(QFont('Arial', 10))

        self.btn_all_reviews = QPushButton('Показать отзывы', self)
        self.btn_all_reviews.setGeometry(530, 570, 250, 50)
        self.btn_all_reviews.setFont(QFont('Arial', 10))
        self.btn_all_reviews.clicked.connect(self.all_reviews)

        self.review_result = QLabel("Отзывы: ",self)
        self.review_result.setGeometry(10, 200, 500, 80)

    def all_reviews(self):
        conn = sqlite3.connect('base.db')
        cursor = conn.cursor()
        cursor.execute("SELECT bitter_review FROM reviews")
        milk_review = cursor.fetchall()
        cursor.close()
        conn.close()
        if milk_review:
            milk_review_text = "\n".join([str(row[0]) for row in milk_review])
            self.review_result.setText(milk_review_text)
            self.review_result.show()
        else:
            self.review_result.setText("Отзывов ещё нет")
            self.review_result.show()

    def send_reviews(self):
        self.send_review = self.sender().text()
        self.check_review = self.review.toPlainText()
        conn = sqlite3.connect('base.db')
        cursor = conn.cursor()
        quer = "SELECT bitter_review FROM reviews"
        cursor.execute(quer)
        result = cursor.fetchall()
        if self.send_review == 'Оставить отзыв':
            query = f"INSERT INTO reviews (bitter_review) VALUES ('{self.check_review}')"
            cursor.execute(query)
            conn.commit()
        cursor.close()
        conn.close()

    def delete_(self):
        self.result.setText('')
        self.review_result.setText('')

    def conclusion(self):
        conn = sqlite3.connect('base.db')
        cursor = conn.cursor()
        cursor.execute("SELECT info FROM drinks_food WHERE name='Bitter'")
        info = cursor.fetchone()
        cursor.close()
        conn.close()
        if info:
            self.result.setText(info[0])
            self.result.show()
        else:
            self.result.setText("Данные не найдены")
            self.result.show()

    def back(self):
        self.close()
        self.window = Main_Drinks_Window()
        self.window.show()

class Kvas_Window(QWidget):
    def __init__(self):
        super().__init__()
        self.index = 0
        self.send_review = ''
        self.check_review = ''
        self.setGeometry(600, 80, 800, 900)
        self.setWindowTitle('Квас Русский Дар')
        self.setStyleSheet("color: #FF00FF; background-color:#00008B")

        self.btn_back = QPushButton('Назад', self)
        self.btn_back.setGeometry(300, 850, 130, 40)
        self.btn_back.clicked.connect(self.back)
        self.btn_back.setFont(QFont('Arial', 10))

        self.btn_conclusion = QPushButton('Показать состав', self)
        self.btn_conclusion.setGeometry(530, 640, 250, 50)
        self.btn_conclusion.setFont(QFont('Arial', 10))
        self.btn_conclusion.clicked.connect(self.conclusion)

        self.btn_delete = QPushButton('Очистить', self)
        self.btn_delete.setGeometry(530, 710, 250, 50)
        self.btn_delete.clicked.connect(self.delete_)
        self.btn_delete.setFont(QFont('Arial', 10))

        self.result = QLabel("Состав: ",self)
        self.result.setGeometry(10, 90, 500, 80)

        self.review = QTextEdit(self)
        self.review.setGeometry(20, 500, 500, 300)
        self.btn_review = QPushButton('Оставить отзыв', self)
        self.btn_review.setGeometry(530, 500, 250, 50)
        self.btn_review.clicked.connect(self.send_reviews)
        self.btn_review.setFont(QFont('Arial', 10))

        self.btn_all_reviews = QPushButton('Показать отзывы', self)
        self.btn_all_reviews.setGeometry(530, 570, 250, 50)
        self.btn_all_reviews.setFont(QFont('Arial', 10))
        self.btn_all_reviews.clicked.connect(self.all_reviews)

        self.review_result = QLabel("Отзывы: ",self)
        self.review_result.setGeometry(10, 200, 500, 80)

    def all_reviews(self):
        conn = sqlite3.connect('base.db')
        cursor = conn.cursor()
        cursor.execute("SELECT kvas_review FROM reviews")
        milk_review = cursor.fetchall()
        cursor.close()
        conn.close()
        if milk_review:
            milk_review_text = "\n".join([str(row[0]) for row in milk_review])
            self.review_result.setText(milk_review_text)
            self.review_result.show()
        else:
            self.review_result.setText("Отзывов ещё нет")
            self.review_result.show()

    def send_reviews(self):
        self.send_review = self.sender().text()
        self.check_review = self.review.toPlainText()
        conn = sqlite3.connect('base.db')
        cursor = conn.cursor()
        quer = "SELECT kvas_review FROM reviews"
        cursor.execute(quer)
        result = cursor.fetchall()
        if self.send_review == 'Оставить отзыв':
            query = f"INSERT INTO reviews (kvas_review) VALUES ('{self.check_review}')"
            cursor.execute(query)
            conn.commit()
        cursor.close()
        conn.close()

    def delete_(self):
        self.result.setText('')
        self.review_result.setText('')

    def conclusion(self):
        conn = sqlite3.connect('base.db')
        cursor = conn.cursor()
        cursor.execute("SELECT info FROM drinks_food WHERE name='Квас - Русский Дар'")
        info = cursor.fetchone()
        cursor.close()
        conn.close()
        if info:
            self.result.setText(info[0])
            self.result.show()
        else:
            self.result.setText("Данные не найдены")
            self.result.show()

    def back(self):
        self.close()
        self.window = Main_Drinks_Window()
        self.window.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Login_and_registration()
    ex.show()
    sys.exit(app.exec())
