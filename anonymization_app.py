import pydicom
import os
import json
import re
from pathlib import Path
from pydicom._dicom_dict import DicomDictionary

from PyQt6 import QtWidgets, QtCore, QtGui

from anonymization import Ui_MainWindow


class MainView(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.tableMetadata.setRowCount(0)
        self.ui.tableMetadata.setColumnCount(4)
        self.ui.tableMetadata.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.ui.tableMetadata.setSelectionBehavior(QtWidgets.QTableWidget.SelectionBehavior.SelectRows)
        self.ui.tableMetadata.setSelectionMode(QtWidgets.QTableWidget.SelectionMode.SingleSelection)
        self.ui.tableMetadata.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.ui.tableMetadata.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem('Name'))
        self.ui.tableMetadata.setHorizontalHeaderItem(1, QtWidgets.QTableWidgetItem('Group'))
        self.ui.tableMetadata.setHorizontalHeaderItem(2, QtWidgets.QTableWidgetItem('Element'))
        self.ui.tableMetadata.setHorizontalHeaderItem(3, QtWidgets.QTableWidgetItem('Value'))
        self.ui.tableMetadata.keyPressEvent = self.table_key_press_event

        self.ui.btnSetInput.clicked.connect(self.btn_set_input_clicked)
        self.ui.btnSetOutput.clicked.connect(self.btn_set_output_clicked)
        self.ui.btnAdd.clicked.connect(self.btn_add_clicked)
        self.ui.btnSavePreset.clicked.connect(self.btn_save_preset_clicked)
        self.ui.btnAnonymization.clicked.connect(self.btn_anonymization_clicked)
        self.ui.comboTag.currentTextChanged.connect(self.combo_tag_selection_changed)
        self.ui.comboPreset.currentTextChanged.connect(self.combo_preset_selection_changed)

        self.ui.comboTag.addItem('')
        self.ui.comboTag.addItem("Patient's Name")
        self.ui.comboTag.addItem("Patient ID")
        self.ui.comboTag.addItem("Patient's Birth Date")
        self.ui.comboTag.addItem("Patient's Sex")
        self.ui.comboTag.addItem("Patient's Age")
        self.ui.comboTag.addItem("Requesting Physician")
        self.ui.comboTag.addItem("Instance Creation Date")
        self.ui.comboTag.addItem("Instance Creation Time")
        self.ui.comboTag.addItem("Study Date")
        self.ui.comboTag.addItem("Series Date")
        self.ui.comboTag.addItem("Acquisition Date")
        self.ui.comboTag.addItem("Content Date")
        self.ui.comboTag.addItem("Study Time")
        self.ui.comboTag.addItem("Series Time")
        self.ui.comboTag.addItem("Acquisition Time")
        self.ui.comboTag.addItem("Content Time")
        self.ui.comboTag.addItem("Institution Name")
        self.ui.comboTag.addItem("Institution Address")
        self.ui.comboTag.addItem("Referring Physician's Name")
        self.ui.comboTag.addItem("Station Name")
        self.ui.comboTag.addItem("Physician(s) of Record")

        self.preset = {}

        if os.path.exists('preset.json'):
            with open('preset.json') as f:
                self.preset = json.load(f)
            f.close()
        else:
            self.preset = {"default": [
                {"name": "Patient's Name",
                 "group": "0010",
                 "element": "0010",
                 "value": "ANONYMIZED"},
                {"name": "Patient ID",
                 "group": "0010",
                 "element": "0020",
                 "value": "ANONYMIZED"},
                {"name": "Patient's Birth Date",
                 "group": "0010",
                 "element": "0030",
                 "value": "UNKNOWN"},
                {"name": "Patient's Age",
                 "group": "0010",
                 "element": "1010",
                 "value": "UNKNOWN"},
                {"name": "Instance Creation Date",
                 "group": "0008",
                 "element": "0012",
                 "value": "000099"},
                {"name": "Instance Creation Time",
                 "group": "0008",
                 "element": "0013",
                 "value": "000000.0000"},
                {"name": "Study Date",
                 "group": "0008",
                 "element": "0020",
                 "value": "000099"},
                {"name": "Series Date",
                 "group": "0008",
                 "element": "0021",
                 "value": "000099"},
                {"name": "Acquisition Date",
                 "group": "0008",
                 "element": "0022",
                 "value": "000099"},
                {"name": "Content Date",
                 "group": "0008",
                 "element": "0023",
                 "value": "000099"},
                {"name": "Acquisition DateTime",
                 "group": "0008",
                 "element": "002A",
                 "value": "000000.0000"},
                {"name": "Study Time",
                 "group": "0008",
                 "element": "0030",
                 "value": "000000.0000"},
                {"name": "Series Time",
                 "group": "0008",
                 "element": "0031",
                 "value": "000000.0000"},
                {"name": "Acquisition Time",
                 "group": "0008",
                 "element": "0032",
                 "value": "000000.0000"},
                {"name": "Content Time",
                 "group": "0008",
                 "element": "0033",
                 "value": "000000.0000"}
            ]}
            with open('preset.json', 'w') as f:
                json.dump(self.preset, f, indent=2)
            f.close()
        self.ui.comboPreset.addItem('')
        if len(self.preset.keys()) != 0:
            for key, val in self.preset.items():
                self.ui.comboPreset.addItem(key)

    def table_key_press_event(self, event):
        QtWidgets.QTableWidget.keyPressEvent(self.ui.tableMetadata, event)
        if event.type() == QtCore.QEvent.Type.KeyPress and event.key() == QtCore.Qt.Key.Key_Delete:
            row = self.ui.tableMetadata.selectedItems()[0].row()
            self.ui.tableMetadata.removeRow(row)

    def btn_set_input_clicked(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            'Select Input DICOM Path'
        )
        if path:
            self.ui.editInput.setText(path)

    def btn_set_output_clicked(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            'Select Output DICOM Path'
        )
        if path:
            self.ui.editOutput.setText(path)

    def combo_tag_selection_changed(self):
        if self.ui.comboTag.currentText() == '':
            return
        elif self.ui.comboTag.currentText() == "Patient's Name":
            self.ui.lineTagHI.setText('0010')
            self.ui.lineTagLO.setText('0010')
        elif self.ui.comboTag.currentText() == "Patient ID":
            self.ui.lineTagHI.setText('0010')
            self.ui.lineTagLO.setText('0020')
        elif self.ui.comboTag.currentText() == "Patient's Birth Date":
            self.ui.lineTagHI.setText('0010')
            self.ui.lineTagLO.setText('0030')
        elif self.ui.comboTag.currentText() == "Patient's Sex":
            self.ui.lineTagHI.setText('0010')
            self.ui.lineTagLO.setText('0040')
        elif self.ui.comboTag.currentText() == "Patient's Age":
            self.ui.lineTagHI.setText('0010')
            self.ui.lineTagLO.setText('1010')
        elif self.ui.comboTag.currentText() == "Requesting Physician":
            self.ui.lineTagHI.setText('0032')
            self.ui.lineTagLO.setText('1032')
        elif self.ui.comboTag.currentText() == "Instance Creation Date":
            self.ui.lineTagHI.setText('0008')
            self.ui.lineTagLO.setText('0012')
        elif self.ui.comboTag.currentText() == "Instance Creation Time":
            self.ui.lineTagHI.setText('0008')
            self.ui.lineTagLO.setText('0013')
        elif self.ui.comboTag.currentText() == "Study Date":
            self.ui.lineTagHI.setText('0008')
            self.ui.lineTagLO.setText('0020')
        elif self.ui.comboTag.currentText() == "Series Date":
            self.ui.lineTagHI.setText('0008')
            self.ui.lineTagLO.setText('0021')
        elif self.ui.comboTag.currentText() == "Acquisition Date":
            self.ui.lineTagHI.setText('0008')
            self.ui.lineTagLO.setText('0022')
        elif self.ui.comboTag.currentText() == "Content Date":
            self.ui.lineTagHI.setText('0008')
            self.ui.lineTagLO.setText('0023')
        elif self.ui.comboTag.currentText() == "Study Time":
            self.ui.lineTagHI.setText('0008')
            self.ui.lineTagLO.setText('0030')
        elif self.ui.comboTag.currentText() == "Series Time":
            self.ui.lineTagHI.setText('0008')
            self.ui.lineTagLO.setText('0031')
        elif self.ui.comboTag.currentText() == "Acquisition Time":
            self.ui.lineTagHI.setText('0008')
            self.ui.lineTagLO.setText('0032')
        elif self.ui.comboTag.currentText() == "Content Time":
            self.ui.lineTagHI.setText('0008')
            self.ui.lineTagLO.setText('0033')
        elif self.ui.comboTag.currentText() == "Institution Name":
            self.ui.lineTagHI.setText('0008')
            self.ui.lineTagLO.setText('0080')
        elif self.ui.comboTag.currentText() == "Institution Address":
            self.ui.lineTagHI.setText('0008')
            self.ui.lineTagLO.setText('0081')
        elif self.ui.comboTag.currentText() == "Referring Physician's Name":
            self.ui.lineTagHI.setText('0008')
            self.ui.lineTagLO.setText('0090')
        elif self.ui.comboTag.currentText() == "Station Name":
            self.ui.lineTagHI.setText('0008')
            self.ui.lineTagLO.setText('1010')
        elif self.ui.comboTag.currentText() == "Physician(s) of Record":
            self.ui.lineTagHI.setText('0008')
            self.ui.lineTagLO.setText('1048')
        else:
            return

    def combo_preset_selection_changed(self):
        if self.ui.comboPreset.currentText() in self.preset:
            self.ui.tableMetadata.setRowCount(0)
            obj = self.preset[self.ui.comboPreset.currentText()]
            if isinstance(obj, list):
                for i in obj:
                    rows = self.ui.tableMetadata.rowCount()
                    self.ui.tableMetadata.insertRow(rows)
                    for key, val in i.items():
                        if key == 'name':
                            self.ui.tableMetadata.setItem(rows, 0, QtWidgets.QTableWidgetItem(val))
                        elif key == 'group':
                            self.ui.tableMetadata.setItem(rows, 1, QtWidgets.QTableWidgetItem(val))
                        elif key == 'element':
                            self.ui.tableMetadata.setItem(rows, 2, QtWidgets.QTableWidgetItem(val))
                        elif key == 'value':
                            self.ui.tableMetadata.setItem(rows, 3, QtWidgets.QTableWidgetItem(val))

    def btn_add_clicked(self):
        p = re.compile('^[0-9a-fA-F]{4}$')
        if not p.match(self.ui.lineTagHI.text()):
            QtWidgets.QMessageBox.critical(self, 'Tag type error', 'Invalid group tag format!')
            return
        if not p.match(self.ui.lineTagLO.text()):
            QtWidgets.QMessageBox.critical(self, 'Tag type error', 'Invalid element tag format!')
            return
        if len(self.ui.editValue.text()) == 0:
            QtWidgets.QMessageBox.critical(self, 'Value field empty', 'Value field is empty!')
            return
        hex_string = '0x' + self.ui.lineTagHI.text().upper() + self.ui.lineTagLO.text().upper()
        an_integer = int(hex_string, 16)

        tag_name = ''
        if an_integer in DicomDictionary:
            tag_name = DicomDictionary[an_integer][2]

        rows = self.ui.tableMetadata.rowCount()
        match_item = self.ui.tableMetadata.findItems(tag_name, QtCore.Qt.MatchFlag.MatchExactly)
        match_flag = False
        if match_item:
            for i in match_item:
                if i.column() == 0:
                    match_flag = True
                    rows = i.row()

        if not match_flag:
            self.ui.tableMetadata.insertRow(rows)

        # self.ui.tableMetadata.setItem(rows, 0, QtWidgets.QTableWidgetItem(self.ui.comboTag.currentText()))
        self.ui.tableMetadata.setItem(rows, 0, QtWidgets.QTableWidgetItem(tag_name))
        self.ui.tableMetadata.setItem(rows, 1, QtWidgets.QTableWidgetItem(self.ui.lineTagHI.text().upper()))
        self.ui.tableMetadata.setItem(rows, 2, QtWidgets.QTableWidgetItem(self.ui.lineTagLO.text().upper()))
        self.ui.tableMetadata.setItem(rows, 3, QtWidgets.QTableWidgetItem(self.ui.editValue.text()))

    def btn_save_preset_clicked(self):
        if len(self.ui.comboPreset.currentText()) != 0:
            rows = self.ui.tableMetadata.rowCount()
            preset_arr = []
            for i in range(rows):
                name = self.ui.tableMetadata.item(i, 0).text()
                group = self.ui.tableMetadata.item(i, 1).text()
                elem = self.ui.tableMetadata.item(i, 2).text()
                value = self.ui.tableMetadata.item(i, 3).text()
                obj = {
                    "name": name,
                    "group": group,
                    "element": elem,
                    "value": value
                }
                preset_arr.append(obj)
            self.preset[self.ui.comboPreset.currentText()] = preset_arr
            with open('preset.json', 'w') as f:
                json.dump(self.preset, f, indent=2)
            f.close()

    def btn_anonymization_clicked(self):
        if len(self.ui.editInput.text()) == 0 or len(self.ui.editOutput.text()) == 0:
            QtWidgets.QMessageBox.critical(self, 'Path field empty', 'Input or Output path is empty!')
            return
        input_path = self.ui.editInput.text()
        output_path = self.ui.editOutput.text()
        if not os.path.exists(input_path):
            QtWidgets.QMessageBox.critical(self, 'Input path is not exist', 'Input path is not exist!')
            return
        flist = get_file_list(input_path)

        try:
            os.makedirs(output_path)
        except FileExistsError:
            pass
        except PermissionError:
            QtWidgets.QMessageBox.critical(self, 'Permission error', 'permission error.')
            return

        obj_anonymization = {}
        rows = self.ui.tableMetadata.rowCount()
        for i in range(rows):
            hex_string = '0x' + self.ui.tableMetadata.item(i, 1).text() + self.ui.tableMetadata.item(i, 2).text()
            an_integer = int(hex_string, 16)
            obj_anonymization[an_integer] = self.ui.tableMetadata.item(i, 3).text()

        de_identifier_count = 0
        dicom_time_dict = dict()
        valid_dicom_list = []
        for fpath in flist:
            if check_valid_dicom(fpath, dicom_time_dict):
                valid_dicom_list.append(fpath)
        f_iter = 0.1
        for key, val in dicom_time_dict.items():
            val.sort(key=lambda x: x[1])
            before_time = 0.0
            for idx, d in enumerate(val):
                if d[1] != before_time:
                    new_tup = (d[0], f_iter)
                    before_time = f_iter
                    f_iter = f_iter + 0.1
                    val[idx] = new_tup
        for fpath in flist:
            e = de_identifier(fpath, input_path, output_path, obj_anonymization, dicom_time_dict)
            if e is None:
                de_identifier_count = de_identifier_count + 1
            else:
                print(e)
        msg = str(de_identifier_count) + 'file(s) are anonymized!'
        QtWidgets.QMessageBox.information(self, 'Done!', msg)


def get_file_list(dir_path):
    flist = []
    for subdir, dirs, files in os.walk(dir_path):
        for file in files:
            filepath = subdir + '/' + file
            flist.append(filepath)

    return flist


datetimeTag = [524306, 524307, 524320, 524321, 524322, 524323, 524330, 524336, 524337, 524338, 524339]


def check_valid_dicom(filepath, dicom_dict):
    try:
        metadata = pydicom.filereader.dcmread(str(filepath))
        if metadata.StudyInstanceUID not in dicom_dict:
            dicom_dict[metadata.StudyInstanceUID] = []
        if metadata.SeriesTime is not None:
            dicom_dict[metadata.StudyInstanceUID].append((filepath, float(metadata.SeriesTime)))
    except(Exception,):
        print(filepath, Exception)
        return False
    return True


def de_identifier(filepath, input_dir, output_dir, dict_anonymization, time_dict):
    try:
        metadata = pydicom.filereader.dcmread(str(filepath))
        input_dir_unix_style = QtCore.QDir.fromNativeSeparators(input_dir)
        output_dir_unix_style = QtCore.QDir.fromNativeSeparators(output_dir)
        filepath_unix_style = QtCore.QDir.fromNativeSeparators(filepath)
        output_filepath = filepath_unix_style.replace(input_dir_unix_style, output_dir_unix_style)
    except(Exception,):
        return 'de_identifier // file reading error. '

    for key, val in dict_anonymization.items():
        try:
            if key in metadata.keys():
                elem = metadata[key]
                if key in datetimeTag:
                    p_date = re.compile('^[0-9]{8}$')
                    p_time = re.compile('^[0-9]{6,14}\\.[0-9]{1,30}$')
                    data_val = elem.value
                    if p_date.match(data_val):
                        data_val = data_val[:6] + '99'
                        elem.value = data_val
                    if p_time.match(data_val):
                        temp_dict = dict(time_dict[metadata.StudyInstanceUID])
                        new_time = "{:011.4f}".format(temp_dict[filepath])
                        elem.value = new_time
                    if key == 524336:
                        elem.value = '000000.0000'
                else:
                    elem.value = val
        except(Exception,):
            print('de_identifier error')

    try:
        metadata.save_as(str(output_filepath))
    except FileNotFoundError:
        dirname = os.path.dirname(output_filepath)
        if not os.path.exists(dirname):
            path = Path(dirname)
            path.mkdir(parents=True, exist_ok=True)
            metadata.save_as(str(output_filepath))
            # os.mkdir(dirname)

    # try:
    #     elem = metadata['PatientName']
    #     print(elem.value)
    #     elem.value = 'MYNAME'
    #     print(metadata.PatientName)
    # except(Exception,):
    #     return 'de_identifier error'


def main():
    import sys

    def resource_path(relative_path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)
    app = QtWidgets.QApplication(sys.argv)
    # app.setWindowIcon(QtGui.QIcon(resource_path('anonymization.ico')))
    main_window = MainView()
    main_window.show()
    sys.exit(app.exec())
    # parser = argparse.ArgumentParser(prog='Anonymization', description="DICOM Anonymization")
    # parser.add_argument('-i', '--input', help='input dicom directory path')
    # parser.add_argument('-o', '--output', help='output dicom directory path')
    #
    # args = parser.parse_args()
    #
    # flist = get_file_list(args.input)
    #
    # for fpath in flist:
    #     e = de_identifier_for_multi(fpath)
    #     if e is not None:
    #         print(e)


if __name__ == '__main__':
    main()
