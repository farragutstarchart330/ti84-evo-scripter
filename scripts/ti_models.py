#!/usr/bin/env python3
"""Shared model registry for the TI calculator family.

lint_ti_python.py, simulate_ti84.py, preflight.py and run_checks.py all read
their per-model rules from here, so there is one place to correct a fact.

Field notes:
  python        False means the model has no Python App at all -- the skill
                cannot target it and must say so.
  modules       Modules importable out of the box.
  extra_modules Modules that exist for the model but must be downloaded and
                sent separately. Using one is a WARN, not an ERROR.
  screen_cols   APPROXIMATE console width used only for wrap warnings. These
                are conservative estimates, not documented TI specs.
  connect       The transfer software that serves this model. Getting this
                wrong is a common mistake: TI Connect CE does not serve the
                Evo, and TI Connect Evo does not serve the CE family.
"""

CORE_MODULES = {"math", "random", "time", "sys", "gc", "builtins"}
TI_CORE = {"ti_system", "ti_plotlib", "ti_hub", "ti_rover"}
CE_GRAPHICS = {"ti_draw", "ti_image", "ti_graphics"}

CONNECT_EVO = {
    "name": "TI Connect Evo",
    "url": "connectevo.ti.com",
    "kind": "web (Chrome 143+, WebUSB)",
}
CONNECT_CE = {
    "name": "TI Connect CE",
    "url": "education.ti.com (desktop download)",
    "kind": "desktop (Windows / macOS)",
}

MODELS = {
    # ---- current generation -----------------------------------------
    "evo": {
        "label": "TI-84 Evo",
        "region": "US / international",
        "python": True,
        "engine": "native ARM Cortex 156 MHz (no coprocessor)",
        "exam_led": False,
        "connect": CONNECT_EVO,
        "modules": CORE_MODULES | TI_CORE | {"cmath"},
        "extra_modules": set(),
        "removed": {"turtle"},
        "screen_cols": 30,
        "basic_ext": ".8xp2",
        "notes": "Launched 28 Apr 2026. TI-BASIC is not backward compatible "
                 "with .8xp files; Python is portable from the CE family.",
    },
    "evo-t": {
        "label": "TI-84 Evo-T",
        "region": "Europe",
        "python": True,
        "engine": "native ARM Cortex 156 MHz (no coprocessor)",
        "exam_led": True,
        "connect": CONNECT_EVO,
        "modules": CORE_MODULES | TI_CORE | {"cmath"},
        "extra_modules": set(),
        "removed": {"turtle"},
        "screen_cols": 30,
        "basic_ext": ".8xp2",
        "notes": "European variant with the exam-mode LED on the top edge, "
                 "required by several EU boards (mandatory in France). Exam "
                 "mode disables user programs while active.",
    },

    # ---- CE family (Python coprocessor) ------------------------------
    "ce-python": {
        "label": "TI-84 Plus CE Python",
        "region": "US",
        "python": True,
        "engine": "Atmel ATSAMD21E18A ARM Cortex-M0+ coprocessor over UART",
        "exam_led": False,
        "connect": CONNECT_CE,
        "modules": CORE_MODULES | TI_CORE | CE_GRAPHICS,
        "extra_modules": {"turtle", "ce_chart", "ce_box", "ce_quivr"},
        "removed": set(),
        "screen_cols": 26,
        "basic_ext": ".8xp",
        "notes": "Python runs on a second chip. No public emulator can run "
                 "it -- CEmu does not emulate the coprocessor.",
    },
    "ce-t-python": {
        "label": "TI-84 Plus CE-T Python Edition",
        "region": "Europe",
        "python": True,
        "engine": "Atmel ATSAMD21E18A ARM Cortex-M0+ coprocessor over UART",
        "exam_led": True,
        "connect": CONNECT_CE,
        "modules": CORE_MODULES | TI_CORE | CE_GRAPHICS,
        "extra_modules": {"turtle", "ce_chart", "ce_box", "ce_quivr"},
        "removed": set(),
        "screen_cols": 26,
        "basic_ext": ".8xp",
        "notes": "European CE with the Press-to-Test LED.",
    },
    "83pce-python": {
        "label": "TI-83 Premium CE Edition Python",
        "region": "France",
        "python": True,
        "engine": "Atmel ATSAMD21E18A ARM Cortex-M0+ coprocessor over UART",
        "exam_led": True,
        "connect": CONNECT_CE,
        "modules": CORE_MODULES | TI_CORE | CE_GRAPHICS,
        "extra_modules": {"turtle", "ce_chart", "ce_box", "ce_quivr"},
        "removed": set(),
        "screen_cols": 26,
        "basic_ext": ".8xp",
        "notes": "French-market CE. OS and menus are localised in French; "
                 "Python keywords are still English. Extra modules (turtle, "
                 "ce_chart, ce_box, ce_quivr) are separate downloads.",
    },
    "82aep": {
        "label": "TI-82 Advanced Edition Python",
        "region": "France",
        "python": True,
        "engine": "Python App (monochrome model)",
        "exam_led": True,
        "connect": CONNECT_CE,
        "modules": CORE_MODULES | {"ti_system", "ti_plotlib"},
        "extra_modules": set(),
        "removed": {"turtle"},
        "screen_cols": 16,
        "basic_ext": ".8xp",
        "notes": "Monochrome, narrow screen. Keep printed labels very short "
                 "and do not assume ti_hub/ti_rover or graphics modules.",
    },

    # ---- no Python: the skill must refuse these ----------------------
    "ce": {
        "label": "TI-84 Plus CE (non-Python)",
        "region": "US",
        "python": False,
        "engine": "eZ80, no Python coprocessor",
        "exam_led": False,
        "connect": CONNECT_CE,
        "modules": set(),
        "extra_modules": set(),
        "removed": set(),
        "screen_cols": 26,
        "basic_ext": ".8xp",
        "notes": "No Python App. Either use TI-BASIC (out of scope for this "
                 "skill) or move to a Python-capable model.",
    },
    "ce-t": {
        "label": "TI-84 Plus CE-T (non-Python)",
        "region": "Europe",
        "python": False,
        "engine": "eZ80, no Python coprocessor",
        "exam_led": True,
        "connect": CONNECT_CE,
        "modules": set(),
        "extra_modules": set(),
        "removed": set(),
        "screen_cols": 26,
        "basic_ext": ".8xp",
        "notes": "No Python App.",
    },
    "84t": {
        "label": "TI-84 Plus T",
        "region": "Netherlands",
        "python": False,
        "engine": "monochrome, no Python",
        "exam_led": True,
        "connect": CONNECT_CE,
        "modules": set(),
        "extra_modules": set(),
        "removed": set(),
        "screen_cols": 16,
        "basic_ext": ".8xp",
        "notes": "Dutch exam model. TI-BASIC only.",
    },
    "82advanced": {
        "label": "TI-82 Advanced (non-Python)",
        "region": "France",
        "python": False,
        "engine": "monochrome, no Python",
        "exam_led": True,
        "connect": CONNECT_CE,
        "modules": set(),
        "extra_modules": set(),
        "removed": set(),
        "screen_cols": 16,
        "basic_ext": ".8xp",
        "notes": "No Python App. Not to be confused with the "
                 "TI-82 Advanced Edition Python.",
    },
}

# Spoken / written names the user is likely to type.
ALIASES = {
    "ti-84 evo": "evo", "ti84 evo": "evo", "84evo": "evo",
    "ti-84 evo-t": "evo-t", "evo t": "evo-t", "84evot": "evo-t",
    "ti-84 plus ce python": "ce-python", "84ce python": "ce-python",
    "cepy": "ce-python", "ce python": "ce-python",
    "ti-84 plus ce-t python": "ce-t-python", "cet python": "ce-t-python",
    "ti-83 premium ce python": "83pce-python", "83pce": "83pce-python",
    "83 premium ce": "83pce-python", "premium ce python": "83pce-python",
    "ti-82 advanced edition python": "82aep", "82aep": "82aep",
    "ti-84 plus ce": "ce", "84ce": "ce",
    "ti-84 plus ce-t": "ce-t",
    "ti-84 plus t": "84t", "84t": "84t",
    "ti-82 advanced": "82advanced",
}

DEFAULT_MODEL = "evo"

# Out of scope, but users ask. Give a straight answer instead of guessing.
OUT_OF_SCOPE = {
    "nspire": "TI-Nspire CX II / CX II-T run Python, but on a different "
              "platform: .tns documents, different modules, and TI-Nspire "
              "software rather than TI Connect. This skill does not target "
              "them -- the generated .py will not transfer the same way.",
    "hp": "Not a TI platform.",
    "casio": "Casio's Python (fx-CG50, fx-9750GIII) is a different "
             "implementation with different modules. Out of scope.",
}


def resolve(name):
    """Map a user-supplied model string to a registry key, or None."""
    if not name:
        return DEFAULT_MODEL
    key = name.strip().lower()
    if key in MODELS:
        return key
    if key in ALIASES:
        return ALIASES[key]
    squashed = key.replace("_", "-").replace(" ", "-")
    if squashed in MODELS:
        return squashed
    if squashed in ALIASES:
        return ALIASES[squashed]
    for alias, target in ALIASES.items():
        if alias.replace(" ", "") == key.replace(" ", "").replace("-", ""):
            return target
    return None


def get(name=None):
    """Return the model dict. Raises KeyError with a helpful list."""
    key = resolve(name)
    if key is None:
        raise KeyError(
            "unknown model %r. Known keys: %s"
            % (name, ", ".join(sorted(MODELS))))
    model = dict(MODELS[key])
    model["key"] = key
    return model


def python_capable():
    return sorted(k for k, v in MODELS.items() if v["python"])


def describe(key=None):
    m = get(key)
    return "%s (%s) - %s" % (m["label"], m["region"],
                             "Python" if m["python"] else "NO Python App")


if __name__ == "__main__":
    print("Python-capable targets:")
    for k in python_capable():
        m = MODELS[k]
        print("  %-14s %-34s %-16s cols~%d  %s"
              % (k, m["label"], m["region"], m["screen_cols"],
                 m["connect"]["name"]))
    print("\nNo Python App (skill must refuse):")
    for k in sorted(MODELS):
        if not MODELS[k]["python"]:
            print("  %-14s %-34s %s"
                  % (k, MODELS[k]["label"], MODELS[k]["region"]))
