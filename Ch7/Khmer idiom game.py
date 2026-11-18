"""
Khmer Idiom Builder — a PyQt6 word-arrangement game
=====================================================
Based on the class exercise: arranging keyword tiles into a correct,
meaningful Khmer sentence / idiom (ការរៀបចំពាក្យគន្លឹះឱ្យក្លាយជាប្រយោគខ្មែរ).

How to play:
  1. A Khmer idiom is split into word "tiles" and shuffled at the bottom.
  2. Click tiles in the correct order to build the sentence at the top.
  3. Click "Check" to see if the order is correct.
  4. Click a tile in the answer row to send it back down (undo).
  5. Score points for correct answers; a timer tracks how long you take.

--------------------------------------------------------------------------
EDIT ME: Replace / extend the IDIOMS list below with the exact idioms
from your course handout. Each entry is (full_sentence, meaning_hint).
The game automatically splits the sentence on spaces into tiles.
--------------------------------------------------------------------------
"""

import sys
import random
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QGridLayout, QFrame, QMessageBox, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

# ---------------------------------------------------------------------
# EDIT ME: idiom bank — (sentence, hint/meaning)
# ---------------------------------------------------------------------
IDIOMS = [
    ("ចេះដឹង តែងតែ ចង់ រៀន បន្ថែម", "The knowledgeable always want to learn more."),
    ("ខំ ប្រឹងប្រែង ដើម្បី ជោគជ័យ ថ្ងៃណាមួយ", "Work hard, and success will come one day."),
    ("ចិត្ត ស្មោះត្រង់ នាំមក នូវ មិត្តភាព", "An honest heart brings friendship."),
    ("ការអប់រំ គឺជា កូនសោ បើក ភាពជោគជ័យ", "Education is the key that opens success."),
    ("ស្នេហា គ្រួសារ សំខាន់ ជាង អ្វីៗទាំងអស់", "Family love matters more than anything."),
]

TILE_COLORS = ["#c62828", "#1565c0", "#2e7d32", "#ef6c00", "#6a1b9a", "#00838f"]


class Tile(QPushButton):
    """A single word tile button."""

    def __init__(self, word: str, color: str):
        super().__init__(word)
        self.word = word
        self.setFont(QFont("Khmer OS Battambang", 16))
        self.setMinimumHeight(48)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border-radius: 10px;
                padding: 8px 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #333;
            }}
        """)


class KhmerIdiomGame(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("លំហាត់ — Khmer Idiom Builder")
        self.resize(900, 600)
        self.setStyleSheet("background-color: #121212; color: white;")

        self.score = 0
        self.round_index = 0
        self.seconds_elapsed = 0
        self.answer_tiles = []   # tiles currently placed in the answer row (in order)
        self.pool_tiles = []     # tiles still waiting to be picked

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)

        self._build_ui()
        self._load_shuffled_idioms()
        self._start_round()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(16)
        root.setContentsMargins(24, 20, 24, 20)

        # Header
        title = QLabel("លំហាត់៖ រៀបចំពាក្យគន្លឹះឱ្យក្លាយជាប្រយោគខ្មែរ")
        title.setFont(QFont("Khmer OS Battambang", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(title)

        subtitle = QLabel("Click the word tiles below, in order, to build the sentence.")
        subtitle.setFont(QFont("Arial", 11))
        subtitle.setStyleSheet("color: #aaaaaa;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(subtitle)

        # Status bar: score / round / timer
        status_bar = QHBoxLayout()
        self.score_label = QLabel("Score: 0")
        self.round_label = QLabel("Round: 1")
        self.timer_label = QLabel("Time: 0s")
        for lbl in (self.score_label, self.round_label, self.timer_label):
            lbl.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        status_bar.addWidget(self.score_label)
        status_bar.addStretch()
        status_bar.addWidget(self.round_label)
        status_bar.addStretch()
        status_bar.addWidget(self.timer_label)
        root.addLayout(status_bar)

        # Answer row (where the sentence is built)
        answer_frame = QFrame()
        answer_frame.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border: 2px dashed #555;
                border-radius: 12px;
            }
        """)
        answer_frame.setMinimumHeight(90)
        self.answer_layout = QHBoxLayout(answer_frame)
        self.answer_layout.setContentsMargins(12, 12, 12, 12)
        self.answer_layout.setSpacing(8)
        self.answer_layout.addStretch()
        root.addWidget(answer_frame)

        # Hint label
        self.hint_label = QLabel("")
        self.hint_label.setFont(QFont("Arial", 11))
        self.hint_label.setStyleSheet("color: #f9a825;")
        self.hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hint_label.setWordWrap(True)
        root.addWidget(self.hint_label)

        # Pool grid (scrambled tiles to pick from)
        self.pool_frame = QFrame()
        self.pool_layout = QGridLayout(self.pool_frame)
        self.pool_layout.setSpacing(10)
        root.addWidget(self.pool_frame)

        root.addStretch()

        # Controls
        controls = QHBoxLayout()
        self.check_btn = QPushButton("✓ Check")
        self.reset_btn = QPushButton("↺ Reset Tiles")
        self.skip_btn = QPushButton("⏭ Skip")

        for btn, color in (
            (self.check_btn, "#2e7d32"),
            (self.reset_btn, "#616161"),
            (self.skip_btn, "#455a64"),
        ):
            btn.setMinimumHeight(42)
            btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border-radius: 8px;
                    padding: 8px 20px;
                }}
                QPushButton:hover {{ background-color: #444; }}
            """)

        self.check_btn.clicked.connect(self._check_answer)
        self.reset_btn.clicked.connect(self._reset_tiles)
        self.skip_btn.clicked.connect(self._next_round)

        controls.addWidget(self.check_btn)
        controls.addWidget(self.reset_btn)
        controls.addWidget(self.skip_btn)
        root.addLayout(controls)

    # ------------------------------------------------------------------
    # Game state / round management
    # ------------------------------------------------------------------
    def _load_shuffled_idioms(self):
        self.idioms = IDIOMS.copy()
        random.shuffle(self.idioms)

    def _start_round(self):
        if self.round_index >= len(self.idioms):
            self._show_final_score()
            return

        sentence, hint = self.idioms[self.round_index]
        self.current_words = sentence.split(" ")
        self.hint_label.setText(f"💡 Hint: {hint}")
        self.round_label.setText(f"Round: {self.round_index + 1}/{len(self.idioms)}")

        self.seconds_elapsed = 0
        self.timer_label.setText("Time: 0s")
        self.timer.start(1000)

        self._reset_tiles()

    def _reset_tiles(self):
        """Clear the board and re-scramble tiles for the current sentence."""
        self._clear_layout(self.answer_layout)
        self._clear_layout(self.pool_layout)
        self.answer_tiles = []

        shuffled_words = self.current_words.copy()
        random.shuffle(shuffled_words)

        self.pool_tiles = []
        cols = 4
        for i, word in enumerate(shuffled_words):
            color = TILE_COLORS[i % len(TILE_COLORS)]
            tile = Tile(word, color)
            tile.clicked.connect(lambda _, t=tile: self._move_to_answer(t))
            self.pool_layout.addWidget(tile, i // cols, i % cols)
            self.pool_tiles.append(tile)

        self.answer_layout.addStretch()

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

    def _move_to_answer(self, tile: Tile):
        """Move a tile from the pool into the answer row."""
        self.pool_layout.removeWidget(tile)
        tile.clicked.disconnect()
        tile.clicked.connect(lambda _, t=tile: self._move_to_pool(t))
        # insert before the trailing stretch
        self.answer_layout.insertWidget(self.answer_layout.count() - 1, tile)
        self.answer_tiles.append(tile)
        self.pool_tiles.remove(tile)
        self._repack_pool()

    def _move_to_pool(self, tile: Tile):
        """Send a tile back from the answer row to the pool (undo)."""
        self.answer_layout.removeWidget(tile)
        tile.clicked.disconnect()
        tile.clicked.connect(lambda _, t=tile: self._move_to_answer(t))
        self.answer_tiles.remove(tile)
        self.pool_tiles.append(tile)
        self._repack_pool()

    def _repack_pool(self):
        """Re-lay the pool grid after tiles move in/out."""
        for i in reversed(range(self.pool_layout.count())):
            self.pool_layout.takeAt(i)
        cols = 4
        for i, tile in enumerate(self.pool_tiles):
            self.pool_layout.addWidget(tile, i // cols, i % cols)

    def _tick(self):
        self.seconds_elapsed += 1
        self.timer_label.setText(f"Time: {self.seconds_elapsed}s")

    # ------------------------------------------------------------------
    # Checking answers
    # ------------------------------------------------------------------
    def _check_answer(self):
        if len(self.answer_tiles) != len(self.current_words):
            QMessageBox.warning(self, "Incomplete", "Place all the tiles before checking.")
            return

        built_sentence = " ".join(t.word for t in self.answer_tiles)
        correct_sentence = " ".join(self.current_words)

        self.timer.stop()

        if built_sentence == correct_sentence:
            gained = max(100 - self.seconds_elapsed * 2, 20)
            self.score += gained
            self.score_label.setText(f"Score: {self.score}")
            QMessageBox.information(
                self, "Correct! 🎉",
                f"Well done!\n\n{correct_sentence}\n\n+{gained} points"
            )
            self._next_round()
        else:
            QMessageBox.critical(
                self, "Not quite",
                "That order isn't right yet. Try again!"
            )
            self.timer.start(1000)

    def _next_round(self):
        self.round_index += 1
        self._start_round()

    def _show_final_score(self):
        self.timer.stop()
        QMessageBox.information(
            self, "Finished!",
            f"You completed all rounds!\n\nFinal score: {self.score}"
        )
        self.round_label.setText("Round: Complete")


def main():
    app = QApplication(sys.argv)
    window = KhmerIdiomGame()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()