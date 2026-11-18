import sys
import math
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QLabel, QFrame
)
from PyQt6.QtCore import Qt, QRect, pyqtSignal, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath

#  CONSTANTS
ROWS = 5
COLS = 5
WIN_LENGTH = 4          # Need 4 in a row to win
EMPTY = 0
PLAYER_X = 1            # Human
PLAYER_O = -1           # AI
AI_DEPTH = 3            # Minimax search depth (increase for stronger AI, but slower)

# Color Palette — dark slate theme
C_BG        = QColor("#0f1117")
C_PANEL     = QColor("#1a1d27")
C_CELL      = QColor("#1e2130")
C_CELL_HOV  = QColor("#252940")
C_BORDER    = QColor("#2e3250")
C_X_COLOR   = QColor("#e05c5c")   # Red for X
C_O_COLOR   = QColor("#4e9eff")   # Blue for O
C_WIN_FLASH = QColor("#f0c040")   # Gold highlight for winning line
C_TEXT      = QColor("#d0d6f0")
C_SUBTEXT   = QColor("#5a607e")
C_BTN       = QColor("#252940")
C_BTN_HOV   = QColor("#2e3560")
C_BTN_ACT   = QColor("#3a4480")


#  GAME LOGIC ENGINE
class GameEngine:
    def __init__(self):
        self.reset()

    def reset(self):
        self.board = [[EMPTY] * COLS for _ in range(ROWS)]
        self.current_player = PLAYER_X
        self.game_over = False
        self.winner = None
        self.winning_cells = []

    def make_move(self, row, col):
        """Place current player's mark. Returns True if valid."""
        if self.game_over or self.board[row][col] != EMPTY:
            return False
        self.board[row][col] = self.current_player
        won, cells = self.check_winner(self.board, row, col, self.current_player)
        if won:
            self.game_over = True
            self.winner = self.current_player
            self.winning_cells = cells
        elif self.is_full(self.board):
            self.game_over = True
            self.winner = None
        else:
            self.current_player = PLAYER_O if self.current_player == PLAYER_X else PLAYER_X
        return True

    def get_empty_cells(self, board):
        return [(r, c) for r in range(ROWS) for c in range(COLS) if board[r][c] == EMPTY]

    def is_full(self, board):
        return all(board[r][c] != EMPTY for r in range(ROWS) for c in range(COLS))

    def check_winner(self, board, last_row, last_col, player):
        """Check if `player` won after placing at (last_row, last_col)."""
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            cells = [(last_row, last_col)]
            # Extend forward
            r, c = last_row + dr, last_col + dc
            while 0 <= r < ROWS and 0 <= c < COLS and board[r][c] == player:
                cells.append((r, c))
                r += dr; c += dc
            # Extend backward
            r, c = last_row - dr, last_col - dc
            while 0 <= r < ROWS and 0 <= c < COLS and board[r][c] == player:
                cells.append((r, c))
                r -= dr; c -= dc
            if len(cells) >= WIN_LENGTH:
                return True, cells
        return False, []

    def check_any_winner(self, board, player):
        """Check entire board for any win by player. Returns (bool, cells)."""
        for r in range(ROWS):
            for c in range(COLS):
                if board[r][c] == player:
                    won, cells = self.check_winner(board, r, c, player)
                    if won:
                        return True, cells
        return False, []

    # ── Minimax with Alpha-Beta Pruning ──
    def evaluate(self, board):
        """Heuristic board score for AI (PLAYER_O)."""
        score = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for r in range(ROWS):
            for c in range(COLS):
                for dr, dc in directions:
                    score += self._line_score(board, r, c, dr, dc)
        return score

    def _line_score(self, board, r, c, dr, dc):
        """Score a line of WIN_LENGTH starting at (r,c) in direction (dr,dc)."""
        end_r = r + dr * (WIN_LENGTH - 1)
        end_c = c + dc * (WIN_LENGTH - 1)
        if not (0 <= end_r < ROWS and 0 <= end_c < COLS):
            return 0
        ai_count = 0
        human_count = 0
        for i in range(WIN_LENGTH):
            cell = board[r + dr * i][c + dc * i]
            if cell == PLAYER_O:
                ai_count += 1
            elif cell == PLAYER_X:
                human_count += 1
        if ai_count > 0 and human_count > 0:
            return 0
        if ai_count > 0:
            return 10 ** ai_count
        if human_count > 0:
            return -(10 ** human_count)
        return 0

    def minimax(self, board, depth, alpha, beta, is_maximizing, last_move):
        # Terminal: check win/loss/draw
        if last_move:
            lr, lc = last_move
            player = PLAYER_O if is_maximizing else PLAYER_X   # last player
            won, _ = self.check_winner(board, lr, lc, player)
            if won:
                score = (1000 + depth) if player == PLAYER_O else -(1000 + depth)
                return score, None
        if self.is_full(board):
            return 0, None
        if depth == 0:
            return self.evaluate(board), None

        empty = self.get_empty_cells(board)
        best_move = None

        if is_maximizing:
            best = -math.inf
            for r, c in empty:
                board[r][c] = PLAYER_O
                val, _ = self.minimax(board, depth - 1, alpha, beta, False, (r, c))
                board[r][c] = EMPTY
                if val > best:
                    best = val
                    best_move = (r, c)
                alpha = max(alpha, best)
                if beta <= alpha:
                    break
            return best, best_move
        else:
            best = math.inf
            for r, c in empty:
                board[r][c] = PLAYER_X
                val, _ = self.minimax(board, depth - 1, alpha, beta, True, (r, c))
                board[r][c] = EMPTY
                if val < best:
                    best = val
                    best_move = (r, c)
                beta = min(beta, best)
                if beta <= alpha:
                    break
            return best, best_move

    def get_ai_move(self):
        """Return the best (row, col) for AI using Minimax."""
        import copy
        board_copy = copy.deepcopy(self.board)
        _, move = self.minimax(board_copy, AI_DEPTH, -math.inf, math.inf, True, None)
        return move

#  BOARD WIDGET  (custom painting)
class BoardWidget(QWidget):
    cell_clicked = pyqtSignal(int, int)

    def __init__(self, engine: GameEngine, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.hover_cell = (-1, -1)
        self.win_flash = False
        self.setMouseTracking(True)
        self.setMinimumSize(400, 400)

        # Flash timer for winning line
        self._flash_timer = QTimer(self)
        self._flash_timer.setInterval(400)
        self._flash_timer.timeout.connect(self._toggle_flash)

    def _toggle_flash(self):
        self.win_flash = not self.win_flash
        self.update()

    def start_win_animation(self):
        self._flash_timer.start()

    def stop_win_animation(self):
        self._flash_timer.stop()
        self.win_flash = True
        self.update()

    def reset_animation(self):
        self._flash_timer.stop()
        self.win_flash = False
        self.hover_cell = (-1, -1)
        self.update()

    def _cell_rect(self, row, col):
        w = self.width()
        h = self.height()
        cell_w = w / COLS
        cell_h = h / ROWS
        margin = 4
        x = col * cell_w + margin
        y = row * cell_h + margin
        return QRect(int(x), int(y), int(cell_w - margin * 2), int(cell_h - margin * 2))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()

        # Background
        painter.fillRect(self.rect(), C_BG)

        winning = set(map(tuple, self.engine.winning_cells))

        for row in range(ROWS):
            for col in range(COLS):
                rect = self._cell_rect(row, col)
                is_hover = (row, col) == self.hover_cell
                is_winning = (row, col) in winning
                cell_val = self.engine.board[row][col]

                # Cell background
                if is_winning and self.win_flash:
                    color = C_WIN_FLASH.darker(180)
                elif is_hover and cell_val == EMPTY and not self.engine.game_over:
                    color = C_CELL_HOV
                else:
                    color = C_CELL

                # Rounded rect
                path = QPainterPath()
                path.addRoundedRect(
                    rect.x(), rect.y(), rect.width(), rect.height(), 10, 10
                )
                painter.fillPath(path, QBrush(color))

                # Border
                if is_winning and self.win_flash:
                    pen = QPen(C_WIN_FLASH, 2)
                else:
                    pen = QPen(C_BORDER, 1)
                painter.setPen(pen)
                painter.drawPath(path)

                # Draw X or O
                if cell_val == PLAYER_X:
                    self._draw_x(painter, rect, is_winning)
                elif cell_val == PLAYER_O:
                    self._draw_o(painter, rect, is_winning)
                elif is_hover and not self.engine.game_over:
                    self._draw_ghost(painter, rect)

        painter.end()

    def _draw_x(self, painter, rect, is_winning):
        color = C_WIN_FLASH if (is_winning and self.win_flash) else C_X_COLOR
        pen = QPen(color, 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        pad = rect.width() // 5
        x1, y1 = rect.x() + pad, rect.y() + pad
        x2, y2 = rect.right() - pad, rect.bottom() - pad
        painter.drawLine(x1, y1, x2, y2)
        painter.drawLine(x2, y1, x1, y2)

    def _draw_o(self, painter, rect, is_winning):
        color = C_WIN_FLASH if (is_winning and self.win_flash) else C_O_COLOR
        pen = QPen(color, 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        pad = rect.width() // 5
        painter.drawEllipse(
            rect.x() + pad, rect.y() + pad,
            rect.width() - pad * 2, rect.height() - pad * 2
        )

    def _draw_ghost(self, painter, rect):
        """Faint preview of current player's symbol on hover."""
        color = QColor(C_X_COLOR)
        color.setAlpha(45)
        pen = QPen(color, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        pad = rect.width() // 5
        x1, y1 = rect.x() + pad, rect.y() + pad
        x2, y2 = rect.right() - pad, rect.bottom() - pad
        painter.drawLine(x1, y1, x2, y2)
        painter.drawLine(x2, y1, x1, y2)

    def mouseMoveEvent(self, event):
        col = int(event.position().x() / (self.width() / COLS))
        row = int(event.position().y() / (self.height() / ROWS))
        if 0 <= row < ROWS and 0 <= col < COLS:
            if (row, col) != self.hover_cell:
                self.hover_cell = (row, col)
                self.update()
        else:
            self.hover_cell = (-1, -1)
            self.update()

    def leaveEvent(self, event):
        self.hover_cell = (-1, -1)
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            col = int(event.position().x() / (self.width() / COLS))
            row = int(event.position().y() / (self.height() / ROWS))
            if 0 <= row < ROWS and 0 <= col < COLS:
                self.cell_clicked.emit(row, col)

#  STYLED WIDGETS
class StyledButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(34)
        self._update_style(False)

    def _update_style(self, hovered):
        bg = C_BTN_HOV.name() if hovered else C_BTN.name()
        self.setStyleSheet(f"""
            QPushButton {{
                background: {bg};
                color: #d0d6f0;
                border: 1px solid #2e3250;
                border-radius: 8px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
                font-weight: 600;
                padding: 0 20px;
                letter-spacing: 0.5px;
            }}
            QPushButton:pressed {{
                background: #3a4480;
            }}
        """)

    def enterEvent(self, e):
        self._update_style(True)

    def leaveEvent(self, e):
        self._update_style(False)

#  MAIN WINDOW
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.engine = GameEngine()
        self.scores = {"X": 0, "O": 0, "Draw": 0}
        self.ai_thinking = False
        self._build_ui()
        self._update_status()

    def _build_ui(self):
        self.setWindowTitle("Tic-Tac-Toe 5×5  |  Minimax AI")
        self.setFixedSize(500, 700)
        self.setStyleSheet(f"background: {C_BG.name()};")

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(16, 12, 16, 12)
        root.setSpacing(8)

        # ── Title ──
        title = QLabel("TIC-TAC-TOE")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            color: #d0d6f0;
            font-family: 'Segoe UI', 'Arial', sans-serif;
            font-size: 18px;
            font-weight: 700;
            letter-spacing: 6px;
        """)
        root.addWidget(title)

        subtitle = QLabel("5 × 5  —  Get 4 in a row to win")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(f"color: {C_SUBTEXT.name()}; font-size: 11px; letter-spacing: 1px;")
        root.addWidget(subtitle)

        # ── Scoreboard ──
        score_frame = QFrame()
        score_frame.setStyleSheet(f"""
            QFrame {{
                background: {C_PANEL.name()};
                border: 1px solid {C_BORDER.name()};
                border-radius: 8px;
            }}
        """)
        score_layout = QHBoxLayout(score_frame)
        score_layout.setContentsMargins(12, 6, 12, 6)

        self.score_x_label  = self._score_block("X (You)", "0", C_X_COLOR)
        self.score_dr_label = self._score_block("Draw", "0", C_SUBTEXT)
        self.score_o_label  = self._score_block("O (AI)", "0", C_O_COLOR)
        score_layout.addWidget(self.score_x_label[0])
        score_layout.addStretch()
        score_layout.addWidget(self.score_dr_label[0])
        score_layout.addStretch()
        score_layout.addWidget(self.score_o_label[0])
        root.addWidget(score_frame)

        # ── Status Label ──
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFixedHeight(30)
        self.status_label.setStyleSheet(f"""
            color: {C_TEXT.name()};
            font-size: 13px;
            font-weight: 600;
            background: {C_PANEL.name()};
            border-radius: 6px;
            border: 1px solid {C_BORDER.name()};
        """)
        root.addWidget(self.status_label)

        # ── Board ──
        self.board_widget = BoardWidget(self.engine)
        self.board_widget.cell_clicked.connect(self._on_cell_clicked)
        root.addWidget(self.board_widget, stretch=1)

        # ── Buttons ──
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        self.reset_btn = StyledButton("New Game")
        self.reset_btn.clicked.connect(self._reset_game)
        self.clear_score_btn = StyledButton("Clear Score")
        self.clear_score_btn.clicked.connect(self._clear_scores)
        btn_row.addWidget(self.reset_btn)
        btn_row.addWidget(self.clear_score_btn)
        root.addLayout(btn_row)

    def _score_block(self, label_text, value_text, color):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        val = QLabel(value_text)
        val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        val.setStyleSheet(f"""
            color: {color.name()};
            font-size: 20px;
            font-weight: 700;
        """)
        lbl = QLabel(label_text)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet(f"color: {C_SUBTEXT.name()}; font-size: 11px; letter-spacing: 0.5px;")
        layout.addWidget(val)
        layout.addWidget(lbl)
        return container, val

    def _update_status(self):
        if self.engine.game_over:
            if self.engine.winner == PLAYER_X:
                self.status_label.setText("🎉  X Wins!")
                self.status_label.setStyleSheet(f"""
                    color: {C_X_COLOR.name()}; font-size: 15px; font-weight: 700;
                    background: {C_PANEL.name()}; border-radius: 8px;
                    border: 1px solid {C_X_COLOR.darker(150).name()};
                """)
            elif self.engine.winner == PLAYER_O:
                self.status_label.setText("🤖  AI Wins!")
                self.status_label.setStyleSheet(f"""
                    color: {C_O_COLOR.name()}; font-size: 15px; font-weight: 700;
                    background: {C_PANEL.name()}; border-radius: 8px;
                    border: 1px solid {C_O_COLOR.darker(150).name()};
                """)
            else:
                self.status_label.setText("🤝  It's a Draw!")
                self.status_label.setStyleSheet(f"""
                    color: {C_TEXT.name()}; font-size: 15px; font-weight: 700;
                    background: {C_PANEL.name()}; border-radius: 8px;
                    border: 1px solid {C_BORDER.name()};
                """)
        elif self.ai_thinking:
            self.status_label.setText("🤖  AI is thinking...")
            self.status_label.setStyleSheet(f"""
                color: {C_O_COLOR.name()}; font-size: 13px; font-weight: 600;
                background: {C_PANEL.name()}; border-radius: 8px;
                border: 1px solid {C_BORDER.name()};
            """)
        else:
            player = self.engine.current_player
            turn_text = "Your turn  (X)" if player == PLAYER_X else "AI's turn  (O)"
            color = C_X_COLOR if player == PLAYER_X else C_O_COLOR
            self.status_label.setText(turn_text)
            self.status_label.setStyleSheet(f"""
                color: {color.name()}; font-size: 14px; font-weight: 600;
                background: {C_PANEL.name()}; border-radius: 8px;
                border: 1px solid {C_BORDER.name()};
            """)

    def _on_cell_clicked(self, row, col):
        if self.engine.game_over or self.ai_thinking:
            return
        # Only human (X) can click
        if self.engine.current_player != PLAYER_X:
            return

        if self.engine.make_move(row, col):
            self.board_widget.update()
            self._update_status()
            if self.engine.game_over:
                self._handle_game_over()
            else:
                # Trigger AI move
                self.ai_thinking = True
                self._update_status()
                QTimer.singleShot(200, self._do_ai_move)

    def _do_ai_move(self):
        move = self.engine.get_ai_move()
        self.ai_thinking = False
        if move:
            self.engine.make_move(*move)
        self.board_widget.update()
        self._update_status()
        if self.engine.game_over:
            self._handle_game_over()

    def _handle_game_over(self):
        if self.engine.winner == PLAYER_X:
            self.scores["X"] += 1
            self.score_x_label[1].setText(str(self.scores["X"]))
        elif self.engine.winner == PLAYER_O:
            self.scores["O"] += 1
            self.score_o_label[1].setText(str(self.scores["O"]))
        else:
            self.scores["Draw"] += 1
            self.score_dr_label[1].setText(str(self.scores["Draw"]))

        if self.engine.winning_cells:
            self.board_widget.start_win_animation()
            QTimer.singleShot(2400, self.board_widget.stop_win_animation)

    def _reset_game(self):
        self.board_widget.reset_animation()
        self.ai_thinking = False
        self.engine.reset()
        self.board_widget.update()
        self._update_status()

    def _clear_scores(self):
        self.scores = {"X": 0, "O": 0, "Draw": 0}
        self.score_x_label[1].setText("0")
        self.score_o_label[1].setText("0")
        self.score_dr_label[1].setText("0")

#  ENTRY POINT
def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()