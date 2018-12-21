from PyQt5 import QtWidgets
from Controller.UIToHandler import UIToHandler
class TableHandler():

    def __init__(self, parent):
        self.parent = parent
    #create a new empty record in the specified table
    #String -> None
    def functionForNewRecord(self, table, **kwargs):
        # add an empty record to the table

        # get the model
        tableView = self.parent.findChild((QtWidgets.QTableView), table)
        model = tableView.model()

        # insert an empty row as the last record
        model.insertRows(model.rowCount(), 1)
        model.submitAll()

        #this makes the first column editable (set, filedir, ect.)
        tableView.openPersistentEditor(model.index(model.rowCount()-1, 1))
        #fields are integer column positions
        fields = kwargs.get('fields')
        if (len(fields) > 0):
            values = kwargs.get('values')
            for i,n in enumerate(fields):
                tableView.model().setData(model.index(model.rowCount()-1, n), values[i])

    #removes selected records from the table and its underlying sql table
    #String -> None
    def functionForDeleteRecord(self, table):
        # get selected rows
        tableView = self.parent.findChild((QtWidgets.QTableView), table)
        model = tableView.model()
        # selected is the indices of the selected rows
        selected = tableView.selectionModel().selection().indexes()
        if len(selected) == 0:
            #exit if no rows were selected
            msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Select Rows',
                                        'Select rows before attempting to delete')
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec()

        else:
            #confirm delete
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

        return