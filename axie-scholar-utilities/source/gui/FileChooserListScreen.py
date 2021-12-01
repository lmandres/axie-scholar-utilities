import os

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.screenmanager import Screen


class FileChooserListScreen(Screen):

    fileChooser = None

    def __init__(self, **kwargs):

        def buttonCallback(instance):
            root = instance.parent.parent.parent
            if instance.text == "Open":
                print(self.fileChooser.selection)
            elif instance.text == "Cancel":
                root.closeDisplayedScreen()

        filters = kwargs.pop("filters", [])
        super(FileChooserListScreen, self).__init__()
        layoutRows = BoxLayout(orientation="vertical")

        self.fileChooser = FileChooserListView()
        self.fileChooser.path = os.getcwd()
        self.fileChooser.filters = filters
        layoutRows.add_widget(self.fileChooser)

        openButton = Button(
            text="Open",
            size_hint=(1, None),
            height=30
        )
        openButton.bind(on_press=buttonCallback)
        layoutRows.add_widget(openButton)

        cancelButton = Button(
            text="Cancel",
            size_hint=(1, None),
            height=30
        )
        cancelButton.bind(on_press=buttonCallback)
        layoutRows.add_widget(cancelButton)

        self.add_widget(layoutRows)