import os, sys

import datetime
import pandas as pd
from PIL import Image, ImageTk
import cv2
import numpy as np
import tkinter as tk
import Levenshtein

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import rcParams
rcParams["font.family"] = "sans-serif"
rcParams["font.sans-serif"] = ["Meiryo"]

from logging import getLogger

from module import config, pkcsv
from mylib import CameraCapture, SearchDB, CameraControl, PkTypeCompatibility, PkHash, CameraFrameForge, OcrRunner, OcrControl

PATH = os.path.dirname(os.path.abspath(sys.argv[0]))

# TODO: メインウィンドウサイズに合わせて、各フレームサイズを自動で調整したい

class PKInfo(tk.Frame):
    """
    ポケモンの名前、図鑑番号、タイプなどの情報や、対戦データベースへの検索ボタンなどを含んだフレームを実装する
    """
    def __init__(self, master:tk, camera_capture:CameraCapture, **kwargs):
        super().__init__(master, **kwargs)
        self.logger = getLogger("Log").getChild("PKInfo")
        self.logger.debug("Hello PkInfo")

        self.camera_capture = camera_capture

        self.font = ("MS ゴシック", 15)
        # ウェジット定義
        self.label_name = tk.Label(self, text = "名前", font=self.font, padx=2, pady=2)
        self.label_index = tk.Label(self, text="図鑑No",font=self.font, padx=2, pady=2)
        self.label_type1 = tk.Label(self, text="タイプ1", font=self.font, padx=2, pady=2)
        self.label_type2 = tk.Label(self, text="タイプ2", font=self.font, padx=2, pady=2)

        self.entry_name = tk.Entry(self, font=self.font)
        self.label_value_name = tk.Label(self, font=self.font, padx=2, pady=2)
        self.label_value_index = tk.Label(self,font=self.font, padx=2, pady=2)
        self.label_value_type1 = tk.Label(self,font=self.font, padx=2, pady=2)
        self.label_value_type2 = tk.Label(self,font=self.font, padx=2, pady=2)

        self.button_searchname = tk.Button(self, text="検索", command=self.func_search_name)
        self.button_searchdb = tk.Button(self, text="使用率ランキングを検索",command=self.func_searchdb)

        # ウェジット配置
        self.entry_name.grid(row=0,column=0, columnspan=2,sticky=tk.W+tk.E)
        self.label_name.grid(row=1,column=0,sticky=tk.W+tk.E)
        self.label_value_name.grid(row=1,column=1,sticky=tk.W+tk.E)
        self.label_index.grid(row=2,column=0,sticky=tk.W+tk.E)
        self.label_value_index.grid(row=2,column=1,sticky=tk.W+tk.E)
        self.label_type1.grid(row=3,column=0,sticky=tk.W+tk.E)
        self.label_value_type1.grid(row=3,column=1,sticky=tk.W+tk.E)
        self.label_type2.grid(row=4,column=0,sticky=tk.W+tk.E)
        self.label_value_type2.grid(row=4,column=1,sticky=tk.W+tk.E)

        self.button_searchname.grid(row=0,column=2,padx=2,pady=2,sticky=tk.W+tk.E+tk.N+tk.S)
        self.button_searchdb.grid(row=1,column=2,padx=2,pady=2,sticky=tk.W+tk.E+tk.N+tk.S)

    def func_search_name(self):
        """
        入力されたポケモン名を検索し、情報を表示する
        """
        self.logger.debug("Execute func_search_name")
        text_name = self.entry_name.get()
        result_df = pkcsv._util.Name_search2csv(text_name)
        self.entry_name.delete(0,tk.END)
        if isinstance(result_df, pd.DataFrame):
            name = result_df.at[result_df.index[0],"Name"]
            index = result_df.index[0]
            type1 = result_df.at[result_df.index[0],"Type1"]
            type2 = result_df.at[result_df.index[0],"Type2"]
            self.func_update_status(index, name, type1, type2)

    def func_update_status(self, index, name, type1, type2):
        """
        番号、名前、タイプ1、タイプ2を引数として与え、UIを更新する
        """
        self.logger.debug("Execute func_update_status")
        self.label_value_name["text"] = name
        self.label_value_index["text"] = index
        self.label_value_type1["text"] = type1
        self.label_value_type2["text"] = type2

    def func_searchdb(self):
        """DBを検索"""
        self.logger.debug("Execute func_searchdb")
        name = self.label_value_name["text"]
        SearchDB().searchdb(name)

    def ocrloop_update(self):
        # self.logger.debug("Execute ocrloop_update")
        if self.ocr_runner.is_ocr_running:
            text = self.ocr_runner.text
            result_df = self.pkhash.name_search2csv(text)
            if isinstance(result_df, pd.DataFrame):
                name = result_df.at[result_df.index[0],"name"]
                index = result_df.index[0]
                type1 = result_df.at[result_df.index[0],"type1"]
                type2 = result_df.at[result_df.index[0],"type2"]
                self.func_update_status(index, name, type1, type2)
                if not name in self.master.frame2.pokemonlist:
                    self.func_addlist()

        self.after(1000, self.ocrloop_update)


# OCRを利用して、現在の相手のポケモンを表示する(開発中)
class PkInfo2(tk.Frame):
    def __init__(self, master:tk, camera_capture:CameraCapture, **kwargs):
        super().__init__(master, **kwargs)
        self.logger = getLogger("Log").getChild("PKInfo2")
        self.logger.info("Called PkInfo2")
        
        self.camera_capture = camera_capture
        
        # OCR制御
        self.ocr_control = {
            "level":OcrControl(OcrRunner(self.camera_capture, "level")),
            "namebox":OcrControl(OcrRunner(self.camera_capture, "namebox"))
        }
        
        self.font = ("MS ゴシック", 15)
        
        # ウェジット定義
        
        self.label_name = tk.Label(self, text = "名前", font=self.font, padx=2, pady=2)  # ポケモン名のラベル列
        self.label_index = tk.Label(self, text="図鑑No",font=self.font, padx=2, pady=2)
        self.label_type1 = tk.Label(self, text="タイプ1", font=self.font, padx=2, pady=2)
        self.label_type2 = tk.Label(self, text="タイプ2", font=self.font, padx=2, pady=2)

        self.label_value_name = tk.Label(self, width=40, font=self.font, padx=2, pady=2)
        self.label_value_index = tk.Label(self,font=self.font, padx=2, pady=2)
        self.label_value_type1 = tk.Label(self,font=self.font, padx=2, pady=2)
        self.label_value_type2 = tk.Label(self,font=self.font, padx=2, pady=2)

        self.button_searchdb = tk.Button(self, text="使用率ランキングを検索",command=self.func_searchdb)

        # ウェジット配置
        self.label_name.grid(row=1,column=0,sticky=tk.W+tk.E)
        self.label_index.grid(row=2,column=0,sticky=tk.W+tk.E)
        self.label_type1.grid(row=3,column=0,sticky=tk.W+tk.E)
        self.label_type2.grid(row=4,column=0,sticky=tk.W+tk.E)
        
        self.label_value_name.grid(row=1,column=1,sticky="EW")
        self.label_value_index.grid(row=2,column=1,sticky="EW")
        self.label_value_type1.grid(row=3,column=1,sticky="EW")
        self.label_value_type2.grid(row=4,column=1,sticky="EW")

        self.button_searchdb.grid(row=4,column=2,padx=2,pady=2,sticky=tk.W+tk.E+tk.N+tk.S)
        
        self.func_check_leveltext()

    def func_check_leveltext(self):
        self.logger.debug("Run check_leveltext()")
        if self.camera_capture.is_capturing: # カメラが有効の場合
            self.logger.debug("Camera is True")
            if not self.ocr_control["level"].activemode: #OCRが無効の場合
                self.logger.debug("OCRを起動")
                self.ocr_control["level"].start_ocr_thread() # OCRを起動
            
            level_text = self.ocr_control["level"].get_ocrtext()
            self.logger.debug("Got ocr-text")
            
            # 文字認識制度が甘い
            if level_text is not None and "Lv" in level_text:
                self.logger.info("Detected Namebox")
                if not self.ocr_control["namebox"].activemode:
                    self.ocr_control["namebox"].start_ocr_thread() # OCRを起動
                name_text = self.ocr_control["namebox"].get_ocrtext()
                self.label_value_name["text"] = f"{level_text} |  {name_text}"
            else:
                if self.ocr_control["namebox"].activemode: # OCRが有効の場合
                    self.logger.debug("OCRを停止")
                    self.ocr_control["namebox"].stop_ocr_thread()
            
        else: # カメラが無効の場合
            if self.ocr_control["level"].activemode: # OCRが有効の場合
                self.logger.debug("OCRを停止")
                self.ocr_control["level"].stop_ocr_thread()
            if self.ocr_control["namebox"].activemode: # OCRが有効の場合
                self.logger.debug("OCRを停止")
                self.ocr_control["namebox"].stop_ocr_thread()
        
        self.after(2000, self.func_check_leveltext)
        
    # UI表記の更新
    def func_update_status(self, index, name, type1, type2):
        """
        番号、名前、タイプ1、タイプ2を引数として与え、UIを更新する
        """
        self.logger.debug("Execute func_update_status")
        self.label_value_name["text"] = name
        self.label_value_index["text"] = index
        self.label_value_type1["text"] = type1
        self.label_value_type2["text"] = type2

    def func_searchdb(self):
        """ポケモンバトルDBを検索"""
        self.logger.debug("Execute func_searchdb")
        name = self.label_value_name["text"]
        SearchDB().searchdb(name)

    def func_update_status(self, index, name, type1, type2):
        """
        番号、名前、タイプ1、タイプ2を引数として与え、UIを更新する
        """
        self.logger.debug("Execute func_update_status")
        self.label_value_name["text"] = name
        self.label_value_index["text"] = index
        self.label_value_type1["text"] = type1
        self.label_value_type2["text"] = type2

class CaptureControl(tk.Frame):
    """
    ゲームキャプチャをコントロールするパネルを作成するフレーム
    """
    def __init__(self, master:tk, camera_capture:CameraCapture, **kwargs):
        """
        Args:
            master(tk.Tk):フレームを配置する親フレーム
            camera_capture(CameraCapture):カメラキャプチャ
        """
        super().__init__(master, **kwargs)
        self.logger = getLogger("Log").getChild("CaptureControl")
        self.logger.info("Called CaptureControl")

        self.camera_control = CameraControl(camera_capture)

        self.flag_capture = False
        self.flag_orc = False

        # ウェジット作成
        self.label_title = tk.Label(self, text="画面キャプチャ操作パネル")
        self.button_cap_control = tk.Button(self, text="キャプチャー起動", font=("MS ゴシック",20), command=self.func_cap_control)
        self.button_screenshot = tk.Button(self, text="スクリーンショット", font=("MS ゴシック",20), command=self.func_screenshot)

        # ウェジット配置
        # self.label_title.grid(padx=2,pady=2,sticky=tk.W+tk.N+tk.E+tk.S)
        # self.button_cap_control.grid(padx=2,pady=2,sticky=tk.W+tk.N+tk.E+tk.S)
        # self.button_screenshot.grid(padx=2,pady=2,sticky=tk.W+tk.N+tk.E+tk.S)
        self.label_title.pack(fill=tk.BOTH, expand=True)
        self.button_cap_control.pack(padx=5,pady=5,fill=tk.BOTH, expand=True)
        self.button_screenshot.pack(padx=5,pady=5,fill=tk.BOTH, expand=True)

    def func_cap_control(self):
        self.logger.debug("Execute func_cap_control")
        if self.flag_capture:
            self.flag_capture = False
            self.button_cap_control.config(text="キャプチャー起動")
            self.camera_control.stop_capture()
            self.logger.debug("Stopped capture")
        else:
            self.flag_capture = True
            self.button_cap_control.config(text="キャプチャー停止")
            self.camera_control.start_capture()
            self.logger.debug("Started capture")

    def func_screenshot(self):
        self.logger.debug("Execute func_screenshot")
        self.camera_control.save_frame()

class CanvasGame(tk.Frame):
    """
    キャプチャ画面を写すフレーム
    """
    def __init__(self, master:tk, camera_capture:CameraCapture, **kwargs):
        super().__init__(master, **kwargs)
        self.logger = getLogger("Log").getChild("CanvasGame")
        self.logger.debug("Hello CanvasGame")

        self.root = master
        self.camera_capture = camera_capture

        self.width = int(config.get("DEFAULT","display_width"))
        self.height = int(config.get("DEFAULT","display_height"))
        self.logger.debug(f"Display_size:{self.width}x{self.height}")


        self.label_title = tk.Label(self, text="画面キャプチャ")
        self.canvas_img = tk.Canvas(self)
        self.canvas_img.configure(width = self.width, height = self.height, bg="gray")

        self.label_title.grid(row=0)
        self.canvas_img.grid(row=1)#, padx=5, pady=5)

        # キャンバスサイズの初期化
        self.canvas_img.update()
        self.canvas_width = self.canvas_img.winfo_width()
        self.canvas_height = self.canvas_img.winfo_height()

        self.loop_update()

    def loop_update(self):
        """
        画面更新のループ処理
        """
        # self.logger.debug("Execute update")
        #print("updateを実行")
        if self.camera_capture.is_capturing:
            frame = self.camera_capture.get_frame()

            if frame is not None:
                # self.logger.debug("Frame is not None")
                # self.ocr_frame.frame = frame

                frame = cv2.resize(frame, (self.width, self.height))

                self.photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
                self.canvas_img.delete()
                self.canvas_img.create_image(0, 0, anchor=tk.NW, image=self.photo)
            else:
                self.logger.debug("Frame is None")
                self.canvas_img.delete()

        self.after(10, self.loop_update)

class CanvasPkBox(tk.Frame):
    """
    対戦開始時の相手の手持ちリストを撮影、表示するフレーム
    """
    def __init__(self, master:tk, camera_capture:CameraCapture, **kwargs):
        super().__init__(master, **kwargs)
        self.logger = getLogger("Log").getChild("CanvasPkBox")
        self.logger.debug("Hello CanvasPkBox")

        self.camera_capture = camera_capture

        self.ocr_control = OcrControl(OcrRunner(self.camera_capture, "rankbattle"))
        
        self.pkhash = PkHash()
        self.imgf = CameraFrameForge(camera_capture,"pokemonbox")

        self.screenshot_folder_path = config.get("DEFAULT","screenshot_folder")

        # サブフレームを6つ作成
        self.pkbox_subframe_list = []
        self.iconlist = [] # 定型アイコン
        self.keylist = []
        self.dislist = []
        self.cutframelist = []
        self.outline_iconlist = [] # 輪郭切り抜きアイコン
        self.box_frame = None
        self.crop_frame = None
        self.cash_frame = None
        
        # ウェジット作成
        self.canvas_frame = tk.Frame(self, width=250)
        self.button_save_pkbox = tk.Button(self, text="更新", command=self.func_reload_pkbox)

        # サブウェジット作成
        for i in range(0,6):
            pksub = SubFrame_PkBox(self.canvas_frame)
            pksub.pack(anchor=tk.NW)
            self.pkbox_subframe_list.append(pksub)
        # print(self.pkbox_subframe_list)

        # ウェジット配置
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        self.button_save_pkbox.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        self.update_pkbox()

    def update_pkbox(self):
            """
            カメラ映像からポケモンリストの画像の取得
            CanvasPkBox.updateを実行
            """
            # FIXME:テキスト取得から画像の取得まで時間がかかることで、画面変化のタイミングでリストが更新される場合がある
            self.logger.debug("Execute update_pkbox")
            # print("CanvasPkBox.updateを実行")
            if self.camera_capture.is_capturing: # カメラが有効だった場合
                if not self.ocr_control.activemode: # OCRが無効化されていたら有効化する
                    self.ocr_control.start_ocr_thread()
                
                # 選出時の画面テキストを取得
                text = self.ocr_control.get_ocrtext()
                
                # 文字列の類似度計算
                if text is not None:
                    # TODO:カジュアルバトルにも対応させる
                    similar_val = Levenshtein.distance(text, "ランクバトル")
                    self.logger.debug(f"OCR read {text}({similar_val})")
                else:
                    similar_val = 99
                
                if similar_val < 3:
                    camera_frame = self.camera_capture.get_frame()
                    if camera_frame is not None:
                        crop_frame = self.imgf.crop_frame(camera_frame)
                        
                        self.func_save_pkbox(crop_frame)
            
            else: # カメラが無効化されていた場合の処理
                if self.ocr_control.activemode: # OCRが有効化されていたら無効化する
                    self.ocr_control.stop_ocr_thread()
            self.after(2000, self.update_pkbox)

    def func_save_pkbox(self, crop_frame):
        """
        画面内の手持ちリストを撮影し、キャンパスに描画する
        """
        self.logger.debug("Execute func_save_pkbox")
        # フレームを取得
        self.crop_frame = crop_frame

        # キャッシュフレームが無い or 画像の類似度が低い場合の処理
        if self.cash_frame is not None: # キャッシュフレーム(直前のフレーム)がある場合に、類似度を調べる
            
            # 画素値比較
            # 参考：https://qiita.com/jun_higuche/items/752ef756a182261fcc55
            similar_val = np.count_nonzero(self.cash_frame == self.crop_frame) / self.crop_frame.size
            self.logger.info(f"Similar vallue : {similar_val}")
            
        
        if self.cash_frame is None or (similar_val <= 0.6): # キャッシュフレームが無いor画像が類似していない場合、表示を更新する
            self.logger.debug("Cash_frame is None" if self.cash_frame is None else "Team image is not similar")

            date = datetime.datetime.now().strftime("%y%m%d%H%M%S")
            folder_path = f"{PATH}/{self.screenshot_folder_path}/frame/"
            filename = f"screenshot_{date}.png"
            # filename2 = f"{PATH}/{self.screenshot_folder_path}/frame/dhash_{date}.json"
            try:
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                    self.logger.info(f"Success makedir {folder_path}")
            except:
                self.logger.error(f"Fault makedir {folder_path}")
            cv2.imwrite(f"{folder_path}{filename}",self.crop_frame)
            # self.save_dhash(filename2, self.crop_frame)
            self.cash_frame = self.crop_frame # キャッシュのコピー

            # フレーム内のポケモンの認識結果のキーと、類似度のリストを取得
            try:
                self.keylist, self.dislist, self.cutframelist, self.outline_iconlist = self.pkhash.RecognitionPokemonImages(self.crop_frame)
            except:
                self.logger.error("Fault to run RecognitionPokemonImages")
                return

            # アイコン画像の保存
            for i in range(0,6):
                if not os.path.exists(f"{PATH}/{self.screenshot_folder_path}/icon/outline"):
                    os.mkdir(f"{PATH}/{self.screenshot_folder_path}/icon/outline")
                if not os.path.exists(f"{PATH}/{self.screenshot_folder_path}/icon/outline"):
                    os.mkdir(f"{PATH}/{self.screenshot_folder_path}/icon/binary")
                
                cv2.imwrite(f"{PATH}/{self.screenshot_folder_path}/icon/outline/{date}_{i}.png",self.outline_iconlist[i])
                gray = cv2.cvtColor(self.outline_iconlist[i], cv2.COLOR_BGR2GRAY)
                _, binary_img = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
                cv2.imwrite(f"{PATH}/{self.screenshot_folder_path}/icon/binary/{date}_{i}.png",binary_img)
                self.logger.debug(f"Write {PATH}/icon/outline/{date}_{i}.png")

            # 表示の更新
            self.func_reload_pkbox()

    def func_reload_pkbox(self):
        """
        フレームの再読み込み
        """
        self.logger.debug("Execute func_reload_pkbox")

        self.keylist, self.dislist, self.cutframelist, self.outline_iconlist = self.pkhash.RecognitionPokemonImages(self.crop_frame)

        for i in range(0,6):
            pokemon_series = pkcsv.get_series(self.keylist[i])
            self.pkbox_subframe_list[i].key = self.keylist[i]
            self.pkbox_subframe_list[i].pokemon_name = pokemon_series["Name"]
            self.pkbox_subframe_list[i].cut_frame = self.cutframelist[i]
            self.pkbox_subframe_list[i].outline_iconframe  = self.outline_iconlist[i]
            self.pkbox_subframe_list[i].pokemon_form = pokemon_series["Form"]
            self.pkbox_subframe_list[i].search_distance = self.dislist[i]
            self.pkbox_subframe_list[i].update_subpkbox()

class SubFrame_PkBox(tk.Frame):
    """
    ポケモンの画像と名前をセットにしたサブフレーム
    """
    # TODO: ポケモンの画像から、データベースの検索やポケ徹の検索ができるようにする
    # TODO: タイプを確認できるようにする
    # TODO: 名前などを表示していない状態でも、空間サイズを固定
    def __init__(self, master:tk, **kwargs):
        super().__init__(master, **kwargs)
        self.logger = getLogger("Log").getChild("SubFrame_PkBox")
        self.logger.debug("Hello SubFrame_PkBox")

        # print("create_SubFrame_PkBox")

        self.root = master

        self.key = None # ポケモンの識別ID
        self.pokemon_name = "" # ポケモン名
        self.pokemon_form = "" # ポケモンのフォルム

        self.cut_frame = cv2.imread(f"{PATH}/monsterball.png") # 切り出し画像(初期画像はモンスターボール)
        self.outline_iconframe = None # ポケモンの輪郭切り取り画像
        
        self.search_distance = 0 # 検索時の類似度
        
        self.source_image = None # キャンバス描画用
        self.photo_image = None # キャンバス描画用

        # 画像の明度
        self.brightness_factor = -50

        self.canvas_pokemon = tk.Canvas(self)
        self.canvas_pokemon.configure(width=106, height=101, bg="gray")
        self.canvas_pokemon.grid(row=0,column=0,rowspan=3, sticky=tk.W+tk.E)

        # 表示テキスト
        self.label_name = tk.Label(self, text="名前\t：", anchor=tk.W)
        self.label_name.grid(row=0,column=1, sticky=tk.W)
        self.label_form = tk.Label(self, text="フォルム\t：", anchor=tk.W)
        self.label_form.grid(row=1,column=1, sticky=tk.W)
        self.label_distance = tk.Label(self, text="類似度\t：", anchor=tk.W)
        self.label_distance.grid(row=2,column=1, sticky=tk.W)
        self.label_value_name = tk.Label(self, text="", width=15, anchor=tk.W)
        self.label_value_name.grid(row=0,column=2, sticky=tk.W)
        self.label_value_form = tk.Label(self, text="", width=15, anchor=tk.W)
        self.label_value_form.grid(row=1, column=2, sticky=tk.W)
        self.label_value_distance = tk.Label(self, text="", width=15, anchor=tk.W)
        self.label_value_distance.grid(row=2, column=2, sticky=tk.W)


        # 右クリックしたときのメニュー
        self.clickmenu = ClickMenu(self)
        
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Hashを追加",command=lambda:self.clickmenu.addHashData(self.cut_frame))
        self.context_menu.add_command(label="Hashを更新",command=lambda:self.clickmenu.updateHashData(self.key, self.cut_frame))
        self.context_menu.add_command(label="DBを検索", command=lambda:self.clickmenu.searchDB(self.pokemon_name))
        self.context_menu.add_command(label="詳細を表示", command=lambda:self.clickmenu.viewInfo(self.key, self.cut_frame))

        # 右クリックした時のイベント
        self.canvas_pokemon.bind("<Button-3>", self.on_canvas_right_click)
        # 左クリックしたときのイベント
        self.canvas_pokemon.bind("<Button-1>", self.on_canvas_left_click)

        self.reload_subpkbox()
    
    def on_canvas_right_click(self,event):
        """
        キャンバス上で右クリックした時のイベント
        メニューを表示
        """
        self.logger.debug("Execute on_canvas_right_click")
        self.context_menu.post(event.x_root, event.y_root)

    def on_canvas_left_click(self, event):
        """
        キャンバス上で左クリックした時のイベント
        """
        self.logger.debug("Execute on_canvas_left_click")
     
        if self.cut_frame is not None and self.cut_frame.size > 0:
            if self.brightness_factor == 0:
                self.brightness_factor = -50
            else:
                self.brightness_factor = 0
            self.reload_subpkbox()
    
    def reload_subpkbox(self):
        self.logger.debug("Execute reload_subpkbox")

        # ソース画像を取得する部分
        self.source_image = cv2.cvtColor(cv2.convertScaleAbs(self.cut_frame, beta=self.brightness_factor), cv2.COLOR_BGR2RGB)

        # ImageTk.PhotoImageを作成する部分
        self.photo_image = ImageTk.PhotoImage(image=Image.fromarray(self.source_image))

        # canvasにイメージを作成する部分
        self.canvas_pokemon.create_image(0, 0, anchor=tk.NW, image=self.photo_image)

    def update_subpkbox(self):
        self.logger.debug("Execute update_subpkbox")
        self.reload_subpkbox()

        if self.search_distance > 8:
           self.label_value_name["text"]=f"({self.pokemon_name})"
        else: 
            self.label_value_name["text"]=self.pokemon_name
            # 画像保存
            cv2.imwrite(f"{PATH}/icon/box/{self.key}.png",self.cut_frame)
            self.logger.debug(f"Write {PATH}/icon/box/{self.key}.png")
        if pd.isna(self.pokemon_form):
            self.label_value_form["text"]=""
        else:
            self.label_value_form["text"]=self.pokemon_form
        self.label_value_distance["text"]=self.search_distance

class ClickMenu:
    # TODO: ウィンドウを開く位置をメインウィンドウに合わせる
    def __init__(self, master:tk):
        self.root = master

        self.logger = getLogger("Log").getChild("ClickMenu")
        self.logger.debug("Hello ClickMenu")

        self.sub_window = None
        self.pkhash = PkHash()
        self.pokemon_df = pkcsv.get_df()

        self.image_frame = None
        self.image_photo = None

        self.searchdb = SearchDB()
        
    def addHashData(self, cut_frame):
        """
        csvの追加処理
        """
        self.logger.debug("Execute addHashData")
        self.cut_frame = cut_frame
        self.outline_frame = self.pkhash.GetImageByAllContours(self.cut_frame)

        # Dhash値の算出
        self.dhash = self.pkhash.CalcPerceptualDhash(self.outline_frame)
        
        width = 400
        height = 200

        self.sub_window = tk.Toplevel(self.root)
        self.sub_window.title("dHash情報の追加")
        self.sub_window.geometry(f"{width}x{height}")

        # メインフレーム
        self.frame = tk.Frame(self.sub_window)
        self.frame.pack(fill=tk.BOTH, padx=5,pady=5)

        # ウェジット
        self.label_key = tk.Label(self.frame, text="識別番号", anchor=tk.W)
        self.entry_key = tk.Entry(self.frame, width=20)

        self.label_name = tk.Label(self.frame, text="ポケモン名", anchor=tk.W)
        self.entry_name = tk.Entry(self.frame, width=20)

        self.label_form = tk.Label(self.frame, text="フォルム", anchor=tk.W)
        self.entry_form = tk.Entry(self.frame, width=20)

        self.label_dhash = tk.Label(self.frame, text="dHash値", anchor=tk.W)
        self.label_dhash_value = tk.Label(self.frame, text=self.dhash,width=20, anchor=tk.W)

        self.canvas_icon = tk.Canvas(self.frame)
        self.canvas_icon.configure(width=106, height=101, bg="gray")
        self.image_photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(self.cut_frame, cv2.COLOR_BGR2RGB)))
        self.canvas_icon.create_image(0, 0, anchor=tk.NW, image=self.image_photo)

        def update_csv():
            """
            csvの追加
            """
            self.logger.debug("Execute update_csv")
            key = self.entry_key.get()
            # name = self.entry_name.get()
            # form = self.entry_form.get()
            # print(self.dic[index])

            self.pokemon_df.loc[key,"Hash"] = self.dhash
            pkcsv.write_csv(self.pokemon_df)
            self.logger.debug(f"dHash has Addedd {self.pokemon_df.loc[key]['Name']}")

            self.logger.debug("Destroy sub_window")
            self.sub_window.destroy()
        
        def search_key():
            try:
                key = self.entry_key.get()
                result_df = self.pokemon_df.loc[str(key)]
                self.entry_name.delete(0,tk.END)
                self.entry_name.insert(0,result_df["Name"])
                self.entry_form.delete(0,tk.END)
                if result_df["Form"] != None:
                    self.entry_form.insert(0,result_df["Form"])
            except:
                self.logger.error("Fault to search unique-num")


        self.button_search = tk.Button(self.frame, text="検索", command=search_key)
        self.button_enter = tk.Button(self.frame, text="登録", width=20, command=update_csv)

        self.canvas_icon.grid(row=0,column=0,rowspan=4,sticky=tk.W)
        self.label_key.grid(row=0, column=1,sticky=tk.W)
        self.entry_key.grid(row=0, column=2, sticky=tk.W)
        self.label_name.grid(row=1, column=1,sticky=tk.W)
        self.entry_name.grid(row=1, column=2, sticky=tk.W)
        self.label_form.grid(row=2, column=1,sticky=tk.W)
        self.entry_form.grid(row=2, column=2, sticky=tk.W)
        self.label_dhash.grid(row=3, column=1,sticky=tk.W)
        self.label_dhash_value.grid(row=3, column=2, sticky=tk.W)
        self.button_search.grid(row=0, column=3)
        self.button_enter.grid(row=5, column=1, columnspan=2)

    def updateHashData(self, key, cut_frame):
        """
        csvの個別更新
        """
        self.logger.debug("Execute updateHashData")
        self.cut_frame = cut_frame
        self.outline_frame = self.pkhash.GetImageByAllContours(self.cut_frame)

        # Dhash値の算出
        self.dhash = self.pkhash.CalcPerceptualDhash(self.outline_frame)

        self.logger.debug(f"Update key:{key}")

        self.pokemon_df.loc[key,"Hash"] = self.dhash
        pkcsv.write_csv(self.pokemon_df)
        self.logger.debug(f"dHash has Update {self.pokemon_df.at[key,'Name']}")

    def searchDB(self, pokemon_name):
        """
        ポケモンバトルデータベースの検索
        """
        self.logger.debug("Execute searchDB")
        self.searchdb.searchdb(pokemon_name)
    
    def viewInfo(self, key, cut_frame):
        """
        ポケモン情報の表示
        """
        
        # ポケモン情報を表示するウィンドウ
        self.logger.debug("Execute view_pkinfo")

        self.cut_frame = cut_frame
        pktype = PkTypeCompatibility()
        self.sub_window = tk.Toplevel(self.root)
        self.sub_window.title("ポケモン情報")

        pokemon_series = pkcsv.get_series(key)

        # メインフレーム
        self.frame = tk.Frame(self.sub_window)
        self.frame.pack(fill=tk.BOTH, pady=10)

        # 基本情報フレーム
        self.frame_baseinfo = tk.Frame(self.frame, bd=2, relief=tk.SOLID)

        self.canvas_pokemon = tk.Canvas(self.frame_baseinfo, bd=2, relief=tk.SOLID)
        self.canvas_pokemon.configure(width=106, height=101, bg="gray")
        # BGR->RGB変換
        self.image_rgb = cv2.cvtColor(self.cut_frame, cv2.COLOR_BGR2RGB)
        # RGB->PILフォーマット
        self.image_pil = Image.fromarray(self.image_rgb)
        # PIL->ImageTkフォーマット
        self.image_tk = ImageTk.PhotoImage(image=self.image_pil)
        # canvasにイメージを作成する部分
        self.canvas_pokemon.create_image(0, 0, anchor=tk.NW, image=self.image_tk)
        self.canvas_pokemon.update_idletasks()
        # time.sleep(0.1)

        self.label_name = tk.Label(self.frame_baseinfo, text="名前")
        self.label_index = tk.Label(self.frame_baseinfo, text="図鑑No")
        self.label_type = tk.Label(self.frame_baseinfo, text="タイプ")

        self.label_name_value = tk.Label(self.frame_baseinfo, text=pokemon_series["Name"])
        if pokemon_series["Form"]==None:
            self.label_form_value = tk.Label(self.frame_baseinfo, text="")
        else:
            self.label_form_value = tk.Label(self.frame_baseinfo, text=pokemon_series["Form"])
        self.label_index_value = tk.Label(self.frame_baseinfo, text=pokemon_series["Index"])
        self.label_type1_value = tk.Label(self.frame_baseinfo, text=pokemon_series["Type1"])
        self.label_type2_value = tk.Label(self.frame_baseinfo, text=pokemon_series["Type2"])

        self.canvas_pokemon.grid(
            row=0, column=0, rowspan=4, sticky=tk.W)
        self.label_index.grid(
            row=0,column=1, sticky=tk.W)
        self.label_index_value.grid(
            row=0,column=2,sticky=tk.W)
        self.label_name.grid(
            row=1,column=1,sticky=tk.W)
        self.label_name_value.grid(
            row=1,column=2,columnspan=2,sticky=tk.W)
        self.label_form_value.grid(
            row=2,column=2,columnspan=2,sticky=tk.W)
        self.label_type.grid(
            row=3,column=1,sticky=tk.W)
        self.label_type1_value.grid(
            row=3,column=2,sticky=tk.W)
        self.label_type2_value.grid(
            row=3,column=3,sticky=tk.W)

        # 種族値フレーム
        self.frame_basestatus = tk.Frame(self.frame, bd=2, relief=tk.SOLID)
        self.label_basestatus = tk.Label(self.frame_basestatus, text="種族値")

        self.label_HP = tk.Label(self.frame_basestatus, text="HP")
        self.label_Atk = tk.Label(self.frame_basestatus, text="こうげき")
        self.label_Def = tk.Label(self.frame_basestatus, text="ぼうぎょ")
        self.label_SpA = tk.Label(self.frame_basestatus, text="とくこう")
        self.label_SpD = tk.Label(self.frame_basestatus, text="とくぼう")
        self.label_Spe = tk.Label(self.frame_basestatus, text="すばやさ")
        self.label_Tot = tk.Label(self.frame_basestatus, text="合計")

        self.label_HP_value = tk.Label(self.frame_basestatus, text=pokemon_series["HP"])
        self.label_Atk_value = tk.Label(self.frame_basestatus, text=pokemon_series["Atk"])
        self.label_Def_value = tk.Label(self.frame_basestatus, text=pokemon_series["Def"])
        self.label_SpA_value = tk.Label(self.frame_basestatus, text=pokemon_series["SpA"])
        self.label_SpD_value = tk.Label(self.frame_basestatus, text=pokemon_series["SpD"])
        self.label_Spe_value = tk.Label(self.frame_basestatus, text=pokemon_series["Spe"])
        self.label_Tot_value = tk.Label(self.frame_basestatus, text=pokemon_series["Tot"])

        # 種族値
        self.label_basestatus.grid(
            row=0,column=0,columnspan=2)
        self.label_HP.grid(
            row=1,column=0,sticky=tk.W
        )
        self.label_Atk.grid(
            row=2,column=0,sticky=tk.W
        )
        self.label_Def.grid(
            row=3,column=0,sticky=tk.W
        )
        self.label_SpA.grid(
            row=4,column=0,sticky=tk.W
        )
        self.label_SpD.grid(
            row=5,column=0,sticky=tk.W
        )
        self.label_Spe.grid(
            row=6,column=0,sticky=tk.W
        )
        self.label_Tot.grid(
            row=7,column=0,sticky=tk.W
        )
        self.label_HP_value.grid(
            row=1,column=1,sticky=tk.W
        )
        self.label_Atk_value.grid(
            row=2,column=1,sticky=tk.W
        )
        self.label_Def_value.grid(
            row=3,column=1,sticky=tk.W
        )
        self.label_SpA_value.grid(
            row=4,column=1,sticky=tk.W
        )
        self.label_SpD_value.grid(
            row=5,column=1,sticky=tk.W
        )
        self.label_Spe_value.grid(
            row=6,column=1,sticky=tk.W
        )
        self.label_Tot_value.grid(
            row=7,column=1,sticky=tk.W
        )

        fig = plt.Figure(figsize=(5,3), dpi=50)
        ax = fig.add_subplot(1,1,1)
        pokemon_series["HP":"Spe"].rename({
            "Atk":"こうげき",
            "Def":"ぼうぎょ",
            "SpA":"とくこう",
            "SpD":"とくぼう",
            "Spe":"すばやさ"
        }).plot(kind="barh",ax=ax, color='skyblue')
        xlist = ["HP","Atk","Def","SpA","SpD","Spe"]
        ax.invert_yaxis() # y軸の反転
        plt.tight_layout() # レイアウトの自動調整
        # 値ラベルを付ける
        for i, col in enumerate(xlist):
            value = pokemon_series[col]
            ax.text(10, i, str(value), ha='left', va='center')
        #ax.set_yticks(range(len(xlist)))  # y軸の位置
        self.canvas_status = FigureCanvasTkAgg(fig, master=self.frame)
        self.canvas_status.draw()

        # 弱点タイプフレーム
        self.frame_baseweaktype = tk.Frame(self.frame, bd=2, relief=tk.SOLID)
        self.label_weaktype = tk.Label(self.frame_baseweaktype, text="弱点").grid(row=0,column=0)

        self.frame_weaktype_effective = tk.Frame(self.frame_baseweaktype)
        self.frame_weaktype_noteffective = tk.Frame(self.frame_baseweaktype)

        self.frame_weaktype_effective.grid(row=1,column=0)
        self.frame_weaktype_noteffective.grid(row=2,column=0)

        weaktype_effective_list = []
        weaktype_noteffective_list = []

        weaktype_df = pktype.effectivetype(pokemon_series["Type1"],pokemon_series["Type2"]).sort_values(ascending=False)
        for index, row in weaktype_df.items():
            if row>=2: #こうかはばつぐん
                weaktype_effective_list.append(tk.Label(self.frame_weaktype_effective, text=f"{index}\tx{row}").pack())
            if row<1: #こうかはいまひとつ
                weaktype_noteffective_list.append(tk.Label(self.frame_weaktype_noteffective, text=f"{index}\tx{row}").pack())

        # フレームの配置
        self.frame_baseinfo.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
        # self.frame_basestatus.grid(row=0, column=1, sticky=tk.W+tk.E+tk.N+tk.S)
        self.frame_baseweaktype.grid(row=0,column=1,rowspan=2,sticky=tk.W+tk.E+tk.N+tk.S)
        self.canvas_status.get_tk_widget().grid(row=1,column=0)

