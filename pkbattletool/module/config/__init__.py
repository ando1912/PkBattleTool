import os, sys

import configparser
from logging import getLogger

sys.path.append(".")

PATH = os.path.dirname(os.path.abspath(sys.argv[0]))

class ConfigIni(configparser.ConfigParser):
    def __init__(self):
        """
        iniコンフィグの操作を行うクラス
        """
        super().__init__()
        self.logger = getLogger("Log").getChild("ConfigIni")
        self.logger.info("Called ConfigIni")

        self.import_conf()

    def set_defaults(self):
        """
        iniコンフィグのデフォルト設定を行う
        """
        self.logger.getChild("set_defaults").debug("Run set_defaults")
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
        self.logger.getChild("print_conf").debug("Run print_conf")
        cnt = 0
        for section in self:
            for label in self[section]:
                if self.has_option(section,label):
                    cnt = cnt + 1
                    print(f"{cnt}:{section}:{label} = {self[section][label]}")

    def import_conf(self):
        """
        iniコンフィグの読み込み
        """
        logger = self.logger.getChild("import_conf")
        logger.debug("Run import_conf")
        self.read(f"{PATH}/config.ini", encoding="utf-8")

        # 設定ファイルが存在しない場合はファイルを生成しデフォルト値を設定
        if not self.has_option("DEFAULT","pokedb_url"):
            logger.debug("Create ini ...")
            self.set_defaults()
            with open(f"{PATH}/config.ini", "w") as configfile:
                self.write(configfile)

    def write_conf(self):
        """config.iniの更新時に古いファイルをリネームする
        """
        logger = self.logger.getChild("write_conf")
        logger.debug("Run write_conf")
        path1 = f"{PATH}/config.ini"
        path2 = f"{PATH}/config.ini.old"
        path3 = f"{PATH}/config.ini.old2"
        
        # 2つ前のiniファイルがあったら削除する
        if os.path.exists(path3):
            os.remove(path3)
            logger.debug(f"Remove config.ini.old2")
        
        # 1つ前のiniファイルがあったらold2へリネームする
        if os.path.exists(path2):
            os.rename(path2, path3)
            logger.debug("Rename config.ini.old -> config.ini.old2")
        
        # config.iniをconfig.ini.oldにリネームする
        os.rename(path1,path2)
        logger.debug("Rename config.ini -> config.ini.old")
        
        # config.iniを新しく書き出す
        with open(f"{PATH}/config.ini", 'w') as configfile:
            self.write(configfile)
        logger.debug("Write config.ini")

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