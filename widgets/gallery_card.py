from kivy.lang import Builder
from kivymd.uix.card import MDCard
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, ListProperty
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.core.clipboard import Clipboard
from kivymd.toast import toast
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.widget import Widget
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp

Builder.load_string('''
<PulseLoader>:
    size_hint: None, None
    size: (root.max_size, root.max_size)
    canvas:
        Color:
            rgba: (root.color[0], root.color[1], root.color[2], root._alpha)
        Ellipse:
            pos: (self.center_x - root._radius, self.center_y - root._radius)
            size: (root._radius * 2, root._radius * 2)
        Color:
            rgba: (root.color[0], root.color[1], root.color[2], 1)
        Ellipse:
            pos: (self.center_x - root.base_size / 4, self.center_y - root.base_size / 4)
            size: (root.base_size / 2, root.base_size / 2)

<DialogContent>:
    orientation: "vertical"
    spacing: "12dp"
    size_hint_y: None
    height: "380dp"
    MDRelativeLayout:
        size_hint_y: 0.75
        AsyncImage:
            id: dialog_image
            source: root.image_path
            size_hint: (1, 1)
            allow_stretch: True
            keep_ratio: True
            radius: [12, 12, 0, 0]
            on_texture:
                spinner_dialog.active = False
                spinner_dialog.opacity = 0
        PulseLoader:
            id: spinner_dialog
            base_size: "20dp"
            max_size: "48dp"
            pos_hint: {"center_x": .5, "center_y": .5}
            active: True
            color: app.theme_cls.primary_color
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
    elevation: 3
    radius: [16, 16, 16, 16]
    md_bg_color: 0.09, 0.08, 0.14, 1
    line_color: 1, 1, 1, 0.06
    line_width: 1
    ripple_behavior: True
    on_release: root.show_prompt_dialog()
    opacity: 0

    canvas.after:
        # Premium animated gradient glow border - color dheere-dheere
        # violet -> blue -> pink -> violet cycle karta hai (Copilot/Siri
        # jaisa "AI glow" accent). SmoothLine anti-aliased hoti hai isliye
        # ek plain Line se zyada soft/glow jaisi dikhti hai.
        Color:
            rgba: root.glow_color
        SmoothLine:
            width: 1.2 + (root.glow_color[3] * 1.6)
            rounded_rectangle: (self.x, self.y, self.width, self.height, 16)

    MDRelativeLayout:
        size_hint: (1, 1)

        FitImage:
            id: card_image
            source: root.image_path
            size_hint: (1, 1)
            radius: [16, 16, 16, 16]

        PulseLoader:
            id: spinner_card
            base_size: "14dp"
            max_size: "36dp"
            pos_hint: {"center_x": .5, "center_y": .5}
            active: True
            color: app.theme_cls.primary_color

        MDBoxLayout:
            size_hint: (1, None)
            height: "62dp"
            pos_hint: {"x": 0, "y": 0}
            md_bg_color: 0, 0, 0, 0.45
            radius: [0, 0, 16, 16]
            padding: "10dp", "6dp"
            spacing: "4dp"

            MDLabel:
                text: root.title
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                font_style: "Subtitle2"
                bold: True
                shorten: True
                shorten_from: "right"
                valign: "bottom"

            MDIconButton:
                icon: "share-variant"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 0.85
                icon_size: "16sp"
                pos_hint: {"center_y": .45}
                padding: 0
                on_release: root.share_prompt()

        # Quick-copy - glass-morphism look: translucent bg + colored glow
        # halo + ek thin light border-ring (glass edge) + upar ek soft
        # white shine (glass reflection jaisa) - premium "frosted glass"
        # feel ke liye.
        MDBoxLayout:
            id: copy_btn_layout
            size_hint: None, None
            size: dp(30), dp(30)
            radius: [15, 15, 15, 15]
            md_bg_color: 1, 1, 1, 0.10
            pos_hint: {"right": 0.95, "top": 0.95}
            canvas.before:
                Color:
                    rgba: root.glow_color[0], root.glow_color[1], root.glow_color[2], root.glow_color[3] * 0.55
                Ellipse:
                    pos: (self.center_x - dp(20), self.center_y - dp(20))
                    size: (dp(40), dp(40))
                Color:
                    rgba: 1, 1, 1, 0.22
                SmoothLine:
                    width: 1
                    rounded_rectangle: (self.x, self.y, self.width, self.height, 15)
            canvas.after:
                Color:
                    rgba: 1, 1, 1, 0.20
                Ellipse:
                    pos: (self.x + self.width * 0.18, self.y + self.height * 0.52)
                    size: (self.width * 0.5, self.height * 0.32)

            MDIconButton:
                id: copy_btn_icon
                icon: "content-copy"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                icon_size: "15sp"
                pos_hint: {"center_x": .5, "center_y": .5}
                padding: 0
                on_release: root.copy_prompt()

        # Favorite toggle - same glass treatment as copy button
        MDBoxLayout:
            id: heart_btn_layout
            size_hint: None, None
            size: dp(30), dp(30)
            radius: [15, 15, 15, 15]
            md_bg_color: 1, 1, 1, 0.10
            pos_hint: {"x": 0.05, "top": 0.95}
            canvas.before:
                Color:
                    rgba: root.glow_color[0], root.glow_color[1], root.glow_color[2], root.glow_color[3] * 0.55
                Ellipse:
                    pos: (self.center_x - dp(20), self.center_y - dp(20))
                    size: (dp(40), dp(40))
                Color:
                    rgba: 1, 1, 1, 0.22
                SmoothLine:
                    width: 1
                    rounded_rectangle: (self.x, self.y, self.width, self.height, 15)
            canvas.after:
                Color:
                    rgba: 1, 1, 1, 0.20
                Ellipse:
                    pos: (self.x + self.width * 0.18, self.y + self.height * 0.52)
                    size: (self.width * 0.5, self.height * 0.32)

            MDIconButton:
                id: heart_btn_icon
                icon: "heart" if root.is_favorite else "heart-outline"
                theme_text_color: "Custom"
                text_color: (1, 0.25, 0.4, 1) if root.is_favorite else (1, 1, 1, 1)
                icon_size: "15sp"
                pos_hint: {"center_x": .5, "center_y": .5}
                padding: 0
                on_release: root.toggle_favorite()
''')


class PulseLoader(Widget):
    active = BooleanProperty(True)
    color = ListProperty([1, 1, 1, 1])
    base_size = NumericProperty("20dp")
    max_size = NumericProperty("48dp")
    _radius = NumericProperty(10)
    _alpha = NumericProperty(0.6)

    def __init__(self, **kwargs):
        self._anim = None
        super().__init__(**kwargs)
        self.bind(active=self._on_active)
        if self.active:
            self._start_pulse()

    def _on_active(self, *args):
        if self.active:
            self._start_pulse()
        else:
            self._stop_pulse()

    def _start_pulse(self, *args):
        self._stop_pulse()
        self._radius = self.base_size / 2
        self._alpha = 0.6
        self._anim = Animation(_radius=self.max_size / 2, _alpha=0, duration=1.0, transition="out_quad")
        self._anim.bind(on_complete=self._loop)
        self._anim.start(self)

    def _loop(self, *args):
        if self.active:
            self._start_pulse()

    def _stop_pulse(self):
        if self._anim:
            self._anim.cancel(self)
            self._anim = None


class DialogContent(MDBoxLayout):
    image_path = StringProperty()
    prompt_text = StringProperty()


class GalleryCard(MDCard):
    title = StringProperty()
    prompt_text = StringProperty()
    image_path = StringProperty()
    is_favorite = BooleanProperty(False)
    # Card ke border aur button-halo dono isi color se render hote hain,
    # taaki poora glow ek saath, sync me shift ho (patchy na lage).
    glow_color = ListProperty([0.65, 0.35, 1.0, 0.45])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        Clock.schedule_once(self.animate_entry, 0.1)
        Clock.schedule_once(self._start_glow_cycle, 0)
        Clock.schedule_once(self._hook_card_image_loader, 0)

    def animate_entry(self, dt):
        Animation(opacity=1, duration=0.4, transition='out_cubic').start(self)

    def _start_glow_cycle(self, *args):
        """
        HIGH-CONTRAST "breathing" glow loop - alpha dramatically dips/rises
        (0.12 <-> 0.85) HAR hue-shift ke saath, isliye glow sirf color nahi
        badalta, balki visibly fade-in/fade-out bhi karta hai - jyada
        "alive"/premium AI-glow feel ke liye (Copilot/Siri jaisa pulse).
        """
        # PERFORMANCE FIX: pehle 8 animation-steps the, ab 4 - aur duration
        # 0.9s se badhakar 1.8s kar diya hai. Isse total animation-frame
        # updates kaafi kam ho jaate hain (roughly half), jo bahut saare
        # cards ek saath animate hone par CPU load kaafi kam kar deta hai,
        # bina visual effect ko poori tarah khatam kiye.
        DIM, BRIGHT = 0.12, 0.85
        stops = [
            [0.65, 0.35, 1.0, DIM],      # violet - dim (start)
            [0.65, 0.35, 1.0, BRIGHT],   # violet - fade IN
            [1.0, 0.40, 0.70, BRIGHT],   # -> pink, still bright
            [1.0, 0.40, 0.70, DIM],      # pink - fade OUT (loop point)
        ]
        anim = Animation(glow_color=stops[1], duration=1.8, t="in_out_sine")
        for stop in stops[2:]:
            anim += Animation(glow_color=stop, duration=1.8, t="in_out_sine")
        anim.repeat = True
        anim.start(self)

    def cleanup(self):
        """
        BUG FIX: har baar card list se hata di jaati thi (filter switch,
        refresh) to iski glow animation aur spinner-pulse animation kabhi
        cancel nahi hoti thi - background me hamesha ke liye chalti rehti
        thi (zombie animation), jisse CPU load use karte-karte badhta
        jaata. Ab card discard hone se theek pehle iski SAARI animations
        (glow, entry-fade, spinner) explicitly cancel kar dete hain.
        """
        Animation.cancel_all(self)
        spinner = self.ids.get("spinner_card")
        if spinner:
            Animation.cancel_all(spinner)
            spinner.active = False

    def pause_glow(self):
        """
        PERFORMANCE: jab ye card currently active tab me nahi hai (jaise
        List View dekh rahe ho, ye Gallery ka card hai), to iska infinite
        glow-loop pause kar dete hain. User ko dikh hi nahi raha, isliye
        animate karte rehna sirf CPU/battery waste hai.
        """
        Animation.cancel_all(self, "glow_color")

    def resume_glow(self):
        """Tab wapas visible/active hone par glow-loop dobara shuru."""
        self._start_glow_cycle()

    def _bounce_button(self, layout):
        """Tap par halka tactile 'press' feedback - one-shot, loop nahi."""
        if not layout:
            return
        base_w, base_h = dp(30), dp(30)
        anim = (
            Animation(width=dp(25), height=dp(25), duration=0.08, t="out_quad")
            + Animation(width=base_w, height=base_h, duration=0.18, t="out_back")
        )
        anim.start(layout)

    def toggle_favorite(self):
        self.is_favorite = not self.is_favorite
        self._bounce_button(self.ids.get("heart_btn_layout"))

    def _hook_card_image_loader(self, dt):
        card_image = self.ids.get("card_image")
        if card_image and card_image._container:
            self._bind_card_image_events(card_image._container)
        elif card_image:
            card_image.bind(_container=self._on_card_container_ready)

    def _on_card_container_ready(self, instance, container):
        if container:
            self._bind_card_image_events(container)

    def _bind_card_image_events(self, container):
        inner_image = container.image
        inner_image.bind(on_load=self._hide_card_spinner, on_error=self._hide_card_spinner)
        if inner_image.texture:
            self._hide_card_spinner()

    def _hide_card_spinner(self, *args):
        spinner = self.ids.get("spinner_card")
        if spinner:
            spinner.active = False
            spinner.opacity = 0

    def show_prompt_dialog(self):
        if not self.dialog:
            self.dialog = MDDialog(
                title=self.title, type="custom",
                content_cls=DialogContent(image_path=self.image_path, prompt_text=self.prompt_text),
                buttons=[
                    MDFlatButton(text="CLOSE", on_release=lambda x: self.dialog.dismiss()),
                    MDFlatButton(text="COPY PROMPT", on_release=self.copy_prompt),
                ],
            )
        self.dialog.open()

    def copy_prompt(self, *args):
        Clipboard.copy(self.prompt_text)
        toast("Prompt copied!")
        self._bounce_button(self.ids.get("copy_btn_layout"))
        if self.dialog:
            self.dialog.dismiss()

    def share_prompt(self, *args):
        """
        Android ka native "Share via..." sheet kholta hai (WhatsApp,
        Instagram, etc. me directly share karne ke liye). Agar kisi
        wajah se native share available na ho (jaise desktop pe testing
        karte waqt), to clipboard me copy karke toast dikha deta hai -
        taaki app kabhi crash na ho, sirf gracefully fallback ho jaye.
        """
        share_text = f"{self.title}\n\n{self.prompt_text}\n\nvia AI Prompt Gallery"
        try:
            from jnius import autoclass, cast  # type: ignore[import]
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            String = autoclass('java.lang.String')

            intent = Intent()
            intent.setAction(Intent.ACTION_SEND)
            intent.setType('text/plain')
            intent.putExtra(Intent.EXTRA_TEXT, cast('java.lang.CharSequence', String(share_text)))

            current_activity = cast('android.app.Activity', PythonActivity.mActivity)
            chooser_title = cast('java.lang.CharSequence', String('Share prompt via'))
            current_activity.startActivity(Intent.createChooser(intent, chooser_title))
        except Exception:
            Clipboard.copy(share_text)
            toast("Prompt copied - paste it anywhere to share!")
