import requests
import json
import sys

from observer import Observer
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


# placeholder address for local testing
# [TEMPORARY]
observer = Observer(sys.argv[1])

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
        self.setGeometry(300, 200, 1500, 500)

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
        self.sendButton = QPushButton("Submit", clicked=lambda: self.submitButton())

        # label to clarify what response is for
        self.responseLabel = QLabel(
            f"{self.nodeSelection.currentText()} --- {self.actionSelection.currentText().upper()}"
        )
        self.responseLabel.setStyleSheet("font-weight: bold; color: blue")

        # text viewer to display response
        self.responseViewer = QTextBrowser()

        # text viewer to display observer data
        self.observerViewer = QTextBrowser()
        self.observerViewer.setText(json.dumps(observer.nodeData, indent=4))

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
        self.centerBox.layout().addWidget(self.responseLabel)
        self.centerBox.layout().addWidget(self.responseViewer)

        #### adding features to right box ####
        self.rightBox.layout().addWidget(self.observerViewer)

        #### adding left/center/right to main ####
        self.layout().addWidget(self.leftBox)
        self.layout().addWidget(self.centerBox)
        self.layout().addWidget(self.rightBox)

        # show window
        self.show()

    def getRequest(self) -> None:
        """Sends GET request to selected node and endpoint"""

        # gets address from selected node in dropdown
        nodeAddress = self.nodeSelection.currentText()
        endpoint = GEToptions[self.actionSelection.currentText()]

        # sending GET request
        response = requests.get(f"{nodeAddress}/{endpoint}")
        # converts to string
        data = json.dumps(response.json(), indent=4)

        # labeling response
        self.responseLabel.setText(
            f"{self.nodeSelection.currentText()} --- {self.actionSelection.currentText().upper()}"
        )

        # set data as viewer text for display
        self.responseViewer.setText(data)

    def postRequest(self) -> None:
        """Sends POST request to selected node and endpoint"""

        actionType = self.actionSelection.currentText()  # str

        # gets address from the selected node in dropdown
        nodeAddress = self.nodeSelection.currentText()

        if actionType == "New Transaction":
            # getting input data
            recipient = self.idInput.text()
            amount = self.amountInput.text()

            # data to be sent
            submission = {
                "recipient": recipient,
                "amount": amount,
            }

            # sending POST request
            response = requests.post(f"{nodeAddress}/transactions/new", json=submission)
            # converting to reading string
            data = json.dumps(response.json(), indent=4)

            # labeling response
            self.responseLabel.setText(
                f"{self.nodeSelection.currentText()} --- {self.actionSelection.currentText().upper()}"
            )

            # set data as viewer text for display
            self.responseViewer.setText(data)

        else:  # registering new node
            # getting input data
            newNode = self.recipientInput.text()

            # data to be sent
            submission = {
                "nodes": [newNode],
            }

            # sending POST request
            response = requests.post(f"{nodeAddress}/nodes/register", json=submission)
            # converting to reading string
            data = json.dumps(response.json(), indent=4)

            # labeling response
            self.responseLabel.setText(
                f"{self.nodeSelection.currentText()} --- {self.actionSelection.currentText().upper()}"
            )

            # set data as viewer text for display
            self.responseViewer.setText(data)

    def observerDataUpdate(self) -> None:
        """Update and display observer data"""

        # updating the observer nodes data for each node on network
        origNodes = observer.nodes
        observer.updateNodes()

        # adding only new nodes to selection menu
        for node in observer.nodes:
            if node not in origNodes:
                self.nodeSelection.addItem(node)

        # updating the authoritative chain tracked by observer
        observer.updateChain()

        # updating individual node status on observer
        observer.updateData()

        # displaying the updated data
        self.observerViewer.setText(json.dumps(observer.nodeData, indent=4))

    def submitButton(self):
        """Changes displayed data based on which node is selected from menu"""

        # determining type of request and handling
        if self.actionSelection.currentText() in GEToptions.keys():
            self.getRequest()
        else:
            self.postRequest()

        # updating observer data after changes made on network
        self.observerDataUpdate()


# instantiating interface
app = QApplication([])
mainWindow = MainWindow()


if __name__ == "__main__":
    app.exec()
