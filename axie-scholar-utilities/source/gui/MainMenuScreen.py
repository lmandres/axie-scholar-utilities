from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
        

class MainMenuScreen(Screen):

    layoutRow = None

    def __init__(self, **kwargs):

        def buttonCallback(instance):
            root = instance.parent.parent.parent
            root.closeMainMenuScreen()
            if instance.text == "Edit Manager Ronin":
                root.openDisplayedScreen(nextScreenIn="ManagerRoninScreen")
            elif instance.text == "Import Payouts from Axie Scholar Utilities CSV":
                print(instance.text)
            elif instance.text == "Import Payouts from Axie Scholar Utilities JSON":
                root.openDisplayedScreen(nextScreenIn="FileChooserListScreenASUJSON")
            elif instance.text == "Add/Edit Payouts":
                print(instance.text)
            elif instance.text == "Add/Edit Secrets":
                print(instance.text)
            elif instance.text == "Run Claims and Auto-Payouts":
                print(instance.text)
            elif instance.text == "Exit":
                App.get_running_app().stop()

        super(MainMenuScreen, self).__init__(**kwargs)

        self.layoutRow = BoxLayout(orientation="vertical")
        self.layoutRow.size_hint = (1, 1)

        self.layoutRow.add_widget(
            Button(
                text="Edit Manager Ronin",
                on_press=buttonCallback
            )
        )
        self.layoutRow.add_widget(
            Button(
                text="Add/Edit/Delete Payouts",
                disabled=True,
                on_press=buttonCallback
            )
        )
        self.layoutRow.add_widget(
            Button(
                text="Import Payouts from Axie Scholar Utilities CSV",
                disabled=True,
                on_press=buttonCallback
            )
        )
        self.layoutRow.add_widget(
            Button(
                text="Import Payouts from Axie Scholar Utilities JSON",
                disabled=False,
                on_press=buttonCallback
            )
        )
        self.layoutRow.add_widget(
            Button(
                text="Add/Edit Secrets",
                disabled=True,
                on_press=buttonCallback
            )
        )
        self.layoutRow.add_widget(
            Button(
                text="Run Claims and Auto-Payouts",
                disabled=True,
                on_press=buttonCallback
            )
        )
        self.layoutRow.add_widget(
            Button(
                text="Exit",
                disabled=False,
                on_press=buttonCallback
            )
        )

        self.add_widget(self.layoutRow)