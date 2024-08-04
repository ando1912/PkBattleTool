import tkinter as tk
import os,sys
from logging import getLogger, StreamHandler, INFO, DEBUG, Formatter, FileHandler

from mylib import OcrRunner, CameraCapture
from gui import MenuBar, PkInfo_OCR, CanvasGame, CaptureControl, CanvasPkBox

import datetime

PATH = os.path.dirname(os.path.abspath(sys.argv[0]))

def gui_main():
    # TODO: ウィンドウを開く位置を前回の位置にしたい
    root = tk.Tk()
    root.withdraw() # ウィンドウを非表示にする
    
    # アイコンの設定
    # 参考；https://qiita.com/KMiura95/items/cae599efa8a908a4bb01
    root.iconbitmap(
        default=f"{PATH}/resources/icon.ico"
    )
    
    root.resizable(0,0) # ウィンドウサイズ変更の禁止
    
    # ウィンドウタイトル
    root.title("ポケモン対戦支援ツール")

    # メニューバーの設定
    menuber = MenuBar(root)
    
    camera_capture = CameraCapture()
    ocr_runner = OcrRunner(camera_capture)

    # フレームウェジットの作成
    # ポケモン情報簡易表示
    frame_pkinfo = PkInfo_OCR(root, ocr_runner, bd=1, relief=tk.SOLID)
    frame_pkinfo.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W+tk.E)
    
    # ゲーム画面
    frame_canvasgame = CanvasGame(root, camera_capture, bd=2, relief=tk.SOLID)
    frame_canvasgame.grid(row=1, rowspan=2, column=0, columnspan=2, padx=5, pady=5)
    
    # キャプチャコントロール
    frame_capturecontrol = CaptureControl(root, camera_capture, ocr_runner, bd=1, relief=tk.SOLID)
    frame_capturecontrol.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W+tk.E+tk.N+tk.S)
    
    # 相手の手持ち一覧
    frame_canvaspkbox = CanvasPkBox(root, camera_capture, ocr_runner, bd=2, relief=tk.SOLID)
    frame_canvaspkbox.grid(row=0, column=2, rowspan=3, padx=5, pady=5, sticky=tk.W+tk.E+tk.N+tk.S)

    # ウィンドウを閉じる時の処理
    def click_close():
        frame_capturecontrol.camera_capture.stop_capture()
        frame_capturecontrol.camera_capture.release_camera()
        frame_pkinfo.ocr_runner.stop_ocr_thread()
        frame_canvaspkbox.ocr_runner.stop_ocr_thread()
        getLogger("Log").getChild("GUImain").info("Process end")
        root.quit()
        root.destroy()
        
    root.protocol("WM_DELETE_WINDOW", click_close)

    frame_pkinfo.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W+tk.E)
    
    root.deiconify() # ウィンドウを再表示する
    root.mainloop()

def main():
    # ログ設定
    logger = getLogger("Log")
    handler = StreamHandler()


    LOGGER_LEVEL = DEBUG
    HANDLER_LEVEL = DEBUG
    
    logger.setLevel(LOGGER_LEVEL)
    handler.setLevel(HANDLER_LEVEL)
    formatter = Formatter('%(asctime)s | %(levelname)s |  %(name)s:%(lineno)d | %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if not os.path.exists(f"{PATH}/log/"):
        os.mkdir(f"{PATH}/log")
    log_path = f"{PATH}/log/log_{datetime.datetime.now().strftime('%y%m%d%H%M%S')}.txt"
    fh = FileHandler(filename=log_path)
    fh.setLevel(LOGGER_LEVEL)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    logger.info("START PkBattleTool")

    gui_main()

if __name__ == "__main__":
    main()