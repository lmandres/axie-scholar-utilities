from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput


class EnterSecretsScreen(Screen):

    keyItems = []
    csvItemRows = []
    layoutRows = None
    layoutBox = None
    scrollview = None

    def __init__(self, **kwargs):
        
        def resizeScreen(instance, width, height):
            self.scrollview.size = (width, height)

        payments = kwargs.pop("payments", [])
        secrets = kwargs.pop("secrets", [])
        super(EnterSecretsScreen, self).__init__(**kwargs)

        self.keyItems = []
        self.csvItemRows = []

        self.keyItems.append(Label(text="Name"))
        self.keyItems.append(Label(text="AccountAddress"))
        self.keyItems.append(Label(text="ScholarPrivateKey"))

        self.csvItemRows.append(self.keyItems)

        if payments and "Scholars" in payments.keys():
            for paymentRow in payments["Scholars"]:

                csvItems = []
                csvItems.append(Label(text=str(paymentRow["Name"])))
                csvItems.append(Label(text=str(paymentRow["AccountAddress"])))

                csvText = ""
                try:
                    csvText = secrets[paymentRow["AccountAddress"]]
                except KeyError:
                    pass

                csvItems.append(
                    TextInput(
                        multiline=False,
                        password=True,
                        text=str(csvText)
                    )
                )

                self.csvItemRows.append(csvItems)

        self.scrollview = ScrollView(bar_width=20)
        self.scrollview.size_hint = (1, None)
        self.scrollview.pos_hint = {"center_x": 0.5, "top": 1}
        self.scrollview.size = (Window.width, Window.height)
        self.scrollview.scroll_type = ["bars"]

        Window.bind(on_resize=resizeScreen)

        self.layoutBox = BoxLayout(orientation="vertical")
        self.layoutBox.size_hint_y = None
        self.layoutBox.height = 30 * (len(self.csvItemRows) + 2)

        self.layoutRow = BoxLayout(orientation="vertical")
        self.layoutRow.size_hint_y = None
        self.layoutRow.height = 30 * len(self.csvItemRows)

        for csvItemRow in self.csvItemRows:
            layout = BoxLayout(orientation="horizontal")
            for csvItem in csvItemRow:
                layout.add_widget(csvItem)
            self.layoutRow.add_widget(layout)
        self.layoutBox.add_widget(self.layoutRow)

        self.layoutBox.add_widget(
            Button(
                text="Save and Exit",
                on_press=self.buttonCallback
            )
        )
        self.layoutBox.add_widget(
            Button(
                text="Cancel",
                on_press=self.buttonCallback
            )
        )
        self.scrollview.add_widget(self.layoutBox)
        self.add_widget(self.scrollview)

    def buttonCallback(self, instance):
        if instance.text == "Save and Exit":
            outputDict = {}
            self.csvItemRows.pop(0)
            for csvItemRow in self.csvItemRows:
                outputDict[csvItemRow[1].text] = csvItemRow[2].text
            instance.parent.parent.parent.parent.closeDisplayedScreen()
        elif instance.text == "Cancel":
            instance.parent.parent.parent.parent.closeDisplayedScreen()