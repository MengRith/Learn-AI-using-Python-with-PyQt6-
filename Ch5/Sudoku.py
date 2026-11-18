import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QGridLayout, QLineEdit, QPushButton, QMessageBox, QHBoxLayout, QVBoxLayout, QLabel)
from PyQt6.QtCore import Qt
import random
import copy
from PyQt6.QtGui import QIntValidator, QKeyEvent


class SudokuCell(QLineEdit):
    """Custom QLineEdit that supports arrow key navigation between cells."""

    def __init__(self, row, col, grid_ref, parent=None):
        super().__init__(parent)
        self.row = row
        self.col = col
        self.grid_ref = grid_ref  # reference to self.cells in SudokuSolver

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        r, c = self.row, self.col

        if key == Qt.Key.Key_Up:
            r -= 1
        elif key == Qt.Key.Key_Down:
            r += 1
        elif key == Qt.Key.Key_Left:
            c -= 1
        elif key == Qt.Key.Key_Right:
            c += 1
        else:
            super().keyPressEvent(event)
            return

        # Clamp to grid bounds
        r = max(0, min(8, r))
        c = max(0, min(8, c))
        self.grid_ref[r][c].setFocus()

class SudokuSolver(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sudoku Solver")
        self.resize(450, 540)  # Set the size

    # Center the window on screen
        screen = self.screen().availableGeometry()
        window = self.frameGeometry()
        window.moveCenter(screen.center())
        self.move(window.topLeft())
        
        self.main_layout = QVBoxLayout()
        
        # Title and instruction
        
        Title_label = QLabel("Sudoku Solver")
        Title_label.setStyleSheet("font-size: 24px; font-weight: bold")
        Title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        Instruction_label = QLabel("Fill the Sudoku grid with digits 1-9. Use 'Get Hint' up to 3 times per puzzle.")
        Instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.main_layout.addWidget(Title_label)
        self.main_layout.addWidget(Instruction_label)
        
        self.grid_Layout = QGridLayout()
        self.cells = [[QLineEdit(self) for _ in range(9)] for _ in range(9)]
        self.Hint_Count = 0
        self.Max_Hint = 3
        
        for row in range(9):
            for col in range(9):
                cell = self.cells[row][col]
                cell.setFixedSize(60, 60)
                cell.setAlignment(Qt.AlignmentFlag.AlignCenter)
                cell.setMaxLength(1)
                cell.setStyleSheet("font-size: 16px")
                cell.setValidator(QIntValidator(1, 9, self))
                self.grid_Layout.addWidget(cell, row, col)
                
        self.Hint_Button = QPushButton(f"Get Hint ({self.Max_Hint - self.Hint_Count} left) ")
        self.Hint_Button.clicked.connect(self.Provide_Hint)
        
        Solve_Button = QPushButton("Solve Button")
        Solve_Button.clicked.connect(self.Solve_Button)
        
        Clear_Button = QPushButton("Clear Board")
        Clear_Button.clicked.connect(self.Clear_Board)
        
        New_Button = QPushButton("New Game")
        New_Button.clicked.connect(self.New_Game)
        
        Button_Layout = QHBoxLayout()
        Button_Layout.addWidget(Solve_Button)
        Button_Layout.addWidget(self.Hint_Button)
        Button_Layout.addWidget(Clear_Button)
        Button_Layout.addWidget(New_Button)
        
        self.main_layout.addLayout(self.grid_Layout)
        self.main_layout.addLayout(Button_Layout)
        self.setLayout(self.main_layout)
    def _apply_cell_style(self, cell, row, col):
        """Apply border styling to visually separate 3x3 boxes."""
        top    = "2px" if row % 3 == 0 else "1px"
        left   = "2px" if col % 3 == 0 else "1px"
        bottom = "2px" if row == 8 else "1px"
        right  = "2px" if col == 8 else "1px"
        cell.setStyleSheet(
            f"font-size: 16px;"
            f"border-top: {top} solid black;"
            f"border-left: {left} solid black;"
            f"border-bottom: {bottom} solid black;"
            f"border-right: {right} solid black;"
        )
    def Get_Board(self):
        Board = []
        for row in range(9):
            Board_Row = []
            for col in range(9):
                text = self.cells[row][col].text()
                try:
                    if text == '':
                        Board_Row.append(0)
                    elif text.isdigit():
                        num = int(text)
                        if 1 <= num <= 9:
                            Board_Row.append(num)
                        else:
                            raise ValueError
                    else:
                        raise ValueError
                except ValueError:
                    QMessageBox.warning(self, "Invaild Input", f"Cell ({row + 1}, {col + 1}) contain an invaild entry.")
                    return None
            Board.append(Board_Row)
        return Board
    
    def Set_Board(self, Board):
        for row in range(9):
            for col in range(9):
                self.cells[row][col].setText(str(Board[row][col]) if Board[row][col] != 0 else "")
        
    def Clear_Board(self):
        for row in range(9):
            for col in range(9):
                self.cells[row][col].clear()
                self.cells[row][col].setStyleSheet("font-size: 16px")
        self.Hint_Count = 0
        self.Hint_Button.setText(f"Get Hint ({self.Max_Hint - self.Hint_Count} left)")
        
    def New_Game(self):
        self.Clear_Board()
        QMessageBox.information(self, "New Game", "New Game Started. Board cleared.")
        
    def Is_Valid(self, Board, row, col, num):
        for i in range(9):
            if Board[row][i] == num  or Board[i][col] == num:
                return False
            
        Start_Row, Start_Col = 3 * (row // 3),  3 * (col // 3)
        for i in range(Start_Row, Start_Row + 3):
            for j in range(Start_Col, Start_Col + 3):
                if Board[i][j] == num:
                    return False
        return True
    
    def Solve_Button(self, Board):
        for row in range(9):
            for col in range(9):
                if Board[row][col] == 0:
                    for num in range(1, 10):
                        if self.Is_Valid(Board, row, col, num):
                            Board[row][col] = num
                            if self.Solve_Button(Board):
                                return True
                            Board[row][col] = 0
                    return False
        return True
    def Solve(self):
        Board = self.Get_Board()
        if Board is None:
            return
        if self.Solve_Button(Board):
            self.Set_Board(Board)
        else:
            QMessageBox.warning(self, "No Solution", "No valid solution exits for the current Suduku puzzle.")
    def Provide_Hint(self):
        if self.Hint_Count >= self.Max_Hint:
            QMessageBox.information(self, "Hint Limit", "You have used all 3 hint")
            return
        
        Current_Board = self.Get_Board()
        if Current_Board is None:
            return
        
        Solve_Board = copy.deepcopy(Current_Board)
        
        if not self.Solve_Button(Solve_Board):
            QMessageBox.warning(self, "No Solution", "No valid exits for the current puzzle.")
            return
        
        Hint_Candidates = [(row, col) for row in range(9) for col in range(9)
                        if Current_Board[row][col] == 0 and Solve_Board[row][col] != 0]
        
        if not Hint_Candidates:
            QMessageBox.information(self, "Hint", "No empty cells availble for hints.")
            return
        
        row, col = random.choice(Hint_Candidates)
        Hint_Value = Solve_Board[row][col]
        self.cells[row][col].setText(str(Hint_Value))
        self.cells[row][col].setStyleSheet("font-size: 16px; color: Blue;")
        self.Hint_Count += 1
        self.Hint_Button.setText(f"Get Hint ({self.Max_Hint - self.Hint_Count} - left)")
        
if __name__ == "__main__":
    from PyQt6.QtGui import QIntValidator
    app = QApplication(sys.argv)
    window = SudokuSolver()
    window.show()
    sys.exit(app.exec())