import sys, os
import webbrowser
sys.path.append(".")
from module import config

class SearchDB:
    """
    ポケモンバトルデータベースのページを開き、ポケモン名で検索をかける
    """
    def __init__(self):
        self.url = config.get("DEFAULT","pokedb_url")
        self.season = config.get("DEFAULT","season")
        self.rule = config.get("DEFAULT","rule")
        self.browser_path = config.get("DEFAULT","browser_path")
        self.browser =  webbrowser.get('"{}" %s'.format(self.browser_path))

    def searchdb(self, name):
        self.browser.open_new("{}?season={}&rule={}&name={}".format(self.url,self.season,self.rule,name))

if __name__=="__main__":
    db = SearchDB()
    db.searchdb("メタグロス")