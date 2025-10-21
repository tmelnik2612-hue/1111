"""
XT-ScalperPro Kivy Mobile App
Simplified version for Android compatibility
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
import threading
import os

class ScalperProApp(App):
    def build(self):
        self.title = "XT-ScalperPro"
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        layout.add_widget(Label(
            text='🤖 XT-ScalperPro Mobile\nAndroid Trading Bot',
            size_hint=(1, 0.2),
            font_size='20sp',
            color=(0, 1, 0, 1),
            halign='center'
        ))
        
        info_text = (
            'This is the mobile version of XT-ScalperPro.\n\n'
            'To use the full web interface:\n'
            '1. Make sure XT_API_KEY and XT_API_SECRET are set\n'
            '2. Run: python main.py\n'
            '3. Access the bot at http://localhost:5000\n\n'
            'For Android, configure your API keys in the environment\n'
            'or use a configuration file before building the APK.'
        )
        
        layout.add_widget(Label(
            text=info_text,
            size_hint=(1, 0.6),
            font_size='14sp',
            halign='center'
        ))
        
        config_btn = Button(
            text='📋 View Configuration Guide',
            size_hint=(1, 0.1),
            background_color=(0.2, 0.6, 1, 1)
        )
        config_btn.bind(on_press=self.show_config)
        layout.add_widget(config_btn)
        
        exit_btn = Button(
            text='❌ Exit',
            size_hint=(1, 0.1),
            background_color=(1, 0.2, 0.2, 1)
        )
        exit_btn.bind(on_press=self.stop_app)
        layout.add_widget(exit_btn)
        
        return layout
    
    def show_config(self, instance):
        """Show configuration information"""
        print("Configuration Guide:")
        print("1. Set XT_API_KEY environment variable")
        print("2. Set XT_API_SECRET environment variable")
        print("3. Configure signal mode: ULTRA, SAFE, or HYBRID")
        print("4. Set SL method (1-8)")
        print("5. Run the bot via python main.py")
    
    def stop_app(self, instance):
        """Stop the application"""
        self.stop()

if __name__ == '__main__':
    ScalperProApp().run()
