import cv2
import os, sys
import pyocr
from PIL import Image
import threading
import re
from logging import getLogger

from module import config
from . import imgforge
PATH = os.path.dirname(os.path.abspath(sys.argv[0]))

class OcrRunner:
    """
    キャプチャ画像に対して画像処理を行う
    .frame=処理前画像
    .cropped_frame=切り出し後画像
    .binaly_frame=二値化処理後画像
    .text=OCR分析結果
    """
    # BUG:スレッドを終了しないままウィンドウを閉じるとプロセスが終わらない
    def __init__(self, camera_capture, ocr_option:str):
        self.logger = getLogger("Log").getChild(f"OcrRunner({ocr_option})")
        self.logger.info(f"Called OcrRunner:{ocr_option}")
        self.tesserac_path = config.get("DEFAULT","tesseract_path")

        self.option = ocr_option
        self.camera_capture = camera_capture

        self.frame_forge = imgforge.CameraFrameForge(camera_capture, ocr_option)
        
        self.frame = None # 文字認識を行う画像
        self.frame_list = [] # マスク処理のための画像リスト

        self.width = int(self.camera_capture.vid.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.camera_capture.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.list_ocr_option =  {
            # メッセージボックス
            "message":{
                "thresh":200
                },
            "level":{
                "thresh":100,
                "lang":"eng"
                },
            "namebox":{
                "thresh":180,
                "lang":"jpn+eng"
                },
            # FIXME:カジュアルバトルの場合もあり、その場合、幅が異なる
            "rankbattle":{
                "thresh":200,
                "lang":"jpn"
                }
            }

        self.ocr_option = self.list_ocr_option[ocr_option]

        self.text = None

        self.is_ocr_running = False

        self.ocr_name_thread = None

    def start_ocr_thread(self):
        self.logger.getChild("start_ocr_thread").info("Execute start_ocr_thread")
        self.is_ocr_running = True
        self.ocr_name_thread = threading.Thread(target=lambda:self.run_ocr_thread())
        self.ocr_name_thread.start()

    def stop_ocr_thread(self):
        self.logger.getChild("stop_ocr_thread").info("Execute stop_ocr_thread")
        self.is_ocr_running = False
        self.frame_list = []

    def run_ocr_thread(self):
        logger = self.logger.getChild("run_ocr_thread")
        
        while self.is_ocr_running:
            logger.info("Execute run_ocr_thread")
            # 画像の取得と加工
            frame = self.get_frame() # CameraCaptureからフレームの取得
            crop_frame = self.frame_forge.crop_frame(frame) # フレームの切り抜き
            
            # グレースケール変換
            frame = self.frame_forge.grayscale_frame(crop_frame)
            # 二値化
            binary_frame = self.frame_forge.binaly_frame(frame)
            
            self.frame_list.append(binary_frame)
            if len(self.frame_list) > 5: # 5枚以上になったら古いフレームから削除
                self.frame_list.pop(0)

            # フレームの差を求める
            self.frame = self.frame_forge.diff_frames(self.frame_list)
            
            text = self.run_ocr(self.frame)
            self.text = self.normalize_text(text)
            logger.debug(f"OCR result : {self.text}")

    def normalize_text(self, text:str) -> str:
        """
        記号文字などを削除する
        """
        self.logger.getChild("normalize_text").debug("Execute normalize_text")
        return re.compile('[!"#$%&\'\\\\()*+,-./:;<=>?@[\\]^_`{|}~「」〔〕“”〈〉『』【】＆＊・（）＄＃＠。、？！｀＋￥％ 　]').sub("",text)

    def get_frame(self):
        """
        カメラからフレームを取得
        return:
            frame
        """
        return  self.camera_capture.get_frame()

    def run_ocr(self, frame) -> str:
        if self.tesserac_path not in os.environ["PATH"].split(os.pathsep):
            os.environ["PATH"] += os.pathsep + self.tesserac_path
        tools = pyocr.get_available_tools()
        tool= tools[0]

        PIL_Image = Image.fromarray(frame)
        text = tool.image_to_string(
            PIL_Image,
            lang=self.ocr_option["lang"],
            builder=pyocr.builders.TextBuilder(tesseract_layout=6))
        
        return text

class OcrControl:
    """
    OcrRunnerを組み合わせて処理を行う
    """
    def __init__(self, ocr_runner:OcrRunner):
        self.logger = getLogger("Log").getChild(f"OcrControl({ocr_runner.option})")
        self.ocr_runner = ocr_runner
        self.activemode = False

    def start_ocr_thread(self):
        self.ocr_runner.start_ocr_thread()
        self.activemode = True
        self.logger.getChild("start_ocr_thread").info("Start ocr thread")

    def stop_ocr_thread(self):
        self.ocr_runner.stop_ocr_thread()
        self.activemode = False
        self.logger.getChild("stop_ocr_thread").info("Stop ocr thread")

    def get_frame(self):
        self.logger.getChild("get_frame").info("Run get_frame")
        return self.ocr_runner.frame

    def get_ocrtext(self):
        self.logger.getChild("get_ocrtext").info("Got text")
        return self.ocr_runner.text
