import os


def runApp():
    import gui.AxieGUIApp
    gui.AxieGUIApp().run()


if __name__ == '__main__':
    os.makedirs('logs', exist_ok=True)
    runApp()
