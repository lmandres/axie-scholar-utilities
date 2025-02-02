import logging

from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView

from gui.LabelLoggingHandler import LabelLoggingHandler


class DisplayLoggingScreen(Screen):

    loggingLabel = None
    closeButton = None
    runButton = None
    scrollview = None

    def __init__(self, **kwargs):

        def runCallbackWrapper(instance):
            runCallback(instance.parent.parent.parent)
            self.closeButton.disabled = False

        def closeCallbackWrapper(instance):
            closeCallback(instance.parent.parent.parent)

        def setSize(instance, sizeIn):
            setattr(instance, "width", sizeIn[0])
            setattr(instance, "height", sizeIn[1])

        def resizeScreen(instance, width, height):
            self.scrollview.size = (width, height)
            self.runButton.size = (width, 30)
            self.closeButton.size = (width, 30)

        runCallback = kwargs.pop("runCallback", lambda instance: None)
        closeCallback = kwargs.pop("closeCallback", lambda instance: None)
        super(DisplayLoggingScreen, self).__init__(**kwargs)

        layout = BoxLayout(orientation="vertical")

        self.loggingLabel = Label(
            size_hint=(None, None)
        )
        self.loggingLabel.bind(texture_size=setSize)
        log = logging.getLogger()
        log.level = logging.INFO
        log.addHandler(LabelLoggingHandler(self.loggingLabel, logging.INFO))

        self.scrollview = ScrollView(bar_width=20)
        self.scrollview.size_hint = (None, None)
        self.scrollview.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        self.scrollview.size = (Window.width, Window.height-60)
        self.scrollview.scroll_type = ["bars"]
        self.scrollview.add_widget(self.loggingLabel)

        Window.bind(on_resize=resizeScreen)
        layout.add_widget(self.scrollview)

        self.runButton = Button(
            text="Run Claim",
            on_press=runCallbackWrapper,
            size_hint=(None, None),
            size=(Window.width, 30)
        )
        layout.add_widget(self.runButton)
        self.closeButton = Button(
            text="Close",
            disabled=True,
            on_press=closeCallbackWrapper,
            size_hint=(None, None),
            size=(Window.width, 30)
        )
        layout.add_widget(self.closeButton)
        self.add_widget(layout)
