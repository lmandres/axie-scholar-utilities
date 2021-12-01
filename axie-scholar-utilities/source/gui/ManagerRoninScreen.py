from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput

from axie.utils import check_ronin


class ManagerRoninScreen(Screen):

    errorLabel = None
    roninID = ""

    def __init__(self, **kwargs):
        managerRoninID = kwargs.pop("managerRoninID", "")
        super(ManagerRoninScreen, self).__init__(**kwargs)

        layoutRow = BoxLayout(orientation="vertical")
        layout = BoxLayout(orientation="horizontal")

        layoutRow.size_hint = (1, None)
        layoutRow.size = (Window.width, 60)
        layoutRow.center = (Window.width/2, Window.height/2)

        layout.add_widget(
            Label(
                text="Manager Ronin ID"
            )
        )
        self.roninID = TextInput(
            multiline=False,
            cursor=True,
            cursor_blink=True
        )
        self.roninID.text = managerRoninID
        self.roninID.bind(on_text_validate=self.onTextEnter)
        layout.add_widget(self.roninID)
        layoutRow.add_widget(layout)

        self.errorLabel = Label(
            color=(1, 0, 0, 1),
            text=""
        )
        layoutRow.add_widget(self.errorLabel)

        self.add_widget(layoutRow)

    def onTextEnter(self, instance):
        checkRonin = check_ronin(self.roninID.text)
        root = instance.parent.parent.parent.parent
        if checkRonin:
            root.closeDisplayedScreen()
            root.runUpdate(managerRoninID=self.roninID.text)
        else:
            self.errorLabel.text = f'Ronin provided ({self.roninID.text}) looks wrong, try again.'
            self.roninID.text = ""