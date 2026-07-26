"""Minimal desktop stub for the calculator's `ti_system` module.

Only exists so verify_program.py can run a program that imports it without
crashing on a PC. The functions are no-ops or return empty data -- they do
NOT emulate the calculator.

A program that depends on real ti_system behaviour cannot be meaningfully
verified off-device. Test that one on the calculator itself, and say so in
the delivery.
"""

_lists = {}
_vars = {}


def recall_list(name):
    return list(_lists.get(name, []))


def store_list(name, values):
    _lists[name] = list(values)
    return None


def recall_value(name):
    return _vars.get(name, 0)


def store_value(name, value):
    _vars[name] = value
    return None


def eval_function(name, arg):
    raise NotImplementedError(
        "ti_system.eval_function() needs the calculator. Test on device.")


def disp_clr():
    return None


def disp_at(*_args, **_kwargs):
    return None


def disp_wait():
    return None


def escape():
    return False


def get_key():
    return ""


def get_platform():
    return "stub"
