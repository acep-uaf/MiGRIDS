from PyQt5 import QtWidgets
from UIToHandler import UIToHandler
class TableHandler():

    def __init__(self, parent):
        self.parent = parent

    def functionForNewRecord(self, table):
        # add an empty record to the table

        # get the model
        tableView = self.parent.findChild((QtWidgets.QTableView), table)
        model = tableView.model()
        # insert an empty row as the last record

        model.insertRows(model.rowCount(), 1)
        model.submitAll()
        #TODO change the persistent editor column to come as a parameter that is table specific
        #this is only for set table
        tableView.openPersistentEditor(model.index(model.rowCount()-1, 1))


    def functionForDeleteRecord(self, table):
        # get selected rows
        tableView = self.parent.findChild((QtWidgets.QTableView), table)
        model = tableView.model()
        # selected is the indices of the selected rows
        selected = tableView.selectionModel().selection().indexes()
        if len(selected) == 0:
            msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Select Rows',
                                        'Select rows before attempting to delete')
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec()
        else:
            msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Confirm Delete',
                                        'Are you sure you want to delete the selected records?')
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)

            result = msg.exec()

            if result == 1024:
                handler = UIToHandler()
                for r in selected:
                    model.removeRows(r.row(), 1)

                # Delete the record from the database and refresh the tableview
                model.submitAll()
                model.select()

