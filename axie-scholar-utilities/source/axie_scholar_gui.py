import os

import gui.AxieGUIApp


if __name__ == '__main__':
    os.makedirs('logs', exist_ok=True)
    gui.AxieGUIApp().run()
