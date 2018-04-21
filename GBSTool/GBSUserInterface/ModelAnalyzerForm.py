class SetupForm(QtWidgets.QWidget):
    global model
    model = SetupInformation()

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setObjectName("setupDialog")
        # self.resize(1754, 3000)
        self.model = model