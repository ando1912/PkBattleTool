import tkinter as tk
import os,sys
from logging import getLogger, Logger, StreamHandler, INFO, DEBUG, Formatter, FileHandler

from mylib import OcrRunner, CameraCapture
from gui import MenuBar, PkInfo_OCR, CanvasGame, CaptureControl, CanvasPkBox

import datetime

PATH = os.path.dirname(os.path.abspath(sys.argv[0]))

class MainWindow(tk.Frame):
    def __init__(self, master:tk.Tk=None):
        super().__init__(master)
        
        self.logger = getLogger("Log").getChild("MainWindow")
        self.root = master
        
        self.camera_capture = CameraCapture()
        self.ocr_runner = OcrRunner(self.camera_capture)

        # フレームウェジットの作成
        # ポケモン情報簡易表示
        self.frame_pkinfo = PkInfo_OCR(self, self.ocr_runner, bd=1, relief=tk.SOLID)
        self.frame_pkinfo.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W+tk.E)
        
        # ゲーム画面
        self.frame_canvasgame = CanvasGame(self, self.camera_capture, bd=2, relief=tk.SOLID)
        self.frame_canvasgame.grid(row=1, rowspan=2, column=0, columnspan=2, padx=5, pady=5)
        
        # キャプチャコントロール
        self.frame_capturecontrol = CaptureControl(self, self.camera_capture, self.ocr_runner, bd=1, relief=tk.SOLID)
        self.frame_capturecontrol.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W+tk.E+tk.N+tk.S)
        
        # 相手の手持ち一覧
        self.frame_canvaspkbox = CanvasPkBox(self, self.camera_capture, self.ocr_runner, bd=2, relief=tk.SOLID)
        self.frame_canvaspkbox.grid(row=0, column=2, rowspan=3, padx=5, pady=5, sticky=tk.W+tk.E+tk.N+tk.S)
    
        self.grid()
        
    def close(self) -> None:
        """
        終了時の処理
        """
        self.frame_capturecontrol.close()
        self.frame_pkinfo.close()
        self.frame_canvaspkbox.close()
        self.ocr_runner.close()
        self.logger.info("Close MainWindow")

class Application(tk.Tk):
    """
    基盤となるアプリケーション
    """
    def __init__(self):
        super().__init__()
        
        self.withdraw() # ウィンドウを非表示にする
        
        # アイコンの設定
        # 参考；https://qiita.com/KMiura95/items/cae599efa8a908a4bb01
        self.iconbitmap(
            default=f"resources/icon.ico"
        )
        
        self.resizable(0,0) # ウィンドウサイズ変更の禁止
        self.title("ポケモン対戦支援ツール")
        self.mainwidget = MainWindow(self)
        
        menubar = MenuBar(self)
        
        self.protocol("WM_DELETE_WINDOW", self.click_close)
        
        self.deiconify() # ウィンドウの再表示
        
    def click_close(self):
        self.mainwidget.close()
        self.quit()
        self.destroy()

def setup_logging() -> Logger:
    # ログ設定
    logger = getLogger("Log")
    handler = StreamHandler()

    LOGGER_LEVEL = DEBUG
    HANDLER_LEVEL = DEBUG
    
    logger.setLevel(LOGGER_LEVEL)
    handler.setLevel(HANDLER_LEVEL)
    formatter = Formatter('%(asctime)s | %(process)d:%(thread)d | %(levelname)s | %(module)s:%(lineno)d |  %(name)s | %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if not os.path.exists(f"{PATH}/log/"):
        os.mkdir(f"{PATH}/log")
    log_path = f"{PATH}/log/log_{datetime.datetime.now().strftime('%y%m%d%H%M%S')}.txt"
    fh = FileHandler(filename=log_path)
    fh.setLevel(LOGGER_LEVEL)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    logger.getChild("setup_logging").info("START PkBattleTool")
    
    return logger
        

def main():
    logger = setup_logging()
    app = Application()
    app.mainloop()

if __name__ == "__main__":
    main()