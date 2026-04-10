import glob
from os.path import dirname, isfile

# 👇 PUT YOUR PLAY FILE HERE (exact path)
PRIORITY_FIRST = [
    "EsproMusic.plugins.play.play"   # ⚠️ change if your path is different
]

def __list_all_modules():
    work_dir = dirname(__file__)
    mod_paths = glob.glob(work_dir + "/*/*.py")

    return [
        (((f.replace(work_dir, "")).replace("/", "."))[:-3])
        for f in mod_paths
        if isfile(f) and f.endswith(".py") and not f.endswith("__init__.py")
    ]

ALL_FOUND = __list_all_modules()

ALL_MODULES = []

# ✅ 1. LOAD PLAY FIRST
for mod in PRIORITY_FIRST:
    if mod in ALL_FOUND:
        ALL_MODULES.append(mod)

# ✅ 2. LOAD EVERYTHING ELSE
for mod in ALL_FOUND:
    if mod not in ALL_MODULES:
        ALL_MODULES.append(mod)

__all__ = ALL_MODULES + ["ALL_MODULES"]
