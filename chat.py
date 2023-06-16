from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QLineEdit, QPushButton, QWidget
from PyQt6.QtCore import QThread, pyqtSignal
from Coaching import Gpt4Coaching
import time

class Worker(QThread):
    message_generated = pyqtSignal(str)

    def __init__(self, prompt, coach):
        super(Worker, self).__init__()
        self.prompt = prompt
        self.coach = coach

    def run(self):
        response = self.coach.generate_chat(self.prompt)
        self.message_generated.emit(response)

class DisplayWorker(QThread):
    word_ready = pyqtSignal(str)

    def __init__(self, full_text):
        super(DisplayWorker, self).__init__()
        self.full_text = full_text

    def run(self):
        words = self.full_text.split()
        for word in words:
            time.sleep(0.05)  # adjust this delay as needed
            self.word_ready.emit(word)

class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.coach = Gpt4Coaching()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Chat Window')
        self.resize(800, 600)
        # Main widget
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)

        # Layout
        self.vbox = QVBoxLayout()

        # Text edit for the chat log
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)

        # Text input for the user's message
        self.text_input = QLineEdit()
        self.text_input.returnPressed.connect(self.send_message)

        # Send button
        self.send_button = QPushButton('Send')
        self.send_button.clicked.connect(self.send_message)

        # Add widgets to the layout
        self.vbox.addWidget(self.text_edit)
        self.vbox.addWidget(self.text_input)
        self.vbox.addWidget(self.send_button)

        # Apply the layout to the central widget
        self.main_widget.setLayout(self.vbox)

    def send_message(self):
        message = self.text_input.text()
        if message:
            self.text_edit.append(f"You: {message}")
            self.worker = Worker(message, self.coach)
            self.worker.message_generated.connect(self.display_response)
            self.worker.start()
            self.text_input.clear()

    def display_response(self, response):
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText("\nAssistant:")
        self.display_worker = DisplayWorker(response)
        self.display_worker.word_ready.connect(self.display_word)
        self.display_worker.start()

    def display_word(self, word):
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(f" {word}")


if __name__ == "__main__":
    app = QApplication([])
    chat_window = ChatWindow()
    chat_window.show()
    app.exec()
