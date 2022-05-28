import requests
import json

from observer import Observer
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

# The placeholder value must be given as input to connect the observer with the network
# we will leave this blank for now
# observer = Observer("http://placeholder")
observer = None  # as placeholder

GETOptions = {
    "Mine": "mine",
    "Get ID": "id",
    "Get Transactions": "transactions",
    "Get Chain": "chain",
    "Get Nodes": "nodes",
    "Resolve Network": "resolve",
    "Get Status": "status",
}


class MainWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()

        # setting title
        self.setWindowTitle("Node Manager")
        # window coords and dimensions
        self.setGeometry(200, 200, 300, 300)

        # vert box layout
        self.setLayout(QVBoxLayout())

        # node registry dropdown selection
        nodes = ["http://127.0.0.1:5000"]
        nodeList = QComboBox()
        nodeList.addItems(nodes)

        # action dropdown selection
        actions = [
            "Mine",
            "Get ID",
            "Get Transactions",
            "Get Chain",
            "Get Nodes",
            "Resolve Network",
            "Get Status",
        ]
        actionList = QComboBox()
        actionList.addItems(actions)

        # button for testing features
        testButton = QPushButton("Press to Test", clicked=lambda: getRequest())

        # basic label to display response [TEMPORARY]
        testLabel = QLabel("")

        # adding features to window
        self.layout().addWidget(nodeList)
        self.layout().addWidget(actionList)
        self.layout().addWidget(testButton)
        self.layout().addWidget(testLabel)

        # show window
        self.show()

        ##################
        ## GET requests ##
        ##################

        def getRequest() -> None:
            """Sends get request to selected node and endpoint"""

            # gets address from selected node in dropdown
            nodeAddress = nodeList.currentText()
            endpoint = GETOptions[actionList.currentText()]

            response = requests.get(f"{nodeAddress}/{endpoint}")
            data = json.dumps(response.json())

            # prints for now since there is no endpoint built
            testLabel.setText(data)


# instantiating interface
app = QApplication([])
mainWindow = MainWindow()


if __name__ == "__main__":
    app.exec()
