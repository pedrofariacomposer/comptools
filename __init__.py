import os
__all__ = []

for entry in os.scandir('.'):
    if entry.is_file():
        if '.py' in entry.name:
            if entry.name != "__init__.py":
                first, last = entry.name.split(".")
                __all__.append(first)
if __name__ == "__main__":
    print(__all__)