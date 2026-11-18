from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QLineEdit
import sys

def greet():
    name = name_input.text()
    greeting_label.setText(f"Hello, {name}")

app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("My First PyQt6 App")

layout = QVBoxLayout()
name_input = QLineEdit()
greeting_label = QLabel("")
button = QPushButton("Greet")
button.clicked.connect(greet)

layout.addWidget(name_input)
layout.addWidget(button)
layout.addWidget(greeting_label)

window.setLayout(layout)
window.show()
sys.exit(app.exec())