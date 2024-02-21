from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QProgressBar, QGroupBox, QLabel, QApplication,
                             QPushButton, QListWidget, QHBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QTextEdit)

from PyQt6.QtCore import QProcess
from subprocess import Popen, PIPE

class LabelText(QLabel):
    def __init__(self, label, sizeh, sizev):
        super(LabelText, self).__init__()
        self.setText(label)
        self.setFixedSize(sizeh, sizev)


class HorizontalGroup(QGroupBox):
    """ UI wrapper for QGroupBox with integrated GridLayout"""
    def __init__(self, *args):
        super(HorizontalGroup, self).__init__(*args)
        self.path_label = QLabel()
        self.path_label.setText('test text')
        self.browser_button = QPushButton()
        self.browser_button.setText('Browse')
        self.internal_layout = QHBoxLayout()
        self.internal_layout.addWidget(self.path_label)
        self.internal_layout.addWidget(self.browser_button)
        self.setLayout(self.internal_layout)

    def addWidget(self, widget):
        self.internal_layout.addWidget(widget)

    def set_path(self, path):
        self.path_label.setText(path)

    def get_path(self):
        return self.path_label.text()

class Console(QTextEdit):
    def __init__(self):
        super(Console, self).__init__()
        self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.setFixedHeight(200)
        self.setFixedWidth(400)
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.read_output)
        self.process.readyReadStandardError.connect(self.read_error)

    def read_output(self):
        self.append(self.process.readAllStandardOutput().data().decode('utf-8'))

    def read_error(self):
        self.append(self.process.readAllStandardError().data().decode('utf-8'))


class MainWindow(QMainWindow):
    def __init__(self, hde_transcoder_exe_path):
        super().__init__()
        # self.setStyleSheet("background: black;")

        self.setObjectName("Batch Convert Images Window")
        self.setWindowTitle("Batch Convert Images")
        self.centralwidget = QWidget()
        self.setCentralWidget(self.centralwidget)
        self.main_layout = QVBoxLayout(self.centralwidget)
        self.child_layout = QHBoxLayout()
        self.child_layout_02 = QHBoxLayout()

        self.hde_transcoder_exe_path = hde_transcoder_exe_path
        self.command_list: list[list]=[]
        self.dict_source_destination: dict[str:str] = {}

        # ---------  HORIZONTAL LAYOUT 1 ----------
        self.horizontal_lay_01_import = QHBoxLayout(self.centralwidget)
        self.horizontal_lay_01_import.setContentsMargins(0, 0, 0, 0)
        self.horizontal_lay_01_import.setSpacing(0)
        self.horizontal_lay_01_import.setObjectName("horizontal_lay_01_import")

        self.button_browser = QPushButton(self.centralwidget)
        self.button_browser.setText('Browse')
        self.button_browser.clicked.connect(self.browse)
        self.horizontal_lay_01_import.addWidget(self.button_browser)

        self.button_launch = QPushButton(self.centralwidget)
        self.button_launch.setText('Launch HDE Transcoder')
        self.button_launch.clicked.connect(self.launch_hde_transcoder)

        # create a console widget to display the output of the process from the command line
        self.console = Console()
        self.child_layout_02.addWidget(self.console)

        self.list_widget = QListWidget(self)
        self.list_widget.setFixedHeight(200)
        self.list_widget.setFixedWidth(400)
        self.child_layout.addWidget(self.list_widget)

        self.horizontal_lay_01_import.addWidget(self.button_launch)

        self.main_layout.addLayout(self.child_layout)
        self.main_layout.addLayout(self.child_layout_02)

        self.main_layout.addLayout(self.horizontal_lay_01_import)

    def browse(self):
        path_source = QFileDialog.getExistingDirectory(self, "choose the source directory", directory='/Volumes/')
        path_destination = QFileDialog.getExistingDirectory(self, "choose the destination directory", directory='/Volumes/')
        # self.horizontal_lay_01_import.set_path(path)
        if path_source and path_destination:
            self.dict_source_destination[path_source] = path_destination
            self.show_trancoding_list()

    def create_command_list(self):
        for source, destination in self.dict_source_destination.items():
            self.command_list.append([self.hde_transcoder_exe_path, '-c', 'xxhash64', '-v', '-i', source, '-o', destination])

    def launch_hde_transcoder(self):
        """
        Launch the HDE transcoder with the command line and print the output in the console
        :return: None
        """
        self.create_command_list()
        if len(self.command_list) == 0:
            # print('No command to launch')
            QMessageBox(self, 'No command to launch')
        else:

            # process = [Popen(command, stdout=PIPE, stderr=PIPE) for command in self.command_list]
            # process = [Popen(command, stdout=PIPE, stderr=PIPE) for command in self.command_list]
            # for p in process:
            #     while True:
            #         output = p.stdout.readline()
            #         if output == '' and p.poll() is not None:
            #             break
            #         if output:
            #             self.console.append(output.strip().decode('utf-8'))
            #     p.wait()
            #     self.console.setText('Process finished with exit code ' + str(p.returncode))
            process = [Popen(command, stdout=PIPE, stderr=PIPE) for command in self.command_list]
            for p in process:
                while True:
                    output = p.stdout.readline()
                    if output == '' and p.poll() is not None:
                        break
                    if output:
                        self.console.append(output.strip().decode('utf-8'))
                # while True:
                #     output = p.stdout.readline()
                #     if output == '' and p.poll() is not None:
                #         break
                #     if output:
                #         print(output.strip().decode('utf-8'))
                #         self.console.append(output.strip().decode('utf-8'))
                p.wait()
                self.console.setText('Process finished with exit code ' + str(p.returncode))

    def show_trancoding_list(self):
        for source, destination in self.dict_source_destination.items():
            self.list_widget.addItem(source + ' -> ' + destination)


    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message',
                                     "Are you sure to quit?", QMessageBox.StandardButton.Yes |
                                     QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    hde_transcoder_exe_path = '/Users/bryanrandell/PycharmProjects/hde_multi_trancoder/arrirawhde'
    app = QApplication([])
    mainWindow = MainWindow(hde_transcoder_exe_path=hde_transcoder_exe_path)
    mainWindow.show()
    app.exec()
