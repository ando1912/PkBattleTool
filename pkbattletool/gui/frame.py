"""
GUIウィンドウにのせるフレーム(tkinter.Frame)のクラスを集めたモジュール

PkInfo_OCR:OCRで認識したポケモン名から情報を表示する
CaptureControl:カメラのキャプチャ切り替えのコントロールパネル
CanvasGame:カメラが取得した画像を見せる
CanvasPkBox:相手の手持ち一覧を表示する
SubFrame_PkBox:相手の個別のポケモンのアイコンボックスを表示させる

ClickMenu:Canvas_PkBox上で右クリックしたときのポップアップメニュー

PokemnImageInfo:ポケモンのアイコンとタイプなどの基本情報を表示する
PokemonStatus:ポケモンの種族値を表示する
WeakType:ポケモンのタイプ相性を表示する
StatusGraph:ポケモンの種族値を棒グラフで表示する
PokemonInfoBaseFrame:ポケモンの詳細情報をまとめて表示する
"""

import os, sys

import datetime
import pandas as pd
from PIL import Image, ImageTk
import cv2
import numpy as np

import tkinter as tk
# フォント設定変更：https://office54.net/python/tkinter/python-tkinter-label

import Levenshtein

import threading

import time

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import rcParams
rcParams["font.family"] = "sans-serif"
rcParams["font.sans-serif"] = ["Meiryo"]

from logging import getLogger

from module import config, pkcsv
from mylib import CameraCapture, SearchDB, PkTypeCompatibility, PkHash, CameraFrameForge, OcrRunner

class PkInfo_OCR(tk.Frame):
    def __init__(self, master:tk.Tk, ocr_runner: OcrRunner, **kwargs):
        """OCRでポケモン名を認識して表示するフレーム

        Args:
            master[tk.Tk]: フレームを表示する親ウィンドウ
            ocr_runner[OcrRunner]:OCRを管理するクラス
        """
        super().__init__(master, **kwargs)
        self.logger = getLogger("Log").getChild("PkInfo_OCR")
        self.logger.info("Called PkInfo_OCR")

        self.root = master

        # OCR制御
        self.ocr_runner = ocr_runner

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

        self.task_id = None
        self.func_check_leveltext()

    def close(self) -> None:
        """
        終了時の処理
        """
        self.ocr_runner.stop_ocr_thread()
        self.after_cancel(self.task_id)
        self.logger.info("Close PkInfo-OCR")

    def func_check_leveltext(self) -> None:
        """
        レベル表示のテキストをOCRで検知した場合に、ポケモン名のOCRを実行する
        """
        logger = self.logger.getChild("func_check_leveltext")
        logger.debug("Run check_leveltext")
        try:
            if self.ocr_runner.is_ocr_running: # カメラが有効の場合
                logger.debug("Camera is True")

                # OCRを実行する共通のフレームリスト
                grayscale_framelist = self.ocr_runner.get_grayscale_framelist()
                level_masked_frame = self.ocr_runner.get_masked_frame(grayscale_framelist, "level")
                level_text = self.ocr_runner.get_ocr_text(level_masked_frame, "level")

                try:
                    logger.debug("Read OCR(level) : %s", level_text)
                except Exception as e:
                    logger.exception(e)

                if level_text != None:
                    if "Lv" in level_text:
                        logger.info("Detected Namebox")
                        name_masked_frame = self.ocr_runner.get_masked_frame(grayscale_framelist, "namebox")
                        name_text = self.ocr_runner.get_ocr_text(name_masked_frame, "namebox")
                        logger.debug(f"Read OCR(pokemonbame) : {name_text}")
                        if name_text is not None or name_text != "":
                            self.func_search_name(name_text)
                
                # grayscale_framelist = self.ocr_runner.get_grayscale_framelist()
                # name_masked_frame = self.ocr_runner.get_masked_frame(grayscale_framelist, "namebox")
                # name_text = self.ocr_runner.get_ocr_text(name_masked_frame, "namebox")
                # logger.debug(f"Read OCR(pokemonbame) : {name_text}")
                # if name_text is not None or name_text != "":
                #     self.func_search_name(name_text)
        except Exception as e:
            logger.error(f"Fault check leveltext : {e}")
        finally:
            self.task_id = self.after(1000, self.func_check_leveltext)

    # UI表記の更新
    def func_update_status(self, name:str, index:str, type1:str, type2:str)  -> None:
        """フレーム上の情報を更新

        Args:
            name (str): ポケモン名
            index (str): 図鑑番号
            type1 (str): タイプ１
            type2 (str): タイプ２
        """
        self.logger.getChild("func_update_status").debug("Run func_update_status")
        self.label_value_name["text"] = name
        self.label_value_index["text"] = index
        self.label_value_type1["text"] = type1
        self.label_value_type2["text"] = type2

    def func_searchdb(self)  -> None:
        """ポケモンバトルDBを検索"""
        self.logger.getChild("func_searchdb").debug("Run func_searchdb")
        name = self.label_value_name["text"]
        SearchDB().searchdb(name)

    def func_search_name(self, text:str) -> None:
        """OCRで認識したポケモン名をcsvから検索し、情報を取得する

        Args:
            text (str): OCRで読み取ったポケモン名
        """
        logger = self.logger.getChild("func_search_name")
        logger.info(f"Run func_search_name : {text}")
        result_df:pd.DataFrame = pkcsv._util.Name_search2csv(text)
        if result_df.empty:
            logger.debug("No matching name found")
            return
        logger.debug(f"Found name: {text} -> {result_df.at[result_df.index[0], 'Name']}")
        try:
            if isinstance(result_df, pd.DataFrame):
                name = result_df.at[result_df.index[0],"Name"]
                index = result_df.index[0]
                type1 = result_df.at[result_df.index[0],"Type1"]
                type2 = result_df.at[result_df.index[0],"Type2"]
                self.func_update_status(name, index, type1, type2)
        except Exception as e:
            logger.error(f"Fault search")
            logger.exception(e)

class CaptureControl(tk.Frame):
    def __init__(self, master:tk.Tk, camera_capture:CameraCapture, ocr_runner:OcrRunner, **kwargs):
        """ゲームキャプチャをコントロールするパネルを作成するフレーム

        Args:
            master (tk.Tk): フレームを配置する親フレーム
            camera_capture (CameraCapture): カメラキャプチャ
            ocr_runner (OcrRunner): OCR管理クラス
        """
        super().__init__(master, **kwargs)
        self.logger = getLogger("Log").getChild("CaptureControl")
        self.logger.info("Called CaptureControl")

        self.camera_capture = camera_capture
        self.ocr_runner = ocr_runner

        self.flag_capture = False
        self.flag_orc = False

        # ウェジット作成
        self.label_title = tk.Label(self, text="画面キャプチャ操作パネル")
        self.button_cap_control = tk.Button(self, text="キャプチャー起動", font=("MS ゴシック",20), command=self.func_cap_control)
        self.button_screenshot = tk.Button(self, text="スクリーンショット", font=("MS ゴシック",20), command=self.func_screenshot)

        # ウェジット配置
        self.label_title.pack(fill=tk.BOTH, expand=True)
        self.button_cap_control.pack(padx=5,pady=5,fill=tk.BOTH, expand=True)
        self.button_screenshot.pack(padx=5,pady=5,fill=tk.BOTH, expand=True)

    def func_cap_control(self)  -> None:
        """
        キャプチャー起動ボタンが押されたときの処理
        """
        logger = self.logger.getChild("func_cap_control")
        logger.info("Run func_cap_control")
        if self.flag_capture: # キャプチャが有効の場合
            self.flag_capture = False
            self.button_cap_control.config(text="キャプチャー起動") # テキストを変更
            self.camera_capture.stop_capture()
            self.ocr_runner.stop_ocr_thread()
            logger.info("Stopped capture")
        else: # キャプチャが無効の場合
            self.flag_capture = True
            self.button_cap_control.config(text="キャプチャー停止") # テキストを変更
            self.camera_capture.start_capture()
            self.ocr_runner.start_ocr_thread()
            logger.info("Started capture")

    def func_screenshot(self)  -> None:
        """
        スクリーンショットボタンが押された時の処理
        """
        self.logger.getChild("func_screenshot").debug("Run func_screenshot")
        self.camera_capture.save_frame()

    def close(self) -> None:
        """
        終了時の処理
        """
        self.camera_capture.stop_capture()
        self.camera_capture.release_camera()
        self.logger.info("Close CaptureControl")

class CanvasGame(tk.Frame):
    # FIXME:フレーム描画処理が時々止まる→mainloopが止まっている
    # FIXME: grayscale変換が連続して発生するタイミングで描画が遅くなる
    def __init__(self, master:tk.Tk, camera_capture:CameraCapture, **kwargs):
        """キャプチャ画面を写すフレーム

        Args:
            master (tk): 親ウィンドウ
            camera_capture (CameraCapture): カメラキャプチャー
        """
        super().__init__(master, **kwargs)
        self.logger = getLogger("Log").getChild("CanvasGame")
        self.logger.info("Called CanvasGame")

        self.root = master
        self.camera_capture = camera_capture

        self.thread_flag = False

        self.width = int(config.get("DEFAULT","display_width"))
        self.height = int(config.get("DEFAULT","display_height"))
        self.logger.debug(f"Display_size : {self.width}x{self.height}")

        self.default_image = cv2.imread(f"resources/wait_image.png")
        self.default_image = cv2.resize(self.default_image, (self.width, self.height))

        self.label_title = tk.Label(self, text="画面キャプチャ")
        self.canvas_img = tk.Canvas(self)
        self.canvas_img.configure(width = self.width, height = self.height, bg="gray")

        self.label_title.grid(row=0)
        self.canvas_img.grid(row=1)

        # キャンバスサイズの初期化
        self.canvas_img.update()
        self.canvas_width = self.canvas_img.winfo_width()
        self.canvas_height = self.canvas_img.winfo_height()

        # デフォルト画面の設定
        self.set_default()

        self.is_thread :bool = True

        self.thread = threading.Thread(target=self.func_thread, name="Thread Canvas")
        self.thread.daemon = True
        self.thread.start()

    def close(self) -> None:
        """
        終了時の処理
        """
        self.is_thread = False
        self.logger.info("Close CanvasGame")

    def func_thread(self) -> None:
        logger = self.logger.getChild("func_thread")
        logger.info("Run func_thread")
        while self.is_thread:
            if self.camera_capture.is_capturing:
                self.func_update_canvas()
            time.sleep(0.01)

    def func_update_canvas(self) -> None:
        """キャンバスを更新する
        """
        logger = self.logger.getChild("func_update_canvas")
        logger.debug("Run func_update_canvas")
        frame = self.camera_capture.get_frame()

        try:
            frame = cv2.resize(frame, (self.width, self.height))

            self.photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
            self.canvas_img.create_image(0, 0, anchor=tk.NW, image=self.photo)
            self.canvas_img.image = self.photo
        except Exception as e:
            logger.error("Fault create_canvas")
            logger.exception(e)

    def set_default(self)  -> None:
        """
        デフォルト画像をcanvasにセットする
        """
        self.logger.getChild("set_default").debug("Run set_default")
        frame = self.default_image
        self.photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
        self.canvas_img.delete("all")
        self.canvas_img.create_image(0, 0, anchor=tk.NW, image=self.photo)

class CanvasPkBox(tk.Frame):
    def __init__(self, master:tk.Tk, camera_capture:CameraCapture, ocr_runner:OcrRunner,**kwargs):
        """対戦開始時の相手の手持ちリストを撮影、表示するフレーム

        Args:
            master (tk.Tk): フレームを表示する親ウィンドウ
            camera_capture (CameraCapture): カメラキャプチャー
            ocr_runner (OcrRunner): OCR管理クラス
        """
        super().__init__(master, **kwargs)
        self.logger = getLogger("Log").getChild("CanvasPkBox")
        self.logger.info("Called CanvasPkBox")

        self.ocr_runner = ocr_runner

        self.pkhash = PkHash()
        self.frame_forge = CameraFrameForge(camera_capture)

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
        for _ in range(0,6):
            pksub = SubFrame_PkBox(self.canvas_frame)
            pksub.pack(anchor=tk.NW)
            self.pkbox_subframe_list.append(pksub)

        # ウェジット配置
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        self.button_save_pkbox.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        self.update_pkbox()

    def update_pkbox(self)  -> None:
        """
        カメラ映像からポケモンリストの画像の取得
        CanvasPkBox.updateを実行
        """
        # FIXME:テキスト取得から画像の取得まで時間がかかることで、画面変化のタイミングでリストが更新される場合がある
        # FIXME: 処理に時間がかかってmainloopが一瞬止まる
        logger = self.logger.getChild("update_pkbox")
        logger.debug("Run update_pkbox")
        if self.ocr_runner.is_ocr_running: # カメラが有効だった場合

            framelist = self.ocr_runner.get_framelist()
            grayscale_framelist = self.ocr_runner.get_grayscale_framelist()

            masked_frame = self.ocr_runner.get_masked_frame(grayscale_framelist, "rankbattle")
            text = self.ocr_runner.get_ocr_text(masked_frame, "rankbattle")

            # 文字列の類似度計算
            if text is not None:
                # TODO:カジュアルバトルにも対応させる
                similar_val = Levenshtein.distance(text, "ランクバトル")
                logger.debug(f"OCR read {text}({similar_val})")
            else:
                similar_val = 99

            if similar_val < 3:
                crop_frame = self.frame_forge.crop_frame(framelist[0], "pokemonbox")
                self.func_save_pkbox(crop_frame)

        self.after(5000, self.update_pkbox)

    def func_save_pkbox(self, crop_frame: np.ndarray)  -> None:
        """画面内の相手のチームリストを撮影し、キャンパスに描画する

        Args:
            crop_frame (np.ndarray): チームリストを切り抜いた画像
        """
        logger = self.logger.getChild("func_save_pkbox")
        logger.debug("Run func_save_pkbox")
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
            folder_path = f"{self.screenshot_folder_path}/battleteam"
            filename = f"battleteam_{date}.png"
            try:
                if os.path.exists(folder_path):
                    self.logger.info(f"Already {folder_path}")
                else:
                    os.makedirs(folder_path)
                    self.logger.info(f"Success makedirs {folder_path}")
                    
            except:
                self.logger.error(f"Fault makedir {folder_path}")
            cv2.imwrite(f"{folder_path}\{filename}",self.crop_frame)
            self.cash_frame = self.crop_frame # キャッシュのコピー

            # フレーム内のポケモンの認識結果のキーと、類似度のリストを取得
            # try:
            self.keylist, self.dislist, self.cutframelist, self.outline_iconlist = self.pkhash.RecognitionPokemonImages(self.crop_frame)

            # アイコン画像の保存
            for i in range(0,6):
                if not os.path.exists(f"{self.screenshot_folder_path}/icon/outline"):
                    os.makedirs(f"{self.screenshot_folder_path}/icon/outline")
                if not os.path.exists(f"{self.screenshot_folder_path}/icon/outline"):
                    os.makedirs(f"{self.screenshot_folder_path}/icon/binary")

                cv2.imwrite(f"{self.screenshot_folder_path}/icon/outline/{date}_{i}.png",self.outline_iconlist[i])
                gray = cv2.cvtColor(self.outline_iconlist[i], cv2.COLOR_BGR2GRAY)
                _, binary_img = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
                cv2.imwrite(f"{self.screenshot_folder_path}/icon/binary/{date}_{i}.png",binary_img)
                self.logger.debug(f"Write icon/outline/{date}_{i}.png")

            # 表示の更新
            self.func_reload_pkbox()

    def func_reload_pkbox(self) -> None:
        """
        フレーム内のボックスを再読み込みする
        """
        self.logger.debug("Run func_reload_pkbox")
        try:
            self.keylist, self.dislist, self.cutframelist, self.outline_iconlist = self.pkhash.RecognitionPokemonImages(self.crop_frame)
        except:
            self.logger.error("Fault RecognitionPokemonImages")
            return
        for i in range(0,6):
            pokemon_series = pkcsv.get_series(self.keylist[i])
            self.pkbox_subframe_list[i].key = self.keylist[i]
            self.pkbox_subframe_list[i].pokemon_name = pokemon_series["Name"]
            self.pkbox_subframe_list[i].cut_frame = self.cutframelist[i]
            self.pkbox_subframe_list[i].outline_iconframe  = self.outline_iconlist[i]
            self.pkbox_subframe_list[i].pokemon_form = pokemon_series["Form"]
            self.pkbox_subframe_list[i].search_distance = self.dislist[i]
            self.pkbox_subframe_list[i].update_subpkbox()

    def close(self) -> None:
        """
        終了時の処理
        """
        self.ocr_runner.stop_ocr_thread()

class SubFrame_PkBox(tk.Frame):
    # TODO: ポケモンの画像から、データベースの検索やポケ徹の検索ができるようにする
    # TODO: タイプを確認できるようにする
    # TODO: 名前などを表示していない状態でも、空間サイズを固定
    def __init__(self, master:tk.Frame, **kwargs):
        """ポケモンの画像と名前をセットにしたサブフレーム

        Args:
            master (tk.Frame): フレームを表示する親ウィンドウ
        """
        super().__init__(master, **kwargs)
        self.logger = getLogger("Log").getChild("SubFrame_PkBox")
        self.logger.info("Called SubFrame_PkBox")

        # print("create_SubFrame_PkBox")

        self.root = master

        self.key = None # ポケモンの識別ID
        self.pokemon_name = "" # ポケモン名
        self.pokemon_form = "" # ポケモンのフォルム

        self.cut_frame = cv2.imread(f"resources/monsterball.png") # 切り出し画像(初期画像はモンスターボール)
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

    def on_canvas_right_click(self, event:tk.Event) -> None:
        """
        キャンバス上で右クリックした時のイベント
        メニューを表示
        """
        self.logger.debug("Run on_canvas_right_click")
        if self.key is None:
            self.logger.info("Not Pokemon info")
            return
        else:
            self.context_menu.post(event.x_root, event.y_root)

    def on_canvas_left_click(self, event:tk.Event) -> None:
        """
        キャンバス上で左クリックした時のイベント
        """
        self.logger.debug("Run on_canvas_left_click")

        if self.cut_frame is not None and self.cut_frame.size > 0:
            if self.brightness_factor == 0:
                self.brightness_factor = -50
            else:
                self.brightness_factor = 0
            self.reload_subpkbox()

    def reload_subpkbox(self) -> None:
        """
        手持ちポケモンの一覧をリロードする
        """
        self.logger.debug("Run reload_subpkbox")

        # ソース画像を取得する部分
        self.source_image = cv2.cvtColor(cv2.convertScaleAbs(self.cut_frame, beta=self.brightness_factor), cv2.COLOR_BGR2RGB)

        # ImageTk.PhotoImageを作成する部分
        self.photo_image = ImageTk.PhotoImage(image=Image.fromarray(self.source_image))

        # canvasにイメージを作成する部分
        self.canvas_pokemon.create_image(0, 0, anchor=tk.NW, image=self.photo_image)

    def update_subpkbox(self) -> None:
        """
        手持ちポケモンの一覧を更新する
        """
        self.logger.debug("Run update_subpkbox")
        self.reload_subpkbox()

        if self.search_distance > 8:
           self.label_value_name["text"]=f"({self.pokemon_name})"
        else:
            self.label_value_name["text"]=self.pokemon_name
            # 画像保存
            cv2.imwrite(f"icon/box/{self.key}.png",self.cut_frame)
            self.logger.debug(f"Write icon/box/{self.key}.png")
        if pd.isna(self.pokemon_form):
            self.label_value_form["text"]=""
        else:
            self.label_value_form["text"]=self.pokemon_form
        self.label_value_distance["text"]=self.search_distance

class ClickMenu:
    # TODO: ウィンドウを開く位置をメインウィンドウに合わせる
    def __init__(self, master:tk.Frame):
        """チーム一覧のキャンバス上でクリックしたときの処理

        Args:
            master (tk.Frame): メニューを配置するフレーム
        """
        self.root = master

        self.logger = getLogger("Log").getChild("ClickMenu")
        self.logger.info("Called ClickMenu")

        self.sub_window = None
        self.pkhash = PkHash()
        self.pokemon_df = pkcsv.get_df()

        self.image_frame = None
        self.image_photo = None

        self.searchdb = SearchDB()

    def addHashData(self, cut_frame:np.ndarray) -> None:
        """ csvにHashを追加する

        Args:
            cut_frame (np.ndarray): アイコンの切抜き画像
        """
        self.logger.debug("Run addHashData")
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

        def update_csv() -> None:
            """
            csvの追加
            """
            self.logger.debug("Run update_csv")
            key = self.entry_key.get()
            # name = self.entry_name.get()
            # form = self.entry_form.get()
            # print(self.dic[index])

            self.pokemon_df.loc[key,"Hash"] = self.dhash
            pkcsv.write_csv(self.pokemon_df)
            self.logger.debug(f"dHash has Addedd {self.pokemon_df.loc[key]['Name']}")

            self.logger.debug("Destroy sub_window")
            self.sub_window.destroy()

        def search_key() -> None:
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

    def updateHashData(self, key:str, cut_frame:np.ndarray) -> None:
        """csvの個別更新

        Args:
            key (str): ポケモンの識別キー
            cut_frame (np.ndarray): ポケモンのアイコン
        """
        self.logger.debug("Run updateHashData")
        self.cut_frame = cut_frame
        self.outline_frame = self.pkhash.GetImageByAllContours(self.cut_frame)

        # Dhash値の算出
        self.dhash = self.pkhash.CalcPerceptualDhash(self.outline_frame)

        self.logger.debug(f"Update key:{key}")

        self.pokemon_df.loc[key,"Hash"] = self.dhash
        pkcsv.write_csv(self.pokemon_df)
        self.logger.debug(f"dHash has Update {self.pokemon_df.at[key,'Name']}")

    def searchDB(self, pokemon_name:str) -> None:
        """
        ポケモンバトルデータベースの検索
        """
        self.logger.debug("Run searchDB")
        self.searchdb.searchdb(pokemon_name)

    def viewInfo(self, key:str, cut_frame:np.ndarray) -> None:
        """ポケモン情報の表示

        Args:
            key (str): ポケモンの識別キー
            cut_frame (np.ndarray): ポケモンのアイコン画像
        """
        #FIXME: 種族値をグラフ表示にしたため、ラベル表示のソースは削除していい
        # ポケモン情報を表示するウィンドウ
        self.logger.debug("Run view_pkinfo")

        self.cut_frame = cut_frame
        
        self.sub_window = tk.Toplevel(self.root)
        self.sub_window.withdraw() # ウィンドウを非表示にする
        self.sub_window.title("基本ポケモン情報")

        # メインフレーム
        self.frame = PokemonInfoBaseFrame(self.sub_window, cut_frame, key)
        self.frame.pack(fill=tk.BOTH, pady=10)
        self.sub_window.deiconify() # ウィンドウの再表示
        
    def process_viewinfo(self, key):
        self.sub_window = tk.Toplevel(self.root)
        self.sub_window.title("基本ポケモン情報")

        # メインフレーム
        self.frame = PokemonInfoBaseFrame(self.sub_window, self.cut_frame, key)
        self.frame.pack(fill=tk.BOTH, pady=10)

class PokemnImageInfo(tk.Frame):

    def __init__(self, master:tk.Frame, frame:np.ndarray, pokemon_series:pd.Series, **kwargs):
        """ポケモンの画像と基本情報を表示するフレーム

        Args:
            master (tk.Frame): 親フレーム
            frame (np.ndarray): アイコン画像
            pokemon_series (pd.Series): ポケモンの情報を格納したSeries
        """
        super().__init__(master, **kwargs)
        self.logger = getLogger("Log").getChild("PokemonImageInfo")
        self.logger.info("Called PokemonImageInfo")

        self.frame = cv2.resize(frame, None, fx=2, fy=2) # 画像サイズを2倍にする
        self.pokemon_series = pokemon_series

        self.set_canvas()
        self.set_labelvalue()
        self.set_labelgrid()


    def set_canvas(self):
        """
        ポケモンの画像を映すキャンバスの設定
        """
        self.logger.debug("Run set_canvas")

        self.canvas_pokemon = tk.Canvas(self, bd=2, relief=tk.SOLID)
        height, width, _ = self.frame.shape[:3]
        self.canvas_pokemon.configure(
            width=width, # 106x
            height=height, # 101x
            bg="gray")
        # BGR->RGB変換
        self.image_rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        # RGB->PILフォーマット
        self.image_pil = Image.fromarray(self.image_rgb)
        # PIL->ImageTkフォーマット
        self.image_tk = ImageTk.PhotoImage(image=self.image_pil)
        # canvasにイメージを作成する部分
        self.canvas_pokemon.create_image(0, 0, anchor=tk.NW, image=self.image_tk)
        self.canvas_pokemon.update_idletasks()

    def set_labelvalue(self):
        """
        表示テキストのデータ入力1
        """
        self.logger.debug("Run set_labelvalue")

        font = tk.font.Font(family="MSゴシック", size=20, weight="bold")

        self.label_name = tk.Label(self, text="名前", font=font)
        self.label_index = tk.Label(self, text="図鑑No", font=font)
        self.label_type = tk.Label(self, text="タイプ", font=font)

        self.label_name_value = tk.Label(self, text=self.pokemon_series["Name"], font=font)
        if self.pokemon_series["Form"]==None:
            self.label_form_value = tk.Label(self, text="", font=font)
        else:
            self.label_form_value = tk.Label(self, text=self.pokemon_series["Form"], font=font)
        self.label_index_value = tk.Label(self, text=self.pokemon_series["Index"], font=font)
        self.label_type1_value = tk.Label(self, text=self.pokemon_series["Type1"], font=font)
        self.label_type2_value = tk.Label(self, text=self.pokemon_series["Type2"], font=font)

    def set_labelgrid(self):
        """
        テキスト情報の配置設定
        """
        self.logger.debug("Run set_labelgrid")

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
            row=4,column=2,sticky=tk.W)

class PokemonStatus(tk.Frame):
    def __init__(self, master:tk.Frame, pokemon_series:pd.Series, **kwargs):
        """ポケモンの種族値フレーム

        Args:
            master (_type_): オヤフレーム
            pokemon_series (_type_): ポケモンの情報を格納したSeries
        """
        super().__init__(master, **kwargs)
        self.logger = getLogger("Log").getChild("PokemonStatus")
        self.logger.info("Called PokemonStatus")

        self.pokemon_series = pokemon_series

        self.label_basestatus = tk.Label(self, text="種族値")

        self.label_HP = tk.Label(self, text="HP")
        self.label_Atk = tk.Label(self, text="こうげき")
        self.label_Def = tk.Label(self, text="ぼうぎょ")
        self.label_SpA = tk.Label(self, text="とくこう")
        self.label_SpD = tk.Label(self, text="とくぼう")
        self.label_Spe = tk.Label(self, text="すばやさ")
        self.label_Tot = tk.Label(self, text="合計")

        self.label_HP_value = tk.Label(self, text=self.pokemon_series["HP"])
        self.label_Atk_value = tk.Label(self, text=self.pokemon_series["Atk"])
        self.label_Def_value = tk.Label(self, text=self.pokemon_series["Def"])
        self.label_SpA_value = tk.Label(self, text=self.pokemon_series["SpA"])
        self.label_SpD_value = tk.Label(self, text=self.pokemon_series["SpD"])
        self.label_Spe_value = tk.Label(self, text=self.pokemon_series["Spe"])
        self.label_Tot_value = tk.Label(self, text=self.pokemon_series["Tot"])

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

class WeakType(tk.Frame):
    def __init__(self, master:tk.Frame, pokemon_series:pd.Series, **kwargs):
        """タイプ相性のフレーム

        Args:
            master (tk.Frame): 親フレーム
            pokemon_series (pd.Series): ポケモンの情報を格納したSeries
        """
        super().__init__(master, **kwargs)
        self.logger = getLogger("Log").getChild("WeakType")
        self.logger.info("Called WeakType")

        font = tk.font.Font(family="MSゴシック", size=20, weight="bold")

        self.label_weaktype = tk.Label(self, text="弱点", font=font).grid(row=0,column=0)

        self.frame_weaktype = tk.Frame(self)
        self.frame_weaktype.grid(row=1, column=0)

        weaktype_effective_list = []
        weaktype_noteffective_list = []
        weaktype_disable_list = []

        weaktype_df = PkTypeCompatibility().effectivetype(pokemon_series["Type1"],pokemon_series["Type2"]).sort_values(ascending=False)
        for index, row in weaktype_df.items():
            if row>=2: #こうかはばつぐん
                weaktype_effective_list.append([
                    tk.Label(self.frame_weaktype, text=f"{index}", anchor=tk.W, font=font),
                    tk.Label(self.frame_weaktype, text=f"x{row}", anchor=tk.W, font=font)])
            elif row==0: # こうかはない
                weaktype_disable_list.append([
                    tk.Label(self.frame_weaktype, text=f"{index}", anchor=tk.W, font=font),
                    tk.Label(self.frame_weaktype, text=f"x{row}", anchor=tk.W, font=font)
                ])
            elif row < 1: #こうかはいまひとつ
                weaktype_noteffective_list.append([
                    tk.Label(self.frame_weaktype, text=f"{index}", anchor=tk.W, font=font),
                    tk.Label(self.frame_weaktype, text=f"x{row}", anchor=tk.W, font=font)])
        
        for i in range(len(weaktype_effective_list)):
            weaktype_effective_list[i][0].grid(row=i, column=0, sticky=tk.W)
            weaktype_effective_list[i][1].grid(row=i, column=1, sticky=tk.W)
        for i in range(len(weaktype_noteffective_list)):
            weaktype_noteffective_list[i][0].grid(row=(i+len(weaktype_effective_list)), column=0, sticky=tk.W)
            weaktype_noteffective_list[i][1].grid(row=(i+len(weaktype_effective_list)), column=1, sticky=tk.W)
        for i in range(len(weaktype_disable_list)):
            weaktype_disable_list[i][0].grid(row=(i+len(weaktype_effective_list)+len(weaktype_noteffective_list)), column=0, sticky=tk.W)
            weaktype_disable_list[i][1].grid(row=(i+len(weaktype_effective_list)+len(weaktype_noteffective_list)), column=1, sticky=tk.W)

# 参考元：https://qiita.com/kotai2003/items/45953b4d037a62b2042c
class StatusGraph(tk.Frame):
    def __init__(self, master:tk.Tk, pokemon_series:pd.Series, **kwargs):
        """
        種族値をグラフ表示するフレーム_
        
        Args:
            master (tk.Tk): 親フレーム
            pokemon_series (pd.Series): ポケモンの情報を格納したSeries
        """
        super().__init__(master, **kwargs)
        self.logger = getLogger("log").getChild("StatusGraph")
        self.logger.info("Called StatusGraph")

        self.pokemon_series = pokemon_series

        fig = plt.Figure(figsize=(6,3), dpi=100)
        ax = fig.add_subplot(1,1,1)
        self.pokemon_series["HP":"Spe"].rename({
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
            value = self.pokemon_series[col]
            ax.text(10, i, str(value), ha='left', va='center')
        self.canvas_status = FigureCanvasTkAgg(fig, master=self)
        self.canvas_status.draw()

        self.canvas_status.get_tk_widget().grid(row=0,column=0)

class PokemonInfoBaseFrame(tk.Frame):
    def __init__(self, master:tk.Toplevel, frame:np.ndarray, key:str, **kwargs):
        """ポケモンの詳細情報をまとめたフレーム

        Args:
            master (tk.Toplevel): フレームを表示するサブウィンドウ
            frame (np.ndarray): ポケモンのアイコン画像
            key (str): ポケモンの識別キー
        """
        super().__init__(master, **kwargs)
        self.logger = getLogger("Log").getChild("PokemonInfoBaseFrame")
        self.logger.info("Called PokemonInfoBaseFrame")

        self.root = master
        self.root.withdraw() # ウィンドウの非表示
        self.frame = frame
        self.pokemon_series = pkcsv.get_series(key)

        # 基本情報フレーム
        self.frame_baseinfo = PokemnImageInfo(self, self.frame, self.pokemon_series, bd=2, relief=tk.SOLID)
        # 種族値フレーム
        self.frame_basestatus = PokemonStatus(self, self.pokemon_series, bd=2, relief=tk.SOLID)
        # 種族値グラフ
        self.frame_statusgraph = StatusGraph(self, self.pokemon_series, bd=2, relief=tk.SOLID)
        # 弱点タイプフレーム
        self.frame_baseweaktype = WeakType(self, self.pokemon_series,  bd=2, relief=tk.SOLID)


        # フレームの配置
        self.frame_baseinfo.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
        self.frame_baseweaktype.grid(row=0,column=1,rowspan=2,sticky=tk.W+tk.E+tk.N+tk.S)
        self.frame_statusgraph.grid(row=1, column=0)

        self.root.deiconify() # ウィンドウの再表示
