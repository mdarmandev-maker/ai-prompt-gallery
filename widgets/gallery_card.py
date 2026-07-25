from kivy.lang import Builder
from kivymd.uix.card import MDCard
from kivy.properties import StringProperty
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.core.clipboard import Clipboard
from kivymd.toast import toast
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.animation import Animation # Animation library import
from kivy.clock import Clock

Builder.load_string('''
<DialogContent>:
    orientation: "vertical"
    spacing: "12dp"
    size_hint_y: None
    height: "380dp" 
    
    AsyncImage: 
        source: root.image_path
        size_hint_y: 0.75
        allow_stretch: True
        keep_ratio: True 

    ScrollView:
        size_hint_y: 0.25
        MDLabel:
            text: root.prompt_text
            theme_text_color: "Secondary"
            font_style: "Body2"
            adaptive_height: True

<GalleryCard>:
    orientation: "vertical"
    size_hint_y: None
    height: "220dp"
    elevation: 2
    radius: [8, 8, 8, 8]
    md_bg_color: app.theme_cls.bg_dark
    ripple_behavior: True # PREMIUM TOUCH EFFECT JODA
    on_release: root.show_prompt_dialog()
    opacity: 0 # Shuru me card gayab rahega (animation ke liye)

    FitImage:
        source: root.image_path
        size_hint_y: 0.75
        radius: [8, 8, 0, 0]

    MDBoxLayout:
        padding: "8dp"
        size_hint_y: 0.25
        MDLabel:
            text: root.title
            theme_text_color: "Primary"
            font_style: "Caption"
            bold: True
            shorten: True
            shorten_from: "right"
            halign: "center"
''')

class DialogContent(MDBoxLayout):
    image_path = StringProperty()
    prompt_text = StringProperty()

class GalleryCard(MDCard):
    title = StringProperty()
    prompt_text = StringProperty()
    image_path = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        # Jaise hi card bane, usko fade-in aane ka command do
        Clock.schedule_once(self.animate_entry, 0.1)
        
    def animate_entry(self, dt):
        # Apple Premium Style Smooth Fade-in Animation
        anim = Animation(opacity=1, duration=0.4, transition='out_cubic')
        anim.start(self)

    def show_prompt_dialog(self):
        if not self.dialog:
            self.dialog = MDDialog(
                title=self.title,
                type="custom", 
                content_cls=DialogContent(
                    image_path=self.image_path,
                    prompt_text=self.prompt_text
                ),
                buttons=[
                    MDFlatButton(
                        text="CLOSE",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: self.dialog.dismiss()
                    ),
                    MDFlatButton(
                        text="COPY PROMPT",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=self.copy_prompt
                    ),
                ],
            )
        self.dialog.open()

    def copy_prompt(self, *args):
        Clipboard.copy(self.prompt_text)
        toast("Prompt copied to clipboard!")
        self.dialog.dismiss()