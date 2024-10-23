import ctypes
import time
import mss
import mss.windows
import cv2
import numpy
import configparser
from pynput.mouse import Listener, Button
from ctypes import wintypes



user32 = ctypes.WinDLL('user32', use_last_error=True)
user32.SetProcessDPIAware()

class Capture:

    def __init__(self, window_name, save_dir='pictures/'):
        mss.windows.CAPTUREBLT = 0
        self.window_name = window_name
        self.save_dir = save_dir
        self.sct = None
        self.window = {
            'left': 0,
            'top': 0,
            'width': 1366,
            'height': 768
        }
        self.initWindow()

    def initWindow(self):
        handle = user32.FindWindowW(None, self.window_name)
        rect = wintypes.RECT()
        user32.GetWindowRect(handle, ctypes.pointer(rect))
        rect = (rect.left, rect.top, rect.right, rect.bottom)
        rect = tuple(max(0, x) for x in rect)
        self.window['left'] = rect[0]
        self.window['top'] = rect[1]
        self.window['width'] = rect[2] - rect[0]
        self.window['height'] = rect[3] - rect[1]
        print(rect)

    def grab_screen(self):
        with mss.mss() as self.sct:
            img = numpy.asarray(self.sct.grab(self.window))
            img_name = str(time.time()) + '.png'
            img_path = self.save_dir + img_name
            cv2.imwrite(img_path, img)

            #show image
            # cv2.imshow('title', img)
            # cv2.waitKey(0)

            print(f'{img_path} saved.')
        return img_path

    def record_screen(self):
        with mss.mss() as self.sct:
            fps = 0
            last_time = time.time()
            while True:
                img = numpy.asarray(self.sct.grab(self.window))
                cv2.imshow('grab', img)
                cv2.waitKey(1)
                if time.time() - last_time < 1:
                    fps += 1
                else:
                    print(fps)
                    last_time = time.time()
                    fps = 0

class InputListener:
    """监听鼠标中建,执行func方法"""

    def __init__(self, func=None):
        self.func = func

    def on_click(self, x, y, button, pressed):
        if button == Button.middle and pressed:
            print('middle clicked')
            self.func()

    def run(self):
        with Listener(on_click=self.on_click) as listener:
            listener.join()


if __name__ == '__main__':
    # capt = Capture('无标题 - Notepad')
    # capt.grab_screen()
    # capt.record_screen()

    config = configparser.ConfigParser()
    config.read('config.ini')
    print(f'window name: {config["window"]["name"]}')
    capture = Capture(window_name=config['window']['name'])
    inl = InputListener(capture.grab_screen)
    inl.run()