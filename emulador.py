import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import math
import json
import os
import sys
import ctypes
import ctypes.wintypes as wt

# ====== Colores y Constantes ======
C = {
    "bg":      "#0b0e14",
    "bg2":     "#12171f",
    "bg3":     "#1a2030",
    "border":  "#1e2d42",
    "accent":  "#00d4ff",
    "accent2": "#7b2fff",
    "green":   "#00ff88",
    "red":     "#ff3b5c",
    "yellow":  "#ffb800",
    "text":    "#c8d8e8",
    "dim":     "#4a6070",
    "white":   "#ffffff",
}
CONFIG_FILE = "mouse2ps5_config.json"

DEFAULT_CONFIG = {
    "sensitivity_x": 0.015,
    "sensitivity_y": 0.015,
    "smoothing":     0.18,
    "deadzone":      0.08,
    "keymap": {
        "A (Saltar)":          "space",
        "B (Agacharse)":       "ctrl_l",
        "X (Recarga/Sprint)":  "shift_l",
        "Y (Interactuar)":     "f",
        "RB (Hombro Der)":     "r",
        "LB (Hombro Izq)":     "tab",
        "LS (Click Izq Joy)":  "q",
        "RS (Click Der Joy)":  "e",
        "START (Menu)":        "escape",
        "BACK (Opciones)":     "return",
        "DPAD Arriba":         "num_1",
        "DPAD Abajo":          "num_2",
        "DPAD Izquierda":      "num_3",
        "DPAD Derecha":        "num_4",
    },
    "mouse_map": {
        "Click Izquierdo": "RT",
        "Click Derecho":   "LT",
        "Scroll Arriba":   "DPAD_UP",
        "Scroll Abajo":    "DPAD_DOWN",
    },
}

# ====== Estado global ======
state = {
    "active":          False,
    "running":         False,
    "mouse_dx":        0.0,
    "mouse_dy":        0.0,
    "rx_smooth":       0.0,
    "ry_smooth":       0.0,
    "pressed_keys":    set(),
    "config":          {k: (v.copy() if isinstance(v, dict) else v)
                        for k, v in DEFAULT_CONFIG.items()},
    "gamepad":         None,
    "key_listener":    None,
    "_mouse_listener": None,
    "_hook":           None,
    "_hook_proc":      None,
    "_last_x":         None,
    "_last_y":         None,
    "lock":            threading.Lock(),
}
WASD = {"w": (0, 1), "s": (0, -1), "a": (-1, 0), "d": (1, 0)}
BUTTON_MAP     = {}
BUTTON_RELEASE = {}

# ====== Dependencias opcionales ======
try:
    import vgamepad as vg
    from pynput import mouse as pmouse, keyboard as pkeyboard
    DEPS_OK = True
except ImportError:
    DEPS_OK = False

class _POINT(ctypes.Structure):
    _fields_ = [("x", wt.LONG), ("y", wt.LONG)]

class _MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("pt",          _POINT),
        ("mouseData",   wt.DWORD),
        ("flags",       wt.DWORD),
        ("time",        wt.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]

WH_MOUSE_LL  = 14
WM_MOUSEMOVE = 0x0200
HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_int, wt.WPARAM, wt.LPARAM)

def clamp(v, lo=-1.0, hi=1.0):
    return max(lo, min(hi, v))
def apply_dz(v, dz):
    if abs(v) < dz:
        return 0.0
    s = 1 if v > 0 else -1
    return s * (abs(v) - dz) / (1.0 - dz)
def load_config():
    if not os.path.exists(CONFIG_FILE):
        return
    try:
        with open(CONFIG_FILE, encoding="utf-8") as f:
            loaded = json.load(f)
        for section in ("keymap", "mouse_map"):
            if section in loaded:
                state["config"][section].update(loaded[section])
        for k, v in loaded.items():
            if k not in ("keymap", "mouse_map"):
                state["config"][k] = v
    except Exception:
        pass
def save_config():
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(state["config"], f, indent=2, ensure_ascii=False)
    except Exception:
        pass

def _build_btn_maps():
    if not DEPS_OK:
        return {}, {}
    B = vg.XUSB_BUTTON
    pairs = [
        ("A",           B.XUSB_GAMEPAD_A),
        ("B",           B.XUSB_GAMEPAD_B),
        ("X",           B.XUSB_GAMEPAD_X),
        ("Y",           B.XUSB_GAMEPAD_Y),
        ("RB",          B.XUSB_GAMEPAD_RIGHT_SHOULDER),
        ("LB",          B.XUSB_GAMEPAD_LEFT_SHOULDER),
        ("LS",          B.XUSB_GAMEPAD_LEFT_THUMB),
        ("RS",          B.XUSB_GAMEPAD_RIGHT_THUMB),
        ("START",       B.XUSB_GAMEPAD_START),
        ("BACK",        B.XUSB_GAMEPAD_BACK),
        ("DPAD_UP",     B.XUSB_GAMEPAD_DPAD_UP),
        ("DPAD_DOWN",   B.XUSB_GAMEPAD_DPAD_DOWN),
        ("DPAD_LEFT",   B.XUSB_GAMEPAD_DPAD_LEFT),
        ("DPAD_RIGHT",  B.XUSB_GAMEPAD_DPAD_RIGHT),
    ]
    press   = {}
    release = {}
    for name, const in pairs:
        c = const
        press[name]   = lambda g, c=c: (g.press_button(c),   g.update())
        release[name] = lambda g, c=c: (g.release_button(c), g.update())
    press["RT"]   = lambda g: (g.right_trigger(value=255), g.update())
    press["LT"]   = lambda g: (g.left_trigger(value=255),  g.update())
    release["RT"] = lambda g: (g.right_trigger(value=0),   g.update())
    release["LT"] = lambda g: (g.left_trigger(value=0),    g.update())
    return press, release
_rev_keymap = {}
_LABEL_TO_BTN = {
    "A (Saltar)": "A", "B (Agacharse)": "B",
    "X (Recarga/Sprint)": "X", "Y (Interactuar)": "Y",
    "RB (Hombro Der)": "RB", "LB (Hombro Izq)": "LB",
    "LS (Click Izq Joy)": "LS", "RS (Click Der Joy)": "RS",
    "START (Menu)": "START", "BACK (Opciones)": "BACK",
    "DPAD Arriba": "DPAD_UP", "DPAD Abajo": "DPAD_DOWN",
    "DPAD Izquierda": "DPAD_LEFT", "DPAD Derecha": "DPAD_RIGHT",
}
_SPECIAL_KEYS = {
    "space": "space", "ctrl_l": "ctrl_l", "ctrl_r": "ctrl_r",
    "shift_l": "shift_l", "shift_r": "shift_r",
    "alt_l": "alt_l", "alt_r": "alt_r",
    "escape": "esc", "return": "enter", "tab": "tab",
    "f1":"f1","f2":"f2","f3":"f3","f4":"f4","f5":"f5",
    "f6":"f6","f7":"f7","f8":"f8","f9":"f9","f10":"f10",
    "num_0":"num_0","num_1":"num_1","num_2":"num_2","num_3":"num_3",
    "num_4":"num_4","num_5":"num_5","num_6":"num_6",
    "num_7":"num_7","num_8":"num_8","num_9":"num_9",
}
def _key_str_to_pynput(s):
    if not DEPS_OK or not s:
        return None
    if s in _SPECIAL_KEYS:
        attr = _SPECIAL_KEYS[s]
        return getattr(pkeyboard.Key, attr, None)
    return s

def build_reverse_keymap():
    result = {}
    for label, key_s in state["config"]["keymap"].items():
        btn = _LABEL_TO_BTN.get(label)
        if not btn or not key_s:
            continue
        pkey = _key_str_to_pynput(key_s)
        if pkey:
            result[pkey] = btn
    return result

def _install_mouse_hook():
    def _proc(nCode, wParam, lParam):
        if nCode >= 0 and wParam == WM_MOUSEMOVE:
            # ... tu código ...
            pass
        return ctypes.windll.user32.CallNextHookEx(
            state["_hook"], nCode, wParam, lParam
        )
    proc_pointer = HOOKPROC(_proc)
    state["_hook_proc"] = proc_pointer
    hook = ctypes.windll.user32.SetWindowsHookExW(
        WH_MOUSE_LL,
        proc_pointer,
        None,
        0
    )
    state["_hook"] = hook
    def _pump():
        msg = wt.MSG()
        while state["running"]:
            ctypes.windll.user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1)
            time.sleep(0.0005)
    threading.Thread(target=_pump, daemon=True, name="hook-pump").start()
    return bool(hook)

def _uninstall_mouse_hook():
    if state["_hook"]:
        ctypes.windll.user32.UnhookWindowsHookEx(state["_hook"])
        state["_hook"]      = None
        state["_hook_proc"] = None

def _on_click(x, y, button, pressed):
    if not state["active"] or not state["gamepad"]:
        return
    g  = state["gamepad"]
    mm = state["config"]["mouse_map"]
    if button == pmouse.Button.left:
        btn = mm.get("Click Izquierdo", "RT")
    elif button == pmouse.Button.right:
        btn = mm.get("Click Derecho", "LT")
    else:
        return
    fn = (BUTTON_MAP if pressed else BUTTON_RELEASE).get(btn)
    if fn:
        fn(g)

def _on_scroll(x, y, dx, dy):
    if not state["active"] or not state["gamepad"]:
        return
    g   = state["gamepad"]
    mm  = state["config"]["mouse_map"]
    key = "Scroll Arriba" if dy > 0 else "Scroll Abajo"
    btn = mm.get(key, "DPAD_UP" if dy > 0 else "DPAD_DOWN")
    fn  = BUTTON_MAP.get(btn)
    fr  = BUTTON_RELEASE.get(btn)
    if fn:
        fn(g)
        threading.Timer(0.12, lambda: fr(g) if fr else None).start()

def _char(key):
    try:
        return key.char.lower() if hasattr(key, "char") and key.char else None
    except Exception:
        return None

def _on_key_press(key):
    if not state["active"] or not state["gamepad"]:
        return
    g  = state["gamepad"]
    ch = _char(key)
    if ch and ch in WASD:
        state["pressed_keys"].add(ch)
        return
    lookup = ch if ch else key
    btn    = _rev_keymap.get(lookup)
    if btn:
        fn = BUTTON_MAP.get(btn)
        if fn:
            fn(g)

def _on_key_release(key):
    if not state["gamepad"]:
        return
    g  = state["gamepad"]
    ch = _char(key)
    if ch and ch in WASD:
        state["pressed_keys"].discard(ch)
        return
    lookup = ch if ch else key
    btn    = _rev_keymap.get(lookup)
    if btn:
        fn = BUTTON_RELEASE.get(btn)
        if fn:
            fn(g)

def reset_gamepad():
    g = state.get("gamepad")
    if not g:
        return
    try:
        g.left_joystick(x_value=0, y_value=0)
        g.right_joystick(x_value=0, y_value=0)
        g.left_trigger(value=0)
        g.right_trigger(value=0)
        g.update()
    except Exception:
        pass

def _update_loop():
    dt = 1.0 / 120
    while state["running"]:
        if state["active"] and state["gamepad"]:
            g   = state["gamepad"]
            cfg = state["config"]
            with state["lock"]:
                dx = state["mouse_dx"];  state["mouse_dx"] = 0.0
                dy = state["mouse_dy"];  state["mouse_dy"] = 0.0
            sm    = cfg["smoothing"]
            rx_r  = clamp(dx * cfg["sensitivity_x"])
            ry_r  = clamp(dy * cfg["sensitivity_y"])
            state["rx_smooth"] = state["rx_smooth"] * sm + rx_r * (1 - sm)
            state["ry_smooth"] = state["ry_smooth"] * sm + ry_r * (1 - sm)
            rx    = apply_dz(state["rx_smooth"], cfg["deadzone"])
            ry    = apply_dz(state["ry_smooth"], cfg["deadzone"])
            lx, ly = 0.0, 0.0
            for k in list(state["pressed_keys"]):
                if k in WASD:
                    lx += WASD[k][0]
                    ly += WASD[k][1]
            mag = math.sqrt(lx**2 + ly**2)
            if mag > 1:
                lx /= mag; ly /= mag
            try:
                g.right_joystick_float(x_value_float=rx,         y_value_float=-ry)
                g.left_joystick_float( x_value_float=clamp(lx),  y_value_float=clamp(ly))
                g.update()
            except Exception:
                pass
        time.sleep(dt)

def start_engine(status_cb):
    global _rev_keymap, BUTTON_MAP, BUTTON_RELEASE
    if not DEPS_OK:
        status_cb("ERROR: instala pynput y vgamepad", "red")
        return False
    try:
        BUTTON_MAP, BUTTON_RELEASE = _build_btn_maps()
        state["gamepad"] = vg.VX360Gamepad()
    except Exception as e:
        status_cb(f"ERROR ViGEmBus: {e}", "red")
        return False
    _rev_keymap = build_reverse_keymap()
    state.update({
        "running": True, "active": False,
        "mouse_dx": 0.0, "mouse_dy": 0.0,
        "rx_smooth": 0.0, "ry_smooth": 0.0,
        "_last_x": None, "_last_y": None,
    })
    state["pressed_keys"].clear()
    ok = _install_mouse_hook()
    if not ok:
        status_cb("Advertencia: hook de mouse falló (¿permisos?)", "yellow")
    state["_mouse_listener"] = pmouse.Listener(
        on_click=_on_click, on_scroll=_on_scroll
    )
    state["_mouse_listener"].start()
    state["key_listener"] = pkeyboard.Listener(
        on_press=_on_key_press, on_release=_on_key_release
    )
    state["key_listener"].start()
    status_cb("Motor activo · presiona ACTIVAR", "green")
    return True

def stop_engine():
    state["running"] = False
    state["active"]  = False
    state["pressed_keys"].clear()
    _uninstall_mouse_hook()
    reset_gamepad()
    for key in ("_mouse_listener", "key_listener"):
        lst = state.get(key)
        if lst:
            try: lst.stop()
            except Exception: pass
    state["gamepad"] = None

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("mouse2ps5")
        self.geometry("860x680")
        self.minsize(780, 560)
        self.configure(bg=C["bg"])
        load_config()
        self._build()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.bind("<Insert>", lambda e: self._toggle_active())

    def _build(self):
        self.sidebar = tk.Frame(self, bg=C["bg2"], width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self._logo(self.sidebar)
        self._nav(self.sidebar)
        self._statusbar(self.sidebar)

        self.main = tk.Frame(self, bg=C["bg"])
        self.main.pack(side="left", fill="both", expand=True)

        self.pages = {}
        for name in ("dashboard", "keymap", "mouse", "settings"):
            f = tk.Frame(self.main, bg=C["bg"])
            self.pages[name] = f

        self._page_dashboard()
        self._page_keymap()
        self._page_mouse()
        self._page_settings()
        self._show("dashboard")

    def _logo(self, p):
        f = tk.Frame(p, bg=C["bg2"], pady=20)
        f.pack(fill="x")
        tk.Label(f, text="🎮", font=("", 28), bg=C["bg2"]).pack()
        tk.Label(f, text="mouse2ps5", font=("Courier", 13, "bold"),
                 fg=C["accent"], bg=C["bg2"]).pack()
        tk.Label(f, text="v2.1", font=("Courier", 8),
                 fg=C["dim"], bg=C["bg2"]).pack()
        tk.Frame(p, bg=C["border"], height=1).pack(fill="x")

    def _nav(self, p):
        self._nav_btns = {}
        items = [
            ("dashboard", "⚡  Dashboard"),
            ("keymap",    "⌨️  Mapeo de Teclas"),
            ("mouse",     "🖱  Mapeo de Mouse"),
            ("settings",  "⚙️  Sensibilidad"),
        ]
        f = tk.Frame(p, bg=C["bg2"], pady=12)
        f.pack(fill="x")
        for key, label in items:
            btn = tk.Button(f, text=label, font=("Courier", 10),
                            fg=C["text"], bg=C["bg2"], bd=0,
                            activebackground=C["bg3"],
                            activeforeground=C["accent"],
                            anchor="w", padx=20, pady=10, cursor="hand2",
                            command=lambda k=key: self._show(k))
            btn.pack(fill="x")
            self._nav_btns[key] = btn

    def _statusbar(self, p):
        tk.Frame(p, bg=C["border"], height=1).pack(fill="x", side="bottom")
        self._status_lbl = tk.Label(
            p, text="● No iniciado", font=("Courier", 9),
            fg=C["dim"], bg=C["bg2"], padx=16, pady=10, anchor="w"
        )
        self._status_lbl.pack(side="bottom", fill="x")

    def _set_status(self, msg, color="dim"):
        self._status_lbl.configure(text=f"● {msg}", fg=C.get(color, C["dim"]))

    def _show(self, name):
        for f in self.pages.values():
            f.pack_forget()
        self.pages[name].pack(fill="both", expand=True)
        for k, b in self._nav_btns.items():
            b.configure(fg=C["accent"] if k == name else C["text"],
                        bg=C["bg3"]    if k == name else C["bg2"])

    def _page_dashboard(self):
        p = self.pages["dashboard"]
        self._header(p, "Dashboard", "Control central de la emulacion")

        c1 = self._card(p, "Motor del gamepad")
        self._engine_lbl = tk.Label(c1, text="⬤  DETENIDO",
                                    font=("Courier", 22, "bold"),
                                    fg=C["red"], bg=C["bg2"])
        self._engine_lbl.pack(pady=10)
        row = tk.Frame(c1, bg=C["bg2"]); row.pack(pady=6)
        self._btn_start  = self._btn(row, "▶  INICIAR MOTOR", self._do_start, "green")
        self._btn_start.pack(side="left", padx=6)
        self._btn_stop   = self._btn(row, "■  DETENER", self._do_stop, "red")
        self._btn_stop.pack(side="left", padx=6)
        self._btn_stop.configure(state="disabled")

        c2 = self._card(p, "Emulacion")
        self._toggle_lbl = tk.Label(c2, text="PAUSADO",
                                    font=("Courier", 18, "bold"),
                                    fg=C["dim"], bg=C["bg2"])
        self._toggle_lbl.pack(pady=8)
        self._btn_toggle = self._btn(c2, "ACTIVAR  [ INSERT ]",
                                     self._toggle_active, "accent")
        self._btn_toggle.pack(pady=4)
        self._btn_toggle.configure(state="disabled")

        c3 = self._card(p, "Referencia rapida")
        refs = [
            ("Mouse",    "->  Joystick derecho (camara)"),
            ("WASD",     "->  Joystick izquierdo"),
            ("Clic Izq", "->  Gatillo derecho (RT)"),
            ("Clic Der", "->  Gatillo izquierdo (LT)"),
            ("INSERT",   "->  Activar / Pausar"),
        ]
        for k, v in refs:
            r = tk.Frame(c3, bg=C["bg2"]); r.pack(fill="x", pady=1)
            tk.Label(r, text=k, font=("Courier", 9, "bold"),
                     fg=C["accent"], bg=C["bg2"], width=12, anchor="w").pack(side="left")
            tk.Label(r, text=v, font=("Courier", 9),
                     fg=C["text"], bg=C["bg2"]).pack(side="left")

    def _page_keymap(self):
        p = self.pages["keymap"]
        self._header(p, "Mapeo de Teclas",
                     "Haz clic en un boton y presiona la tecla que quieras asignar")
        wrap   = tk.Frame(p, bg=C["bg"])
        wrap.pack(fill="both", expand=True, padx=24, pady=8)
        canvas = tk.Canvas(wrap, bg=C["bg"], highlightthickness=0)
        sb     = ttk.Scrollbar(wrap, orient="vertical", command=canvas.yview)
        self._km_inner = tk.Frame(canvas, bg=C["bg"])
        self._km_inner.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self._km_inner, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self._km_widgets = {}
        self._build_km_rows()
        self._btn(p, "💾  Guardar Mapeo",
                  self._save_keymap, "accent").pack(pady=10)

    def _build_km_rows(self):
        for w in self._km_inner.winfo_children():
            w.destroy()
        hdr = tk.Frame(self._km_inner, bg=C["bg3"])
        hdr.pack(fill="x", pady=(0, 2))
        for txt, w in [("Boton del Control", 24), ("Tecla Asignada", 20), ("", 6)]:
            tk.Label(hdr, text=txt, font=("Courier", 9, "bold"),
                     fg=C["dim"], bg=C["bg3"], width=w, anchor="w",
                     padx=10, pady=6).pack(side="left")

        self._km_widgets = {}
        for label, key_s in state["config"]["keymap"].items():
            row = tk.Frame(self._km_inner, bg=C["bg2"], pady=1)
            row.pack(fill="x", pady=1)
            tk.Label(row, text=label, font=("Courier", 10),
                     fg=C["text"], bg=C["bg2"],
                     width=24, anchor="w", padx=10).pack(side="left")
            var = tk.StringVar(value=key_s or "(sin asignar)")
            lbl = tk.Label(row, textvariable=var,
                           font=("Courier", 10, "bold"),
                           fg=C["accent"], bg=C["bg3"],
                           width=20, padx=10, pady=6,
                           cursor="hand2", anchor="w")
            lbl.pack(side="left", padx=4)
            self._km_widgets[label] = (var, lbl)

            def _make(lbl_w, var_r, btn_l):
                def start(e):
                    lbl_w.configure(fg=C["yellow"],
                                    text="[ presiona tecla... ]")
                    self._listening = (lbl_w, var_r, btn_l)
                    self.bind("<KeyPress>", self._capture_key)
                lbl_w.bind("<Button-1>", start)
            _make(lbl, var, label)

            self._btn(row, "X",
                      lambda l=label: self._clear_key(l),
                      "dim", small=True).pack(side="left")

    def _capture_key(self, event):
        if not hasattr(self, "_listening"):
            return
        lbl_w, var_r, btn_l = self._listening
        key_name = event.keysym.lower()
        norm = {
            "control_l":"ctrl_l","control_r":"ctrl_r",
            "shift_l":"shift_l","shift_r":"shift_r",
            "alt_l":"alt_l","alt_r":"alt_r",
            "return":"return","escape":"escape","tab":"tab",
            "insert":"insert","delete":"delete","space":"space",
        }
        key_name = norm.get(key_name, key_name)
        var_r.set(key_name)
        lbl_w.configure(fg=C["accent"], text=key_name)
        state["config"]["keymap"][btn_l] = key_name
        self.unbind("<KeyPress>")
        del self._listening

    def _clear_key(self, label):
        if label in self._km_widgets:
            var, lbl = self._km_widgets[label]
            var.set("(sin asignar)")
            lbl.configure(text="(sin asignar)")
            state["config"]["keymap"][label] = ""

    def _save_keymap(self):
        global _rev_keymap
        save_config()
        _rev_keymap = build_reverse_keymap()
        self._set_status("Mapeo de teclas guardado", "green")

    def _page_mouse(self):
        p = self.pages["mouse"]
        self._header(p, "Mapeo de Mouse",
                     "Asigna acciones del mouse a botones del control")
        OPTIONS = ["RT","LT","A","B","X","Y","RB","LB",
                   "DPAD_UP","DPAD_DOWN","DPAD_LEFT","DPAD_RIGHT","(ninguno)"]
        card = self._card(p, "Botones y Scroll")
        self._mouse_vars = {}
        for action, default in state["config"]["mouse_map"].items():
            row = tk.Frame(card, bg=C["bg2"]); row.pack(fill="x", pady=4)
            tk.Label(row, text=action, font=("Courier", 10),
                     fg=C["text"], bg=C["bg2"],
                     width=20, anchor="w").pack(side="left")
            var = tk.StringVar(value=default)
            self._mouse_vars[action] = var
            ttk.Combobox(row, textvariable=var, values=OPTIONS,
                         width=16, state="readonly",
                         font=("Courier", 10)).pack(side="left", padx=8)
        self._btn(p, "💾  Guardar",
                  self._save_mouse, "accent").pack(pady=12)

    def _save_mouse(self):
        for action, var in self._mouse_vars.items():
            state["config"]["mouse_map"][action] = var.get()
        save_config()
        self._set_status("Mapeo de mouse guardado", "green")

    def _page_settings(self):
        p = self.pages["settings"]
        self._header(p, "Sensibilidad",
                     "Ajusta el comportamiento del joystick")
        cfg  = state["config"]
        defs = [
            ("sensitivity_x", "Sensibilidad X (horizontal)",     0.001, 0.08),
            ("sensitivity_y", "Sensibilidad Y (vertical)",       0.001, 0.08),
            ("smoothing",     "Suavizado (0=directo, 1=suave)",  0.0,   0.95),
            ("deadzone",      "Zona muerta del joystick",         0.0,   0.5),
        ]
        self._sliders = {}
        card = self._card(p, "Parametros")
        for key, label, lo, hi in defs:
            self._slider_row(card, key, label, lo, hi, cfg.get(key, 0.1))
        self._btn(p, "💾  Guardar",
                  self._save_settings, "accent").pack(pady=12)

    def _slider_row(self, parent, key, label, lo, hi, val):
        row = tk.Frame(parent, bg=C["bg2"]); row.pack(fill="x", pady=6)
        tk.Label(row, text=label, font=("Courier", 9),
                 fg=C["text"], bg=C["bg2"],
                 width=36, anchor="w").pack(side="left")
        var     = tk.DoubleVar(value=val)
        val_str = tk.StringVar(value=f"{val:.3f}")
        self._sliders[key] = var
        var.trace_add("write",
                      lambda *a: val_str.set(f"{var.get():.3f}"))
        tk.Label(row, textvariable=val_str, font=("Courier", 9, "bold"),
                 fg=C["accent"], bg=C["bg2"],
                 width=6).pack(side="right")
        ttk.Scale(row, from_=lo, to=hi, variable=var,
                  orient="horizontal", length=200).pack(side="right", padx=8)

    def _save_settings(self):
        for key, var in self._sliders.items():
            state["config"][key] = round(var.get(), 4)
        save_config()
        self._set_status("Configuracion guardada", "green")

    def _header(self, parent, title, subtitle=""):
        f = tk.Frame(parent, bg=C["bg"], pady=20, padx=24)
        f.pack(fill="x")
        tk.Label(f, text=title, font=("Courier", 18, "bold"),
                 fg=C["white"], bg=C["bg"]).pack(anchor="w")
        if subtitle:
            tk.Label(f, text=subtitle, font=("Courier", 9),
                     fg=C["dim"], bg=C["bg"]).pack(anchor="w")
        tk.Frame(parent, bg=C["border"], height=1).pack(fill="x")

    def _card(self, parent, title=""):
        w = tk.Frame(parent, bg=C["bg"], padx=24, pady=10)
        w.pack(fill="x")
        if title:
            tk.Label(w, text=title.upper(), font=("Courier", 8, "bold"),
                     fg=C["dim"], bg=C["bg"]).pack(anchor="w", pady=(0, 4))
        inner = tk.Frame(w, bg=C["bg2"], padx=16, pady=14,
                         highlightbackground=C["border"],
                         highlightthickness=1)
        inner.pack(fill="x")
        return inner

    def _btn(self, parent, text, cmd, color="accent", small=False):
        fg = C.get(color, C["accent"])
        return tk.Button(
            parent, text=text, command=cmd,
            font=("Courier", 8 if small else 10, "bold"),
            fg=C["bg"], bg=fg, activebackground=fg,
            bd=0, padx=8 if small else 18,
            pady=3 if small else 8,
            cursor="hand2", relief="flat"
        )

    def _do_start(self):
        if state["running"]: return
        ok = start_engine(self._set_status)
        if ok:
            self._engine_lbl.configure(text="⬤  ACTIVO", fg=C["green"])
            self._btn_start.configure(state="disabled")
            self._btn_stop.configure(state="normal")
            self._btn_toggle.configure(state="normal")

    def _do_stop(self):
        stop_engine()
        self._engine_lbl.configure(text="⬤  DETENIDO", fg=C["red"])
        self._toggle_lbl.configure(text="PAUSADO", fg=C["dim"])
        self._btn_start.configure(state="normal")
        self._btn_stop.configure(state="disabled")
        self._btn_toggle.configure(state="disabled")
        self._set_status("Motor detenido", "dim")

    def _toggle_active(self):
        if not state["running"]: return
        state["active"] = not state["active"]
        if state["active"]:
            state["_last_x"] = None
            state["_last_y"] = None
            self._toggle_lbl.configure(text="ACTIVO  ✓", fg=C["green"])
            self._set_status("Emulacion activa", "green")
        else:
            reset_gamepad()
            self._toggle_lbl.configure(text="PAUSADO", fg=C["dim"])
            self._set_status("Emulacion pausada", "yellow")

    def _on_close(self):
        stop_engine()
        self.destroy()

if __name__ == "__main__":
    if not DEPS_OK:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Dependencias faltantes",
            "Instala las dependencias primero:\n\n"
            "    pip install pynput vgamepad\n\n"
            "Tambien necesitas ViGEmBus driver:\n"
            "https://github.com/ViGEm/ViGEmBus/releases"
        )
        root.destroy()
        sys.exit(1)
    App().mainloop()