import tkinter as tk
import cv2
from logging import getLogger

import webbrowser

from module import config

class MenuBar(tk.Menu):
    def __init__(self, master: tk.Tk, **kwargs):
        """メニューバーの表示

        Args:
            master (tk.Tk): メニューバーを表示する親ウィンドウ
        """
        super().__init__(master, **kwargs)
        self.root = master
        master.config(menu=self)
        
        # Loggerの設定
        self.logger = getLogger("Log").getChild("MenuBar")
        self.logger.debug("Called MenuBar")
        
        # self.subwindow = SubWindowMenu(self.root)
        self.subwindow = None

        # 設定タブ
        setting_menu = tk.Menu(self,tearoff=0)
        setting_menu.add_command(label="環境設定", command=self.on_setting)
        setting_menu.add_command(label="終了",command=self.on_exit)
        self.add_cascade(label="設定",menu=setting_menu)

        # ヘルプ
        help_menu = tk.Menu(self, tearoff=0)
        help_menu.add_command(label="バージョン情報", command=self.on_versioninfo)
        self.add_cascade(label="ヘルプ", menu=help_menu)
    
    def on_setting(self) -> None:
        """
        環境設定
        """
        logger = self.logger.getChild("on_setting")
        logger.info("Run on_setting")
        if self.subwindow is None or not tk.Toplevel.winfo_exists(self.subwindow):
            self.subwindow = tk.Toplevel(self.root)
            self.subwindow.title("環境設定")
            width = 600
            height = 200
            self.set_subwindow_geometry(width, height)
            
            frame = SettingInfo(self.subwindow)
            
            frame.pack(fill=tk.BOTH, pady=10)
        else:
            self.subwindow.lift()

    def on_exit(self) -> None:
        """
        終了確認
        """
        logger = self.logger.getChild("on_exit")
        logger.info("Run on_exit")
        if self.subwindow is None or not tk.Toplevel.winfo_exists(self.subwindow):

            self.subwindow = tk.Toplevel(self.root)
            self.subwindow.title("終了確認")
            width = 300
            height = 100
            self.set_subwindow_geometry(width, height)
            
            frame = CloseSoftware(self.subwindow, self.root)
            frame.pack(fill=tk.BOTH, pady=10)
        else:
            self.subwindow.lift()
        
    def on_versioninfo(self):
        """
        バージョン情報を表示
        """
        logger = self.logger.getChild("on_versioninfo")
        logger.info("Run on_versioninfo")
        if self.subwindow is None or not tk.Toplevel.winfo_exists(self.subwindow):
            self.subwindow = tk.Toplevel(self.root)
            self.subwindow.title = ("バージョン情報")
            width = 300
            height = 120
            self.set_subwindow_geometry(width, height)
            
            frame = VersionInfo(self.subwindow)
            frame.pack(fill=tk.BOTH, pady=10)
        else:
            self.subwindow.lift()
    
    def set_subwindow_geometry(self, width:int, height:int) -> None:
        """画面サイズと位置の設定

        Args:
            width (int): 横幅
            height (int): 縦幅
        """
        logger = self.logger.getChild("set_suwindow_geometry")
        logger.debug("Run set_subwindow_geometry")
        self.subwindow.geometry("{}x{}+{}+{}".format(
                width,
                height,
                int(self.root.winfo_x()+self.root.winfo_width()/2-width/2),
                int(self.root.winfo_y()+self.root.winfo_height()/2-height/2)))

#参考：参考：https://tomtom-stock.com/2022/03/01/tkinter-texthyperlink/
class VersionInfo(tk.Frame):
    def __init__ (self, master:tk.Toplevel, **kwargs):
        """バージョン情報を表示するクラス

        Args:
            master (tk.Toplevel): 親のサブウィンドウ
        """
        super().__init__(master, **kwargs)
        self.root = master
        
        self.logger = getLogger("Log").getChild("VersionInfo")
        self.logger.info("Called VersionInfo")

        label_title = tk.Label(self, text="ポケモン対戦支援ツール", font=("MSゴシック", "10", "bold")).pack()
        label_version = tk.Label(self, text="Version 2.1.3 Beta").pack()
        label_githublink = tk.Label(self, text="https://github.com/ando1912/PkBattleTool", fg="blue", cursor="hand1")
        label_githublink.pack()
        label_githublink.bind("<Button-1>", lambda e:webbrowser.open_new("https://github.com/ando1912/PkBattleTool"))
        label_creator = tk.Label(self, text="Create by Ando Ryoga").pack()
        button_close = tk.Button(self, text="OK", command=self.close).pack()

    # ウィンドウを閉じる
    def close(self):
        """
        終了処理
        """
        self.logger.getChild("close").debug("Run close")
        self.root.destroy()

class CloseSoftware(tk.Frame):
    def __init__(self, master:tk.Toplevel, app:tk.Tk):
        """アプリ終了の確認ポップアップ

        Args:
            master (tk.Toplevel): サブウィンドウ
            app (tk.Tk): メインウィンドウ
        """
        super().__init__(master)
        self.logger = getLogger("Log").getChild("CloseSoftware")
        self.logger.info("Called CloseSoftware")
        
        self.root = master
        self.app = app
        
        # ウェジット
        label_message = tk.Label(self, text="ソフトウェアを終了しますか？",font=("MSゴシック", "15", "bold")).grid(columnspan=2)
        button_yes = tk.Button(self, text="はい", command=self.close_app).grid(row=1,column=0)
        button_no = tk.Button(self, text="いいえ", command=self.close).grid(row=1,column=1)
    
    def close(self) -> None:
        """
        ウィンドウを閉じる
        """
        self.root.destroy()
    
    def close_app(self) -> None:
        """
        アプリケーションを終了させる
        """
        self.app.click_close()

class SettingInfo(tk.Frame):
    #FIXME: カメラのID調査で一時的にアプリケーション処理が止まる
    def __init__(self, master:tk.Toplevel, **kwargs):
        """環境設定ウィンドウ

        Args:
            master (tk.Toplevel): サブウィンドウ
        """
        super().__init__(master, **kwargs)
        self.root = master
        
        self.logger = getLogger("Log").getChild("SettingInfo")
        self.logger.info("Called SettingInfo")

        # ウェジット
        self.label_pokemondb_url = tk.Label(self, text="ポケモンDB-URL")
        self.entry_pokemondb_url = tk.Entry(self, width=40)
        self.entry_pokemondb_url.insert(0,config.get("DEFAULT","pokedb_url"))

        self.label_season = tk.Label(self, text="シーズン設定")
        self.entry_season = tk.Entry(self, width=40)
        self.entry_season.insert(0,config.get("DEFAULT","season"))

        self.label_rule = tk.Label(self, text="ルール\n(0：シングル / 1：ダブル)",justify="left")
        
        self.rule_options = {
            "シングル":0,
            "ダブル":1
        }
        self.rule_value = config.get("DEFAULT","rule")
        self.default_rule_display = "シングル" if self.rule_value=="0" else "ダブル"
        
        self.rule_var = tk.StringVar(value = self.default_rule_display)
        self.option_rule_menu = tk.OptionMenu(self, self.rule_var, *self.rule_options.keys())

        self.label_cameraid = tk.Label(self, text="カメラID")
        
        self.caminfo = self.getCamInfo()
        self.cameraid_options = {f"Camera ID = {key} ({index})":key for key, index in self.caminfo.items()}
        self.cameraid2label = {index:key for key, index in self.cameraid_options.items()}
        
        self.cameraid_value = config.get("DEFAULT","camera_id")
        self.default_cameraid_display = self.cameraid2label[int(self.cameraid_value)]
        
        self.cameraid_var = tk.StringVar(value = self.default_cameraid_display)
        self.option_cameraid_menu = tk.OptionMenu(self, self.cameraid_var, *self.cameraid_options.keys())

        self.label_browser_path = tk.Label(self, text="ブラウザのパス")
        self.entry_browser_path = tk.Entry(self, width=40)
        self.entry_browser_path.insert(0,config.get("DEFAULT","browser_path"))

        self.label_tesseract_path = tk.Label(self, text="Tesseractのパス")
        self.entry_tesseract_path = tk.Entry(self, width=40)
        self.entry_tesseract_path.insert(0,config.get("DEFAULT","tesseract_path"))


        self.button_conf_update = tk.Button(self, text="設定を更新する", command=self.update_config)

        # ウェジットの配置
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # データベースのURL
        self.label_pokemondb_url.grid(row=0,column=0,sticky="W")
        self.entry_pokemondb_url.grid(row=0,column=1,columnspan=2,sticky="EW")

        # シーズン指定
        self.label_season.grid(row=1,column=0,sticky="W")
        self.entry_season.grid(row=1,column=1,columnspan=2,sticky="EW")

        # ルール指定
        self.label_rule.grid(row=2,column=0,sticky="W")
        self.option_rule_menu.grid(row=2,column=1,columnspan=2,sticky="EW")

        # ChromeブラウザのPATH
        self.label_browser_path.grid(row=3,column=0,sticky="W")
        self.entry_browser_path.grid(row=3,column=1,columnspan=2,sticky="EW")

        # カメラID
        self.label_cameraid.grid(row=4,column=0,sticky="W")
        self.option_cameraid_menu.grid(row=4,column=1,columnspan=2,sticky="EW")

        # tesseractのPATH
        self.label_tesseract_path.grid(row=5,column=0,sticky="W")
        self.entry_tesseract_path.grid(row=5,column=1,columnspan=2,sticky="EW")

        self.button_conf_update.grid(row=10,column=1)
        
    def close(self):
        """
        終了処理
        """
        self.root.destroy()
    
    def check_activecam(self, id:int) -> bool:
        """カメラのアクティブ確認

        Args:
            id (int): カメラID

        Returns:
            bool: アクティブ→True, ノンアクティブ→False
        """
        self.logger.getChild("check_activecam").debug("Run check_activecam")
        cap = cv2.VideoCapture(id)
        if cap.isOpened():
            cap.release()
            return True
        else:
            cap.release()
            
            return False
    # カメラのID一覧を取得
    def getCamInfo(self) -> dict:
        """アクティブカメラのID情報を取得

        Returns:
            dict: IDとアクティブ情報の辞書リスト
        """
        logger = self.logger.getChild("getCamInfo")
        logger.debug("Run getCamInfo")
        caminfo = {}

        for i in range(6):
            try:
                cap = cv2.VideoCapture(i)
                caminfo[i] = "Active" if cap.isOpened() else "None"
            except Exception as e:
                self.logger.exception(e)
            finally:
                cap.release()

        return caminfo
    
    def update_config(self) -> None:
        """
        環境設定の更新
        """
        self.logger.getChild("update_config").debug("Run update_config")
        
        # 環境設定の取得
        new_config = {
                "pokedb_url":self.entry_pokemondb_url.get(),
                "season":self.entry_season.get(),
                "rule":str(self.rule_options[self.rule_var.get()]),
                "camera_id":str(self.cameraid_options[self.cameraid_var.get()]),
                "browser_path":self.entry_browser_path.get(),
                "tesseract_path":self.entry_tesseract_path.get()
            }

        # configの更新
        for key, index in new_config.items():
            config.update("DEFAULT",key,index)

        # config.iniを更新する
        config.write()
        
        self.close()