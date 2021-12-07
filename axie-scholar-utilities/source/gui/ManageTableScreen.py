from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
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
    updateTableCallback = None
    deleteTableCallback = None

    def __init__(self, **kwargs):

        def resizeScreen(instance, width, height):
            self.scrollview.size = (width, height)

        self.keyItems = kwargs.pop("keyItems", [])
        self.rowIDColumn = kwargs.pop("rowIDColumn", "")
        self.rowData = kwargs.pop("rowData", [])
        self.updateTableCallback = kwargs.pop("updateCallback", lambda data: None)
        self.deleteTableCallback = kwargs.pop("deleteCallback", lambda data: None)
        super(ManageTableScreen, self).__init__(**kwargs)

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

        for keyItem in self.keyItems:
            self.layoutGrid.add_widget(Label(text=keyItem[0]))
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

        for rowItem in rowDataIn:

            csvItems = []

            for keyItem in keyItemsIn:
                csvItem = self.buildCSVItem(
                    keyItem,
                    rowItem[self.rowIDColumn],
                    len(self.csvItemRows),
                    rowItem
                )
                csvItems.append(csvItem)

            self.csvItemRows.append(csvItems)

    def buildCSVItem(self, keyItem, columnID, rowIndex, rowItem):

        csvItem = None
        csvText = ""
        try:
            if rowItem[keyItem[0]]:
                csvText = str(rowItem[keyItem[0]])
        except KeyError:
            pass

        if keyItem[1] in [
            "deletebutton",
            "button"
        ]:

            buttonText = "Delete"
            callback = self.deleteCallback

            if keyItem[1] == "button":

                def callbackFunc(instance):
                    buttonFunc(
                        instance.parent.parent.parent.parent.parent,
                        rowItem
                    )

                buttonText = keyItem[2]
                callback = callbackFunc
                buttonFunc = keyItem[3]

            csvItem = Button(
                text=buttonText,
                on_press=callback
            )
            csvItem.columnID = columnID
            csvItem.field = None
            csvItem.rowIndex = rowIndex
            if keyItem[1] == "button":
                csvItem.text = keyItem[2]
                if columnID is None:
                    csvItem.disabled = True

        elif keyItem[1] in [
            "textinput",
            "addressinput",
            "privatekeyinput",
            "passwordinput"
        ]:

            csvItem = TextInput(
                multiline=False,
                text=csvText
            )

            if keyItem[1] == "addressinput":
                csvItem.bind(on_text_validate=self.onAddressEnter)
                csvItem.bind(text=self.onAddressText)

            csvItem.columnID = columnID
            csvItem.field = keyItem[0]
            csvItem.rowIndex = rowIndex

            if keyItem[1] == "addressinput":
                csvItem.bind(on_text_validate=self.onAddressEnter)
                csvItem.bind(text=self.onAddressText)

            if keyItem[1] == "passwordinput":
                csvItem.password = True

        elif keyItem[1] == "dropdownbutton":

            csvItemText = ""
            for keySelectItem in keyItem[2]:
                if keySelectItem[0] == rowItem[keyItem[0]]:
                    csvItemText = keySelectItem[1]

            csvItem = DropDownButton(text=csvItemText)

            try:
                csvItem.itemID = rowItem[keyItem[0]]
            except KeyError:
                csvItem.itemID = None

            csvItem.columnID = columnID
            csvItem.field = keyItem[0]
            csvItem.rowIndex = rowIndex

            for dropDownItem in keyItem[2]:
                dropDownButton = Button(
                    text=dropDownItem[1],
                    size_hint=(1, None),
                    height=30
                )
                dropDownButton.itemID = dropDownItem[0]
                dropDownButton.bind(on_press=csvItem.dropDownButtonCallback)
                csvItem.add_widget(dropDownButton)

        elif keyItem[1] in [
            "label",
            "addresslabel"
        ]:

            csvItem = Label(text=csvText)
            csvItem.columnID = columnID
            csvItem.field = keyItem[0]
            csvItem.rowIndex = rowIndex

        return csvItem

    def onAddressEnter(self, instance):

        if check_ronin(instance.text):
            instance.background_color = (1, 1, 1, 1)
            self.saveAndExitButton.disabled = False
        else:
            instance.background_color = (1, 0, 0, 1)
            self.saveAndExitButton.disabled = True

    def onAddressText(self, instance, value):

        if check_ronin(value):
            instance.background_color = (1, 1, 1, 1)
            self.saveAndExitButton.disabled = False
        else:
            self.saveAndExitButton.disabled = True

    def deleteCallback(self, instance):

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

            for keyItem in self.keyItems:
                csvItem = self.buildCSVItem(keyItem, None, len(self.csvItemRows), {})
                csvItems.append(csvItem)
                self.layoutGrid.add_widget(csvItem)

            self.csvItemRows.append(csvItems)
            self.layoutGrid.height = 30 * len(self.csvItemRows)

        elif instance.text == "Save and Exit":

            queryParams = []
            deleteParams = []

            for rowItem in self.csvItemRows:
                newDict = {}
                moveToDelete = False
                for csvItem in rowItem:
                    newDict[self.rowIDColumn] = csvItem.columnID
                    try:
                        newDict[csvItem.field] = csvItem.itemID
                    except AttributeError:
                        newDict[csvItem.field] = csvItem.text
                        for keyItem in self.keyItems:
                            if (
                                keyItem[0] == csvItem.field and
                                keyItem[1] in ["addressinput", "addresslabel"]
                            ):
                                if not check_ronin(csvItem.text):
                                    moveToDelete = True
                            elif (
                                keyItem[0] == csvItem.field and
                                keyItem[1] in ["privatekeyinput"]
                            ):
                                if False:
                                    moveToDelete = True

                if not moveToDelete:
                    queryParams.append(newDict)
                else:
                    self.deleteItemRows.append(rowItem)

            self.updateTableCallback(queryParams)

            for rowItem in self.deleteItemRows:
                newDict = {}
                for csvItem in rowItem:
                    newDict[self.rowIDColumn] = csvItem.columnID
                    deleteParams.append(newDict)
            self.deleteTableCallback(deleteParams)

            root.closeDisplayedScreen()

        elif instance.text == "Cancel":
            root.closeDisplayedScreen()
