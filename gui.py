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
        nodeSelection = QComboBox()
        nodeSelection.addItems(observer.nodes)

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
        actionSelection = QComboBox()
        actionSelection.addItems(actions)

        # input boxes and associated labels
        recipientLabel = QLabel("Recipient Address:")
        recipientInput = QLineEdit()

        amountLabel = QLabel("Amount:")
        amountInput = QLineEdit()

        addressLabel = QLabel("New Node Address:")
        addressInput = QLineEdit()

        # button for testing features
        sendButton = QPushButton(
            "Press to Test",
            clicked=lambda: getRequest()
            if actionSelection.currentText() in GEToptions.keys()
            else postRequest(),
        )

        # text viewer to display response
        responseViewer = QTextBrowser()

        # text viewer to display observer data
        observerViewer = QTextBrowser()
        observerViewer.setText(json.dumps(observer.nodeData, indent=4))

        #### adding features to left box ####
        leftAdd = [
            nodeSelection,
            actionSelection,
            recipientLabel,
            recipientInput,
            amountLabel,
            amountInput,
            addressLabel,
            addressInput,
            sendButton,
        ]

        for item in leftAdd:
            self.leftBox.layout().addWidget(item)

        #### adding features to center box ####
        self.centerBox.layout().addWidget(responseViewer)

        #### adding features to right box ####
        self.rightBox.layout().addWidget(observerViewer)

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
                newNode = addressInput.text()
                print(newNode)

                # data to be sent
                submission = {
                    "nodes": [newNode],
                }

                # sending POST request
                requests.post(f"{nodeAddress}/nodes/register", json=submission)


# instantiating interface
app = QApplication([])
mainWindow = MainWindow()


if __name__ == "__main__":
    app.exec()
