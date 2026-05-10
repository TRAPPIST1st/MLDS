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
        prev_keyboard = getattr(emulador, "pkeyboard", None)
        try:
            emulador.DEPS_OK = True
            emulador.pkeyboard = _FakeKeyboard
            self.assertEqual(emulador._key_str_to_pynput("num_3"), ("VK", 0x63))
            self.assertEqual(emulador._key_str_to_pynput("f12"), "F12")
            self.assertEqual(emulador._key_str_to_pynput("x"), "x")
            self.assertIsNone(emulador._key_str_to_pynput("unknown_special"))
        finally:
            emulador.DEPS_OK = prev_deps_ok
            emulador.pkeyboard = prev_keyboard


if __name__ == "__main__":
    unittest.main()
