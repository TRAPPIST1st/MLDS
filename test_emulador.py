import unittest
import sys
import types

if "tkinter" not in sys.modules:
    tk_stub = types.ModuleType("tkinter")

    class _TkStub:
        def __init__(self, *args, **kwargs):
            pass

    class _Var(_TkStub):
        def __init__(self, value=None):
            self._value = value

        def set(self, value):
            self._value = value

        def get(self):
            return self._value

    tk_stub.Tk = _TkStub
    tk_stub.Frame = _TkStub
    tk_stub.Label = _TkStub
    tk_stub.Button = _TkStub
    tk_stub.Canvas = _TkStub
    tk_stub.StringVar = _Var
    tk_stub.DoubleVar = _Var
    tk_stub.Event = _TkStub
    ttk_stub = types.ModuleType("tkinter.ttk")
    ttk_stub.Scrollbar = _TkStub
    ttk_stub.Combobox = _TkStub
    ttk_stub.Scale = _TkStub
    messagebox_stub = types.ModuleType("tkinter.messagebox")
    messagebox_stub.showerror = lambda *args, **kwargs: None
    tk_stub.ttk = ttk_stub
    tk_stub.messagebox = messagebox_stub
    sys.modules["tkinter"] = tk_stub
    sys.modules["tkinter.ttk"] = ttk_stub
    sys.modules["tkinter.messagebox"] = messagebox_stub

import emulador


class _FakeKey:
    space = "SPACE"
    f12 = "F12"


class _FakeKeyCode:
    @staticmethod
    def from_vk(vk):
        return ("VK", vk)


class _FakeKeyboard:
    Key = _FakeKey
    KeyCode = _FakeKeyCode


class EmuladorTests(unittest.TestCase):
    def test_normalize_key_name_maps_tk_numpad(self):
        self.assertEqual(emulador._normalize_key_name("KP_1"), "num_1")
        self.assertEqual(emulador._normalize_key_name("kp_end"), "num_1")
        self.assertEqual(emulador._normalize_key_name("Control_L"), "ctrl_l")

    def test_build_validated_config_clamps_numeric_and_filters_values(self):
        loaded = {
            "sensitivity_x": 9,
            "sensitivity_y": "bad",
            "smoothing": -1,
            "deadzone": 9,
            "keymap": {
                "A (Saltar)": "KP_2",
                "B (Agacharse)": [],
            },
            "mouse_map": {
                "Click Izquierdo": "INVALID",
                "Click Derecho": "LT",
            },
        }
        cfg = emulador._build_validated_config(loaded)
        self.assertEqual(cfg["sensitivity_x"], 0.08)
        self.assertEqual(cfg["sensitivity_y"], emulador.DEFAULT_CONFIG["sensitivity_y"])
        self.assertEqual(cfg["smoothing"], 0.0)
        self.assertEqual(cfg["deadzone"], 0.5)
        self.assertEqual(cfg["keymap"]["A (Saltar)"], "num_2")
        self.assertEqual(cfg["keymap"]["B (Agacharse)"], emulador.DEFAULT_CONFIG["keymap"]["B (Agacharse)"])
        self.assertEqual(cfg["mouse_map"]["Click Izquierdo"], emulador.DEFAULT_CONFIG["mouse_map"]["Click Izquierdo"])
        self.assertEqual(cfg["mouse_map"]["Click Derecho"], "LT")

    def test_key_str_to_pynput_supports_numpad_and_special_keys(self):
        prev_deps_ok = emulador.DEPS_OK
        prev_pkeyboard = getattr(emulador, "pkeyboard", None)
        try:
            emulador.DEPS_OK = True
            emulador.pkeyboard = _FakeKeyboard
            self.assertEqual(emulador._key_str_to_pynput("num_3"), ("VK", 0x63))
            self.assertEqual(emulador._key_str_to_pynput("f12"), "F12")
            self.assertEqual(emulador._key_str_to_pynput("x"), "x")
            self.assertIsNone(emulador._key_str_to_pynput("unknown_special"))
        finally:
            emulador.DEPS_OK = prev_deps_ok
            emulador.pkeyboard = prev_pkeyboard

    def test_accumulate_mouse_delta_updates_dx_dy(self):
        with emulador.state["lock"]:
            prev = {
                "_last_x": emulador.state.get("_last_x"),
                "_last_y": emulador.state.get("_last_y"),
                "mouse_dx": emulador.state.get("mouse_dx"),
                "mouse_dy": emulador.state.get("mouse_dy"),
                "_last_hook_move_ts": emulador.state.get("_last_hook_move_ts"),
            }
            emulador.state["_last_x"] = None
            emulador.state["_last_y"] = None
            emulador.state["mouse_dx"] = 0.0
            emulador.state["mouse_dy"] = 0.0
            emulador.state["_last_hook_move_ts"] = 0.0
        try:
            emulador._accumulate_mouse_delta(100, 200)
            emulador._accumulate_mouse_delta(115, 230, hook_event=True)
            with emulador.state["lock"]:
                self.assertEqual(emulador.state["mouse_dx"], 15.0)
                self.assertEqual(emulador.state["mouse_dy"], 30.0)
                self.assertEqual(emulador.state["_last_x"], 115)
                self.assertEqual(emulador.state["_last_y"], 230)
                self.assertGreater(emulador.state["_last_hook_move_ts"], 0.0)
        finally:
            with emulador.state["lock"]:
                emulador.state.update(prev)

    def test_on_move_fallback_ignores_when_recent_hook_event(self):
        with emulador.state["lock"]:
            prev = {
                "active": emulador.state.get("active"),
                "gamepad": emulador.state.get("gamepad"),
                "_use_hook_mouse_move": emulador.state.get("_use_hook_mouse_move"),
                "_last_hook_move_ts": emulador.state.get("_last_hook_move_ts"),
                "_last_x": emulador.state.get("_last_x"),
                "_last_y": emulador.state.get("_last_y"),
                "mouse_dx": emulador.state.get("mouse_dx"),
                "mouse_dy": emulador.state.get("mouse_dy"),
            }
            emulador.state["active"] = True
            emulador.state["gamepad"] = object()
            emulador.state["_use_hook_mouse_move"] = True
            emulador.state["_last_hook_move_ts"] = emulador.time.monotonic()
            emulador.state["_last_x"] = 10
            emulador.state["_last_y"] = 10
            emulador.state["mouse_dx"] = 0.0
            emulador.state["mouse_dy"] = 0.0
        try:
            emulador._on_move(20, 30)
            with emulador.state["lock"]:
                self.assertEqual(emulador.state["mouse_dx"], 0.0)
                self.assertEqual(emulador.state["mouse_dy"], 0.0)
            with emulador.state["lock"]:
                emulador.state["_use_hook_mouse_move"] = False
            emulador._on_move(20, 30)
            with emulador.state["lock"]:
                self.assertEqual(emulador.state["mouse_dx"], 10.0)
                self.assertEqual(emulador.state["mouse_dy"], 20.0)
        finally:
            with emulador.state["lock"]:
                emulador.state.update(prev)

    def test_mouse_delta_to_stick_does_not_apply_deadzone(self):
        self.assertAlmostEqual(emulador._mouse_delta_to_stick(1.0, 0.015), 0.015)
        self.assertAlmostEqual(emulador._mouse_delta_to_stick(-2.0, 0.015), -0.03)
        self.assertEqual(emulador._mouse_delta_to_stick(999.0, 0.015), 1.0)

    def test_suppress_stick_noise(self):
        self.assertEqual(emulador._suppress_stick_noise(0.001), 0.0)
        self.assertAlmostEqual(emulador._suppress_stick_noise(0.015), 0.015)
        self.assertEqual(emulador._suppress_stick_noise(2.0), 1.0)


if __name__ == "__main__":
    unittest.main()
