from kivy.lang import Builder
from kivymd.uix.card import MDCard
from kivy.properties import StringProperty, ListProperty
from kivy.core.clipboard import Clipboard
from kivymd.toast import toast
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRoundFlatIconButton
from kivy.animation import Animation
from kivy.clock import Clock

Builder.load_string('''
<PromptCard>:
    orientation: "vertical"
    padding: "16dp"
    spacing: "8dp"
    size_hint_y: None
    height: "180dp"
    elevation: 2
    md_bg_color: 0.09, 0.08, 0.14, 1
    line_color: 1, 1, 1, 0.08
    line_width: 1
    radius: [16, 16, 16, 16]
    ripple_behavior: True
    on_release: root.show_full_prompt()
    opacity: 0

    canvas.after:
        # GalleryCard jaisa hi matching animated gradient glow -
        # poori app me consistent premium "AI glow" theme ke liye.
        Color:
            rgba: root.glow_color
        SmoothLine:
            width: 1.1 + (root.glow_color[3] * 1.5)
            rounded_rectangle: (self.x, self.y, self.width, self.height, 16)


    MDBoxLayout:
        size_hint_y: None
        height: self.minimum_height
        spacing: "10dp"

        MDLabel:
            text: root.title
            font_style: "H6"
            bold: True
            size_hint_y: None
            height: self.texture_size[1]
            theme_text_color: "Primary"
            shorten: True
            shorten_from: "right"

        # Category "chip" - premium pill badge instead of plain caption text
        MDBoxLayout:
            adaptive_size: True
            padding: "20dp", "4dp"
            radius: [10, 10, 10, 10]
            md_bg_color:
                app.theme_cls.primary_color[0], app.theme_cls.primary_color[1], app.theme_cls.primary_color[2], 0.20
            pos_hint: {"center_y": .5}

            MDLabel:
                text: root.category
                font_style: "Caption"
                bold: True
                theme_text_color: "Custom"
                text_color: app.theme_cls.primary_color
                adaptive_size: True

    MDLabel:
        text: root.prompt_text
        theme_text_color: "Secondary"
        font_style: "Body2"
        shorten: True
        shorten_from: "right"

    MDBoxLayout:
        size_hint_y: None
        height: "38dp"

        Widget:
            # spacer - copy button ko right side pe push karta hai

        MDRoundFlatIconButton:
            text: "Copy Prompt"
            icon: "content-copy"
            theme_text_color: "Custom"
            text_color: app.theme_cls.primary_color
            line_color: root.glow_color[0], root.glow_color[1], root.glow_color[2], root.glow_color[3] + 0.15
            on_release: root.copy_to_clipboard()
''')


class PromptCard(MDCard):
    title = StringProperty()
    category = StringProperty()
    prompt_text = StringProperty()
    # GalleryCard jaisa hi synced "gradient glow" - border aur copy
    # button ka outline dono isi color se cycle karte hain.
    glow_color = ListProperty([0.65, 0.35, 1.0, 0.35])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        # GalleryCard jaisa hi smooth fade-in entry animation
        Clock.schedule_once(self.animate_entry, 0.1)
        Clock.schedule_once(self._start_glow_cycle, 0)

    def animate_entry(self, dt):
        anim = Animation(opacity=1, duration=0.4, transition="out_cubic")
        anim.start(self)

    def _start_glow_cycle(self, *args):
        """
        GalleryCard jaisa hi HIGH-CONTRAST "breathing" glow loop - alpha
        dramatically dips/rises har hue-shift ke saath. List view mein
        thoda toned-down rakha hai (DIM/BRIGHT kam) taaki gallery cards
        hi sabse "hero"/prominent lagein.
        """
        DIM, BRIGHT = 0.08, 0.55
        stops = [
            [0.65, 0.35, 1.0, DIM],
            [0.65, 0.35, 1.0, BRIGHT],
            [0.35, 0.55, 1.0, BRIGHT],
            [0.35, 0.55, 1.0, DIM],
            [1.0, 0.40, 0.70, DIM],
            [1.0, 0.40, 0.70, BRIGHT],
            [0.65, 0.35, 1.0, BRIGHT],
            [0.65, 0.35, 1.0, DIM],
        ]
        anim = Animation(glow_color=stops[1], duration=0.9, t="in_out_sine")
        for stop in stops[2:]:
            anim += Animation(glow_color=stop, duration=0.9, t="in_out_sine")
        anim.repeat = True
        anim.start(self)

    def copy_to_clipboard(self):
        Clipboard.copy(self.prompt_text)
        toast("Prompt copied to clipboard!")

    def show_full_prompt(self):
        """
        NAYA FEATURE: card par tap karne se poora (untruncated) prompt
        ek dialog me dikhta hai - list view me lambe prompts "shorten"
        ho jaate the, ab user unhe pura padh bhi sakta hai bina gallery
        tab me jaaye.
        """
        if not self.dialog:
            self.dialog = MDDialog(
                title=self.title,
                text=self.prompt_text,
                buttons=[
                    MDFlatButton(
                        text="CLOSE",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: self.dialog.dismiss(),
                    ),
                    MDFlatButton(
                        text="COPY PROMPT",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: self._copy_and_close(),
                    ),
                ],
            )
        self.dialog.open()

    def _copy_and_close(self):
        self.copy_to_clipboard()
        if self.dialog:
            self.dialog.dismiss()
