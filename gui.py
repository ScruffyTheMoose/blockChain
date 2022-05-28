from observer import Observer
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

# The placeholder value must be given as input to connect the observer with the network
# we will leave this blank for now
# observer = Observer("http://placeholder")


class MainWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()

        # setting title
        self.setWindowTitle("Node Manager")

        # setting layout to vert box
        self.setLayout(QHBoxLayout())

        # creating label
        label = QLabel("Test Label")
        label.setFont(QFont("Helvetica", 25))
        self.layout().addWidget(label)

        # creating input box
        inputBox = QLineEdit()
        inputBox.setObjectName("name_field")
        inputBox.setText("")
        self.layout().addWidget(inputBox)

        # creating a button
        button = QPushButton("PRESS", clicked=lambda: press_button())
        self.layout().addWidget(button)

        def press_button():
            label.setText(f"Hello {inputBox.text()}")
            inputBox.setText("")

        # showing window
        self.show()


# instantiating interface
app = QApplication([])
mainWindow = MainWindow()


if __name__ == "__main__":
    app.exec()
