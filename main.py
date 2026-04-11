from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle

# --- Core calculation functions ---
def generate_sequence_coeff(x, B, coeff):
    martingales = []
    cumulative = 0
    if x < 1 or x > B or coeff <= 1:
        return None
    martingales.append(x)
    cumulative += x
    while True:
        next_lot = martingales[-1] * coeff
        if cumulative + next_lot > B:
            break
        martingales.append(next_lot)
        cumulative += next_lot
    return martingales

def generate_sequence_percent(x, B, percent):
    martingales = []
    cumulative = 0
    if x < 1 or x > B:
        return None
    martingales.append(x)
    cumulative += x
    target_profit = x * (percent / 100.0)
    while True:
        required_win = cumulative + target_profit
        next_lot = required_win / (percent / 100.0)
        if cumulative + next_lot > B:
            break
        martingales.append(next_lot)
        cumulative += next_lot
    return martingales

def last_term(n):
    return 100 / (2 ** n)

# --- Kivy Layout ---
class MartingaleLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        self.mode = "coeff"

        # Inputs
        self.first_lot = self.make_input("First Lot ($)")
        self.balance = self.make_input("Balance ($)")

        # Dynamic input row: TextInput + button
        self.dynamic_input = self.make_input("Coefficient", text="2.1")
        self.switch_btn = Button(
            text="X",  # Default text
            font_size=146,
            size_hint=(None, 1),
            width=180,
            height=240,
            background_normal="",
            background_color=(0, 0, 0, 0),
            color=(0.2, 0.2, 0.2, 1)  # Gray text color
        )
        self.switch_btn.bind(on_press=self.switch_mode)

        # Custom rounded rectangle background
        with self.switch_btn.canvas.before:
            self.color = Color(0.3, 0.5, 0.8, 1)
            self.rect = RoundedRectangle(
                pos=self.switch_btn.pos,
                size=self.switch_btn.size,
                radius=[40]
            )
        self.switch_btn.bind(pos=self.update_rect, size=self.update_rect, state=self.update_color)

        row = BoxLayout(orientation="horizontal", size_hint_y=None, height=self.dynamic_input.height)
        row.add_widget(self.dynamic_input)
        row.add_widget(self.switch_btn)

        self.add_widget(self.first_lot)
        self.add_widget(self.balance)
        self.add_widget(row)

        # Bind instant calculation
        self.first_lot.bind(text=self.calculate)
        self.balance.bind(text=self.calculate)
        self.dynamic_input.bind(text=self.calculate)

        # Outputs
        sum_count_row = BoxLayout(orientation="horizontal", size_hint_y=0.8)

        sum_box = BoxLayout(orientation="vertical")
        self.result_sum_label = self.make_label("Sum:")
        self.result_sum_value = self.make_label("")
        sum_box.add_widget(self.result_sum_label)
        sum_box.add_widget(self.result_sum_value)

        count_box = BoxLayout(orientation="vertical")
        self.result_num_label = self.make_label("Count:")
        self.result_num_value = self.make_label("")
        count_box.add_widget(self.result_num_label)
        count_box.add_widget(self.result_num_value)

        sum_count_row.add_widget(sum_box)
        sum_count_row.add_widget(count_box)

        # Martingales section
        self.result_martingales_label = self.make_label("Martingales:")
        self.result_martingales_value = self.make_label("", size_hint_y=2.0)

        # Probability row
        self.result_prob_label = self.make_label("Probability:", size_hint_y=0.4)
        self.result_prob_value = self.make_label("", size_hint_y=0.4)

        # Add outputs
        self.add_widget(sum_count_row)
        self.add_widget(self.result_martingales_label)
        self.add_widget(self.result_martingales_value)
        self.add_widget(self.result_prob_label)
        self.add_widget(self.result_prob_value)

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def update_color(self, instance, value):
        if instance.state == "down":
            self.color.rgba = (0.2, 0.4, 0.6, 1)
        else:
            self.color.rgba = (0.3, 0.5, 0.8, 1)

    def switch_mode(self, instance):
        if self.mode == "coeff":
            self.mode = "percent"
            self.dynamic_input.hint_text = "Percent (%)"
            self.dynamic_input.text = "92"
            self.switch_btn.text = "%"
            self.switch_btn.color = (0.2, 0.2, 0.2, 1)  # Gray text color
        else:
            self.mode = "coeff"
            self.dynamic_input.hint_text = "Coefficient"
            self.dynamic_input.text = "2.1"
            self.switch_btn.text = "X"
            self.switch_btn.color = (0.2, 0.2, 0.2, 1)  # Gray text color
        self.calculate()

    def make_input(self, hint, text=""):
        inp = TextInput(
            hint_text=hint,
            text=text,
            multiline=False,
            halign="center",
            font_size=103,
            background_color=(0.2, 0.2, 0.2, 1),
            foreground_color=(1, 1, 1, 1),
            size_hint_y=None,
            height=240
        )
        inp.bind(size=lambda inst, val: setattr(inst, "padding_y",
                     [(inst.height - inst.line_height) / 2, 0]))
        return inp

    def make_label(self, text, size_hint_y=0.8):
        lbl = Label(
            text=text,
            halign="center",
            valign="middle",
            color=(1, 1, 1, 1),
            font_size=103,
            size_hint_y=size_hint_y
        )
        lbl.bind(size=lambda inst, val: setattr(inst, "text_size", inst.size))
        return lbl

    def calculate(self, *args):
        try:
            a = float(self.first_lot.text)
            B = float(self.balance.text)
            val = float(self.dynamic_input.text)

            if self.mode == "coeff":
                sequence = generate_sequence_coeff(a, B, val)
            else:
                sequence = generate_sequence_percent(a, B, val)

            if sequence is None:
                self.result_martingales_value.text = "Invalid input"
                self.result_sum_value.text = ""
                self.result_num_value.text = ""
                self.result_prob_value.text = ""
                return

            martingales = [f"{val:.2f}" for val in sequence]
            sum_martingale = round(sum(sequence), 2)
            num_martingale = len(sequence)
            prob = round(last_term(num_martingale), 3)

            self.result_martingales_value.text = "  ".join(martingales)
            self.result_sum_value.text = str(sum_martingale)
            self.result_num_value.text = str(num_martingale)
            self.result_prob_value.text = f"{num_martingale}-th time: {prob}%"

        except ValueError:
            self.result_martingales_value.text = ""
            self.result_sum_value.text = ""
            self.result_num_value.text = ""
            self.result_prob_value.text = ""

# --- App Runner ---
class MartingaleApp(App):
    def build(self):
        return MartingaleLayout()

if __name__ == "__main__":
    MartingaleApp().run()
    
    
