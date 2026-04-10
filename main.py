from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

# --- Core calculation functions ---
def generate_sequence(x, B, percent):
    martingales = []
    cumulative = 0

    # Validation
    if x < 1 or x > B:
        return None

    # First lot
    martingales.append(x)
    cumulative += x

    # Hypothetical first win profit
    target_profit = x * (percent / 100.0)

    while True:
        # Next lot must cover all previous losses + target profit
        required_win = cumulative + target_profit
        next_lot = required_win / (percent / 100.0)

        # Check balance
        if cumulative + next_lot > B:
            break

        martingales.append(next_lot)
        cumulative += next_lot

    return martingales

def last_term(n):
    return 100 / (2 ** n)

# --- Kivy Layout ---
class MartingaleLayout(BoxLayout):
    def __init__(self, **kwargs):   # ✅ fixed
        super().__init__(orientation="vertical", **kwargs)

        # --- Input fields ---
        self.first_lot = self.make_input("First Lot ($)")
        self.balance = self.make_input("Balance ($)")
        self.percent = self.make_input("Percent (%)", text="92")

        # Bind instant calculation
        self.first_lot.bind(text=self.calculate)
        self.balance.bind(text=self.calculate)
        self.percent.bind(text=self.calculate)

        # Add inputs
        self.add_widget(self.first_lot)
        self.add_widget(self.balance)
        self.add_widget(self.percent)

        # --- Output labels ---
        self.result_martingales_label = self.make_label("Martingales:")
        self.result_martingales_value = self.make_label("", size_hint_y=2.0)

        self.result_sum_label = self.make_label("Sum:")
        self.result_sum_value = self.make_label("")
        self.result_num_label = self.make_label("Count:")
        self.result_num_value = self.make_label("")
        self.result_prob_label = self.make_label("Probability:")
        self.result_prob_value = self.make_label("")

        # Vertical sizing
        self.result_martingales_label.size_hint_y = 1.0
        self.result_martingales_value.size_hint_y = 2.0
        for lbl in [
            self.result_sum_label, self.result_sum_value,
            self.result_num_label, self.result_num_value,
            self.result_prob_label, self.result_prob_value
        ]:
            lbl.size_hint_y = 0.8

        # Add outputs
        self.add_widget(self.result_martingales_label)
        self.add_widget(self.result_martingales_value)
        self.add_widget(self.result_sum_label)
        self.add_widget(self.result_sum_value)
        self.add_widget(self.result_num_label)
        self.add_widget(self.result_num_value)
        self.add_widget(self.result_prob_label)
        self.add_widget(self.result_prob_value)

    def make_input(self, hint, text=""):
        inp = TextInput(
            hint_text=hint,
            text=text,
            multiline=False,
            halign="center",
            font_size=86,
            background_color=(0.2, 0.2, 0.2, 1),
            foreground_color=(1, 1, 1, 1),
        )
        # Center text vertically
        inp.bind(size=lambda inst, val: setattr(inst, "padding_y",
                     [(inst.height - inst.line_height) / 2, 0]))
        return inp

    def make_label(self, text, size_hint_y=0.8):
        lbl = Label(
            text=text,
            halign="center",
            valign="middle",
            color=(1, 1, 1, 1),
            font_size=86,
            size_hint_y=size_hint_y
        )
        # Ensure valign works by setting text_size
        lbl.bind(size=lambda inst, val: setattr(inst, "text_size", inst.size))
        return lbl

    def calculate(self, *args):
        try:
            a = float(self.first_lot.text)
            B = float(self.balance.text)
            y = float(self.percent.text) if self.percent.text else 92

            sequence = generate_sequence(a, B, y)
            
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

            # Display results
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
    
