import cv2 as cv
import os
import pyocr
from PIL import Image
import threading
import re
from logging import getLogger

from module import config

class OcrRunner:
    """
    キャプチャ画像に対して画像処理を行う
    .frame=処理前画像
    .cropped_frame=切り出し後画像
    .binaly_frame=二値化処理後画像
    .text=OCR分析結果
    """
    def __init__(self, camera_capture, ocr_option:str):
        self.logger = getLogger("Log").getChild(f"OcrRunner:{ocr_option}")
        self.logger.info(f"Called OcrRunner:{ocr_option}")
        self.tesserac_path = config.get("DEFAULT","tesseract_path")
        self.logger = getLogger("Log").getChild("OcrRunner")


        self.option = ocr_option
        self.camera_capture = camera_capture

        # クラス内管理ではなく、return管理にしたため、削除予定
        self.frame = None
        # self.cropped_frame = None
        # self.grayscale_frame = None
        # self.binaly_frame = None
        
        self.frame_list = []

        self.width = int(self.camera_capture.vid.get(cv.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.camera_capture.vid.get(cv.CAP_PROP_FRAME_HEIGHT))

        self.list_ocr_option =  {
            # メッセージボックス
            "message":{
                "top":int(self.height/14*10),
                "bottom":int(self.height/14*12),
                "left":int(self.width/8),
                "right":int(self.width/8*7),
                "bgr":[230,230,230],
                "thresh":200},

            # 相手のレベル
            # 1920x1080での座標
            #     top:49
            #     bottom:89
            #     left:1540
            #     right:1690
            "level":{
                "top":int(self.height*0.045),
                "bottom":int(self.height*0.082),
                "left":int(self.width*0.802),
                "right":int(self.width*0.880),
                "bgr":[230,230,230],
                "thresh":30,
                "lang":"eng"},
            # ネームボックス
            # 1920x1080での座標
            #     top:98
            #     bottom:140
            #     left:1535
            #     right:1825
            "namebox":{
                "top":int(self.height*0.091),
                "bottom":int(self.height*0.130),
                "left":int(self.width*0.799),
                "right":int(self.width*0.951),
                "bgr":[230,230,230],
                "thresh":240,
                "lang":"jpn"},
            # 選出時のポケモンボックス
            # 1920x1080での座標
            #     top:223
            #     bottom:836
            #     left:1338
            #     right:1232
            "pokemonbox":{
                "top":int(self.height*0.206),
                "bottom":int(self.height*0.774),
                "left":int(self.width*0.642),
                "right":int(self.width*0.697),
                "bgr":[230,230,230],
                "thresh":220},
            # 選出時の左上のラベルテキスト
            "rankbattle":{
                "top":int(self.height*0.017),
                "bottom":int(self.height*0.058),
                "left":int(self.width*0.075),
                "right":int(self.width*0.188),
                "thresh":30,
                "lang":"jpn"}
            }

        self.ocr_option = self.list_ocr_option[ocr_option]

        self.text = None

        self.is_ocr_running = False

        self.ocr_name_thread = None

    def start_ocr_thread(self):
        self.logger.info("Execute start_ocr_thread")
        self.is_ocr_running = True
        self.ocr_name_thread = threading.Thread(target=lambda:self.run_ocr_thread())
        self.ocr_name_thread.start()

    def stop_ocr_thread(self):
        self.logger.debug("Execute stop_ocr_thread")
        self.is_ocr_running = False
        if self.ocr_name_thread and self.ocr_name_thread.is_alive():
            self.ocr_name_thread.join()

    def run_ocr_thread(self):
        # TODO:1枚ずつのOCRを、直近複数枚をあわせたOCR処理にしたい
        self.logger.info("Execute run_ocr_thread()")
        while self.is_ocr_running:
            # 画像の取得と加工
            frame = self.get_frame() # CameraCaptureからフレームの取得
            frame = self.cropped_img(frame) # フレームの切り抜き
            frame = self.grayscale_img(frame) # 切り抜いたフレームをグレースケール変換
            
            self.frame_list.append(frame)
            if len(self.frame_list) > 5: # 10枚以上になったら古いフレームから削除
                self.frame_list.pop(0)

            self.frame = self.calc_diff(self.frame_list)
            
            # self.save_frame(frame, "test.jpg")
            
            text = self.run_ocr(self.frame)
            self.text = self.normalize_text(text)
    

    def normalize_text(self, text):
        """
        記号文字などを削除する
        """
        self.logger.debug("Execute normalize_text")
        return re.compile('[!"#$%&\'\\\\()*+,-./:;<=>?@[\\]^_`{|}~「」〔〕“”〈〉『』【】＆＊・（）＄＃＠。、？！｀＋￥％ 　]').sub("",text)

    def get_frame(self):
        """
        カメラからフレームを取得
        return:
            frame
        """
        return  self.camera_capture.get_frame()

    def cropped_img(self, frame):
        """
        画像の切り出し
        Arg:
            top(int):上方向の座標
            bottom(int):下方向の座標
            left(int):左方向の座標
            right(int):右方向の座標
        Return
            frame:切り出し後のフレーム
        """
        # print("run OcrRunner.cropped_img")
        self.logger.debug("Executecropped_img")
        top = self.ocr_option["top"]
        bottom = self.ocr_option["bottom"]
        left = self.ocr_option["left"]
        right = self.ocr_option["right"]

        self.logger.debug(f"top:{top} / bottom:{bottom} / left:{left} / right:{right}")
        # print("top:{}\nbottom:{}\nleft:{}\nright:{}".format(top,bottom,left,right))

        return frame[top:bottom,left:right]

    def grayscale_img(self, frame):
        """
        画像のグレースケール処理
        """
        self.logger.debug("Execute grayscale_img")
        return cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    def binaly_img(self, frame):
        """
        画像の二値化処理
        """
        self.logger.debug("Execute binaly_img")
        return cv.threshold(frame, self.ocr_option["thresh"], 255, cv.THRESH_BINARY)

    def calc_diff(self, frame_list):
        base_img = frame_list[0]
        # self.logger.debug(base_img.__array_interface__)
        for image in frame_list[1:]:
            # 差分を計算
            diff = cv.absdiff(base_img, image)
            # 共通部分のマスクを作成
            _, mask = cv.threshold(diff, self.ocr_option["thresh"], 255, cv.THRESH_BINARY_INV)
            base_img = cv.bitwise_and(base_img, base_img, mask=mask)
        self.logger.debug("Executed calc_diff()")
        # self.logger.debug(base_img.__array_interface__)
        return base_img

    def run_ocr(self, frame):
        """
        ループ処理用
        cropped_imgとbinaly_imgを実行した後に処理
        """
        if self.tesserac_path not in os.environ["PATH"].split(os.pathsep):
            os.environ["PATH"] += os.pathsep + self.tesserac_path
        tools = pyocr.get_available_tools()
        tool= tools[0]

        # self.save_frame(frame, f"ocr_image_{self.option}.jpg")
        # _, frame = self.binaly_img(frame)
        # self.save_frame(frame, "ocr_image_binary.jpg")
        PIL_Image = Image.fromarray(frame)
        self.text = tool.image_to_string(
            PIL_Image,
            lang=self.ocr_option["lang"],
            builder=pyocr.builders.TextBuilder(tesseract_layout=6))
        
        self.logger.debug(f"OCR : '{self.text}'")
        return self.text
    
    def save_frame(self, frame=None, filename="ocr_frame.jpg"):
        """
        Arg:
            frame:保存したいフレーム
            file_name:ファイル名、要拡張子
        """
        if frame is None:
            frame = self.frame
        try:
            cv.imwrite("{}".format(filename),frame)
            self.logger.info(f"Save image to {filename}")
        except:
            self.logger.error("Can't save image")

class OcrControl:
    """
    OcrRunnerを組み合わせて処理を行う
    """
    def __init__(self, ocr_runner:OcrRunner):
        self.ocr_runner = ocr_runner
        self.activemode = False

    def start_ocr_thread(self):
        self.ocr_runner.start_ocr_thread()
        self.activemode = True

    def stop_ocr_thread(self):
        self.ocr_runner.stop_ocr_thread()
        self.activemode = False
    
    def get_cropped_frame(self):
        self.ocr_runner.get_frame()
        self.ocr_runner.cropped_img()
        return self.ocr_runner.cropped_frame

    def get_binaly_frame(self):
        self.ocr_runner.get_frame()
        self.ocr_runner.cropped_img()
        self.ocr_runner.grayscale_img()
        self.ocr_runner.binaly_img()
        return self.ocr_runner.binaly_frame

    def get_ocrtext(self):
        self.ocr_runner.save_frame(filename=f"ocr_frame_{self.ocr_runner.option}.jpg")
        return self.ocr_runner.text
