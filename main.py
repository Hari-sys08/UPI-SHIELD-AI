
from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
import re, json, os, random
from datetime import datetime

APP_NAME = "UPI SHIELD"
BG = "#081321"
PANEL = "#101F31"
PANEL2 = "#14283D"
TEAL = "#22D3B6"
WHITE = "#F4F8FC"
MUTED = "#9BAFC2"
RED = "#FF6377"
AMBER = "#FFBE5C"
GREEN = "#43D6A3"

Window.clearcolor = get_color_from_hex(BG)

def label(text, size=15, color=WHITE, bold=False, **kwargs):
    return Label(text=text, font_size=dp(size), color=get_color_from_hex(color),
                 bold=bold, halign="left", valign="middle",
                 **kwargs)

class Card(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(16)
        self.spacing = dp(8)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter("height"))
        with self.canvas.before:
            Color(*get_color_from_hex(PANEL))
            self.bg = RoundedRectangle(radius=[dp(18)])
        self.bind(pos=self._paint, size=self._paint)
    def _paint(self, *_):
        self.bg.pos = self.pos
        self.bg.size = self.size

class ActionButton(Button):
    def __init__(self, text, on_press=None, primary=False, **kwargs):
        super().__init__(text=text, **kwargs)
        self.size_hint_y = None
        self.height = dp(48)
        self.font_size = dp(14)
        self.bold = True
        self.background_normal = ""
        self.background_down = ""
        self.background_color = get_color_from_hex(TEAL if primary else PANEL2)
        self.color = get_color_from_hex(BG if primary else WHITE)
        if on_press:
            self.bind(on_release=on_press)

class BaseScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.page = BoxLayout(orientation="vertical", padding=[dp(18), dp(12)], spacing=dp(12))
        self.add_widget(self.page)
        self.add_header()
    def add_header(self):
        top = BoxLayout(size_hint_y=None, height=dp(44))
        top.add_widget(label("◈  UPI SHIELD", 17, TEAL, True))
        top.add_widget(label("AI • SAFETY", 10, MUTED, True, halign="right"))
        self.page.add_widget(top)
    def body(self):
        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", spacing=dp(12), size_hint_y=None)
        content.bind(minimum_height=content.setter("height"))
        scroll.add_widget(content)
        self.page.add_widget(scroll)
        return content
    def add_bottom(self):
        nav = GridLayout(cols=4, spacing=dp(6), size_hint_y=None, height=dp(52))
        for title, target in [("HOME","home"),("SCAN","scan"),("QR","qr"),("LEARN","learn")]:
            b = Button(text=title, font_size=dp(10), bold=True, background_normal="", background_color=get_color_from_hex(PANEL2), color=get_color_from_hex(TEAL))
            b.bind(on_release=lambda _, t=target: setattr(self.manager, "current", t))
            nav.add_widget(b)
        self.page.add_widget(nav)

class HomeScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        c = self.body()
        hero = Card()
        hero.add_widget(label("YOUR DIGITAL BODYGUARD", 10, TEAL, True))
        hero.add_widget(label("Pause. Check.\nPay safely.", 29, WHITE, True, size_hint_y=None, height=dp(88)))
        hero.add_widget(label("Spot suspicious UPI requests before they spot you.", 13, MUTED, size_hint_y=None, height=dp(42)))
        hero.add_widget(ActionButton("CHECK A MESSAGE  →", lambda *_: setattr(self.manager, "current", "scan"), True))
        c.add_widget(hero)
        stats = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(92))
        for number, caption in [("01","SMART CHECKS"),("24/7","STAY ALERT")]:
            card = Card()
            card.add_widget(label(number, 23, TEAL, True))
            card.add_widget(label(caption, 10, MUTED, True))
            stats.add_widget(card)
        c.add_widget(stats)
        c.add_widget(label("PROTECTION TOOLS", 12, MUTED, True, size_hint_y=None, height=dp(24)))
        for title, desc, target in [
            ("Message scanner","Check SMS, WhatsApp and payment requests","scan"),
            ("UPI QR inspector","Inspect a UPI payment link before opening","qr"),
            ("UPI safety school","Learn the red flags in a few minutes","learn"),
            ("Shield challenge","Test your scam-spotting instincts","quiz")]:
            card = Card()
            card.add_widget(label(title, 16, WHITE, True))
            card.add_widget(label(desc, 11, MUTED))
            card.add_widget(ActionButton("OPEN  →", lambda _, t=target: setattr(self.manager, "current", t)))
            c.add_widget(card)
        self.add_bottom()

class ScanScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        c = self.body()
        c.add_widget(label("MESSAGE SCANNER", 23, WHITE, True, size_hint_y=None, height=dp(36)))
        c.add_widget(label("Paste a suspicious SMS, WhatsApp message or payment request.", 12, MUTED, size_hint_y=None, height=dp(42)))
        self.input = TextInput(hint_text="Example: Your account will be blocked. Share OTP now...", multiline=True, size_hint_y=None, height=dp(150), padding=dp(12), background_color=get_color_from_hex(PANEL2), foreground_color=get_color_from_hex(WHITE), hint_text_color=get_color_from_hex(MUTED), cursor_color=get_color_from_hex(TEAL))
        c.add_widget(self.input)
        c.add_widget(ActionButton("ANALYSE MESSAGE", self.analyse, True))
        self.result = Card()
        self.result.add_widget(label("YOUR RESULT WILL APPEAR HERE", 12, MUTED, True))
        c.add_widget(self.result)
        c.add_widget(label("Checks for urgency, OTP/PIN requests, suspicious links, KYC threats and fake rewards. This is an educational indicator, not a guarantee.", 10, MUTED))
        self.add_bottom()
    def analyse(self, *_):
        text = self.input.text.strip().lower()
        if not text:
            self.result.clear_widgets()
            self.result.add_widget(label("Paste a message first.", 14, AMBER, True))
            return
        rules = [
            (r"\b(otp|one.time.password|verification code)\b", 28, "OTP / verification-code language"),
            (r"\b(pin|upi pin|mpin|password)\b", 28, "PIN or password mentioned"),
            (r"\b(urgent|immediately|within \d+ hours|blocked|suspend|deactivate)\b", 18, "Pressure or account-threat language"),
            (r"\b(kyc|re.?verify|update your account)\b", 14, "KYC / account-update request"),
            (r"\b(cashback|prize|won|reward|lottery|free gift)\b", 12, "Unexpected reward language"),
            (r"(https?://|bit\.ly|tinyurl|\.xyz\b)", 18, "Link or shortened URL detected"),
            (r"\b(customer care|helpline|support number|call this number)\b", 10, "Support / callback language"),
            (r"\b(collect request|approve request|receive money|scan to get)\b", 22, "Potential collect-request trick"),
        ]
        score, hits = 0, []
        for pattern, points, why in rules:
            if re.search(pattern, text):
                score += points
                hits.append(why)
        score = min(score, 100)
        if score >= 61:
            level, color, advice = "HIGH RISK", RED, "Do not click, call, scan or approve. Verify independently using your bank's official app."
        elif score >= 31:
            level, color, advice = "CAUTION", AMBER, "Pause and verify the sender through an official channel before acting."
        else:
            level, color, advice = "LOW SIGNAL", GREEN, "No strong red flags matched. Still verify the payee and amount in your UPI app."
        self.result.clear_widgets()
        self.result.add_widget(label("RISK INDICATOR", 10, MUTED, True))
        self.result.add_widget(label(f"{score}/100  •  {level}", 23, color, True))
        self.result.add_widget(label(advice, 12, WHITE))
        self.result.add_widget(label("SIGNALS FOUND", 10, TEAL, True))
        for hit in (hits or ["No configured red flags matched."]):
            self.result.add_widget(label("• " + hit, 11, MUTED))
        self.result.add_widget(label("Rule-based demo only — not bank-grade AI.", 9, MUTED))

class QRScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        c = self.body()
        c.add_widget(label("UPI LINK INSPECTOR", 22, WHITE, True, size_hint_y=None, height=dp(36)))
        c.add_widget(label("Paste the decoded UPI URI (for example, upi://pay?...). Never pay from an untrusted QR.", 12, MUTED, size_hint_y=None, height=dp(52)))
        self.uri = TextInput(hint_text="upi://pay?pa=merchant@upi&pn=Store&am=100", multiline=True, size_hint_y=None, height=dp(110), padding=dp(12), background_color=get_color_from_hex(PANEL2), foreground_color=get_color_from_hex(WHITE), hint_text_color=get_color_from_hex(MUTED))
        c.add_widget(self.uri)
        c.add_widget(ActionButton("INSPECT UPI URI", self.inspect, True))
        self.out = Card()
        self.out.add_widget(label("PAYEE DETAILS WILL APPEAR HERE", 11, MUTED, True))
        c.add_widget(self.out)
        c.add_widget(label("Camera QR scanning is not enabled in this starter build. Use a trusted QR scanner to decode, then paste the URI here.", 10, MUTED))
        self.add_bottom()
    def inspect(self, *_):
        from urllib.parse import urlparse, parse_qs
        raw = self.uri.text.strip()
        self.out.clear_widgets()
        if not raw.lower().startswith("upi://pay"):
            self.out.add_widget(label("Not a recognised upi://pay URI.", 14, RED, True))
            return
        q = parse_qs(urlparse(raw).query)
        payee = q.get("pn", ["Not provided"])[0]
        vpa = q.get("pa", ["Not provided"])[0]
        amount = q.get("am", ["Not specified"])[0]
        note = q.get("tn", [""])[0]
        risk = []
        if vpa == "Not provided" or "@" not in vpa: risk.append("Payee address is missing or unusual.")
        if amount != "Not specified":
            try:
                if float(amount) <= 0: risk.append("Amount is zero or negative.")
            except ValueError: risk.append("Amount format is unusual.")
        if not risk: risk.append("Basic URI structure looks readable; this does NOT prove the payee is trustworthy.")
        self.out.add_widget(label("PAYEE NAME", 10, MUTED, True))
        self.out.add_widget(label(payee, 17, WHITE, True))
        self.out.add_widget(label("UPI ID", 10, MUTED, True))
        self.out.add_widget(label(vpa, 14, TEAL))
        self.out.add_widget(label("AMOUNT", 10, MUTED, True))
        self.out.add_widget(label("₹" + amount if amount != "Not specified" else amount, 17, WHITE, True))
        if note: self.out.add_widget(label("NOTE: " + note, 11, MUTED))
        self.out.add_widget(label("SAFETY NOTES", 10, AMBER, True))
        for item in risk: self.out.add_widget(label("• " + item, 11, MUTED))

class LearnScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        c = self.body()
        c.add_widget(label("THE SHIELD PLAYBOOK", 22, WHITE, True, size_hint_y=None, height=dp(36)))
        lessons = [
            ("01  OTPs stay private","Never share an OTP, UPI PIN or screen-sharing access — not even with someone claiming to be bank staff."),
            ("02  You don't enter a PIN to receive","A UPI PIN authorises a debit. You do not need to enter it to receive money."),
            ("03  QR codes are not magic","Scanning a QR or approving a collect request can lead to a payment. Check the payee and amount."),
            ("04  Don't trust caller ID","Disconnect and find the official bank number yourself. Never call numbers sent by strangers."),
            ("05  Urgency is a red flag","Threats about account blocking, KYC expiry or instant rewards are common pressure tactics."),
            ("06  If money is lost","Contact your bank immediately and report cyber financial fraud at 1930 / cybercrime.gov.in.")
        ]
        for title, body in lessons:
            card = Card()
            card.add_widget(label(title, 15, TEAL, True))
            card.add_widget(label(body, 12, MUTED))
            c.add_widget(card)
        self.add_bottom()

class QuizScreen(BaseScreen):
    QUESTIONS = [
        ("Someone says you must enter your UPI PIN to receive a refund. What do you do?", ["Enter it","Refuse; PIN authorises payment","Share OTP instead"], 1, "A UPI PIN is used to authorise a debit, not to receive money."),
        ("A stranger sends a QR code for a prize. Safest action?", ["Scan and approve","Share your PIN","Do not scan; verify independently"], 2, "Unexpected prize QR codes can lead to payment requests."),
        ("A caller asks for your OTP to stop account closure.", ["Share quickly","Hang up and contact official support","Send a screenshot"], 1, "Banks do not need your OTP or PIN over a call."),
        ("Before paying a shop by UPI, you should:", ["Check payee name and amount","Trust the QR sticker","Ignore the amount"], 0, "Always verify the payee and amount on your own UPI app.")
    ]
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.index = 0
        self.score = 0
        c = self.body()
        c.add_widget(label("SHIELD CHALLENGE", 22, WHITE, True, size_hint_y=None, height=dp(36)))
        self.progress = label("", 11, TEAL, True, size_hint_y=None, height=dp(24))
        c.add_widget(self.progress)
        self.question = Card()
        c.add_widget(self.question)
        self.options = BoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None)
        self.options.bind(minimum_height=self.options.setter("height"))
        c.add_widget(self.options)
        self.feedback = label("", 12, AMBER, size_hint_y=None, height=dp(60))
        c.add_widget(self.feedback)
        self.next_btn = ActionButton("NEXT QUESTION  →", self.next_q, True)
        c.add_widget(self.next_btn)
        self.render()
        self.add_bottom()
    def render(self):
        self.progress.text = f"QUESTION {self.index+1} OF {len(self.QUESTIONS)}   •   SCORE {self.score}"
        self.question.clear_widgets()
        self.question.add_widget(label(self.QUESTIONS[self.index][0], 16, WHITE, True))
        self.options.clear_widgets()
        self.feedback.text = ""
        for i, option in enumerate(self.QUESTIONS[self.index][1]):
            self.options.add_widget(ActionButton(option, lambda _, n=i: self.answer(n)))
        self.next_btn.text = "FINISH  →" if self.index == len(self.QUESTIONS)-1 else "NEXT QUESTION  →"
    def answer(self, n):
        q = self.QUESTIONS[self.index]
        self.options.clear_widgets()
        if n == q[2]:
            self.score += 1
            self.feedback.text = "✓ Correct. " + q[3]
            self.feedback.color = get_color_from_hex(GREEN)
        else:
            self.feedback.text = "Not quite. " + q[3]
            self.feedback.color = get_color_from_hex(AMBER)
        for i, option in enumerate(q[1]):
            self.options.add_widget(label(("✓ " if i == q[2] else "• ") + option, 12, GREEN if i == q[2] else MUTED))
    def next_q(self, *_):
        if self.index == len(self.QUESTIONS)-1:
            self.question.clear_widgets()
            self.question.add_widget(label(f"YOU SCORED {self.score}/{len(self.QUESTIONS)}", 22, TEAL, True))
            self.options.clear_widgets()
            self.feedback.text = "Keep your guard up. Verify every payment."
            self.next_btn.text = "PLAY AGAIN"
            self.index = -1
            return
        if self.index == -1:
            self.index = 0
            self.score = 0
        else:
            self.index += 1
        self.render()

class ShieldApp(App):
    def build(self):
        self.title = APP_NAME
        sm = ScreenManager(transition=FadeTransition(duration=.15))
        for name, cls in [("home",HomeScreen),("scan",ScanScreen),("qr",QRScreen),("learn",LearnScreen),("quiz",QuizScreen)]:
            sm.add_widget(cls(name=name))
        return sm

if __name__ == "__main__":
    ShieldApp().run()
