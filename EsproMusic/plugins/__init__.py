import glob
from os.path import dirname, isfile

# ================== PRIORITY ==================
PRIORITY_MODULES = [
    "EsproMusic.plugins.play.play",     # 🎵 music first
    "EsproMusic.plugins.bot",
]

SECONDARY_MODULES = [
    "EsproMusic.plugins.management.locks",
    "EsproMusic.plugins.management.approve",
    "EsproMusic.plugins.management.antichannel",
]

# ================== AUTO LOAD ==================
def __list_all_modules():
    work_dir = dirname(__file__)
    mod_paths = glob.glob(work_dir + "/*/*.py")

    modules = [
        (((f.replace(work_dir, "")).replace("/", "."))[:-3])
        for f in mod_paths
        if isfile(f) and f.endswith(".py") and not f.endswith("__init__.py")
    ]

    return modules

ALL_FOUND = __list_all_modules()

# ================== FINAL ORDER ==================
ALL_MODULES = []

# 1. add priority first
for mod in PRIORITY_MODULES:
    if mod in ALL_FOUND:
        ALL_MODULES.append(mod)

# 2. add remaining (excluding duplicates)
for mod in ALL_FOUND:
    if mod not in ALL_MODULES and mod not in SECONDARY_MODULES:
        ALL_MODULES.append(mod)

# 3. add heavy modules LAST
for mod in SECONDARY_MODULES:
    if mod in ALL_FOUND:
        ALL_MODULES.append(mod)

__all__ = ALL_MODULES + ["ALL_MODULES"]
