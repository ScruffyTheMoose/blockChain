import requests
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout

app = QApplication([])
app.setStyle("Fusion")

window = QWidget()

layout = QVBoxLayout()
layout.addWidget(QPushButton("top"))
layout.addWidget(QPushButton("bottom"))

window.setLayout(layout)

if __name__ == "__main__":
    window.show()
    app.exec()
