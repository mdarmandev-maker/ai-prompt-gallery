from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from screens.main_screen import MainScreen
from kivy.core.window import Window

# Set the window size to simulate a mobile phone (e.g., iPhone/Pixel aspect ratio)
#Window.size = (360, 740)

class AIPromptGalleryApp(MDApp):
    def build(self):
        # Configure Modern Dark Theme
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.material_style = "M3"
        
        # Setup Screen Manager with smooth transitions
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(MainScreen(name='main'))
        
        return sm

if __name__ == '__main__':
    AIPromptGalleryApp().run()
    
