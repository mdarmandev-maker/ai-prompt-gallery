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
from kivy.animation import Animation  
from kivy.properties import ListProperty, NumericProperty
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
''')

Builder.load_file('screens/main_screen.kv')


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

    def load_cards(self, filter_category):
        self.current_filter = filter_category
        self.ids.prompt_list.clear_widgets()
        self.ids.gallery_grid.clear_widgets()
        
        self.update_top_bar()
        
        if self.card_loading_event:
            self.card_loading_event.cancel()
        
        prompts = load_prompts()
        
        self.filtered_prompts = [
            item for item in prompts 
            if filter_category == "All" or item.get("category", "General") == filter_category
        ]
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
            "A creative and results-driven Visual Content Designer (AI Specialist) with 4+ years of experience delivering high-impact visual content for brands, media houses, and digital platforms.\n\n"
            "Expert in cinematic video editing, motion graphics, branding, and AI-powered creative workflows. Known for transforming ideas into premium, scroll-stopping visuals."
        )
        self._open_custom_dialog("About The Creator", text)

    def show_contact_us(self):
        self.ids.nav_drawer.set_state("close")
        text = (
            "[b]Let's Connect & Collaborate[/b]\n\n"
            "[b]Email:[/b] armaanfaiz02@gmail.com\n"
            "[b]Phone:[/b] +91 7970529205\n"
            "[b]Location:[/b] Okhla, New Delhi, 110025\n\n"
            "[b]Portfolio:[/b] md-arman.lovable.app"
        )
        self._open_custom_dialog("Contact Details", text, show_portfolio_btn=True)

    def open_portfolio(self):
        webbrowser.open("https://md-arman.lovable.app")
        if self.dialog:
            self.dialog.dismiss()

    def show_privacy_policy(self):
        self.ids.nav_drawer.set_state("close")
        text = (
            "[b]Privacy Policy[/b]\n\n"
            "We value your privacy. The AI Prompt Gallery app does not collect any personal user data. We use standard ad networks which may collect anonymous usage data to serve personalized ads.\n\n"
            "Please click the button below to read our complete Privacy Policy."
        )
        self._open_custom_dialog("Privacy Policy", text, url="https://sites.google.com/view/your-privacy-policy-link-here")

    def show_terms(self):
        self.ids.nav_drawer.set_state("close")
        text = (
            "[b]Terms & Conditions[/b]\n\n"
            "By using the AI Prompt Gallery, you agree to utilize the provided prompts and visual designs respectfully.\n\n"
            "The prompts curated in this application are designed for inspiration and AI art generation. While you are free to copy and use them, the overarching app structure, branding, and proprietary assets remain the intellectual property of Md Arman (Visual Content Designer)."
        )
        self._open_custom_dialog("Terms of Use", text)

    def open_url(self, url):
        webbrowser.open(url)
        if self.dialog:
            self.dialog.dismiss()

    def _open_custom_dialog(self, title, text, show_portfolio_btn=False, url=None):
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
            title=title,
            text=text,
            buttons=buttons,
        )
        self.dialog.ids.text.markup = True
        self.dialog.open()
