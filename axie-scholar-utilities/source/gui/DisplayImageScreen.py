import io

import win32clipboard

from kivy.uix.image import CoreImage

from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView


class DisplayImageScreen(Screen):

    closeButton = None
    copyButton = None
    scrollview = None

    def __init__(self, **kwargs):

        def closeCallbackWrapper(instance):
            closeCallback(instance.parent.parent)

        def setSize(instance, sizeIn):
            setattr(instance, "width", sizeIn[0])
            setattr(instance, "height", sizeIn[1])

        def resizeScreen(instance, width, height):
            self.scrollview.size = (width, height)
            self.copyButton.size = (width, 30)
            self.closeButton.size = (width, 30)

        def sendToClipboard(instance):

            output = io.BytesIO()
            image.convert('RGB').save(output, 'BMP')
            data = output.getvalue()[14:]
            output.close()

            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            win32clipboard.CloseClipboard()

        image = kwargs.pop("image", None)
        closeCallback = kwargs.pop("closeCallback", lambda instance: None)
        qrCodeValid = kwargs.pop("qrCodeValid", False)
        super(DisplayImageScreen, self).__init__(**kwargs)

        layout = BoxLayout(orientation="vertical")

        data = io.BytesIO()
        image.save(data, format="png")
        data.seek(0)

        imageWidget = Image()
        imageWidget.texture = CoreImage(io.BytesIO(data.read()), ext="png").texture

        self.scrollview = ScrollView(bar_width=20)
        self.scrollview.size_hint = (None, None)
        self.scrollview.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        self.scrollview.size = (Window.width, Window.height-60)
        self.scrollview.scroll_type = ["bars"]
        self.scrollview.add_widget(imageWidget)

        Window.bind(on_resize=resizeScreen)
        layout.add_widget(self.scrollview)

        self.copyButton = Button(
            text="Copy to Clipboard",
            disabled=(not qrCodeValid),
            on_press=sendToClipboard,
            size_hint=(None, None),
            size=(Window.width, 30)
        )
        layout.add_widget(self.copyButton)

        self.closeButton = Button(
            text="Close",
            disabled=False,
            on_press=closeCallbackWrapper,
            size_hint=(None, None),
            size=(Window.width, 30)
        )
        layout.add_widget(self.closeButton)
        self.add_widget(layout)
