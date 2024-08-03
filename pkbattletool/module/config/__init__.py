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

    def write_conf(self):
        path1 = f"{PATH}/config.ini"
        path2 = f"{PATH}/config.ini.old"
        path3 = f"{PATH}/config.ini.old2"
        
        # 2つ前のiniファイルがあったら削除する
        if os.path.exists(path3):
            os.remove(path3)
        # 1つ前のiniファイルがあったらold2へリネームする
        if os.path.exists(path2):
            os.rename(path2, path3)
        # config.iniをconfig.ini.oldにリネームする
        os.rename(path1,path2)
        # config.iniを新しく書き出す
        with open(f"{PATH}/config.ini", 'w') as configfile:
            self.write(configfile)

_util = ConfigIni()

# 設定値の取得
def get(section,key):
    return _util.get(section,key)

# 設定の更新
def update(section,key,value):
    _util[section][key] = value

def write():
    _util.write_conf()

def debug():
    print("Import ini file ...")
    _util.print_conf()

if __name__=="__main__":
    PATH = os.path.abspath(os.path.join(PATH, os.pardir))
    debug()