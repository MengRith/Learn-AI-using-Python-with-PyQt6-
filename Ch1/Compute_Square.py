from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QLineEdit
import sys

def compute_square():
    try:
        number = int(name_input.text())
        greeting_label.setText(f"Square = {number * number}")
    except ValueError:
        greeting_label.setText("Please enter a valid integer")
        
app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("Compute Square App")

# Widgets
name_input = QLineEdit()
name_input.setPlaceholderText("Enter a number")

greet_button = QPushButton("Compute Square")
greet_button.clicked.connect(compute_square)

greeting_label = QLabel("")

# Layout

layout = QVBoxLayout()
layout.addWidget(name_input)
layout.addWidget(greet_button)
layout.addWidget(greeting_label)

window.setLayout(layout)
window.show()
sys.exit(app.exec())