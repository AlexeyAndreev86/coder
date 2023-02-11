from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QFileDialog
import sys
import os
import shutil
import importlib
from google.protobuf import text_format


class Window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.mkdirs()
        self.default_config_path = os.path.join(os.getcwd(), 'pb2', 'Config_pb2.py')
        self.config = self.get_config()
        self.config_short = self.get_short_config_path(self.config)
        self.working_file = None
        self.compiled_config_file = None
        self.get_actual_pb2_by_default(self.config_short)

        self.setWindowTitle('Coder')

        self.button1 = QtWidgets.QPushButton('Choose pb_2 file', self)
        self.button1.setGeometry(10, 10, 200, 50)
        self.button1.setToolTip('Choose your config file. Example, Config_pb2.py')
        self.button1.clicked.connect(self.choose_pb2)

        self.button2 = QtWidgets.QPushButton('Choose file to convert', self)
        self.button2.setGeometry(10, 80, 200, 50)
        self.button2.setToolTip('Choose file to encode or decode')
        self.button2.clicked.connect(self.choose_file)

        self.button3 = QtWidgets.QPushButton('Convert file', self)
        self.button3.setGeometry(10, 150, 200, 50)
        self.button3.setToolTip('Click to encode or decode chosen file')
        self.button3.clicked.connect(self.convert)

        self.label1 = QtWidgets.QLabel(f'Choosen default pb2 file: {self.config_short}', self)
        self.label1.setGeometry(230, 10, 400, 50)
        self.label2 = QtWidgets.QLabel(self)
        self.label2.setGeometry(230, 80, 400, 50)
        self.label3 = QtWidgets.QLabel(self)
        self.label3.setGeometry(230, 150, 400, 50)

    @staticmethod
    def mkdirs():
        scrypt_path = os.getcwd()
        pb2_path = os.path.join(scrypt_path, 'pb2')
        result = os.path.join(scrypt_path, 'result')
        if not os.path.exists(pb2_path):
            os.mkdir('pb2')
        if not os.path.exists(result):
            os.mkdir('result')

    def get_config(self):
        if self.default_config_path is not None:
            if os.path.exists(self.default_config_path):
                return os.path.abspath(self.default_config_path)
        return None

    def get_short_config_path(self, path):
        if path is not None:
            return os.path.basename(path)
        return None

    def get_actual_pb2_by_default(self, short_path):
        """ Если при старте программы файл pb2 лежит в папке pb2, то пытаемся его импортировать. """
        if short_path:
            try:
                path = os.path.join('pb2', short_path[:-3]).replace('\\', '.').replace('/', '.')
                self.compiled_config_file = importlib.import_module(path)
            except Exception as e:
                print(e)
                return None
        else:
            print('You need to choose pb2 file')

    def choose_pb2(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        pb2_file, _ = QFileDialog.getOpenFileName(self, "Choose config file", "", "*.py", options=options)
        if pb2_file:
            self.config = os.path.abspath(pb2_file)
            cfg_path = os.path.basename(self.config)
            # Копируем выбранный файл в подпапку pb2 и пытаемся его импортировать
            try:
                shutil.copy(src=self.config, dst=os.path.join(os.path.splitext(os.getcwd())[0], "pb2"))

                path = os.path.join('pb2', cfg_path[:-3]).replace('\\', '.').replace('/', '.')
                self.compiled_config_file = importlib.import_module(path)
                self.label1.setText(f'Chosen file: {cfg_path}')
            except Exception as e:
                self.label1.setText(f'Exception: {e}')
                print(e)

    def choose_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file, _ = QFileDialog.getOpenFileName(self, "Choose working file (binary or txt)", "", "", options=options)
        if file:
            ext = os.path.splitext(os.path.basename(file))[1]
            if ext not in ('', '.txt'):
                self.label2.setText('<h3 style="color: rgb(250, 55, 55);">Choose other file txt or binary format</h3>')
            else:
                self.working_file = os.path.abspath(file)
                file_path = os.path.basename(self.working_file)
                filetype = os.path.splitext(self.working_file)[1]
                self.label2.setText(f'Chosen file: {file_path}')
                if filetype == '.txt':
                    self.label3.setText('Click to encode')
                elif filetype == '':
                    self.label3.setText('Click to decode')

    @staticmethod
    def ip_to_int32(ip):
        ip = [hex(int(i))[2:] for i in ip.split('.')]
        ip_hex = "0x"
        for num in ip:
            if len(num) < 2:
                ip_hex += "0" + num
            else:
                ip_hex += num
        ip_int32 = int(ip_hex, 0)
        return ip_int32

    @staticmethod
    def int32_to_ip(ip_int32):
        ip_hex = hex(ip_int32)
        first_decimal = str(int(ip_hex[2:4], 16))
        second_decimal = str(int(ip_hex[4:6], 16))
        third_decimal = str(int(ip_hex[6:8], 16))
        fourth_decimal = str(int(ip_hex[8:10], 16))
        ip = first_decimal + "." + second_decimal + "." + third_decimal + "." + fourth_decimal
        return ip

    @staticmethod
    def read_config(path):
        with open(path, "rb") as file:
            config = file.read()
        return config

    @staticmethod
    def write_config_to_txt(config, path):
        with open(path, "w") as file:
            file.write(str(config))

    @staticmethod
    def write_config(config, path):
        with open(path, "wb") as file:
            file.write(config)

    def convert(self):
        if self.working_file is not None:
            filetype = os.path.splitext(self.working_file)[1]
            if filetype == '.txt':
                self.encode()
            elif filetype == '':
                self.decode()

    def decode_fac_ip(self, cfg):
        cfg_str = str(cfg)
        if hasattr(cfg.data.fac.beGw, 'serverIp') and cfg.data.fac.beGw.serverIp != 0:
            beGw_serverIp = cfg.data.fac.beGw.serverIp
            cfg_str = cfg_str.replace(str(beGw_serverIp), self.int32_to_ip(beGw_serverIp))
        if hasattr(cfg.data.fac.canDataGwSvc, 'serverIp') and cfg.data.fac.canDataGwSvc.serverIp != 0:
            canDataGwSvc_serverIp = cfg.data.fac.canDataGwSvc.serverIp
            cfg_str = cfg_str.replace(str(canDataGwSvc_serverIp), self.int32_to_ip(canDataGwSvc_serverIp))
        return cfg_str

    def decode_cfg(self, binary):
        cfg = self.compiled_config_file.CfgMsg()
        cfg.ParseFromString(binary)
        return cfg

    def decode(self):
        try:
            cfg = self.decode_cfg(self.read_config(self.working_file))
            if os.path.basename(self.working_file) == 'facLayerCfg':
                cfg = self.decode_fac_ip(cfg)
            filename = os.path.basename(self.working_file) + '.txt'
            self.write_config_to_txt(cfg, 'result/_' + filename)
            self.label3.setText(f'File saved in: result/{filename}')
        except Exception as e:
            self.label3.setText(f'<h5 style="color: rgb(250, 55, 55);">Error: {e}</h5>')

    def encode_cfg(self, str_):
        try:
            cfg = self.compiled_config_file.CfgMsg()
            cfg = text_format.Parse(str_, cfg)
            return cfg.SerializeToString()
        except Exception as e:
            self.label3.setText(f'<h5 style="color: rgb(250, 55, 55);">Error: {e}</h5>')
            return None

    def encode_fac_ip(self, cfg):
        str_cfg = str(cfg)[2:-1]
        temp = str_cfg.split('serverIp: ')
        for i in range(1, len(temp)):
            ip = self.ip_to_int32(temp[i].split('\\n')[0])
            str_cfg = str_cfg.replace(temp[i].split('\\n')[0], str(ip))
        str_cfg = str_cfg.replace('\\n', '\n')
        return bytes(str_cfg, 'utf-8')

    def encode(self):
        cfg = self.read_config(self.working_file)
        if self.working_file[-16:] == '_facLayerCfg.txt':
            cfg = self.encode_fac_ip(cfg)

        cfg = self.encode_cfg(cfg)
        if cfg is not None:
            filename = os.path.basename(self.working_file)[1:-4]
            self.write_config(cfg, 'result/' + filename)
            self.label3.setText(f'File saved in: result/{filename}')


if __name__ == '__main__':
    application = QApplication(sys.argv)
    win = Window()
    win.setFixedSize(600, 250)
    win.show()
    sys.exit(application.exec())
