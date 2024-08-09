import sys, os
import webbrowser
sys.path.append(".")
from module import config

class SearchDB:
    def __init__(self):
        """
        ポケモンバトルデータベースのページを開き、ポケモン名で検索をかける
        """
        self.url = config.get("DEFAULT","pokedb_url")
        self.season = config.get("DEFAULT","season")
        self.rule = config.get("DEFAULT","rule")
        self.browser_path = config.get("DEFAULT","browser_path")
        self.browser =  webbrowser.get('"{}" %s'.format(self.browser_path))

    def searchdb(self, name:str) -> None:
        """ポケモンバトルデータベースのブラウザを開く

        Args:
            name (str): ポケモン名
        """
        self.browser.open_new("{}?season={}&rule={}&name={}".format(self.url,self.season,self.rule,name))