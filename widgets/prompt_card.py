from kivy.lang import Builder
from kivymd.uix.card import MDCard
from kivy.properties import StringProperty
from kivy.core.clipboard import Clipboard
from kivymd.toast import toast

Builder.load_string('''
<PromptCard>:
    orientation: "vertical"
    padding: "16dp"
    spacing: "8dp"
    size_hint_y: None
    height: "160dp"
    elevation: 2
    md_bg_color: app.theme_cls.bg_dark
    radius: [12, 12, 12, 12]

    MDLabel:
        text: root.title
        font_style: "H6"
        size_hint_y: None
        height: self.texture_size[1]
        theme_text_color: "Primary"

    MDLabel:
        text: root.category
        font_style: "Caption"
        theme_text_color: "Secondary"
        size_hint_y: None
        height: self.texture_size[1]

    MDLabel:
        text: root.prompt_text
        theme_text_color: "Primary"
        shorten: True
        shorten_from: "right"
    
    MDRaisedButton:
        text: "Copy Prompt"
        pos_hint: {"right": 1}
        elevation: 1
        on_release: root.copy_to_clipboard()
''')

class PromptCard(MDCard):
    title = StringProperty()
    category = StringProperty()
    prompt_text = StringProperty()

    def copy_to_clipboard(self):
        Clipboard.copy(self.prompt_text)
        toast("Prompt copied to clipboard!")