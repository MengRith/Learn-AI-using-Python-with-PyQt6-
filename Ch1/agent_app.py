from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QSlider, QGroupBox, QTextEdit
from PyQt6.QtCore import Qt
import sys

class SimpleAgent:
    # A very vasic rule-based AI agent.
    def decide(self, environment):
        price = environment["price"]
        if price < 30:
            return "Buy"
        elif price > 70:
            return "Sell"
        else:
            return "Wait"
        
class AIAgentSimulator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Agent Simulator")
        self.setGeometry(100, 100, 400, 300)
        
        self.environment = {"price": 50}
        self.agent = SimpleAgent()
        
        self.create_widgets()
        self.layout_widgets()
        
    def create_widgets(self):
        self.price_label = QLabel(f"Price: {self.environment['price']}")
        self.price_slider = QSlider(Qt.Orientation.Horizontal)
        self.price_slider.setRange(0, 100)
        self.price_slider.setValue(self.environment['price'])
        self.price_slider.valueChanged.connect(self.update_price)
        # create button
        self.action_group = QGroupBox("Trigger Agent Action")
        self.buy_button = QPushButton("Buy")
        self.Sell_button = QPushButton("Sell")
        self.Wait_button = QPushButton("Wait")
        # connect button to manual action function so ths human can add manually
        self.buy_button.clicked.connect(lambda: self.manual_action("Buy"))
        self.Sell_button.clicked.connect(lambda: self.manual_action("Sell"))
        self.Wait_button.clicked.connect(lambda: self.manual_action("Wait"))
        # Read only so user can't edit 
        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        
        self.auto_decide_button = QPushButton("Auto Decide")
        self.auto_decide_button.clicked.connect(self.agent_decision)
        
        
    def layout_widgets(self):
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Environment Controls"))
        layout.addWidget(self.price_label)
        layout.addWidget(self.price_slider)
        
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.buy_button)
        h_layout.addWidget(self.Sell_button)
        h_layout.addWidget(self.Wait_button)
        self.action_group.setLayout(h_layout)
        layout.addWidget(self.action_group)
        
        layout.addWidget(self.auto_decide_button)
        layout.addWidget(QLabel("🤖Agent Output"))
        layout.addWidget(self.result_box)
        
        self.setLayout(layout)
    
    def update_price(self, value):
        self.environment["price"] = value
        self.price_label.setText(f"Price = {value}")
        
    def manual_action(self, action):
        self.result_box.append(f"👨‍💻 Manual action triggered: {action}")
        
    def agent_decision(self):
        decision = self.agent.decide(self.environment)
        self.result_box.append(f"🤖 Agent decision based on price {self.environment['price']}: {decision}")
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    simulator = AIAgentSimulator()
    simulator.show()
    sys.exit(app.exec())