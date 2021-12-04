from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown 


class DropDownButton(Button):

    dropDown = None

    def __init__(self, **kwargs):
        super(DropDownButton, self).__init__(**kwargs)
        self.dropDown = DropDown()
        self.bind(on_press=self.dropDownOpen)
        self.dropDown.bind(on_select=self.dropDownCallback)

    def dropDownCallback(self, instance, clickedItem):
        setattr(self, "text", clickedItem.text)
        setattr(self, "itemID", clickedItem.itemID)

    def dropDownButtonCallback(self, instance):
        self.dropDown.select(instance)

    def dropDownOpen(self, instance):
        self.dropDown.open(instance)

    def add_widget(self, widgetIn):
        self.dropDown.add_widget(widgetIn)