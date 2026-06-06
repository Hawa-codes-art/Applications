import tkinter as tk
from tkinter import ttk, messagebox, colorchooser, font as tkfont
import json
import os
from datetime import datetime

# ── Data file ──────────────────────────────────────────────────────────────────
DATA_FILE = os.path.join(os.path.dirname(__file__), "todo_data.json")

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return {"users": {}, "theme": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ── Default theme ──────────────────────────────────────────────────────────────
DEFAULT_THEME = {
    "bg":        "#1A1A2E",
    "surface":   "#16213E",
    "card":      "#0F3460",
    "accent":    "#E94560",
    "text":      "#EAEAEA",
    "subtext":   "#A0AEC0",
    "done_bg":   "#0D7377",
    "font_size":  13,
}

# ══════════════════════════════════════════════════════════════════════════════
class ToDoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        raw = load_data()
        self.all_data   = raw
        self.users      = raw.get("users", {})
        self.theme      = {**DEFAULT_THEME, **raw.get("theme", {})}
        self.current_user = None

        self.title("✅  My To-Do List")
        self.geometry("520x680")
        self.resizable(True, True)
        self.minsize(400, 500)
        self._apply_theme_globals()
        self._build_login_screen()

    # ── Theme helpers ──────────────────────────────────────────────────────────
    def _apply_theme_globals(self):
        t = self.theme
        self.configure(bg=t["bg"])
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TScrollbar",
                        background=t["surface"], troughcolor=t["bg"],
                        borderwidth=0, arrowcolor=t["accent"])

    def _fg(self, widget):
        """Recursively recolour every widget after a theme change."""
        t = self.theme
        cls = widget.winfo_class()
        try:
            if cls in ("Frame", "Toplevel"):
                widget.configure(bg=t["bg"])
            elif cls == "Label":
                widget.configure(bg=widget.cget("bg"), fg=t["text"])
            elif cls == "Button":
                widget.configure(bg=t["accent"], fg=t["text"],
                                  activebackground=t["card"],
                                  activeforeground=t["text"])
            elif cls == "Entry":
                widget.configure(bg=t["surface"], fg=t["text"],
                                  insertbackground=t["accent"],
                                  relief="flat")
            elif cls == "Canvas":
                widget.configure(bg=t["bg"])
        except tk.TclError:
            pass
        for child in widget.winfo_children():
            self._fg(child)

    # ── Shared widget factories ────────────────────────────────────────────────
    def _btn(self, parent, text, cmd, color=None, width=18, pady=8):
        t = self.theme
        b = tk.Button(parent, text=text, command=cmd,
                       bg=color or t["accent"], fg=t["text"],
                       activebackground=t["card"], activeforeground=t["text"],
                       font=("Georgia", t["font_size"]-1, "bold"),
                       bd=0, cursor="hand2", width=width, pady=pady,
                       relief="flat")
        b.bind("<Enter>", lambda e: b.configure(bg=t["card"]))
        b.bind("<Leave>", lambda e: b.configure(bg=color or t["accent"]))
        return b

    def _entry(self, parent, placeholder="", width=30):
        t = self.theme
        e = tk.Entry(parent, bg=t["surface"], fg=t["subtext"],
                      insertbackground=t["accent"],
                      font=("Georgia", t["font_size"]), bd=0,
                      relief="flat", width=width)
        e.insert(0, placeholder)
        def on_focus_in(event):
            if e.get() == placeholder:
                e.delete(0, tk.END)
                e.configure(fg=t["text"])
        def on_focus_out(event):
            if not e.get():
                e.insert(0, placeholder)
                e.configure(fg=t["subtext"])
        e.bind("<FocusIn>", on_focus_in)
        e.bind("<FocusOut>", on_focus_out)
        return e

    def _label(self, parent, text, size=None, bold=False, color=None):
        t = self.theme
        style = "bold" if bold else "normal"
        return tk.Label(parent, text=text, bg=t["bg"], fg=color or t["text"],
                         font=("Georgia", size or t["font_size"], style))

    # ══════════════════════════════════════════════════════════════════════════
    # LOGIN SCREEN
    # ══════════════════════════════════════════════════════════════════════════
    def _build_login_screen(self):
        for w in self.winfo_children():
            w.destroy()
        t = self.theme

        outer = tk.Frame(self, bg=t["bg"])
        outer.pack(expand=True, fill="both", padx=40, pady=40)

        # Header
        tk.Label(outer, text="📝", font=("Georgia", 48), bg=t["bg"],
                  fg=t["accent"]).pack(pady=(20,4))
        self._label(outer, "My To-Do List", 22, bold=True,
                     color=t["accent"]).pack()
        self._label(outer, "Enter your name to continue", 11,
                     color=t["subtext"]).pack(pady=(4,24))

        # Name input
        card = tk.Frame(outer, bg=t["surface"], padx=24, pady=24)
        card.pack(fill="x")
        self._label(card, "Your Name", 11, color=t["subtext"]).pack(anchor="w")
        self.name_entry = self._entry(card, "e.g.  Alice", width=32)
        self.name_entry.pack(fill="x", pady=(4,12), ipady=8)

        self._btn(card, "  → Open My Tasks", self._login, width=30).pack(fill="x")

        # Existing users
        if self.users:
            sep = tk.Frame(outer, bg=t["subtext"], height=1)
            sep.pack(fill="x", pady=20)
            self._label(outer, "— or pick a name —", 10,
                         color=t["subtext"]).pack()
            btn_frame = tk.Frame(outer, bg=t["bg"])
            btn_frame.pack(pady=8)
            for name in sorted(self.users):
                self._btn(btn_frame, name,
                           lambda n=name: self._quick_login(n),
                           color=t["card"], width=14, pady=5).pack(
                               side="left", padx=4, pady=4)

        # Theme button
        tk.Frame(outer, bg=t["bg"], height=20).pack()
        self._btn(outer, "🎨  Appearance", self._open_theme_editor,
                   color=t["surface"], width=20, pady=6).pack()

    def _login(self):
        name = self.name_entry.get().strip()
        if not name or name == "e.g.  Alice":
            messagebox.showwarning("Oops", "Please enter your name first.")
            return
        self.current_user = name
        if name not in self.users:
            self.users[name] = []
        self._save()
        self._build_main_screen()

    def _quick_login(self, name):
        self.current_user = name
        self._build_main_screen()

    # ══════════════════════════════════════════════════════════════════════════
    # MAIN TASK SCREEN
    # ══════════════════════════════════════════════════════════════════════════
    def _build_main_screen(self):
        for w in self.winfo_children():
            w.destroy()
        t = self.theme
        tasks = self.users.get(self.current_user, [])

        # ── Top bar ───────────────────────────────────────────────────────────
        topbar = tk.Frame(self, bg=t["card"], padx=16, pady=10)
        topbar.pack(fill="x")
        tk.Label(topbar, text=f"👤  {self.current_user}",
                  bg=t["card"], fg=t["accent"],
                  font=("Georgia", t["font_size"], "bold")).pack(side="left")
        self._btn(topbar, "← Back", self._build_login_screen,
                   color=t["surface"], width=8, pady=4).pack(side="right", padx=4)
        self._btn(topbar, "🎨", self._open_theme_editor,
                   color=t["surface"], width=3, pady=4).pack(side="right", padx=4)

        # ── Stats strip ───────────────────────────────────────────────────────
        done   = sum(1 for tk_ in tasks if tk_.get("done"))
        total  = len(tasks)
        remain = total - done
        stats = tk.Frame(self, bg=t["surface"], padx=16, pady=8)
        stats.pack(fill="x")
        for label, val, col in [
            ("Total", total, t["text"]),
            ("Done ✓", done, t["done_bg"]),
            ("Left", remain, t["accent"]),
        ]:
            f = tk.Frame(stats, bg=t["surface"])
            f.pack(side="left", expand=True)
            tk.Label(f, text=str(val), font=("Georgia", 20, "bold"),
                      bg=t["surface"], fg=col).pack()
            tk.Label(f, text=label, font=("Georgia", 9),
                      bg=t["surface"], fg=t["subtext"]).pack()

        # ── Input area ────────────────────────────────────────────────────────
        inp = tk.Frame(self, bg=t["bg"], padx=16, pady=12)
        inp.pack(fill="x")
        self.task_entry = self._entry(inp, "Add a new task…", width=34)
        self.task_entry.pack(side="left", fill="x", expand=True, ipady=8)
        self.task_entry.bind("<Return>", lambda e: self._add_task())
        tk.Frame(inp, bg=t["bg"], width=8).pack(side="left")
        self._btn(inp, "+ Add", self._add_task, width=8, pady=8).pack(side="left")

        # ── Task list (scrollable) ─────────────────────────────────────────────
        self.list_frame_outer = tk.Frame(self, bg=t["bg"])
        self.list_frame_outer.pack(fill="both", expand=True, padx=16, pady=(0,8))

        canvas = tk.Canvas(self.list_frame_outer, bg=t["bg"],
                            highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.list_frame_outer, orient="vertical",
                                   command=canvas.yview)
        self.list_frame = tk.Frame(canvas, bg=t["bg"])
        self.list_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0,0), window=self.list_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.bind_all("<MouseWheel>",
                         lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        self._render_tasks()

    # ── Task rendering ─────────────────────────────────────────────────────────
    def _render_tasks(self):
        for w in self.list_frame.winfo_children():
            w.destroy()
        t = self.theme
        tasks = self.users.get(self.current_user, [])
        if not tasks:
            tk.Label(self.list_frame, text="No tasks yet — add one above! 🎉",
                      bg=t["bg"], fg=t["subtext"],
                      font=("Georgia", t["font_size"]-1, "italic")).pack(pady=40)
            return

        # pending first, then done
        ordered = [tk_ for tk_ in tasks if not tk_.get("done")] + \
                  [tk_ for tk_ in tasks if tk_.get("done")]

        for i, task in enumerate(ordered):
            orig_i = tasks.index(task)
            self._task_card(self.list_frame, task, orig_i)

    def _task_card(self, parent, task, idx):
        t  = self.theme
        done = task.get("done", False)
        bg   = t["done_bg"] if done else t["card"]

        card = tk.Frame(parent, bg=bg, padx=12, pady=10)
        card.pack(fill="x", pady=4)

        # Checkbox toggle
        chk_txt = "✅" if done else "⬜"
        chk = tk.Label(card, text=chk_txt, bg=bg, fg=t["text"],
                         font=("Georgia", 16), cursor="hand2")
        chk.pack(side="left", padx=(0,10))
        chk.bind("<Button-1>", lambda e, i=idx: self._toggle_task(i))

        # Task text (editable inline)
        txt_var = tk.StringVar(value=task["text"])
        txt_entry = tk.Entry(card, textvariable=txt_var,
                              bg=bg, fg=t["text"],
                              disabledbackground=bg,
                              disabledforeground=t["subtext"] if done else t["text"],
                              font=("Georgia", t["font_size"],
                                    "overstrike" if done else "normal"),
                              bd=0, relief="flat", width=24,
                              state="disabled" if done else "normal",
                              insertbackground=t["accent"])
        txt_entry.pack(side="left", fill="x", expand=True)
        txt_entry.bind("<Return>",
                        lambda e, i=idx, v=txt_var: self._save_task_text(i, v))
        txt_entry.bind("<FocusOut>",
                        lambda e, i=idx, v=txt_var: self._save_task_text(i, v))

        # Date label
        date_str = task.get("date", "")
        if date_str:
            tk.Label(card, text=date_str, bg=bg, fg=t["subtext"],
                      font=("Georgia", 8)).pack(side="left", padx=6)

        # Delete button
        del_btn = tk.Label(card, text="✕", bg=bg, fg=t["accent"],
                            font=("Georgia", 14, "bold"), cursor="hand2")
        del_btn.pack(side="right")
        del_btn.bind("<Button-1>", lambda e, i=idx: self._delete_task(i))

    # ── Task actions ───────────────────────────────────────────────────────────
    def _add_task(self):
        text = self.task_entry.get().strip()
        if not text or text == "Add a new task…":
            return
        task = {"text": text, "done": False,
                 "date": datetime.now().strftime("%b %d")}
        self.users[self.current_user].append(task)
        self._save()
        self.task_entry.delete(0, tk.END)
        self._build_main_screen()

    def _toggle_task(self, idx):
        tasks = self.users[self.current_user]
        tasks[idx]["done"] = not tasks[idx].get("done", False)
        self._save()
        self._build_main_screen()

    def _delete_task(self, idx):
        self.users[self.current_user].pop(idx)
        self._save()
        self._build_main_screen()

    def _save_task_text(self, idx, var):
        text = var.get().strip()
        if text:
            self.users[self.current_user][idx]["text"] = text
            self._save()

    def _save(self):
        self.all_data["users"]  = self.users
        self.all_data["theme"]  = self.theme
        save_data(self.all_data)

    # ══════════════════════════════════════════════════════════════════════════
    # THEME EDITOR
    # ══════════════════════════════════════════════════════════════════════════
    def _open_theme_editor(self):
        win = tk.Toplevel(self)
        win.title("🎨  Appearance")
        win.geometry("400x560")
        t = self.theme
        win.configure(bg=t["bg"])

        tk.Label(win, text="Appearance", font=("Georgia", 16, "bold"),
                  bg=t["bg"], fg=t["accent"]).pack(pady=(20,4))
        tk.Label(win, text="Customise colours & text size",
                  font=("Georgia", 10), bg=t["bg"],
                  fg=t["subtext"]).pack(pady=(0,16))

        scroll_frame = tk.Frame(win, bg=t["bg"])
        scroll_frame.pack(fill="both", expand=True, padx=24)

        colour_keys = [
            ("bg",       "Background"),
            ("surface",  "Surface / Input"),
            ("card",     "Task Card"),
            ("accent",   "Accent Colour"),
            ("text",     "Primary Text"),
            ("subtext",  "Secondary Text"),
            ("done_bg",  "Done Task Colour"),
        ]

        swatches = {}
        for key, label in colour_keys:
            row = tk.Frame(scroll_frame, bg=t["bg"])
            row.pack(fill="x", pady=5)
            tk.Label(row, text=label, bg=t["bg"], fg=t["text"],
                      font=("Georgia", 11), width=18, anchor="w").pack(side="left")
            swatch = tk.Label(row, bg=t[key], width=6, height=1,
                               relief="flat", cursor="hand2",
                               bd=2)
            swatch.pack(side="right")
            swatches[key] = swatch
            def pick(k=key, sw=swatch):
                col = colorchooser.askcolor(color=self.theme[k],
                                             title=f"Pick {k}")[1]
                if col:
                    self.theme[k] = col
                    sw.configure(bg=col)
            swatch.bind("<Button-1>", lambda e, p=pick: p())

        # Font size slider
        tk.Frame(scroll_frame, bg=t["bg"], height=10).pack()
        tk.Label(scroll_frame, text="Font Size", bg=t["bg"], fg=t["text"],
                  font=("Georgia", 11)).pack(anchor="w")
        font_var = tk.IntVar(value=t["font_size"])
        slider = tk.Scale(scroll_frame, from_=10, to=20,
                           orient="horizontal", variable=font_var,
                           bg=t["bg"], fg=t["text"], troughcolor=t["surface"],
                           highlightthickness=0, activebackground=t["accent"],
                           length=300)
        slider.pack(fill="x", pady=4)

        # Preset themes
        tk.Frame(scroll_frame, bg=t["bg"], height=6).pack()
        tk.Label(scroll_frame, text="Presets", bg=t["bg"], fg=t["subtext"],
                  font=("Georgia", 10)).pack(anchor="w")
        presets_frame = tk.Frame(scroll_frame, bg=t["bg"])
        presets_frame.pack(fill="x", pady=6)
        presets = {
            "🌙 Dark":  DEFAULT_THEME,
            "☀️ Light": {**DEFAULT_THEME, "bg":"#F7F7F7","surface":"#EFEFEF",
                          "card":"#FFFFFF","text":"#1A1A2E","subtext":"#666688",
                          "accent":"#E94560","done_bg":"#0D9378"},
            "🌿 Forest":{**DEFAULT_THEME, "bg":"#1B2F1B","surface":"#233223",
                          "card":"#2D4A2D","accent":"#76C442","text":"#E8F5E8",
                          "subtext":"#9DBF9E","done_bg":"#3A7D44"},
            "🌸 Rose":  {**DEFAULT_THEME, "bg":"#2D1B2E","surface":"#3D2040",
                          "card":"#4D2850","accent":"#FF69B4","text":"#FDE8F5",
                          "subtext":"#D4A0C8","done_bg":"#8B4F7A"},
        }
        for name, preset in presets.items():
            b = tk.Button(presets_frame, text=name, bg=t["card"], fg=t["text"],
                           font=("Georgia", 9), bd=0, relief="flat",
                           cursor="hand2", padx=8, pady=4,
                           command=lambda p=preset, s=swatches, fv=font_var: 
                               self._apply_preset(p, s, fv))
            b.pack(side="left", padx=4)

        # Apply button
        def apply_and_close():
            self.theme["font_size"] = font_var.get()
            self._save()
            win.destroy()
            if self.current_user:
                self._build_main_screen()
            else:
                self._build_login_screen()

        btn_row = tk.Frame(win, bg=t["bg"])
        btn_row.pack(pady=16)
        self._btn(btn_row, "✓  Apply Changes", apply_and_close,
                   width=20, pady=8).pack()

    def _apply_preset(self, preset, swatches, font_var):
        for k, v in preset.items():
            self.theme[k] = v
        for key, sw in swatches.items():
            sw.configure(bg=self.theme[key])
        font_var.set(self.theme["font_size"])


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = ToDoApp()
    app.mainloop()
