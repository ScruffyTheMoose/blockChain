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
        nodeBox = QGroupBox("Select Node:")
        nodeBox.setLayout(QVBoxLayout())
        nodeSelection = QComboBox()
        nodeSelection.addItems(observer.nodes)
        nodeBox.layout().addWidget(nodeSelection)
        # end node registry dropdown build

        # action dropdown selection
        actionBox = QGroupBox("Select Action")
        actionBox.setLayout(QVBoxLayout())
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
        actionSelection = QComboBox()
        actionSelection.addItems(actions)
        actionBox.layout().addWidget(actionSelection)
        # end action dropdown build

        # recipient address input
        recipientBox = QGroupBox("Registration Address:")
        recipientBox.setLayout(QVBoxLayout())
        recipientInput = QLineEdit()
        recipientInput.setPlaceholderText("http://192.168.1.1:5000")
        recipientBox.layout().addWidget(recipientInput)
        # end recipient address build

        # ID address input
        idBox = QGroupBox("Node ID:")
        idBox.setLayout(QVBoxLayout())
        idInput = QLineEdit()
        idInput.setPlaceholderText("52ad26bbc61941d3bff1f8ecd27ab81e")
        idBox.layout().addWidget(idInput)
        # end ID address build

        # amount to send input
        amountBox = QGroupBox("Amount:")
        amountBox.setLayout(QVBoxLayout())
        amountInput = QLineEdit()
        amountInput.setPlaceholderText("100")
        amountBox.layout().addWidget(amountInput)
        # end amount build

        # button applying action
        sendButton = QPushButton(
            "Submit",
            clicked=lambda: getRequest()
            if actionSelection.currentText() in GEToptions.keys()
            else postRequest(),
        )

        # text viewer to display response
        responseViewer = QTextBrowser()

        # text viewer to display observer data
        observerViewer = QTextBrowser()
        observerViewer.setText(json.dumps(observer.nodeData, indent=4))

        # button to update observerViewer
        updateObservations = QPushButton("Update", clicked=lambda: observerDataUpdate())

        #### adding features to left box ####
        leftAdd = [
            nodeBox,
            actionBox,
            recipientBox,
            idBox,
            amountBox,
            sendButton,
        ]

        for item in leftAdd:
            self.leftBox.layout().addWidget(item)

        #### adding features to center box ####
        self.centerBox.layout().addWidget(responseViewer)

        #### adding features to right box ####
        self.rightBox.layout().addWidget(observerViewer)
        self.rightBox.layout().addWidget(updateObservations)

        #### adding left/center/right to main ####
        self.layout().addWidget(self.leftBox)
        self.layout().addWidget(self.centerBox)
        self.layout().addWidget(self.rightBox)

        # show window
        self.show()

        def getRequest() -> None:
            """Sends GET request to selected node and endpoint"""

            # gets address from selected node in dropdown
            nodeAddress = nodeSelection.currentText()
            endpoint = GEToptions[actionSelection.currentText()]

            # sending GET request
            response = requests.get(f"{nodeAddress}/{endpoint}")
            # converts to string [TEMPORARY]
            data = json.dumps(response.json(), indent=4)

            # set data as label text for display [TEMPORARY]
            responseViewer.setText(data)

        def postRequest() -> None:
            """Sends POST request to selected node and endpoint"""

            actionType = actionSelection.currentText()  # str

            # gets address from the selected node in dropdown
            nodeAddress = nodeSelection.currentText()

            if actionType == "New Transaction":
                # getting input data
                recipient = recipientInput.text()
                amount = amountInput.text()

                # data to be sent
                submission = {
                    "recipient": recipient,
                    "amount": amount,
                }

                # sending POST request
                requests.post(f"{nodeAddress}/transactions/new", json=submission)

            else:  # registering new node
                # getting input data
                newNode = recipientInput.text()

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
            observerViewer.setText(json.dumps(observer.nodeData, indent=4))


# instantiating interface
app = QApplication([])
mainWindow = MainWindow()


if __name__ == "__main__":
    app.exec()
