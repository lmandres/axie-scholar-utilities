from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput


def create_payments_dict(csvRowsIn):
    payments = {"Scholars": []}
    for rowIndex in range(1, len(csvRowsIn), 1):
        newDict = {}
        for colIndex in range(0, len(csvRowsIn[rowIndex])-1, 1):
            newDict[csvRowsIn[0][colIndex].text] = csvRowsIn[rowIndex][colIndex].text
        payments["Scholars"].append(newDict)
    return payments


class EnterPaymentsScreen(Screen):

    keyItems = []
    csvItemRows = []
    layoutRows = None
    layoutBox = None
    saveAndExitButton = None
    scrollview = None

    def __init__(self, **kwargs):
        
        def resizeScreen(instance, width, height):
            self.scrollview.size = (width, height)

        def onAddressEnter(instance):

            checkRonin = check_ronin(instance.text)
            if checkRonin:
                instance.background_color = (1, 1, 1, 1)
                self.saveAndExitButton.disabled = False
            else:
                instance.background_color = (1, 0, 0, 1)
                self.saveAndExitButton.disabled = True

        def onAddressText(instance, value):

            checkRonin = check_ronin(value)
            if checkRonin:
                instance.background_color = (1, 1, 1, 1)
                self.saveAndExitButton.disabled = False
            else:
                self.saveAndExitButton.disabled = True

        def deleteCallback(instance):
            root = instance.parent.parent.parent.parent.parent.parent
            self.csvItemRows.pop(instance.rowIndex)
            root.runUpdate(paymentsDictIn=create_payments_dict(self.csvItemRows))
            root.closeDisplayedScreen()      

        payments = kwargs.pop("payments", [])
        super(EnterPaymentsScreen, self).__init__(**kwargs)

        self.keyItems = []
        self.csvItemRows = []

        self.keyItems.append(Label(text="Name"))
        self.keyItems.append(Label(text="AccountAddress"))
        self.keyItems.append(Label(text="ScholarPayoutAddress"))
        self.keyItems.append(Label(text="ScholarPercent"))
        self.keyItems.append(Label(text="ScholarPayout"))
        self.keyItems.append(Label(text="TrainerPayoutAddress"))
        self.keyItems.append(Label(text="TrainerPercent"))
        self.keyItems.append(Label(text="TrainerPayout"))
        self.keyItems.append(Label(text=""))

        self.csvItemRows.append(self.keyItems)

        if payments and "Scholars" in payments.keys():
            rowIndex = 0
            for paymentRow in payments["Scholars"]:

                csvItems = []

                for paymentKey in self.keyItems:

                    csvText = ""
                    try:
                        csvText = str(paymentRow[paymentKey.text])
                    except KeyError:
                        pass

                    csvItem = TextInput(
                        multiline=False,
                        text=csvText
                    )

                    if paymentKey.text in [
                        "AccountAddress",
                        "ScholarPayoutAddress"
                    ]:
                        csvItem.bind(on_text_validate=onAddressEnter)
                        csvItem.bind(text=onAddressText)

                    csvItems.append(csvItem)

                button = Button(
                    text="Delete",
                    on_press=deleteCallback
                )
                button.rowIndex = rowIndex
                csvItems.append(button)
                self.csvItemRows.append(csvItems)

        self.scrollview = ScrollView(bar_width=20)
        self.scrollview.size_hint = (1, None)
        self.scrollview.pos_hint = {"center_x": 0.5, "top": 1}
        self.scrollview.size = (Window.width, Window.height)
        self.scrollview.scroll_type = ["bars"]

        Window.bind(on_resize=resizeScreen)

        self.layoutBox = BoxLayout(orientation="vertical")
        self.layoutBox.size_hint_y = None
        self.layoutBox.height = 30 * (len(self.csvItemRows) + 3)

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
                text="Add New Row",
                on_press=self.buttonCallback
            )
        )
        self.saveAndExitButton = Button(
            text="Save and Exit",
            on_press=self.buttonCallback
        )
        self.layoutBox.add_widget(self.saveAndExitButton)
        self.layoutBox.add_widget(
            Button(
                text="Cancel",
                on_press=self.buttonCallback
            )
        )
        self.scrollview.add_widget(self.layoutBox)
        self.add_widget(self.scrollview)

    def buttonCallback(self, instance):
        root = instance.parent.parent.parent.parent
        if instance.text == "Add New Row":

            csvItems = []
            layout = BoxLayout(orientation="horizontal")

            for paymentKey in self.keyItems:
                newText = TextInput()
                csvItems.append(newText)
                layout.add_widget(newText)

            self.csvItemRows.append(csvItems)
            self.layoutRow.add_widget(layout)

            self.layoutBox.height = 30 * (len(self.csvItemRows) + 3)
            self.layoutRow.height = 30 * len(self.csvItemRows)

        elif instance.text == "Save and Exit":
            root.runUpdate(paymentsDictIn=create_payments_dict(self.csvItemRows))
            root.closeDisplayedScreen()

        elif instance.text == "Cancel":
            root.closeDisplayedScreen()