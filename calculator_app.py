"""
calculator_app.py
─────────────────
Advanced Scientific Calculator – Tkinter UI Layer

Design: Dark industrial theme with amber accent highlights.
Layout: 2-column: history panel (left) + calculator (right)

Features:
  • Full scientific function panel (sin/cos/tan/log/ln/√/x²/1x/n!)
  • Memory operations (MS, MR, M+, MC) with indicator
  • Keyboard binding for ALL standard keys
  • Live expression display + result display
  • Scrollable history panel
  • Animated button press feedback
  • Error display with automatic recovery
"""

import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk

from calculator_engine import CalculatorEngine


# ─────────────────────────────────────────────────────────
#  Colour Palette  (Industrial Dark + Amber)
# ─────────────────────────────────────────────────────────
PALETTE = {
    "bg_main":     "#1a1a1a",
    "bg_panel":    "#111111",
    "bg_display":  "#0d0d0d",
    "bg_btn_num":  "#2a2a2a",
    "bg_btn_op":   "#1e2a35",
    "bg_btn_sci":  "#1c1c2e",
    "bg_btn_eq":   "#c47d00",          # Amber
    "bg_btn_mem":  "#1e1e1e",
    "bg_btn_clear":"#3a1a1a",
    "fg_main":     "#f0e8d8",          # Warm white
    "fg_expr":     "#888880",          # Subdued grey for expression
    "fg_result":   "#f5c842",          # Amber yellow for result
    "fg_sci":      "#7eb8c4",          # Cyan-blue for scientific
    "fg_mem":      "#9b7fd4",          # Purple for memory
    "fg_op":       "#e0a050",          # Orange for operators
    "fg_clear":    "#e06060",          # Red for clear
    "accent":      "#c47d00",
    "hover_num":   "#383838",
    "hover_op":    "#253545",
    "hover_sci":   "#252540",
    "hover_eq":    "#d68a00",
    "border":      "#333333",
    "history_bg":  "#141414",
    "history_item":"#1e1e1e",
    "history_expr":"#666660",
    "history_res": "#c47d00",
    "mem_active":  "#9b7fd4",
    "mem_inactive":"#333333",
}

# ─────────────────────────────────────────────────────────
#  Button layout specification
#  Each entry: (label, width, style, action_key)
#  action_key maps to CalculatorApp._handle_action()
# ─────────────────────────────────────────────────────────
BUTTON_GRID = [
    # Row 0 – Memory
    [
        ("MC",   1, "mem",   "mem_clear"),
        ("MR",   1, "mem",   "mem_recall"),
        ("M+",   1, "mem",   "mem_add"),
        ("MS",   1, "mem",   "mem_store"),
    ],
    # Row 1 – Scientific row 1
    [
        ("sin",  1, "sci",   "sin"),
        ("cos",  1, "sci",   "cos"),
        ("tan",  1, "sci",   "tan"),
        ("π",    1, "sci",   "pi"),
    ],
    # Row 2 – Scientific row 2
    [
        ("log",  1, "sci",   "log"),
        ("ln",   1, "sci",   "ln"),
        ("x²",   1, "sci",   "square"),
        ("√",    1, "sci",   "sqrt"),
    ],
    # Row 3 – Scientific row 3
    [
        ("1/x",  1, "sci",   "inverse"),
        ("n!",   1, "sci",   "factorial"),
        ("e",    1, "sci",   "euler"),
        ("+/-",  1, "sci",   "negate"),
    ],
    # Row 4 – Clear row
    [
        ("AC",   1, "clear", "clear_all"),
        ("CE",   1, "clear", "clear_entry"),
        ("%",    1, "op",    "percent"),
        ("÷",    1, "op",    "divide"),
    ],
    # Row 5 – Digits 7-8-9 + multiply
    [
        ("7",    1, "num",   "7"),
        ("8",    1, "num",   "8"),
        ("9",    1, "num",   "9"),
        ("×",    1, "op",    "multiply"),
    ],
    # Row 6 – Digits 4-5-6 + subtract
    [
        ("4",    1, "num",   "4"),
        ("5",    1, "num",   "5"),
        ("6",    1, "num",   "6"),
        ("−",    1, "op",    "subtract"),
    ],
    # Row 7 – Digits 1-2-3 + add
    [
        ("1",    1, "num",   "1"),
        ("2",    1, "num",   "2"),
        ("3",    1, "num",   "3"),
        ("+",    1, "op",    "add"),
    ],
    # Row 8 – Zero + dot + paren + equals
    [
        ("0",    1, "num",   "0"),
        (".",    1, "num",   "dot"),
        ("( )",  1, "op",    "paren"),
        ("=",    1, "eq",    "equals"),
    ],
]

# ─────────────────────────────────────────────────────────
#  Style → colour mapping
# ─────────────────────────────────────────────────────────
STYLE_MAP = {
    "num":   (PALETTE["bg_btn_num"], PALETTE["fg_main"],  PALETTE["hover_num"]),
    "op":    (PALETTE["bg_btn_op"],  PALETTE["fg_op"],    PALETTE["hover_op"]),
    "sci":   (PALETTE["bg_btn_sci"], PALETTE["fg_sci"],   PALETTE["hover_sci"]),
    "eq":    (PALETTE["bg_btn_eq"],  PALETTE["fg_main"],  PALETTE["hover_eq"]),
    "mem":   (PALETTE["bg_btn_mem"], PALETTE["fg_mem"],   "#2a2a3a"),
    "clear": (PALETTE["bg_btn_clear"],PALETTE["fg_clear"],"#4a1a1a"),
}


class CalculatorApp:
    """Main application class – owns the Tk root and all widgets."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.engine = CalculatorEngine()
        self._paren_count = 0       # Track open parentheses for auto-close

        self._configure_root()
        self._build_fonts()
        self._build_layout()
        self._bind_keyboard()

    # ─────────────────────────────────────────────────────
    #  Root configuration
    # ─────────────────────────────────────────────────────
    def _configure_root(self) -> None:
        self.root.title("Advanced Scientific Calculator")
        self.root.configure(bg=PALETTE["bg_main"])
        self.root.resizable(False, False)
        # Center on screen
        self.root.update_idletasks()
        w, h = 780, 680
        x = (self.root.winfo_screenwidth()  - w) // 2
        y = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.minsize(780, 680)

    # ─────────────────────────────────────────────────────
    #  Fonts
    # ─────────────────────────────────────────────────────
    def _build_fonts(self) -> None:
        self.font_result  = tkfont.Font(family="Courier New", size=32, weight="bold")
        self.font_expr    = tkfont.Font(family="Courier New", size=13)
        self.font_btn     = tkfont.Font(family="Helvetica",   size=14, weight="bold")
        self.font_btn_sci = tkfont.Font(family="Helvetica",   size=12)
        self.font_history = tkfont.Font(family="Courier New", size=10)
        self.font_title   = tkfont.Font(family="Helvetica",   size=11, weight="bold")
        self.font_mem_ind = tkfont.Font(family="Helvetica",   size=9)

    # ─────────────────────────────────────────────────────
    #  Top-level layout: history pane + calculator pane
    # ─────────────────────────────────────────────────────
    def _build_layout(self) -> None:
        # Outer container
        outer = tk.Frame(self.root, bg=PALETTE["bg_main"], padx=10, pady=10)
        outer.pack(fill="both", expand=True)

        # ── History panel (left, fixed width)
        self._build_history_panel(outer)

        # ── Calculator panel (right)
        self._build_calculator_panel(outer)

    # ─────────────────────────────────────────────────────
    #  History panel
    # ─────────────────────────────────────────────────────
    def _build_history_panel(self, parent: tk.Frame) -> None:
        hist_frame = tk.Frame(parent, bg=PALETTE["history_bg"], width=200,
                              relief="flat", bd=0)
        hist_frame.pack(side="left", fill="y", padx=(0, 10))
        hist_frame.pack_propagate(False)

        # Title
        title_bar = tk.Frame(hist_frame, bg=PALETTE["bg_panel"], pady=8)
        title_bar.pack(fill="x")
        tk.Label(title_bar, text="HISTORY", font=self.font_title,
                 bg=PALETTE["bg_panel"], fg=PALETTE["fg_sci"]).pack()

        # Scrollable list
        scroll = tk.Scrollbar(hist_frame, orient="vertical",
                              bg=PALETTE["bg_panel"],
                              troughcolor=PALETTE["bg_main"],
                              activebackground=PALETTE["accent"])
        scroll.pack(side="right", fill="y")

        self.history_list = tk.Listbox(
            hist_frame,
            yscrollcommand=scroll.set,
            bg=PALETTE["history_bg"],
            fg=PALETTE["history_expr"],
            selectbackground=PALETTE["bg_btn_op"],
            selectforeground=PALETTE["fg_result"],
            font=self.font_history,
            relief="flat",
            bd=0,
            highlightthickness=0,
            activestyle="none",
        )
        self.history_list.pack(side="left", fill="both", expand=True)
        scroll.config(command=self.history_list.yview)

        # Click-to-recall from history
        self.history_list.bind("<Double-Button-1>", self._recall_history)

        # Clear history button
        clear_hist = tk.Button(
            hist_frame, text="Clear History",
            font=self.font_mem_ind,
            bg=PALETTE["bg_btn_clear"], fg=PALETTE["fg_clear"],
            activebackground="#4a1a1a", activeforeground=PALETTE["fg_clear"],
            relief="flat", bd=0, padx=4, pady=4, cursor="hand2",
            command=self._clear_history
        )
        clear_hist.pack(fill="x", padx=4, pady=4)

    # ─────────────────────────────────────────────────────
    #  Main calculator panel
    # ─────────────────────────────────────────────────────
    def _build_calculator_panel(self, parent: tk.Frame) -> None:
        calc_frame = tk.Frame(parent, bg=PALETTE["bg_main"])
        calc_frame.pack(side="left", fill="both", expand=True)

        self._build_display(calc_frame)
        self._build_buttons(calc_frame)

    # ─────────────────────────────────────────────────────
    #  Display area: memory indicator + expression + result
    # ─────────────────────────────────────────────────────
    def _build_display(self, parent: tk.Frame) -> None:
        display_frame = tk.Frame(parent, bg=PALETTE["bg_display"],
                                 pady=12, padx=14,
                                 relief="flat", bd=0)
        display_frame.pack(fill="x", pady=(0, 8))

        # Memory indicator (top-left badge)
        mem_row = tk.Frame(display_frame, bg=PALETTE["bg_display"])
        mem_row.pack(fill="x")
        self.mem_indicator = tk.Label(
            mem_row, text="M", font=self.font_mem_ind,
            bg=PALETTE["mem_inactive"], fg=PALETTE["bg_display"],
            padx=4, pady=1, relief="flat"
        )
        self.mem_indicator.pack(side="left")

        self.mode_label = tk.Label(
            mem_row, text="DEG", font=self.font_mem_ind,
            bg=PALETTE["bg_display"], fg=PALETTE["fg_expr"]
        )
        self.mode_label.pack(side="right")

        # Expression (smaller, above result)
        self.expr_var = tk.StringVar(value="")
        self.expr_label = tk.Label(
            display_frame,
            textvariable=self.expr_var,
            font=self.font_expr,
            bg=PALETTE["bg_display"],
            fg=PALETTE["fg_expr"],
            anchor="e",
            justify="right",
            wraplength=520,
        )
        self.expr_label.pack(fill="x", pady=(6, 2))

        # Main result display
        self.result_var = tk.StringVar(value="0")
        self.result_label = tk.Label(
            display_frame,
            textvariable=self.result_var,
            font=self.font_result,
            bg=PALETTE["bg_display"],
            fg=PALETTE["fg_result"],
            anchor="e",
            justify="right",
        )
        self.result_label.pack(fill="x")

        # Error label (hidden by default)
        self.error_var = tk.StringVar(value="")
        self.error_label = tk.Label(
            display_frame,
            textvariable=self.error_var,
            font=self.font_history,
            bg=PALETTE["bg_display"],
            fg=PALETTE["fg_clear"],
            anchor="e",
        )
        self.error_label.pack(fill="x")

    # ─────────────────────────────────────────────────────
    #  Button grid
    # ─────────────────────────────────────────────────────
    def _build_buttons(self, parent: tk.Frame) -> None:
        btn_frame = tk.Frame(parent, bg=PALETTE["bg_main"])
        btn_frame.pack(fill="both", expand=True)

        self._buttons: dict[str, tk.Button] = {}

        for row_idx, row in enumerate(BUTTON_GRID):
            for col_idx, (label, width, style, action) in enumerate(row):
                bg, fg, hover = STYLE_MAP[style]
                f = self.font_btn if style in ("num", "eq", "clear") else self.font_btn_sci

                btn = tk.Button(
                    btn_frame,
                    text=label,
                    font=f,
                    bg=bg, fg=fg,
                    activebackground=hover,
                    activeforeground=fg,
                    relief="flat",
                    bd=0,
                    padx=0, pady=0,
                    cursor="hand2",
                    command=lambda a=action: self._handle_action(a),
                )
                btn.grid(
                    row=row_idx, column=col_idx,
                    sticky="nsew",
                    padx=2, pady=2,
                    ipady=10,
                )

                # Hover animation
                btn.bind("<Enter>", lambda e, b=btn, h=hover: b.config(bg=h))
                btn.bind("<Leave>", lambda e, b=btn, c=bg:   b.config(bg=c))

                # Press animation
                btn.bind("<ButtonPress-1>",   lambda e, b=btn: b.config(relief="sunken"))
                btn.bind("<ButtonRelease-1>", lambda e, b=btn, c=bg: b.config(relief="flat", bg=c))

                self._buttons[action] = btn

            btn_frame.rowconfigure(row_idx, weight=1)

        for col in range(4):
            btn_frame.columnconfigure(col, weight=1)

    # ─────────────────────────────────────────────────────
    #  Keyboard bindings
    # ─────────────────────────────────────────────────────
    def _bind_keyboard(self) -> None:
        kb = self.root

        # Digits
        for d in "0123456789":
            kb.bind(d, lambda e, x=d: self._handle_action(x))

        # Operators
        kb.bind("+",        lambda e: self._handle_action("add"))
        kb.bind("-",        lambda e: self._handle_action("subtract"))
        kb.bind("*",        lambda e: self._handle_action("multiply"))
        kb.bind("/",        lambda e: self._handle_action("divide"))
        kb.bind("%",        lambda e: self._handle_action("percent"))
        kb.bind("^",        lambda e: self._handle_action("power"))
        kb.bind(".",        lambda e: self._handle_action("dot"))
        kb.bind("(",        lambda e: self._handle_action("open_paren"))
        kb.bind(")",        lambda e: self._handle_action("close_paren"))

        # Enter / Equals
        kb.bind("<Return>",  lambda e: self._handle_action("equals"))
        kb.bind("<KP_Enter>",lambda e: self._handle_action("equals"))

        # Backspace / Delete
        kb.bind("<BackSpace>",lambda e: self._handle_action("clear_entry"))
        kb.bind("<Delete>",   lambda e: self._handle_action("clear_all"))

        # Escape = AC
        kb.bind("<Escape>",   lambda e: self._handle_action("clear_all"))

        # Ctrl+H = clear history
        kb.bind("<Control-h>", lambda e: self._clear_history())

    # ─────────────────────────────────────────────────────
    #  Central action dispatcher
    # ─────────────────────────────────────────────────────
    def _handle_action(self, action: str) -> None:
        self._clear_error()

        match action:
            # ── Digits & decimal
            case d if d in "0123456789":
                self.engine.append(d)
            case "dot":
                self.engine.append(".")

            # ── Basic operators
            case "add":
                self.engine.append("+")
            case "subtract":
                self.engine.append("-")
            case "multiply":
                self.engine.append("*")
            case "divide":
                self.engine.append("/")
            case "percent":
                self.engine.apply_percent()
            case "power":
                self.engine.append("**")

            # ── Parentheses (smart toggle)
            case "paren":
                self._handle_paren()
            case "open_paren":
                self.engine.append("(")
                self._paren_count += 1
            case "close_paren":
                if self._paren_count > 0:
                    self.engine.append(")")
                    self._paren_count -= 1

            # ── Clear / backspace
            case "clear_all":
                self.engine.clear_all()
                self._paren_count = 0
            case "clear_entry":
                self.engine.clear_entry()

            # ── Negate
            case "negate":
                self.engine.apply_negate()

            # ── Constants
            case "pi":
                self.engine.append("pi")
            case "euler":
                self.engine.append("e")

            # ── Scientific (evaluate immediately)
            case "sqrt":
                self._run_and_show(self.engine.apply_sqrt)
                return
            case "square":
                self._run_and_show(self.engine.apply_square)
                return
            case "inverse":
                self._run_and_show(self.engine.apply_inverse)
                return
            case "factorial":
                self._run_and_show(self.engine.apply_factorial)
                return
            case "log":
                self._run_and_show(self.engine.apply_log)
                return
            case "ln":
                self._run_and_show(self.engine.apply_ln)
                return
            case "sin":
                self._run_and_show(self.engine.apply_sin)
                return
            case "cos":
                self._run_and_show(self.engine.apply_cos)
                return
            case "tan":
                self._run_and_show(self.engine.apply_tan)
                return

            # ── Memory
            case "mem_store":
                self.engine.memory_store()
                self._update_mem_indicator()
                return
            case "mem_recall":
                self.engine.memory_recall()
            case "mem_add":
                self.engine.memory_add()
                self._update_mem_indicator()
                return
            case "mem_clear":
                self.engine.memory_clear()
                self._update_mem_indicator()
                return

            # ── Evaluate
            case "equals":
                self._run_and_show(self.engine.evaluate)
                return

        self._refresh_display()

    # ─────────────────────────────────────────────────────
    #  Smart parenthesis logic
    # ─────────────────────────────────────────────────────
    def _handle_paren(self) -> None:
        expr = self.engine.current_expression
        # Open paren if: expression is empty, or last char is an operator
        last = expr[-1] if expr else ""
        if not expr or last in "+-*/(":
            self.engine.append("(")
            self._paren_count += 1
        elif self._paren_count > 0:
            self.engine.append(")")
            self._paren_count -= 1
        else:
            self.engine.append("(")
            self._paren_count += 1
        self._refresh_display()

    # ─────────────────────────────────────────────────────
    #  Run an engine callable and update display
    # ─────────────────────────────────────────────────────
    def _run_and_show(self, fn) -> None:
        result, error = fn()
        if error:
            self._show_error(error)
        else:
            self._update_history_panel()
        self._refresh_display()

    # ─────────────────────────────────────────────────────
    #  Display refresh
    # ─────────────────────────────────────────────────────
    def _refresh_display(self) -> None:
        expr = self.engine.current_expression
        if not expr:
            self.result_var.set("0")
            self.expr_var.set("")
        else:
            # Show the expression in the result display while building;
            # after evaluation, _run_and_show will have set the result.
            self.result_var.set(expr if len(expr) <= 20 else "…" + expr[-18:])
            self.expr_var.set("")
        self._update_mem_indicator()

    def _show_error(self, message: str) -> None:
        self.error_var.set(f"⚠ {message}")
        self.result_var.set("Error")
        # Auto-clear error after 3 seconds
        self.root.after(3000, self._clear_error)

    def _clear_error(self) -> None:
        self.error_var.set("")

    def _update_mem_indicator(self) -> None:
        if self.engine.memory != 0.0:
            self.mem_indicator.config(
                bg=PALETTE["mem_active"], fg="#ffffff"
            )
        else:
            self.mem_indicator.config(
                bg=PALETTE["mem_inactive"], fg=PALETTE["bg_display"]
            )

    # ─────────────────────────────────────────────────────
    #  History panel updates
    # ─────────────────────────────────────────────────────
    def _update_history_panel(self) -> None:
        self.history_list.delete(0, "end")
        for expr, result in self.engine.get_history():
            self.history_list.insert("end", f"{expr}")
            self.history_list.insert("end", f"  = {result}")
            self.history_list.insert("end", "")   # Blank separator

    def _recall_history(self, event) -> None:
        """Double-click on a history item to recall the result."""
        selection = self.history_list.curselection()
        if not selection:
            return
        text = self.history_list.get(selection[0])
        text = text.strip()
        if text.startswith("= "):
            value = text[2:]
            self.engine.current_expression = value
            self._refresh_display()

    def _clear_history(self) -> None:
        self.engine.clear_history()
        self.history_list.delete(0, "end")


# ─────────────────────────────────────────────────────────
#  After-evaluate display hook
#  Monkey-patch evaluate so the display refreshes post-eval
# ─────────────────────────────────────────────────────────
def _patched_evaluate(app: CalculatorApp):
    original = app.engine.evaluate

    def wrapper():
        result, error = original()
        if not error and result:
            # Show the previous expression in expr_label, result in big font
            # The expression was stored in history before current_expression was overwritten
            history = app.engine.get_history()
            if history:
                prev_expr, _ = history[0]
                app.expr_var.set(prev_expr + " =")
            app.result_var.set(result)
        return result, error

    app.engine.evaluate = wrapper


# ─────────────────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────────────────
def main() -> None:
    root = tk.Tk()
    app = CalculatorApp(root)

    # Patch evaluate to update expression label after each computation
    _patched_evaluate(app)

    root.mainloop()


if __name__ == "__main__":
    main()
