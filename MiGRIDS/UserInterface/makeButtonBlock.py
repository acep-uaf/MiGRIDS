# Widget, method, String, String, String -> QtQidget.QPushButton
# returns a button with specified text, icon, hint and connection to the specified function
def makeButtonBlock(parent, buttonFunction, text=None, icon=None, hint=None):
    from PyQt5 import QtWidgets
    if text is not None:
        button = QtWidgets.QPushButton(text, parent)
    else:

        button = QtWidgets.QPushButton(parent)
        button.setIcon(button.style().standardIcon(getattr(QtWidgets.QStyle, icon)))
    if hint is not None:
        button.setToolTip(hint)
        button.setToolTipDuration(2000)
    button.clicked.connect(lambda: parent.onClick(buttonFunction))


    return button
