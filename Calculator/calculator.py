"""
Elegant Calculator — Python / Tkinter
Run with: python3 calculator.py
Requires: Python 3.8+ with tkinter (included in standard Python installs)
"""

import tkinter as tk
from tkinter import font as tkfont

# ── Palette ────────────────────────────────────────────────────────────────────
BG          = "#1a1a1e"
DISPLAY_BG  = "#111115"
DISPLAY_FG  = "#ffffff"
EXPR_FG     = "#555566"

NUM_BG      = "#2a2a30"
NUM_FG      = "#f0f0f5"
NUM_ACTIVE  = "#36363e"

OP_BG       = "#2d2440"
OP_FG       = "#c4b5fd"
OP_ACTIVE   = "#3a2f55"

FN_BG       = "#1e2e28"
FN_FG       = "#6ee7b7"
FN_ACTIVE   = "#253d34"

EQ_BG       = "#7c3aed"
EQ_FG       = "#ffffff"
EQ_ACTIVE   = "#6d28d9"

CLR_BG      = "#2e1f1f"
CLR_FG      = "#f87171"
CLR_ACTIVE  = "#3d2828"


class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculator")
        self.resizable(False, False)
        self.configure(bg=BG)

        # State
        self.cur        = "0"
        self.prev       = ""
        self.op         = ""
        self.just_evaled = False

        self._build_fonts()
        self._build_display()
        self._build_keypad()
        self._bind_keys()

        self.update_display()

    # ── Fonts ──────────────────────────────────────────────────────────────────
    def _build_fonts(self):
        self.font_result = tkfont.Font(family="Courier New", size=36, weight="normal")
        self.font_expr   = tkfont.Font(family="Courier New", size=12, weight="normal")
        self.font_btn    = tkfont.Font(family="Courier New", size=17, weight="normal")
        self.font_btn_sm = tkfont.Font(family="Courier New", size=13, weight="normal")
        self.font_label  = tkfont.Font(family="Georgia",     size=9,  weight="normal")

    # ── Display ────────────────────────────────────────────────────────────────
    def _build_display(self):
        # Subtle top label
        lbl = tk.Label(self, text="C A L C U L A T O R", bg=BG,
                       fg="#333344", font=self.font_label)
        lbl.pack(pady=(18, 0), padx=24, anchor="w")

        frame = tk.Frame(self, bg=DISPLAY_BG, bd=0, relief="flat",
                         highlightbackground="#222230", highlightthickness=1)
        frame.pack(fill="x", padx=20, pady=(8, 14))

        self.expr_var = tk.StringVar(value="")
        expr_lbl = tk.Label(frame, textvariable=self.expr_var,
                            bg=DISPLAY_BG, fg=EXPR_FG, font=self.font_expr,
                            anchor="e", justify="right", height=1)
        expr_lbl.pack(fill="x", padx=14, pady=(12, 0))

        self.result_var = tk.StringVar(value="0")
        result_lbl = tk.Label(frame, textvariable=self.result_var,
                              bg=DISPLAY_BG, fg=DISPLAY_FG, font=self.font_result,
                              anchor="e", justify="right")
        result_lbl.pack(fill="x", padx=14, pady=(2, 14))

    # ── Keypad ─────────────────────────────────────────────────────────────────
    def _build_keypad(self):
        pad = tk.Frame(self, bg=BG)
        pad.pack(padx=20, pady=(0, 20))

        layout = [
            # (label, colspan, style, action)
            [("AC",  1, "clr", self.do_ac),
             ("+/−", 1, "fn",  self.do_sign),
             ("%",   1, "fn",  self.do_pct),
             ("÷",   1, "op",  lambda: self.do_op("÷"))],

            [("7", 1, "num", lambda: self.do_num("7")),
             ("8", 1, "num", lambda: self.do_num("8")),
             ("9", 1, "num", lambda: self.do_num("9")),
             ("×", 1, "op",  lambda: self.do_op("×"))],

            [("4", 1, "num", lambda: self.do_num("4")),
             ("5", 1, "num", lambda: self.do_num("5")),
             ("6", 1, "num", lambda: self.do_num("6")),
             ("−", 1, "op",  lambda: self.do_op("−"))],

            [("1", 1, "num", lambda: self.do_num("1")),
             ("2", 1, "num", lambda: self.do_num("2")),
             ("3", 1, "num", lambda: self.do_num("3")),
             ("+", 1, "op",  lambda: self.do_op("+"))],

            [("0", 2, "num", lambda: self.do_num("0")),
             (".", 1, "num", self.do_dot),
             ("=", 1, "eq",  self.do_equals)],
        ]

        styles = {
            "num": (NUM_BG,  NUM_FG,  NUM_ACTIVE,  self.font_btn),
            "op":  (OP_BG,   OP_FG,   OP_ACTIVE,   self.font_btn),
            "fn":  (FN_BG,   FN_FG,   FN_ACTIVE,   self.font_btn_sm),
            "clr": (CLR_BG,  CLR_FG,  CLR_ACTIVE,  self.font_btn_sm),
            "eq":  (EQ_BG,   EQ_FG,   EQ_ACTIVE,   self.font_btn),
        }

        GAP = 8
        BTN_H = 60
        BTN_W = 72

        for r, row in enumerate(layout):
            col = 0
            for (label, span, style, action) in row:
                bg, fg, active, fnt = styles[style]
                width = BTN_W * span + GAP * (span - 1)

                btn = tk.Label(
                    pad, text=label, bg=bg, fg=fg, font=fnt,
                    width=1, height=1, cursor="hand2",
                    relief="flat", bd=0
                )
                btn.place(
                    x=col * (BTN_W + GAP),
                    y=r * (BTN_H + GAP),
                    width=width,
                    height=BTN_H
                )
                self._round_button(btn, bg, active, fg, action)
                col += span

        pad.configure(width=4 * BTN_W + 3 * GAP,
                      height=5 * BTN_H + 4 * GAP)

    def _round_button(self, btn, bg, active, fg, action):
        def on_enter(e):  btn.configure(bg=active)
        def on_leave(e):  btn.configure(bg=bg)
        def on_press(e):
            btn.configure(bg=active)
            action()
        btn.bind("<Enter>",          on_enter)
        btn.bind("<Leave>",          on_leave)
        btn.bind("<ButtonPress-1>",  on_press)
        btn.bind("<ButtonRelease-1>", lambda e: btn.configure(bg=bg))

    # ── Logic ──────────────────────────────────────────────────────────────────
    def update_display(self):
        txt = self.cur
        try:
            val = float(self.cur)
            if "." not in self.cur and abs(val) >= 1e12:
                txt = f"{val:.4e}"
        except ValueError:
            pass
        self.result_var.set(txt)
        expr = f"{self.prev} {self.op}" if self.prev and self.op else ""
        self.expr_var.set(expr)

    def do_num(self, n):
        if self.just_evaled:
            self.cur = n; self.just_evaled = False
        elif self.cur == "0":
            self.cur = n
        elif len(self.cur.lstrip("-")) < 13:
            self.cur += n
        self.update_display()

    def do_dot(self):
        if self.just_evaled:
            self.cur = "0."; self.just_evaled = False
        elif "." not in self.cur:
            self.cur += "."
        self.update_display()

    def do_ac(self):
        self.cur = "0"; self.prev = ""; self.op = ""; self.just_evaled = False
        self.update_display()

    def do_sign(self):
        if self.cur not in ("0", "Error"):
            self.cur = self.cur[1:] if self.cur.startswith("-") else "-" + self.cur
        self.update_display()

    def do_pct(self):
        try:
            self.cur = self._fmt(float(self.cur) / 100)
        except ValueError:
            pass
        self.update_display()

    def do_op(self, o):
        if self.op and self.prev and not self.just_evaled:
            self._compute()
        self.prev = self.cur; self.op = o
        self.cur = "0"; self.just_evaled = False
        self.update_display()

    def do_equals(self):
        if not self.op or not self.prev:
            return
        self._compute()
        self.just_evaled = True
        self.update_display()
        # Brief flash
        self.result_var.set("  " + self.result_var.get())
        self.after(80, self.update_display)

    def _compute(self):
        try:
            a, b = float(self.prev), float(self.cur)
            if   self.op == "+": r = a + b
            elif self.op == "−": r = a - b
            elif self.op == "×": r = a * b
            elif self.op == "÷": r = "Error" if b == 0 else a / b
            else: r = b
            self.cur = "Error" if r == "Error" else self._fmt(r)
        except ValueError:
            self.cur = "Error"
        self.prev = ""; self.op = ""

    @staticmethod
    def _fmt(v):
        if v == int(v) and abs(v) < 1e12:
            return str(int(v))
        return str(round(v, 10)).rstrip("0").rstrip(".")

    # ── Keyboard ───────────────────────────────────────────────────────────────
    def _bind_keys(self):
        self.bind("<Key>", self._on_key)

    def _on_key(self, e):
        k = e.keysym
        ch = e.char
        if ch.isdigit():              self.do_num(ch)
        elif ch == ".":               self.do_dot()
        elif ch == "+":               self.do_op("+")
        elif ch in ("-", "minus"):    self.do_op("−")
        elif ch in ("*", "asterisk"): self.do_op("×")
        elif ch in ("/", "slash"):    self.do_op("÷")
        elif ch == "%":               self.do_pct()
        elif k in ("Return", "equal"): self.do_equals()
        elif k == "BackSpace":
            if self.cur not in ("0", "Error"):
                self.cur = self.cur[:-1] or "0"
            self.update_display()
        elif k == "Escape":           self.do_ac()


if __name__ == "__main__":
    app = Calculator()
    app.mainloop()
