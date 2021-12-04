from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

from axie.utils import check_ronin

from gui.DropDownButton import DropDownButton


class ManageTableScreen(Screen):

    keyItems = []
    csvItemRows = []
    deleteItemRows = []

    layoutRows = None
    layoutBox = None
    saveAndExitButton = None
    scrollview = None

    addressColumns = []
    rowIDColumn = ""
    rowData = []
    updateTableCallback = lambda data: None
    deleteTableCallback = lambda data: None

    def __init__(self, **kwargs):
        
        def resizeScreen(instance, width, height):
            self.scrollview.size = (width, height)

        self.keyItems = kwargs.pop("keyItems", [])
        self.rowIDColumn = kwargs.pop("rowIDColumn", "")
        self.rowData = kwargs.pop("rowData", [])
        self.updateTableCallback = kwargs.pop("updateCallback", lambda data: None)
        self.deleteTableCallback = kwargs.pop("deleteCallback", lambda data: None)
        super(ManageTableScreen, self).__init__(**kwargs)

        self.keyItems.append(("", "deletebutton",))
        self.populateRowData(self.keyItems, self.rowData)

        self.scrollview = ScrollView(bar_width=20)
        self.scrollview.size_hint = (1, None)
        self.scrollview.pos_hint = {"center_x": 0.5, "top": 1}
        self.scrollview.size = (Window.width, Window.height-90)
        self.scrollview.scroll_type = ["bars"]

        Window.bind(on_resize=resizeScreen)

        layoutBox = BoxLayout(orientation="vertical")
        self.layoutGrid = GridLayout(
            cols=len(self.keyItems),
            row_force_default=True,
            row_default_height=30
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

    def populateRowData(self, keyItemsIn, rowDataIn):

        self.csvItemRows = []
        labels = []
        for keyItem in keyItemsIn:
            labels.append(Label(text=keyItem[0]))
        self.csvItemRows.append(labels)

        for rowItem in rowDataIn:

            csvItems = []

            for keyItem in keyItemsIn:

                csvText = ""
                try:
                    csvText = str(rowItem[keyItem[0]])
                except KeyError:
                    pass

                if keyItem[1] == "deletebutton":
                    csvItem = Button(
                        text="Delete",
                        on_press=self.deleteCallback
                    )
                    csvItem.columnID = rowItem[self.rowIDColumn]
                    csvItem.field = None
                    csvItem.rowIndex = len(self.csvItemRows)
                elif keyItem[1] == "textinput" or keyItem[1] == "addressinput":

                    csvItem = TextInput(
                        multiline=False,
                        text=csvText
                    )
                    csvItem.columnID = rowItem[self.rowIDColumn]
                    csvItem.field = keyItem[0]
                    csvItem.rowIndex = len(self.csvItemRows)

                    if keyItem[1] == "addressinput":
                        csvItem.bind(on_text_validate=self.onAddressEnter)
                        csvItem.bind(text=self.onAddressText)

                elif keyItem[1] == "dropdownbutton":

                    csvItemText = ""
                    for keySelectItem in keyItem[2]:
                        if keySelectItem[0] == rowItem[keyItem[0]]:
                            csvItemText = keySelectItem[1]

                    csvItem = DropDownButton(text=csvItemText)
                    csvItem.itemID = rowItem[keyItem[0]]
                    csvItem.columnID = rowItem[self.rowIDColumn]
                    csvItem.field = keyItem[0]
                    csvItem.rowIndex = len(self.csvItemRows)

                    for dropDownItem in keyItem[2]:
                        dropDownButton = Button(
                            text=dropDownItem[1],
                            size_hint=(1, None),
                            height=30
                        )
                        dropDownButton.itemID = dropDownItem[0]
                        dropDownButton.bind(on_press=csvItem.dropDownButtonCallback)
                        csvItem.add_widget(dropDownButton)

                csvItems.append(csvItem)

            self.csvItemRows.append(csvItems)

    def onAddressEnter(self, instance):

        checkRonin = check_ronin(instance.text)
        if checkRonin:
            instance.background_color = (1, 1, 1, 1)
            self.saveAndExitButton.disabled = False
        else:
            instance.background_color = (1, 0, 0, 1)
            self.saveAndExitButton.disabled = True

    def onAddressText(self, instance, value):

        checkRonin = check_ronin(value)
        if checkRonin:
            instance.background_color = (1, 1, 1, 1)
            self.saveAndExitButton.disabled = False
        else:
            self.saveAndExitButton.disabled = True

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

            for keyIndex in range(0, len(self.keyItems), 1):

                csvItem = None
                csvGridItem = None

                if self.keyItems[keyIndex][1] == "deletebutton":

                    csvItem = Button(
                        text="Delete",
                        on_press=self.deleteCallback
                    )
                    csvItem.columnID = None
                    csvItem.field = None
                    csvItem.rowIndex = len(self.csvItemRows)

                elif self.keyItems[keyIndex][1] == "textinput" or self.keyItems[keyIndex][1] == "addressinput":

                    csvItem = TextInput()

                    if self.keyItems[keyIndex][1] == "addressinput":
                        csvItem.bind(on_text_validate=self.onAddressEnter)
                        csvItem.bind(text=self.onAddressText)

                    csvItem.columnID = None
                    csvItem.field = self.keyItems[keyIndex][0]
                    csvItem.rowIndex = len(self.csvItemRows)

                elif self.keyItems[keyIndex][1] == "dropdownbutton":

                    csvItemText = ""
                    for keySelectItem in self.keyItems[keyIndex][2]:
                        if keySelectItem[0] == None:
                            csvItemText = keySelectItem[1]

                    csvItem = DropDownButton(text=csvItemText)
                    csvItem.itemID = None
                    csvItem.columnID = None
                    csvItem.field = self.keyItems[keyIndex][0]
                    csvItem.rowIndex = len(self.csvItemRows)

                    for dropDownItem in self.keyItems[keyIndex][2]:
                        dropDownButton = Button(
                            text=dropDownItem[1],
                            size_hint=(1, None),
                            height=30
                        )
                        dropDownButton.itemID = dropDownItem[0]
                        dropDownButton.bind(on_press=csvItem.dropDownButtonCallback)
                        csvItem.add_widget(dropDownButton)

                csvItems.append(csvItem)
                self.layoutGrid.add_widget(csvItem)

            self.csvItemRows.append(csvItems)
            self.layoutGrid.height = 30 * len(self.csvItemRows)

        elif instance.text == "Save and Exit":

            queryParams = []
            for rowIndex in range(1, len(self.csvItemRows), 1):
                newDict = {}
                for csvItem in self.csvItemRows[rowIndex]:
                    newDict[self.rowIDColumn] = csvItem.columnID
                    try:
                        newDict[csvItem.field] = csvItem.itemID
                    except AttributeError:
                        newDict[csvItem.field] = csvItem.text
                queryParams.append(newDict)
            self.updateTableCallback(queryParams)

            deleteParams = []
            for rowIndex in range(1, len(self.deleteItemRows), 1):
                newDict = {}
                for csvItem in self.deleteItemRows[rowIndex]:
                    newDict[self.rowIDColumn] = csvItem.columnID
                    deleteParams.append(newDict)
            self.deleteTableCallback(deleteParams)

            root.closeDisplayedScreen()

        elif instance.text == "Cancel":
            root.closeDisplayedScreen()