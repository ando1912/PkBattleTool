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
    def __init__(self, camera_capture, ocr_option):#width, height):
        self.tesserac_path = config.get("DEFAULT","tesseract_path")
        self.logger = getLogger("Log").getChild("OcrRunner")


        self.camera_capture = camera_capture

        self.frame = None
        self.cropped_frame = None
        self.grayscale_frame = None
        self.binaly_frame = None

        self.width = int(self.camera_capture.vid.get(cv.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.camera_capture.vid.get(cv.CAP_PROP_FRAME_HEIGHT))

        self.list_ocr_option =  {
            "message":{
                "top":int(self.height/14*10),
                "bottom":int(self.height/14*12),
                "left":int(self.width/8),
                "right":int(self.width/8*7),
                "bgr":[230,230,230],
                "thresh":200},
            "namebox":{
                "top":int(self.height/22*2),
                "bottom":int(self.height/22*3),
                "left":int(self.width/20*16),
                "right":int(self.width/20*19),
                "bgr":[230,230,230],
                "thresh":240},
            "pokemonbox":{
                "top":int(self.height*0.212),#0.212),
                "bottom":int(self.height*0.773),#0.772),
                "left":int(self.width*0.642),#0.642),
                "right":int(self.width*0.697+420),#0.697),
                "bgr":[230,230,230],
                "thresh":220}
            
        }
        self.ocr_option = self.list_ocr_option[ocr_option]

        self.text = None

        self.is_ocr_running = False

        self.ocr_name_thread = None

    def start_ocr_thread(self):
        self.logger.debug("Execute start_ocr_thread")
        self.is_ocr_running = True
        self.ocr_name_thread = threading.Thread(target=lambda:self.run_ocr_thread())
        self.ocr_name_thread.start()

    def stop_ocr_thread(self):
        self.logger.debug("Execute stop_ocr_thread")
        self.is_ocr_running = False
        if self.ocr_name_thread and self.ocr_name_thread.is_alive():
            self.ocr_name_thread.join()

    def run_ocr_thread(self):
        self.logger.debug("Execute run_ocr_thread")
        while self.is_ocr_running:
            self.get_frame()
            self.cropped_img()
            self.grayscale_img()
            self.binaly_img()
            self.run_ocr()
            self.normalize_text()

    def normalize_text(self):
        """
        記号文字などを削除する
        """
        self.logger.debug("Execute normalize_text")
        self.text = re.compile('[!"#$%&\'\\\\()*+,-./:;<=>?@[\\]^_`{|}~「」〔〕“”〈〉『』【】＆＊・（）＄＃＠。、？！｀＋￥％ 　]').sub("",self.text)

    def get_frame(self):
        """
        カメラからフレームを取得
        return:
            frame
        """
        # print("run OcrRunner.get_frame")
        # self.logger.debug("Execute get_frame")
        self.frame =  self.camera_capture.get_frame()

    def cropped_img(self):
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

        self.cropped_frame = self.frame[top:bottom,left:right]

    def grayscale_img(self):
        """
        画像のグレースケール処理
        """
        self.logger.debug("Execute grayscale_img")
        self.grayscale_frame = cv.cvtColor(self.cropped_frame, cv.COLOR_BGR2GRAY)

    def binaly_img(self):
        """
        画像の二値化処理
        """
        self.logger.debug("Execute binaly_img")
        ret, self.binaly_frame = cv.threshold(self.grayscale_frame, self.ocr_option["thresh"], 255, cv.THRESH_BINARY)


    def run_ocr(self):
        """
        ループ処理用
        cropped_imgとbinaly_imgを実行した後に処理
        """
        if self.tesserac_path not in os.environ["PATH"].split(os.pathsep):
            os.environ["PATH"] += os.pathsep + self.tesserac_path
        tools = pyocr.get_available_tools()
        tool= tools[0]

        PIL_Image = Image.fromarray(self.binaly_frame)
        self.text = tool.image_to_string(
            PIL_Image,
            lang='jpn+eng',
            builder=pyocr.builders.TextBuilder(tesseract_layout=6))
    
    def save_frame(self, frame, file_name):
        """
        Arg:
            frame:保存したいフレーム
            file_name:ファイル名、要拡張子
        """
        cv.imwrite("{}".format(file_name),frame)
        print("save as {}".format(file_name))

class OcrControl:
    """
    OcrRunnerを組み合わせて処理を行う
    """
    def __init__(self, ocr_runner):
        self.ocr_runner = ocr_runner

    def start_ocr_thread(self):
        self.ocr_runner.start_ocr_thread()

    def stop_ocr_thread(self):
        self.ocr_runner.stop_ocr_thread()
    
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
