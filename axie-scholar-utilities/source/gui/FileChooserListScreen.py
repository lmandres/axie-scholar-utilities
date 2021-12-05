import os

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.screenmanager import Screen


class FileChooserListScreen(Screen):

    openButton = None
    fileChooser = None

    def __init__(self, **kwargs):

        def buttonCallback(instance):
            root = instance.parent.parent.parent
            if instance.text == "Cancel":
                root.closeDisplayedScreen()

        def chooseEntryCallback(instance, selection, touch):
            root = instance.parent.parent.parent
            if len(selection):
                chooseFileCallback(selection[0])
                root.closeDisplayedScreen()

        filters = kwargs.pop("filters", [])
        openButtonLabel = kwargs.pop("openButtonLabel", "Open")
        chooseFileCallback = kwargs.pop("chooseFileCallback", lambda data: None)
        super(FileChooserListScreen, self).__init__()
        layoutRows = BoxLayout(orientation="vertical")

        self.fileChooser = FileChooserListView()
        self.fileChooser.path = os.getcwd()
        self.fileChooser.filters = filters
        self.fileChooser.bind(on_submit=chooseEntryCallback)
        layoutRows.add_widget(self.fileChooser)

        cancelButton = Button(
            text="Cancel",
            size_hint=(1, None),
            height=30
        )
        cancelButton.bind(on_press=buttonCallback)
        layoutRows.add_widget(cancelButton)

        self.add_widget(layoutRows)