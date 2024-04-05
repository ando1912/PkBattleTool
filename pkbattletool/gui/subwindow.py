import tkinter as tk
import re
import cv2
import pandas as pd
from PIL import Image, ImageTk
from logging import getLogger

from mylib import PkHash

class SubWindow(tk.Toplevel):
    def __init__(self, master):
        self.root = master
        self.logger = getLogger("Log").getChild("SubWindow")

        self.root_width = 0
        self.root_height = 0
        self.root_x = 0
        self.root_y = 0

        self.cut_frame = None
        self.image_rgb = None
        self.image_pil = None
        self.image_tk = None

    # メインウィンドウの座標計算
    def extract_coordinates(self):
        self.logger.debug("Exectute extract_coordinates")
        # 正規表現パターン
        pattern = r"(\d+)x(\d+)\+(\d+)\+(\d+)"
        match = re.search(pattern, self.root.geometry())
        if match:
            self.root_width,self.root_height,self.root_x, self.root_y = map(int, match.groups())
    
    def close(self, root):
        self.logger.debug("Execute close")
        """
        引数として与えたrootを閉じる
        """
        root.destroy()
    
    # ポケモン情報を表示するウィンドウ
    def view_pkinfo(self, key):
        self.logger.debug("Execute view_pkinfo")
        # self.extract_coordinates()
        try:
            self.cut_frame = cv2.imread(f"icon/box/{key}.png")
            #cv2.imshow("debug", self.cut_frame)
            height, width, channels = self.cut_frame.shape[:3]
            self.logger.debug(f"Load icon/box/{key}.png, Image size:{height}x{width}")
        except:
            self.cut_frame = cv2.imread("monsterball.png")
            self.logger.debug("Load monsterball.png")
        self.sub_window = tk.Toplevel(self.root)
        self.sub_window.title("ポケモン情報")

        pkhash = PkHash()
        pokemon_df = pkhash.searchkey2csv(key)
        
        width = 600
        height = 400

        self.sub_window.geometry("{}x{}+{}+{}".format(
            width,
            height,
            int(self.root_x+self.root_width/2-width/2),
            int(self.root_y+self.root_height/2-height/2)))

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

        self.label_name_value = tk.Label(self.frame_baseinfo, text=pokemon_df["Name"])
        if pd.isna(pokemon_df["Form"]):
            self.label_form_value = tk.Label(self.frame_baseinfo, text="")
        else:
            self.label_form_value = tk.Label(self.frame_baseinfo, text=pokemon_df["Form"])
        self.label_index_value = tk.Label(self.frame_baseinfo, text=pokemon_df["Index"])
        self.label_type1_value = tk.Label(self.frame_baseinfo, text=pokemon_df["Type1"])
        self.label_type2_value = tk.Label(self.frame_baseinfo, text=pokemon_df["Type2"])

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

        self.label_HP_value = tk.Label(self.frame_basestatus, text=pokemon_df["Atk"])
        self.label_Atk_value = tk.Label(self.frame_basestatus, text=pokemon_df["Atk"])
        self.label_Def_value = tk.Label(self.frame_basestatus, text=pokemon_df["Def"])
        self.label_SpA_value = tk.Label(self.frame_basestatus, text=pokemon_df["SpA"])
        self.label_SpD_value = tk.Label(self.frame_basestatus, text=pokemon_df["SpD"])
        self.label_Spe_value = tk.Label(self.frame_basestatus, text=pokemon_df["Spe"])
        self.label_Tot_value = tk.Label(self.frame_basestatus, text=pokemon_df["Tot"])

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

        # フレームの配置
        self.frame_baseinfo.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
        self.frame_basestatus.grid(row=0, column=1, sticky=tk.W+tk.E+tk.N+tk.S)




