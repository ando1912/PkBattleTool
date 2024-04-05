import os, sys

import configparser
import datetime
from logging import getLogger

sys.path.append(".")

PATH = os.path.dirname(os.path.abspath(sys.argv[0]))

class ConfigIni(configparser.ConfigParser):
    """
    iniコンフィグの操作を行うクラス
    """
    def __init__(self):
        super().__init__()
        self.logger = getLogger("Log").getChild("ConfigIni")
        self.logger.debug("Hello ConfigIni")

        self.import_conf()

    def set_defaults(self):
        """
        iniコンフィグのデフォルト設定を行う
        """
        self.logger.debug("Execuse set_defaults")
        self["DEFAULT"] = {
                "pokedb_url": "https://sv.pokedb.tokyo/pokemon/list",
                "season": 14,
                "rule": 1,
                "browser_path": "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
                "camera_id": 3,
                "tesseract_path": "C:\\Program Files\\Tesseract-OCR",
                "screenshot_folder": "\\screenshot",
                "display_fps" : 30,
                "display_width" : 640,
                "display_height" : 360}

    def print_conf(self):
        # FIXME: configparserの仕様で、セクションに含まれないキーをDEFAULTから持ってきてしまう
        self.logger.debug("Execuse print_conf")
        cnt = 0
        for section in self:
            for label in self[section]:
                if self.has_option(section,label):
                    cnt = cnt + 1
                    print(f"{cnt}:{section}:{label} = {self[section][label]}")

    def import_conf(self) -> dict:
        """
        iniコンフィグの読み込み
        """
        self.logger.debug("Execuse import_conf")
        self.read(f"{PATH}/config.ini", encoding="utf-8")

        # 設定ファイルが存在しない場合はファイルを生成しデフォルト値を設定
        if not self.has_option("DEFAULT","pokedb_url"):
            print("Create ini ...")
            self.set_defaults()
            with open(f"{PATH}/config.ini", "w") as configfile:
                self.write(configfile)

    def write_conf(self,new_conf):
        # 元のファイルをリネーム
        os.rename(f"{PATH}/config.ini",f"{PATH}/config_{datetime.datetime.now().strftime('%y%m%d%H%M%S')}.ini")
        with open(f"{PATH}/config.ini", 'w') as configfile:
            new_conf.write(configfile)

_util = ConfigIni()

def get(section,key):
    return _util.get(section,key)

def update(new_conf):
    _util.update(new_conf)
    with open(f"{PATH}/config.ini", 'w') as configfile:
        _util.write(configfile)

def debug():
    print("Import ini file ...")
    _util.print_conf()

if __name__=="__main__":
    PATH = os.path.abspath(os.path.join(PATH, os.pardir))
    debug()