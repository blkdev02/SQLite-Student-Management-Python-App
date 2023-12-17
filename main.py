from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QLabel, QWidget, QGridLayout, \
QLineEdit, QPushButton, QMainWindow, QTableWidget, QTableWidgetItem, QDialog, QVBoxLayout, \
QComboBox, QToolBar, QStatusBar, QMessageBox
from PyQt6.QtGui import QAction, QIcon
import sys, sqlite3


class DatabaseConnection():
    def __init__(self, database_file="database.db"):
        self.database_file = database_file
    
    def connect(self):
        connection = sqlite3.connect(self.database_file)
        return connection



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management Ssystem")
        self.setMinimumSize(800,800)

        # Adding Menus
        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        edit_menu_item = self.menuBar().addMenu("&Edit")

        # File Sub Menu
        add_student_action = QAction(QIcon("icons/add.png"),"Add Student", self)
        add_student_action.triggered.connect(self.insert_data)
        file_menu_item.addAction(add_student_action)

        # Help  Sub Menu
        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        about_action.triggered.connect(self.about)
         # for macs about_action.setMenuRole(QAction.MenuRole.NoRole)

        # Edit Sub Menu
        search_action = QAction(QIcon("icons/search.png"), "Search", self)
        edit_menu_item.addAction(search_action)
        search_action.triggered.connect(self.search_data)

        # Create Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Id", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)
        # self.load_data

        # Create Toolbar and add toolbar elements
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)

        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

        # Create status bar and add status bar elements
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Detect a cell click
        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self):

        # Added Edit Record button
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit_data)

        # Added Delete Record button
        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete_data)

        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)

        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)

    def load_data(self):
        connection = DatabaseConnection().connect()
        result = connection.execute("SELECT * FROM students")
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            print(row_data)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        connection.close()

    
    def insert_data(self):
        dialog = InsertDialog()
        dialog.exec()
    
    def search_data(self):
        search_dialog = SearchDialog()
        search_dialog.exec()

    def edit_data(self):
        dialog = EditDialog()
        dialog.exec()

    def delete_data(self):
        dialog = DeleteDialog()
        dialog.exec()
    
    def about(self):
        dialog = AboutDialog()
        dialog.exec()


class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content = """This app is Student Management Python built to improve my OOP understanding"""
        self.setText(content)
        # self.exec()

class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(400)
    
        layout = QVBoxLayout()

        # Get Index and Id from selected row
        index = student_management_window.table.currentRow()
        self.student_id = student_management_window.table.item(index, 0).text()

        # Get student name
        student_name_data = student_management_window.table.item(index, 1).text()
        self.student_name = QLineEdit(student_name_data)
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # GET current course name
        course_data = student_management_window.table.item(index, 2).text()
        self.course_name = QComboBox()
        courses = ["Biology", "Maths", "Chemistry", "Physics"]
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(course_data)
        layout.addWidget(self.course_name)

        #   Get mobile number
        mobile_data = student_management_window.table.item(index, 3).text()
        self.mobile = QLineEdit(mobile_data)
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        # Add submit button
        button = QPushButton("Register")
        button.clicked.connect(self.update_student_data)
        layout.addWidget(button)


        self.setLayout(layout)

    
    def update_student_data(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = ?, course = ?, mobile = ? WHERE id = ?", 
                       (self.student_name.text(), 
                        self.course_name.itemText(self.course_name.currentIndex()), 
                        self.mobile.text(),
                        self.student_id))
        connection.commit()
        cursor.close()
        connection.close()

        # Refresh the table
        student_management_window.load_data()

 

class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Student Data")

        layout = QGridLayout()

        confirmation = QLabel("A you sure you want to delete student data?")
        yes = QPushButton("Yes")
        no = QPushButton("No")

        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)

        # yes deletion execution
        yes.clicked.connect(self.delete_student_data)

        self.setLayout(layout)

    
    def delete_student_data(self):
        # Get selected row index and student id 
        index = student_management_window.table.currentRow()
        student_id = student_management_window.table.item(index, 0).text()

        # Connection to database
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("DELETE from students WHERE  id = ?", (student_id, ))
        connection.commit()
                
        # Closing connection to database
        cursor.close()
        connection.close()

        # Refresh the table
        student_management_window.load_data()

        # Close the current delete window
        self.close()

        # Created a deletion confirmation box
        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("The record was deleted successfully!")
        confirmation_widget.exec()





class SearchDialog(QDialog):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(400)
    
        layout = QVBoxLayout()

        # Add student name widget
        self.search_name = QLineEdit()
        self.search_name.setPlaceholderText("Name")
        layout.addWidget(self.search_name)

        # Add submit button
        button = QPushButton("Search")
        button.clicked.connect(self.display_results)
        layout.addWidget(button)

        self.setLayout(layout)
    

    def display_results(self):
        search_name = self.search_name.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        result = cursor.execute("SELECT * FROM students WHERE name = ?",
                       (search_name,))
        rows = list(result)
        print(rows)
        items = student_management_window.table.findItems(search_name, Qt.MatchFlag.MatchFixedString)

        for item in items:
            print(item)
            student_management_window.table.item(item.row(),1).setSelected(True)

        cursor.close()
        connection.close()


class InsertDialog(QDialog):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(400)
    
        layout = QVBoxLayout()

        # Add student name widget
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Add combo box of courses
        self.course_name = QComboBox()
        courses = ["Biology", "Maths", "Chemistry", "Physics"]
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        # Add mobile number
        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("Mobile number")
        layout.addWidget(self.mobile)

        # Add submit button
        button = QPushButton("Register")
        button.clicked.connect(self.add_student)
        layout.addWidget(button)


        self.setLayout(layout)

    def add_student(self):
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.mobile.text()
        connection =DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES (?, ?, ?)",
                       (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()
        
        # Reload Data
        student_management_window.load_data()



app = QApplication(sys.argv)
student_management_window = MainWindow()
student_management_window.show()
student_management_window.load_data()
sys.exit(app.exec())