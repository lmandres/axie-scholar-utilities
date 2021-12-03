from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput


class ManageScholarsScreen(Screen):

    keyItems = []
    csvItemRows = []
    deleteItemRows = []
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

        scholars = kwargs.pop("scholars", [])
        super(ManageScholarsScreen, self).__init__(**kwargs)

        self.keyItems = []
        self.csvItemRows = []

        keys = [
            "scholarName",
            "scholarAddress",
            "scholarPayoutAddress",
            "scholarPercent",
            "scholarPayout"
        ]
        keys.append("")

        rowIndex = len(self.csvItemRows)
        for key in keys:
            label = Label(text=key)
            label.ID = None
            label.rowIndex = rowIndex
            label.field = None
            self.keyItems.append(label)
        self.csvItemRows.append(self.keyItems)

        rowIndex = len(self.csvItemRows)
        for scholar in scholars:

            csvItems = []

            for dictKey in self.keyItems:

                csvText = ""
                try:
                    csvText = str(scholar[dictKey.text])
                except KeyError:
                    pass

                if dictKey.text == "":
                    csvItem = Button(
                        text="Delete",
                        on_press=self.deleteCallback
                    )
                    csvItem.ID = scholar["scholarID"]
                    csvItem.field = None
                    csvItem.rowIndex = rowIndex
                else:
                    csvItem = TextInput(
                        multiline=False,
                        text=csvText
                    )
                    csvItem.ID = scholar["scholarID"]
                    csvItem.rowIndex = rowIndex
                    csvItem.field = dictKey.text

                if dictKey.text in [
                    "scholarAddress",
                    "scholarPayoutAddress"
                ]:
                    csvItem.bind(on_text_validate=onAddressEnter)
                    csvItem.bind(text=onAddressText)

                csvItems.append(csvItem)

            self.csvItemRows.append(csvItems)

        self.scrollview = ScrollView(bar_width=20)
        self.scrollview.size_hint = (1, None)
        self.scrollview.pos_hint = {"center_x": 0.5, "top": 1}
        self.scrollview.size = (Window.width, Window.height-90)
        self.scrollview.scroll_type = ["bars"]

        Window.bind(on_resize=resizeScreen)

        layoutBox = BoxLayout(orientation="vertical")
        self.layoutGrid = GridLayout(
            cols=6,
            row_force_default=True,
            row_default_height=40
        )

        for csvItemRow in self.csvItemRows:
            for csvItem in csvItemRow:
                self.layoutGrid.add_widget(csvItem)

        self.scrollview.add_widget(self.layoutGrid)
        layoutBox.add_widget(self.scrollview)
        layoutBox.add_widget(
            Button(
                text="Add New Row",
                on_press=self.buttonCallback,
                size_hint=[1, None],
                height=30
            )
        )
        self.saveAndExitButton = Button(
            text="Save and Exit",
            on_press=self.buttonCallback,
            size_hint=[1, None],
            height=30
        )
        layoutBox.add_widget(self.saveAndExitButton)
        layoutBox.add_widget(
            Button(
                text="Cancel",
                on_press=self.buttonCallback,
                size_hint=[1, None],
                height=30
            )
        )
        self.add_widget(layoutBox)

    def deleteCallback(self, instance):
        root = instance.parent.parent.parent.parent.parent.parent

        self.deleteItemRows.append(self.csvItemRows.pop(instance.rowIndex))
        self.layoutGrid.clear_widgets()

        for rowIndex in range(0, len(self.csvItemRows), 1):
            for csvItem in self.csvItemRows[rowIndex]:
                csvItem.rowIndex = rowIndex
                self.layoutGrid.add_widget(csvItem)

    def buttonCallback(self, instance):
        root = instance.parent.parent.parent
        if instance.text == "Add New Row":

            csvItems = []

            rowIndex = len(self.csvItemRows)
            for keyIndex in range(0, len(self.keyItems), 1):
                if self.keyItems[keyIndex].text == "":
                    button = Button(
                        text="Delete",
                        on_press=self.deleteCallback
                    )
                    button.ID = None
                    button.field = None
                    button.rowIndex = rowIndex
                    csvItems.append(button)
                    self.layoutGrid.add_widget(button)
                else:
                    newText = TextInput()
                    newText.ID = None
                    newText.field = self.keyItems[keyIndex].text
                    newText.rowIndex = rowIndex
                    csvItems.append(newText)
                    self.layoutGrid.add_widget(newText)

            self.csvItemRows.append(csvItems)
            self.layoutGrid.height = 30 * len(self.csvItemRows)

        elif instance.text == "Save and Exit":

            queryParams = []
            for rowIndex in range(1, len(self.csvItemRows), 1):
                newDict = {}
                for csvItem in self.csvItemRows[rowIndex]:
                    newDict["scholarID"] = csvItem.ID
                    newDict[csvItem.field] = csvItem.text
                queryParams.append(newDict)
            root.dbreader.updateScholars(queryParams)

            deleteParams = []
            for rowIndex in range(1, len(self.deleteItemRows), 1):
                newDict = {}
                for csvItem in self.deleteItemRows[rowIndex]:
                    newDict["scholarID"] = csvItem.ID
                deleteParams.append(newDict)
            root.dbreader.deleteScholars(deleteParams)

            root.closeDisplayedScreen()

        elif instance.text == "Cancel":
            root.closeDisplayedScreen()