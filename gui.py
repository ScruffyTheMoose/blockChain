import requests
import json

from observer import Observer
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


# placeholder address for local testing
observer = Observer("http://127.0.0.1:5000")

# all GET request options to make menu operations easier
GEToptions = {
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
        self.setGeometry(200, 200, 800, 500)

        # horizontal main box layout
        self.setLayout(QHBoxLayout())

        # build left box
        self.leftBox = QGroupBox("Menu")
        self.leftBox.setLayout(QVBoxLayout())

        # build center box
        self.centerBox = QGroupBox("Response")
        self.centerBox.setLayout(QVBoxLayout())

        # build right box
        self.rightBox = QGroupBox("Observer")
        self.rightBox.setLayout(QVBoxLayout())

        # node registry dropdown selection
        self.nodeBox = QGroupBox("Select Node:")
        self.nodeBox.setLayout(QVBoxLayout())
        self.nodeSelection = QComboBox()
        self.nodeSelection.addItems(observer.nodes)
        self.nodeSelection
        self.nodeBox.layout().addWidget(self.nodeSelection)
        # end node registry dropdown build

        # action dropdown selection
        self.actionBox = QGroupBox("Select Action")
        self.actionBox.setLayout(QVBoxLayout())
        self.actionsList = (
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
        self.actionSelection = QComboBox()
        self.actionSelection.addItems(self.actionsList)
        self.actionBox.layout().addWidget(self.actionSelection)
        # end action dropdown build

        # recipient address input
        self.recipientBox = QGroupBox("Registration Address:")
        self.recipientBox.setLayout(QVBoxLayout())
        self.recipientInput = QLineEdit()
        self.recipientInput.setPlaceholderText("http://192.168.1.1:5000")
        self.recipientBox.layout().addWidget(self.recipientInput)
        # end recipient address build

        # ID address input
        self.idBox = QGroupBox("Node ID:")
        self.idBox.setLayout(QVBoxLayout())
        self.idInput = QLineEdit()
        self.idInput.setPlaceholderText("52ad26bbc61941d3bff1f8ecd27ab81e")
        self.idBox.layout().addWidget(self.idInput)
        # end ID address build

        # amount to send input
        self.amountBox = QGroupBox("Amount:")
        self.amountBox.setLayout(QVBoxLayout())
        self.amountInput = QLineEdit()
        self.amountInput.setPlaceholderText("100")
        self.amountBox.layout().addWidget(self.amountInput)
        # end amount build

        # button applying action
        self.sendButton = QPushButton(
            "Submit",
            clicked=lambda: getRequest()
            if self.actionSelection.currentText() in GEToptions.keys()
            else postRequest(),
        )

        # text viewer to display response
        self.responseViewer = QTextBrowser()

        # text viewer to display observer data
        self.observerViewer = QTextBrowser()
        self.observerViewer.setText(json.dumps(observer.nodeData, indent=4))

        # button to update observerViewer
        self.updateObservations = QPushButton(
            "Update", clicked=lambda: observerDataUpdate()
        )

        #### adding features to left box ####
        self.leftAdd = [
            self.nodeBox,
            self.actionBox,
            self.recipientBox,
            self.idBox,
            self.amountBox,
            self.sendButton,
        ]

        for item in self.leftAdd:
            self.leftBox.layout().addWidget(item)

        #### adding features to center box ####
        self.centerBox.layout().addWidget(self.responseViewer)

        #### adding features to right box ####
        self.rightBox.layout().addWidget(self.observerViewer)
        self.rightBox.layout().addWidget(self.updateObservations)

        #### adding left/center/right to main ####
        self.layout().addWidget(self.leftBox)
        self.layout().addWidget(self.centerBox)
        self.layout().addWidget(self.rightBox)

        # show window
        self.show()

        def getRequest() -> None:
            """Sends GET request to selected node and endpoint"""

            # gets address from selected node in dropdown
            nodeAddress = self.nodeSelection.currentText()
            endpoint = GEToptions[self.actionSelection.currentText()]

            # sending GET request
            response = requests.get(f"{nodeAddress}/{endpoint}")
            # converts to string [TEMPORARY]
            data = json.dumps(response.json(), indent=4)

            # set data as label text for display [TEMPORARY]
            self.responseViewer.setText(data)

        def postRequest() -> None:
            """Sends POST request to selected node and endpoint"""

            actionType = self.actionSelection.currentText()  # str

            # gets address from the selected node in dropdown
            nodeAddress = self.nodeSelection.currentText()

            if actionType == "New Transaction":
                # getting input data
                recipient = self.recipientInput.text()
                amount = self.amountInput.text()

                # data to be sent
                submission = {
                    "recipient": recipient,
                    "amount": amount,
                }

                # sending POST request
                requests.post(f"{nodeAddress}/transactions/new", json=submission)

            else:  # registering new node
                # getting input data
                newNode = self.recipientInput.text()

                # data to be sent
                submission = {
                    "nodes": [newNode],
                }

                # sending POST request
                requests.post(f"{nodeAddress}/nodes/register", json=submission)

        def observerDataUpdate() -> None:
            """Update and display observer data"""

            # updating the observer nodes data for each node on network
            observer.updateNodes()
            observer.updateData()

            # displaying the updated data
            self.observerViewer.setText(json.dumps(observer.nodeData, indent=4))


# instantiating interface
app = QApplication([])
mainWindow = MainWindow()


if __name__ == "__main__":
    app.exec()
