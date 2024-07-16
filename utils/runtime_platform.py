import subprocess, logging, venv, sys, os
from contextlib import suppress


logger = logging.getLogger(__name__)

_venv_name = "venv"

# i know only about two paths xd
if sys.platform == "linux":
    VENV = [_venv_name, "bin"]
    _PYTHON = ["python"]

else:
    VENV = [_venv_name, "Scripts"]
    _PYTHON = ["python.exe"]


PYTHON = VENV + _PYTHON
PATH_TO_PYTHON = os.sep.join(PYTHON)


def in_venv():
    return (sys.prefix != sys.base_prefix) or (len(sys.argv)>1 and sys.argv[2] == "--in-venv")


def run_popen(command) -> int:
    p = subprocess.Popen(command)
    with suppress(KeyboardInterrupt):
        returncode = p.wait()
        return returncode
    return -1


def check_platform():
    # if venv not exists then create it
    if not os.path.isfile(PATH_TO_PYTHON):
        # print(f"Creating {_venv_name}...")
        venv.create(_venv_name, with_pip=True)
        install_packages()
        start_venv()
    
    elif not in_venv():
        start_venv()


def install_packages():
    custom_requirements = "requirements.txt"
    command = [PATH_TO_PYTHON, "-m", "pip", "install", "-r", custom_requirements]
    # print(f"Starting install packages from {custom_requirements!r}")

    returncode = run_popen(command)
    if returncode != 0:
        # logger.error("idk what happened. write to me, maybe i can do something: https://a1ekzfame.t.me")
        exit(returncode)
    # print("Packages installed")
    return


def install_package(package: str) -> bool:
    command = [PATH_TO_PYTHON, "-m", "pip", "install", package]
    # print(f"Starting install package {package!r}")

    returncode = run_popen(command)
    if returncode != 0:
        # logger.error("idk what happened. something goes wrong")
        return False
    # print("Package installed")
    return True


def start_venv():
    command = [PATH_TO_PYTHON, "main.py", "--in-venv"]
    # print(f"Starting main.py with {PATH_TO_PYTHON!r}")
    returncode = run_popen(command)
    exit(returncode)


check_platform()
