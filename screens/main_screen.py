
from kivy.lang import Builder
from kivymd.uix.screen import MDScreen
from widgets.prompt_card import PromptCard
from widgets.gallery_card import GalleryCard
from utils.json_manager import load_prompts
from kivy.clock import Clock
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.list import OneLineListItem
from kivy.graphics.texture import Texture
from kivy.graphics import Rectangle, Color
from kivy.animation import Animation  # Splash Screen animation ke liye
import webbrowser

Builder.load_file('screens/main_screen.kv')

class MainScreen(MDScreen):
    dialog = None
    current_filter = "All"
    card_loading_event = None
    gradient_rect = None 

    def on_enter(self):
        self.apply_gradient()
        # Data turant load karne ke bajaye, Splash screen ka timer start karo (2.5 seconds)
        Clock.schedule_once(self.start_splash_transition, 2.5)

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

    def apply_gradient(self):
        container = self.ids.top_bar_container
        
        texture = Texture.create(size=(2, 1), colorfmt='rgba')
        buf = bytes([26, 0, 51, 255,   75, 0, 130, 255])
        texture.blit_buffer(buf, colorfmt='rgba', bufferfmt='ubyte')
        
        with container.canvas.before:
            Color(1, 1, 1, 1) 
            self.gradient_rect = Rectangle(pos=container.pos, size=container.size, texture=texture)
            
        container.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, instance, value):
        if self.gradient_rect:
            self.gradient_rect.pos = instance.pos
            self.gradient_rect.size = instance.size

    def load_initial_data(self, dt):
        self.load_categories()
        self.load_cards(filter_category="All")

    def load_categories(self):
        self.ids.category_list.clear_widgets()
        prompts = load_prompts()
        
        categories = set(item.get("category", "General") for item in prompts if item.get("category"))
        
        item_all = OneLineListItem(
            text="[b]All Categories[/b]", 
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            bg_color=(0.25, 0.25, 0.25, 1),
            divider="Full",
            on_release=lambda x: self.filter_and_switch("All")
        )
        item_all.ids._lbl_primary.markup = True 
        self.ids.category_list.add_widget(item_all)

        for cat in sorted(categories):
            item = OneLineListItem(
                text=f"[b]{cat}[/b]", 
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                bg_color=(0.15, 0.15, 0.15, 1),
                divider="Full",
                on_release=lambda x, selected_cat=cat: self.filter_and_switch(selected_cat)
            )
            item.ids._lbl_primary.markup = True 
            self.ids.category_list.add_widget(item)

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

    def filter_and_switch(self, category_name):
        self.load_cards(filter_category=category_name)
        self.ids.bottom_nav.switch_tab('screen_gallery')

    # Professional Dialog Handlers based on CV
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