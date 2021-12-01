import base64

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
        

class PasswordScreen(Screen):

    errorLabel = ""
    layoutRow = None  
    password = None
    passwordSalt = None

    def __init__(self, **kwargs):

        def resizeScreen(instance, width, height):
            self.layoutRow.size = (width, 60)
            self.layoutRow.center = (width/2, height/2)

        def callbackWrapper(instance):
            callback(instance.parent.parent.parent)

        labelStr = kwargs.pop("label", "Password")
        self.errorLabel = kwargs.pop("error", "")
        self.passwordSalt = kwargs.pop("salt", b"nl\xa35\xbf(3\x0e\xff#+X\xb1\xben\xde")
        callback = kwargs.pop("callback", lambda instance: None)

        super(PasswordScreen, self).__init__(**kwargs)

        self.layoutRow = BoxLayout(orientation="vertical")
        layout = BoxLayout(orientation="horizontal")

        Window.bind(on_resize=resizeScreen)

        self.layoutRow.size_hint = (None, None)
        self.layoutRow.size = (Window.width, 60)
        self.layoutRow.center = (Window.width/2, Window.height/2)

        layout.add_widget(
            Label(
                text=labelStr
            )
        )

        self.password = TextInput(
            password=True,
            multiline=False,
            cursor=True,
            cursor_blink=True
        )
        self.password.bind(on_text_validate=callbackWrapper)
        layout.add_widget(self.password)
        self.layoutRow.add_widget(layout)

        self.errorLabel = Label(
            color=(1, 0, 0, 1),
            text=self.errorLabel
        )
        self.layoutRow.add_widget(self.errorLabel)

        self.add_widget(self.layoutRow)

    def getEncryptionKey(self, passwordIn):
        password = passwordIn.encode("utf-8")
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.passwordSalt,
            #salt = os.urandom(16),
            iterations=390000
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key