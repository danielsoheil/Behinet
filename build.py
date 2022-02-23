import os
import sys
import PyInstaller.__main__

if os.name == 'nt':
    pyinstaller_syntax = ';'
else:
    pyinstaller_syntax = ':'


os.system(' '.join([sys.executable, "setup.py", "build_ext"]))

with open("requirements.txt") as f:
    requirements = f.read()

pyinstaller_entrypoint = ["launcher.py", "--clean", "--onefile"]

for line in requirements.split('\n'):
    if len(line) > 2:
        pyinstaller_entrypoint.append('--hidden-import=' + line)

for name in os.listdir("build"):
    if name.startswith('lib'):
        pyinstaller_entrypoint.append(f'--add-data=build/{name}{pyinstaller_syntax}.')

pyinstaller_entrypoint.append(f'--add-data=dependencies{pyinstaller_syntax}dependencies')
PyInstaller.__main__.run(pyinstaller_entrypoint)
