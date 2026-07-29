from kivy.lang import Builder
from kivymd.uix.screen import MDScreen
from widgets.prompt_card import PromptCard
from widgets.gallery_card import GalleryCard
from utils.json_manager import load_prompts
from kivy.clock import Clock
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.list import OneLineListItem
from kivymd.uix.refreshlayout import MDScrollViewRefreshLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.animation import Animation  
from kivy.properties import ListProperty, NumericProperty, StringProperty
from kivy.uix.widget import Widget
from kivy.metrics import dp
from collections import Counter
import random
import webbrowser

Builder.load_string('''
<AmbientGradientBG>:
    canvas:
        # Blob 1 - bottom-left
        Color:
            rgba: root.blob1_color
        Ellipse:
            pos: (self.width * 0.10 - self.width * 0.45, self.height * 0.85 - self.width * 0.45)
            size: (self.width * 0.9, self.width * 0.9)
        # Blob 2 - top-right
        Color:
            rgba: root.blob2_color
        Ellipse:
            pos: (self.width * 0.85 - self.width * 0.40, self.height * 0.70 - self.width * 0.40)
            size: (self.width * 0.8, self.width * 0.8)
        # Blob 3 - upper-center
        Color:
            rgba: root.blob3_color
        Ellipse:
            pos: (self.width * 0.50 - self.width * 0.35, self.height * 0.10 - self.width * 0.35)
            size: (self.width * 0.7, self.width * 0.7)

<InfoDialogContent>:
    orientation: "vertical"
    spacing: "16dp"
    size_hint_y: None
    height: "440dp"
    padding: "4dp", "4dp", "4dp", "4dp"

    MDBoxLayout:
        size_hint_y: None
        height: "48dp"
        spacing: "14dp"

        MDBoxLayout:
            size_hint: None, None
            size: "48dp", "48dp"
            radius: [24, 24, 24, 24]
            md_bg_color: 0.65, 0.35, 1.0, 0.16
            MDIcon:
                icon: root.icon
                theme_text_color: "Custom"
                text_color: 0.78, 0.58, 1.0, 1
                font_size: "26sp"
                pos_hint: {"center_x": .5, "center_y": .5}

        MDLabel:
            text: root.header_title
            font_style: "H6"
            bold: True
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 1
            valign: "middle"

    MDBoxLayout:
        size_hint_y: None
        height: "1dp"
        md_bg_color: 1, 1, 1, 0.08

    ScrollView:
        do_scroll_x: False
        MDLabel:
            text: root.body_text
            markup: True
            theme_text_color: "Secondary"
            font_style: "Body1"
            adaptive_height: True
            line_height: 1.25
''')

Builder.load_file('screens/main_screen.kv')


class InfoDialogContent(MDBoxLayout):
    icon = StringProperty("information-outline")
    header_title = StringProperty("")
    body_text = StringProperty("")


class AmbientGradientBG(Widget):
    """
    Poore screen ke peeche ek slow, colorful "aurora" jaisa ambient
    gradient background - 3 soft glowing blobs jo dheere-dheere apna
    color cycle karte hain, ek dusre se thoda out-of-phase (alag delay
    par shuru hote hain) taaki organic/"living" feel aaye - jaisa
    Notion AI / ChatGPT / Linear jaise premium AI apps mein background
    hota hai. Sirf decorative hai - touches ko intercept nahi karta.
    """
    blob1_color = ListProperty([0.45, 0.25, 0.85, 0.14])
    blob2_color = ListProperty([0.15, 0.45, 0.85, 0.12])
    blob3_color = ListProperty([0.85, 0.25, 0.55, 0.10])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self._start_all_cycles, 0)

    def _start_all_cycles(self, *args):
        stops = {
            "blob1_color": ([0.45, 0.25, 0.85, 0.14], [0.15, 0.45, 0.85, 0.12], [0.85, 0.25, 0.55, 0.10]),
            "blob2_color": ([0.15, 0.45, 0.85, 0.12], [0.85, 0.25, 0.55, 0.10], [0.45, 0.25, 0.85, 0.14]),
            "blob3_color": ([0.85, 0.25, 0.55, 0.10], [0.45, 0.25, 0.85, 0.14], [0.15, 0.45, 0.85, 0.12]),
        }
        durations = {"blob1_color": 5.0, "blob2_color": 6.0, "blob3_color": 7.0}
        delays = {"blob1_color": 0.0, "blob2_color": 1.2, "blob3_color": 2.4}

        for prop_name, (c1, c2, c3) in stops.items():
            Clock.schedule_once(
                self._make_starter(prop_name, c1, c2, c3, durations[prop_name]),
                delays[prop_name],
            )

    def _make_starter(self, prop_name, c1, c2, c3, duration):
        def start(*_args):
            anim = Animation(**{prop_name: c2}, duration=duration, t="in_out_sine")
            anim += Animation(**{prop_name: c3}, duration=duration, t="in_out_sine")
            anim += Animation(**{prop_name: c1}, duration=duration, t="in_out_sine")
            anim.repeat = True
            anim.start(self)
        return start

class MainScreen(MDScreen):
    dialog = None
    current_filter = "All"
    card_loading_event = None
    # "Surprise Me" FAB ke peeche breathing glow-ring ke liye - infinite
    # loop, isliye MainScreen par hi rakha hai (widget kabhi remove nahi
    # hota, isliye animation hamesha safe rehta hai, koi leak nahi).
    fab_glow_alpha = NumericProperty(0.20)

    def on_enter(self):
        # FAB ka glow-loop turant shuru - ye hamesha chalta rehta hai
        Clock.schedule_once(self._start_fab_glow_loop, 0)
        # Splash logo ka premium "pop-in" entrance
        Clock.schedule_once(self._animate_splash_logo, 0)
        # Data turant load karne ke bajaye, Splash screen ka timer start karo (2.5 seconds)
        Clock.schedule_once(self.start_splash_transition, 2.5)
        # PERFORMANCE: jab bhi tab switch ho, sirf currently visible tab
        # ke cards hi glow-animate karein - baaki sab pause. Gallery aur
        # List dono tabs ke cards ek saath create hote hain, isliye bina
        # is fix ke hamesha dono tab ke saare cards background me bhi
        # animate karte rehte the (jo dikhta hi nahi tha, sirf CPU waste).
        self.ids.bottom_nav.bind(current=self._on_bottom_nav_switch)

    def _on_bottom_nav_switch(self, instance, active_tab):
        self._set_tab_animations(active_tab)

    def _set_tab_animations(self, active_tab):
        tab_containers = {
            "screen_gallery": self.ids.get("gallery_grid"),
            "screen_list": self.ids.get("prompt_list"),
        }
        for tab_name, container in tab_containers.items():
            if not container:
                continue
            is_active = tab_name == active_tab
            for card in container.children:
                try:
                    if is_active and hasattr(card, "resume_glow"):
                        card.resume_glow()
                    elif not is_active and hasattr(card, "pause_glow"):
                        card.pause_glow()
                except Exception:
                    # Kabhi bhi ye fail ho (jaise widget already removed),
                    # to app crash nahi karni - sirf silently skip karo.
                    pass

    def _start_fab_glow_loop(self, *args):
        anim = (
            Animation(fab_glow_alpha=0.55, duration=1.2, t="in_out_sine")
            + Animation(fab_glow_alpha=0.18, duration=1.2, t="in_out_sine")
        )
        anim.repeat = True
        anim.start(self)

    def _animate_splash_logo(self, dt):
        logo = self.ids.get("splash_logo")
        if logo:
            Animation(
                size=(dp(160), dp(160)), duration=0.6, t="out_back"
            ).start(logo)

    def start_splash_transition(self, dt):
        # Splash screen ko smoothly fade out karne ka code (0.6 seconds me gayab)
        anim = Animation(opacity=0, duration=0.6, transition='out_quad')
        anim.bind(on_complete=self.on_splash_complete)
        anim.start(self.ids.splash_layout)

    def on_splash_complete(self, animation, widget):
        # Jab splash gayab ho jaye, usko memory se hata do taaki app fast chale
        self.remove_widget(widget)
        # Aur phir finally Cards aur categories load karo
        Clock.schedule_once(self.load_initial_data, 0.1)

    def load_initial_data(self, dt):
        self.load_categories()
        self.load_cards(filter_category="All")

    def load_categories(self):
        self.ids.category_list.clear_widgets()
        prompts = load_prompts()

        categories = set(item.get("category", "General") for item in prompts if item.get("category"))
        # NAYA FEATURE: har category ke saamne kitne prompts hain, wo count
        counts = Counter(item.get("category", "General") for item in prompts)

        items = []

        item_all = OneLineListItem(
            text=f"[b]All Categories[/b]   ({len(prompts)})",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            bg_color=(0.2, 0.2, 0.25, 0.6), # Glass feel (transparent)
            divider="Full",
            radius=[12, 12, 12, 12],
            opacity=0,
            on_release=lambda x: self.filter_and_switch("All")
        )
        item_all.ids._lbl_primary.markup = True 
        self.ids.category_list.add_widget(item_all)
        items.append(item_all)

        for cat in sorted(categories):
            item = OneLineListItem(
                text=f"[b]{cat}[/b]   ({counts[cat]})",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                bg_color=(0.1, 0.1, 0.15, 0.6), # Glass feel
                divider="Full",
                radius=[12, 12, 12, 12],
                opacity=0,
                on_release=lambda x, selected_cat=cat: self.filter_and_switch(selected_cat)
            )
            item.ids._lbl_primary.markup = True 
            self.ids.category_list.add_widget(item)
            items.append(item)

        # Cascade / staggered fade-in - ek ke baad ek smoothly reveal hote hain
        for index, item in enumerate(items):
            Clock.schedule_once(
                lambda dt, it=item: Animation(opacity=1, duration=0.3, t="out_cubic").start(it),
                index * 0.05,
            )

    def open_menu_or_go_back(self):
        if self.current_filter == "All":
            self.ids.nav_drawer.set_state("open")
        else:
            self.filter_and_switch("All")

    def update_top_bar(self):
        if self.current_filter == "All":
            self.ids.top_bar_title.text = "AI Prompt Gallery"
            self.ids.left_icon_btn.icon = "menu"
            
            self.ids.right_icon_btn.opacity = 0
            self.ids.right_icon_btn.disabled = True
        else:
            self.ids.top_bar_title.text = f"{self.current_filter} Prompts"
            self.ids.left_icon_btn.icon = "arrow-left"
            
            self.ids.right_icon_btn.opacity = 1
            self.ids.right_icon_btn.disabled = False

    # Home tab ('All' filter) par poori list ki jagah sirf itne hi
    # recent/trending prompts dikhate hain - taaki home halka aur fast
    # rahe. Kisi specific category pe click karne se us category ki
    # SAARI images dikhti hain, ye limit sirf 'All' tab ke liye hai.
    HOME_FEED_LIMIT = 50

    def load_cards(self, filter_category):
        self.current_filter = filter_category

        if self.card_loading_event:
            self.card_loading_event.cancel()

        # BUG FIX: clear_widgets() sirf cards ko screen se hata deta hai -
        # unki infinite glow animation background me hamesha chalti rehti
        # thi, kabhi cancel hi nahi hoti thi. Matlab jitni baar category
        # badlo ya refresh karo, utne purane "zombie" cards ka animation
        # hamesha ke liye chalte rehte the, aur CPU load use karte-karte
        # progressively badhta jaata (app dheere-dheere aur slow hoti
        # jaati). Ab widgets hatane se PEHLE unki animation explicitly
        # cancel karte hain.
        for card in list(self.ids.prompt_list.children) + list(self.ids.gallery_grid.children):
            if hasattr(card, "cleanup"):
                try:
                    card.cleanup()
                except Exception:
                    pass

        self.ids.prompt_list.clear_widgets()
        self.ids.gallery_grid.clear_widgets()

        self.update_top_bar()

        prompts = load_prompts()

        self.filtered_prompts = [
            item for item in prompts 
            if filter_category == "All" or item.get("category", "General") == filter_category
        ]

        if filter_category == "All":
            # Naye/recent prompts sabse pehle (id sabse bada = sabse naya
            # maan kar), aur sirf top HOME_FEED_LIMIT hi rakhte hain.
            self.filtered_prompts = sorted(
                self.filtered_prompts,
                key=lambda item: item.get("id", 0),
                reverse=True,
            )[: self.HOME_FEED_LIMIT]

        self.current_load_index = 0
        
        if self.filtered_prompts:
            self.card_loading_event = Clock.schedule_interval(self._add_single_card, 0.05)

    def _add_single_card(self, dt):
        if self.current_load_index >= len(self.filtered_prompts):
            return False 
            
        item = self.filtered_prompts[self.current_load_index]
        title = item.get("title", "Untitled")
        prompt_text = item.get("prompt", "")
        image_path = item.get("image", "")
        cat = item.get("category", "General")

        list_card = PromptCard(title=title, category=cat, prompt_text=prompt_text)
        self.ids.prompt_list.add_widget(list_card)

        gallery_card = GalleryCard(title=title, prompt_text=prompt_text, image_path=image_path)
        self.ids.gallery_grid.add_widget(gallery_card)

        # PERFORMANCE: dono cards create hote hi, jo tab abhi visible
        # nahi hai uska glow turant pause - sirf active tab ke cards
        # animate hote rehte hain.
        active_tab = self.ids.bottom_nav.current
        if active_tab != "screen_list" and hasattr(list_card, "pause_glow"):
            list_card.pause_glow()
        if active_tab != "screen_gallery" and hasattr(gallery_card, "pause_glow"):
            gallery_card.pause_glow()

        self.current_load_index += 1

    # ==========================================
    # PULL-TO-REFRESH (Instagram jaisa swipe-down refresh)
    # Teeno tabs (Gallery, Categories, List) ke liye alag-alag
    # callback - user upar se neeche swipe karega to ye chalega,
    # aur load_prompts() dobara GitHub se fresh JSON fetch karega.
    # ==========================================

    def refresh_gallery(self, *args):
        def do_refresh(interval):
            self.load_cards(filter_category=self.current_filter)
            self.load_categories()
            self.ids.refresh_layout_gallery.refresh_done()
        Clock.schedule_once(do_refresh, 1)

    def refresh_categories(self, *args):
        def do_refresh(interval):
            self.load_categories()
            self.ids.refresh_layout_categories.refresh_done()
        Clock.schedule_once(do_refresh, 1)

    def refresh_list(self, *args):
        def do_refresh(interval):
            self.load_cards(filter_category=self.current_filter)
            self.ids.refresh_layout_list.refresh_done()
        Clock.schedule_once(do_refresh, 1)

    def filter_and_switch(self, category_name):
        self.load_cards(filter_category=category_name)
        self.ids.bottom_nav.switch_tab('screen_gallery')

    def show_random_prompt(self):
        """
        NAYA FEATURE: "Surprise Me" - abhi jo gallery cards load/filter
        ho rakhe hain unme se ek random uthakar uska poora prompt dialog
        khol deta hai. Discovery ko thoda fun/engaging banane ke liye,
        pehle se maujood GalleryCard.show_prompt_dialog() hi reuse karta
        hai isliye koi naya dialog-logic risk nahi hai.
        """
        cards = list(self.ids.gallery_grid.children)
        if not cards:
            return
        random.choice(cards).show_prompt_dialog()

    def show_about_us(self):
        self.ids.nav_drawer.set_state("close")
        text = (
            "[b]Md Arman[/b]\n"
            "[i]Multimedia & Visual Content Designer[/i]\n\n"
            "AI Prompt Gallery was built to solve a simple problem: finding "
            "reliable, ready-to-use prompts for AI image generation shouldn't "
            "take hours of scrolling through scattered posts and forums.\n\n"
            "Every prompt in this app is hand-curated and tested across "
            "popular AI art tools, so you can go from idea to image in "
            "seconds instead of guessing what phrasing works.\n\n"
            "Md Arman is a Visual Content Designer with 4+ years of "
            "experience across cinematic editing, motion graphics, branding, "
            "and AI-powered creative workflows -- the same eye for detail "
            "that goes into every prompt curated here.\n\n"
            "New prompts and categories are added regularly, so there's "
            "always something fresh to explore."
        )
        self._open_custom_dialog("About Us", text, icon="star-four-points-outline")

    def show_contact_us(self):
        self.ids.nav_drawer.set_state("close")
        text = (
            "Questions, feedback, or a prompt request? I'd love to hear "
            "from you.\n\n"
            "[b]Email[/b]\narmaanfaiz02@gmail.com\n\n"
            "[b]Phone[/b]\n+91 7970529205\n\n"
            "[b]Location[/b]\nOkhla, New Delhi, 110025, India\n\n"
            "[b]Portfolio[/b]\nmd-arman.lovable.app\n\n"
            "Response time is usually within 1-2 business days."
        )
        self._open_custom_dialog("Contact Us", text, icon="email-outline", show_portfolio_btn=True)

    def open_portfolio(self):
        webbrowser.open("https://md-arman.lovable.app")
        if self.dialog:
            self.dialog.dismiss()

    def show_privacy_policy(self):
        self.ids.nav_drawer.set_state("close")
        text = (
            "Your privacy matters, and this policy explains exactly what "
            "happens (and doesn't happen) with your data.\n\n"
            "[b]Data We Collect[/b]\n"
            "AI Prompt Gallery does not require sign-up and does not collect "
            "any personally identifiable information such as your name, "
            "email, or phone number.\n\n"
            "[b]Advertising[/b]\n"
            "We use standard, industry-recognized ad networks to display "
            "ads. These networks may collect anonymous, non-personal usage "
            "data (such as device type or general region) to serve relevant "
            "ads, in line with their own privacy policies.\n\n"
            "[b]Permissions[/b]\n"
            "The app requests internet access only, used to fetch the "
            "latest prompts and images.\n\n"
            "[b]Your Rights[/b]\n"
            "Since no personal data is stored by this app, there is nothing "
            "to request, correct, or delete on our end. For questions, "
            "reach out via the Contact page.\n\n"
            "[b]Policy Updates[/b]\n"
            "This policy may be updated periodically. Continued use of the "
            "app after changes means you accept the revised policy.\n\n"
            "Tap below to read the complete, hosted Privacy Policy."
        )
        self._open_custom_dialog(
            "Privacy Policy", text, icon="shield-lock-outline",
            url="https://sites.google.com/view/your-privacy-policy-link-here",
        )

    def show_terms(self):
        self.ids.nav_drawer.set_state("close")
        text = (
            "By downloading or using AI Prompt Gallery, you agree to the "
            "following terms.\n\n"
            "[b]Use of Prompts[/b]\n"
            "Prompts in this app are provided for inspiration and personal "
            "use with AI art generation tools. You're free to copy, adapt, "
            "and use them in your own creative work, including commercially.\n\n"
            "[b]Intellectual Property[/b]\n"
            "The app's design, branding, curated categorization, and overall "
            "structure remain the property of Md Arman. Individual prompt "
            "text may be freely reused as described above.\n\n"
            "[b]Acceptable Use[/b]\n"
            "You agree not to use the app to generate or distribute illegal, "
            "harmful, or infringing content, or to attempt to disrupt or "
            "reverse-engineer the app itself.\n\n"
            "[b]No Warranty[/b]\n"
            "The app is provided \"as is.\" We work to keep content accurate "
            "and available, but can't guarantee uninterrupted access.\n\n"
            "[b]Changes to These Terms[/b]\n"
            "Terms may be updated from time to time. Continued use after an "
            "update means you accept the revised terms.\n\n"
            "Questions about these terms? Reach out via the Contact page."
        )
        self._open_custom_dialog("Terms of Use", text, icon="file-document-outline")

    def open_url(self, url):
        webbrowser.open(url)
        if self.dialog:
            self.dialog.dismiss()

    def _open_custom_dialog(self, title, text, icon="information-outline", show_portfolio_btn=False, url=None):
        buttons = [
            MDFlatButton(
                text="CLOSE",
                theme_text_color="Custom",
                text_color=self.theme_cls.primary_color,
                on_release=lambda x: self.dialog.dismiss()
            )
        ]
        
        if show_portfolio_btn:
            buttons.insert(0, MDFlatButton(
                text="VIEW PORTFOLIO",
                theme_text_color="Custom",
                text_color=self.theme_cls.primary_color,
                on_release=lambda x: self.open_portfolio()
            ))
            
        if url:
            buttons.insert(0, MDFlatButton(
                text="READ ONLINE",
                theme_text_color="Custom",
                text_color=self.theme_cls.primary_color,
                on_release=lambda x: self.open_url(url)
            ))

        self.dialog = MDDialog(
            type="custom",
            content_cls=InfoDialogContent(icon=icon, header_title=title, body_text=text),
            buttons=buttons,
        )
        self.dialog.open()
