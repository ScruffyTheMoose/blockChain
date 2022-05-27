from observer import Observer
from PyQt5.QtWidgets import *

# The placeholder value must be given as input to connect the observer with the network
# we will leave this blank for now
observer = Observer("PLACEHOLDER")

# instantiating interface
app = QApplication([])
app.setStyle("Fusion")

# instantiating window
window = QWidget()

# choosing layout mode
layout = QVBoxLayout()
layout.addWidget(QPushButton("top"))
layout.addWidget(QPushButton("bottom"))

# assigning layout to window
window.setLayout(layout)

#############################
# Building basic features
# Order, appearance, etc will be handled later 100% no joke it will happen i swear
#############################

# Dropdown menu to select which node you will be operating
# this needs to be updated when node registry is updated
nodeSelection = QComboBox()
nodeSelection.addItems(list(observer.nodes))

if __name__ == "__main__":
    window.show()
    app.exec()
