from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.core.window import Window

# Dictionaries for values
color_band_values = {
    'Black': 0, 'Brown': 1, 'Red': 2, 'Orange': 3, 'Yellow': 4,
    'Green': 5, 'Blue': 6, 'Violet': 7, 'Gray': 8, 'White': 9
}

color_multipliers = {
    'Black': 1, 'Brown': 10, 'Red': 100, 'Orange': 1000, 'Yellow': 10000,
    'Green': 100000, 'Blue': 1000000, 'Violet': 10000000, 'Gray': 100000000, 'White': 1000000000
}

color_tolerance = {
    'Brown': 1, 'Red': 2, 'Green': 0.5, 'Blue': 0.25, 'Violet': 0.1, 'Gray': 0.05, 'Gold': 5, 'Silver': 10
}

color_map = {
    'Black': (0, 0, 0, 1), 'Brown': (0.6, 0.3, 0, 1), 'Red': (1, 0, 0, 1),
    'Orange': (1, 0.5, 0, 1), 'Yellow': (1, 1, 0, 1), 'Green': (0, 1, 0, 1),
    'Blue': (0, 0, 1, 1), 'Violet': (0.6, 0, 1, 1), 'Gray': (0.5, 0.5, 0.5, 1),
    'White': (1, 1, 1, 1), 'Gold': (1, 0.84, 0, 1), 'Silver': (0.75, 0.75, 0.75, 1)
}

class BandButton(Button):
    def __init__(self, app, band_index, is_tolerance=False, **kwargs):
        super().__init__(**kwargs)
        self.band_index = band_index
        self.app = app
        self.is_tolerance = is_tolerance
        self.text = f'Band {band_index + 1}' if not is_tolerance else 'Tolerance'
        self.background_color = (1, 1, 1, 1)
        self.bind(on_press=self.open_color_selection)

    def open_color_selection(self, instance):
        # Create a Popup to select the color
        popup_layout = GridLayout(cols=2, spacing=10, padding=10)
        if self.is_tolerance:
            for color_name in color_tolerance.keys():
                color_btn = Button(text=color_name, background_color=color_map[color_name])
                color_btn.bind(on_press=self.select_color)
                popup_layout.add_widget(color_btn)
        else:
            for color_name in color_band_values.keys():
                color_btn = Button(text=color_name, background_color=color_map[color_name])
                color_btn.bind(on_press=self.select_color)
                popup_layout.add_widget(color_btn)
        self.popup = Popup(title='Select a color', content=popup_layout, size_hint=(0.8, 0.8))
        self.popup.open()

    def select_color(self, instance):
        selected_color = instance.text
        self.background_color = color_map[selected_color]
        self.text = selected_color
        self.popup.dismiss()
        # Store the selected color in the main application
        if self.is_tolerance:
            self.app.selected_tolerance = selected_color
        else:
            self.app.selected_colors[self.band_index] = selected_color

class ResistorApp(App):
    def build(self):
        self.icon = 'resistor.ico'
        # Set window size
        Window.size = (600, 600)

        # Initialize selected colors
        self.selected_colors = [None, None, None]
        self.selected_tolerance = None

        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        # Layout for resistor bands
        resistor_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.6), spacing=10)
        self.band_buttons = []
        for i in range(3):
            band_button = BandButton(app=self, band_index=i)
            self.band_buttons.append(band_button)
            resistor_layout.add_widget(band_button)

        # Button for tolerance band
        tolerance_button = BandButton(app=self, band_index=3, is_tolerance=True)
        resistor_layout.add_widget(tolerance_button)

        # Calculate button
        calculate_button = Button(text='Calculate', size_hint=(1, 0.1))
        calculate_button.bind(on_press=self.calculate_resistance)

        # Label to display the result
        self.result_label = Label(text='Resistance value: ', font_size=20, size_hint=(1, 0.2))
        
        # New label to display additional text
        self.extra_label = Label(text='', font_size=20, size_hint=(1, 0.2))

        main_layout.add_widget(resistor_layout)
        main_layout.add_widget(calculate_button)
        main_layout.add_widget(self.result_label)
        main_layout.add_widget(self.extra_label)

        return main_layout

    def calculate_resistance(self, instance):
        if None in self.selected_colors or self.selected_tolerance is None:
            self.result_label.text = 'Please select the 3 colors and tolerance.'
            return

        # Get band values
        value1 = color_band_values[self.selected_colors[0]]
        value2 = color_band_values[self.selected_colors[1]]
        multiplier = color_multipliers[self.selected_colors[2]]
        tolerance = color_tolerance[self.selected_tolerance]

        # Calculate resistance
        resistance_value = (value1 * 10 + value2) * multiplier
        tolerance_value = resistance_value * (tolerance / 100)
        
         # Determine prefix based on multiplier
        if self.selected_colors[2] in ["Orange", "Yellow", "Green"]:
            prefix = "K"
            div = 1000
        elif self.selected_colors[2] in ["Blue", "Violet", "Gray"]:
            prefix = "M"
            div = 1000000
        elif self.selected_colors[2] == "White":
            prefix = "G"
            div = 1000000000
        else:
            prefix = ""
            div = 1

        # Adjust resistance and tolerance values
        resistance_value_with_prefix = resistance_value // div
        tolerance_value_with_prefix = tolerance_value // div
        max_ohms = (resistance_value + tolerance_value) // div
        min_ohms = (resistance_value - tolerance_value) // div

        # Show result with tolerance and prefix
        self.result_label.text = (f'Resistance value: {resistance_value_with_prefix} {prefix} ohms ± '
                                  f'{tolerance_value_with_prefix} {prefix} ohms ({tolerance}%)')

        # Show additional text below
        self.extra_label.text = (f'Max: {max_ohms} {prefix}\nMin: {min_ohms} {prefix}')

if __name__ == '__main__':
    ResistorApp().run()
