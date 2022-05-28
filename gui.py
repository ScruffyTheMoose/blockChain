import requests
import json

from observer import Observer
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

# The placeholder value must be given as input to connect the observer with the network
# we will leave this blank for now
# observer = Observer("http://placeholder")
observer = None  # as placeholder

GEToptions = {
    "Mine": "mine",
    "Get ID": "id",
    "Get Transactions": "transactions",
    "Get Chain": "chain",
    "Get Nodes": "nodes",
    "Resolve Network": "resolve",
    "Get Status": "status",
}

POSToptions = {
    "New Transaction": "transactions/new",
    "Register Node": "nodes/register",
}


class MainWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()

        # setting title
        self.setWindowTitle("Node Manager")
        # window coords and dimensions
        self.setGeometry(200, 200, 800, 500)

        # horizontal main box layout
        self.setLayout(QHBoxLayout())

        # build left box
        self.leftBox = QGroupBox("Requests")
        self.leftBox.setLayout(QVBoxLayout())

        # build right box
        self.rightBox = QGroupBox("Info")
        self.rightBox.setLayout(QVBoxLayout())

        # node registry dropdown selection
        nodes = ["http://127.0.0.1:5000"]
        nodeList = QComboBox()
        nodeList.addItems(nodes)

        # action dropdown selection
        actions = (
            "Mine",
            "New Transaction",
            "Register Node",
            "Get ID",
            "Get Transactions",
            "Get Chain",
            "Get Nodes",
            "Resolve Network",
            "Get Status",
        )
        actionList = QComboBox()
        actionList.addItems(actions)

        # button for testing features
        testButton = QPushButton(
            "Press to Test",
            clicked=lambda: getRequest()
            if actionList.currentText() in GEToptions.keys()
            else postRequest(),
        )

        # basic label to display response [TEMPORARY]
        responseViewer = QTextBrowser()

        # adding features to left box
        self.leftBox.layout().addWidget(nodeList)
        self.leftBox.layout().addWidget(actionList)
        self.leftBox.layout().addWidget(testButton)

        # adding features to right box
        self.rightBox.layout().addWidget(responseViewer)

        # adding left/right to main
        self.layout().addWidget(self.leftBox)
        self.layout().addWidget(self.rightBox)

        # show window
        self.show()

        ##################
        ## GET requests ##
        ##################

        def getRequest() -> None:
            """Sends get request to selected node and endpoint"""

            # gets address from selected node in dropdown
            nodeAddress = nodeList.currentText()
            endpoint = GEToptions[actionList.currentText()]

            response = requests.get(f"{nodeAddress}/{endpoint}")
            # converts to string [TEMPORARY]
            data = json.dumps(response.json(), indent=4)

            # set data as label text for display [TEMPORARY]
            responseViewer.setText(data)


# instantiating interface
app = QApplication([])
mainWindow = MainWindow()


if __name__ == "__main__":
    app.exec()
