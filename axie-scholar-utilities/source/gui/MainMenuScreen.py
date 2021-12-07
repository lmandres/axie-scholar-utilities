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
            if instance.text == "Edit Team Information":
                root.openDisplayedScreen(nextScreenIn="ManagerRoninScreen")
            elif instance.text == "Manage Scholar Roster":
                root.openDisplayedScreen(nextScreenIn="ManageScholarsScreen")
            elif instance.text == "Manage Trainer Roster":
                root.openDisplayedScreen(nextScreenIn="ManageTrainersScreen")
            elif instance.text == "Import Payouts from Axie Scholar Utilities CSV":
                root.openDisplayedScreen(nextScreenIn="FileChooserListScreenPaymentsASUCSV")
            elif instance.text == "Import Payouts from Axie Scholar Utilities JSON":
                root.openDisplayedScreen(nextScreenIn="FileChooserListScreenPaymentsASUJSON")
            elif instance.text == "Import Secrets from Axie Scholar Utilities CSV":
                root.openDisplayedScreen(nextScreenIn="FileChooserListScreenSecretsASUCSV")
            elif instance.text == "Import Secrets from Axie Scholar Utilities JSON":
                root.openDisplayedScreen(nextScreenIn="FileChooserListScreenSecretsASUJSON")
            elif instance.text == "Manage Payouts":
                root.openDisplayedScreen(nextScreenIn="EnterPaymentsScreen")
            elif instance.text == "Run Claims and Auto-Payouts":
                root.openDisplayedScreen(nextScreenIn="RunClaimsAndAutoPayouts")
            elif instance.text == "Import Secrets from Axie Scholar Utilities JSON":
                root.openDisplayedScreen(nextScreenIn="FileChooserListScreenSecretsASUJSON")
            elif instance.text == "Exit":
                App.get_running_app().stop()

        super(MainMenuScreen, self).__init__(**kwargs)

        self.layoutRow = BoxLayout(orientation="vertical")
        self.layoutRow.size_hint = (1, 1)

        self.layoutRow.add_widget(
            Button(
                text="Edit Team Information",
                on_press=buttonCallback
            )
        )
        self.layoutRow.add_widget(
            Button(
                text="Manage Scholar Roster",
                on_press=buttonCallback
            )
        )
        self.layoutRow.add_widget(
            Button(
                text="Manage Trainer Roster",
                on_press=buttonCallback
            )
        )
        self.layoutRow.add_widget(
            Button(
                text="Manage Payouts",
                disabled=False,
                on_press=buttonCallback
            )
        )
        self.layoutRow.add_widget(
            Button(
                text="Import Payouts from Axie Scholar Utilities CSV",
                disabled=False,
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
                text="Import Secrets from Axie Scholar Utilities CSV",
                disabled=False,
                on_press=buttonCallback
            )
        )
        self.layoutRow.add_widget(
            Button(
                text="Import Secrets from Axie Scholar Utilities JSON",
                disabled=False,
                on_press=buttonCallback
            )
        )
        self.layoutRow.add_widget(
            Button(
                text="Run Claims and Auto-Payouts",
                disabled=False,
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
