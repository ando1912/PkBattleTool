import tkinter as tk
import re
from logging import getLogger

from module import config

class MenuBar(tk.Menu):
    # TODO サブウィンドウが表示されていた場合は追加で表示しないようにする
    """メニューバー作成クラス"""
    def __init__(self, master,**kwargs):
        super().__init__(master, **kwargs)
        self.root = master
        master.config(menu=self)
        self.logger = getLogger("Log").getChild("MenuBar")
        self.logger.debug("Hello MenuBar")
        
        self.subwindow = SubWindowMenu(self)

        # 設定タブ
        setting_menu = tk.Menu(self,tearoff=0)
        self.add_cascade(label="設定",menu=setting_menu)
        setting_menu.add_cascade(label="環境設定", command=self.on_setting)
        setting_menu.add_command(label="終了",command=self.on_exit)

        # ヘルプ
        help_menu = tk.Menu(self, tearoff=0)
        self.add_cascade(label="ヘルプ", menu=help_menu)
        help_menu.add_command(label="バージョン情報", command=self.on_versioninfo)
    
    def on_setting(self):
        # print("環境設定を選択")
        self.logger.debug("Execute on_setting")
        self.subwindow.create_setting_window()

    def on_exit(self):
        # print("終了を選択")
        self.logger.debug("Execute on_exit")
        self.subwindow.create_close_window(self.root)
    def on_versioninfo(self):
        # print("バージョン情報を選択")
        self.logger.debug("Execute on_versioninfo")
        self.subwindow.create_versioninfo_window()


# サブウィンドウ作成
class SubWindowMenu(tk.Toplevel):
    """
    サブウィンドウ作成クラス
    引数として親ルート、iniコンフィグを渡す
    """
    def __init__(self, master:tk):
        self.root = master
        self.sub_window = None
        self.logger = getLogger("Log").getChild("SubWindowMenu")

        self.root_width = 0
        self.root_height = 0
        self.root_x = 0
        self.root_y = 0
    
    # メインウィンドウの座標計算
    def extract_coordinates(self):
        self.logger.debug("Exectute extract_coordinates")
        # 正規表現パターン
        pattern = r"(\d+)x(\d+)\+(\d+)\+(\d+)"
        match = re.search(pattern, self.root.master.geometry())
        if match:
            self.root_width,self.root_height,self.root_x, self.root_y = map(int, match.groups())

    def close(self, root):
        self.logger.debug("Execute close")
        """
        引数として与えたrootを閉じる
        """
        root.destroy()

    def create_versioninfo_window(self):
        """
        バージョン情報ウィンドウ
        """
        self.logger.debug("Execute create_versioninfo_window")
        self.extract_coordinates()
        width = 300
        height = 150

        self.sub_window = tk.Toplevel(self.root)
        self.sub_window.title("バージョン情報")
        self.sub_window.geometry("{}x{}+{}+{}".format(
            width,
            height,
            int(self.root_x+self.root_width/2-width/2),
            int(self.root_y+self.root_height/2-height/2)))

        # メインフレーム
        frame = tk.Frame(self.sub_window)
        frame.pack(fill=tk.BOTH, pady=10)

        label_title = tk.Label(frame, text="ポケモン対戦支援ツール", font=("MSゴシック", "10", "bold")).pack()
        label_version = tk.Label(frame, text="version beta 1.3").pack()
        label_creator = tk.Label(frame, text="Create by Ando Ryoga").pack()
        button_close = tk.Button(frame, text="OK", command=lambda:self.close(self.sub_window)).pack()

    def create_close_window(self, master):
        """
        終了ウィンドウ
        引数としてメインウィンドウのrootを渡す
        """
        self.logger.debug("Execute create_close_window")
        self.extract_coordinates()
        width = 300
        height = 100

        self.sub_window = tk.Toplevel(self.root)
        self.sub_window.title("ウィンドウを閉じる")
        self.sub_window.geometry("{}x{}+{}+{}".format(
            width,
            height,
            int(self.root_x+self.root_width/2-width/2),
            int(self.root_y+self.root_height/2-height/2)))

        # メインフレーム
        frame = tk.Frame(self.sub_window)
        frame.pack(fill=tk.BOTH, pady=10)

        # ウェジット
        label_message = tk.Label(frame, text="ソフトウェアを終了しますか？",font=("MSゴシック", "15", "bold")).grid(columnspan=2)
        # button_yes = tk.Button(frame, text="はい", command=lambda:self.close(master)).grid(row=1,column=0)
        button_yes = tk.Button(frame, text="はい", command=master.destroy).grid(row=1,column=0)
        button_no = tk.Button(frame, text="いいえ", command=lambda:self.close(self.sub_window)).grid(row=1,column=1)

    def create_setting_window(self):
        """
        環境設定ウィンドウ
        iniコンフィグを渡す
        """
        self.logger.debug("Execute create_setting_window")
        self.extract_coordinates()
        width = 400
        height = 200

        self.sub_window = tk.Toplevel(self.root)
        self.sub_window.title("環境設定")
        self.sub_window.geometry("{}x{}+{}+{}".format(
            width,
            height,
            int(self.root_x+self.root_width/2-width/2),
            int(self.root_y+self.root_height/2-height/2)))


        # メインフレーム
        frame = tk.Frame(self.sub_window)
        frame.pack(fill=tk.BOTH, pady=10)

        # ウェジット
        label_pokemondb_url = tk.Label(frame, text="ポケモンDB-URL")
        entry_pokemondb_url = tk.Entry(frame, width=20)
        entry_pokemondb_url.insert(0,config.get("DEFAULT","pokedb_url"))

        label_season = tk.Label(frame, text="シーズン設定")
        entry_season = tk.Entry(frame, width=20)
        entry_season.insert(0,config.get("DEFAULT","season"))

        label_rule = tk.Label(frame, text="ルール\n(0：シングル / 1：ダブル)",justify="left")
        entry_rule = tk.Entry(frame, width=20)
        entry_rule.insert(0,config.get("DEFAULT","rule"))

        label_cameraid = tk.Label(frame, text="カメラID")
        entry_cameraid = tk.Entry(frame, width=20)
        entry_cameraid.insert(0,config.get("DEFAULT","camera_id"))

        label_browser_path = tk.Label(frame, text="ブラウザのパス")
        entry_browser_path = tk.Entry(frame, width=20)
        entry_browser_path.insert(0,config.get("DEFAULT","browser_path"))

        label_tesseract_path = tk.Label(frame, text="Tesseractのパス")
        entry_tesseract_path = tk.Entry(frame, width=20)
        entry_tesseract_path.insert(0,config.get("DEFAULT","tesseract_path"))


        def update_config():
            self.logger.debug("Execute update_config")
            pokemondb_url = entry_pokemondb_url.get()
            season = entry_season.get()
            rule = entry_rule.get()
            cameraid = entry_cameraid.get()
            browser_path = entry_browser_path.get()
            tesseract_path = entry_tesseract_path.get()

            new_ini_config["DEFAULT"]["pokedb_url"] = pokemondb_url
            new_ini_config["DEFAULT"]["season"] = season
            new_ini_config["DEFAULT"]["rule"] = rule
            new_ini_config["DEFAULT"]["camera_id"] = cameraid
            new_ini_config["DEFAULT"]["browser_path"] = browser_path
            new_ini_config["DEFAULT"]["tesseract_path"] = tesseract_path

            self.config.write_conf(new_ini_config)

        button_update = tk.Button(frame, text="設定を更新する", command=update_config)

        # ウェジットの配置
        label_pokemondb_url.grid(row=0,column=0,sticky="W")
        entry_pokemondb_url.grid(row=0,column=1,columnspan=2,sticky="W")

        label_season.grid(row=1,column=0,sticky="W")
        entry_season.grid(row=1,column=1,columnspan=2,sticky="W")

        label_rule.grid(row=2,column=0,sticky="W")
        entry_rule.grid(row=2,column=1,columnspan=2,sticky="W")

        label_browser_path.grid(row=3,column=0,sticky="W")
        entry_browser_path.grid(row=3,column=1,columnspan=2,sticky="W")

        label_cameraid.grid(row=4,column=0,sticky="W")
        entry_cameraid.grid(row=4,column=1,columnspan=2,sticky="W")

        label_tesseract_path.grid(row=5,column=0,sticky="W")
        entry_tesseract_path.grid(row=5,column=1,columnspan=2,sticky="W")

        button_update.grid(row=10,column=2)
