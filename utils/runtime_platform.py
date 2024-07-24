import subprocess, logging, venv, sys, re, os
from contextlib import suppress


logger = logging.getLogger(__name__)

_venv_name = ".venv"

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


def run_popen(command, **kwargs) -> int:
    p = subprocess.Popen(command, **kwargs)
    with suppress(KeyboardInterrupt):
        returncode = p.wait()
        return returncode
    return -1


def check_platform():
    # if venv not exists then create it
    if not os.path.isfile(PATH_TO_PYTHON):
        logger.info(f"Creating {_venv_name}...")
        venv.create(_venv_name, with_pip=True, upgrade_deps=True)
        install_packages()
        start_venv()
    
    elif not in_venv():
        start_venv()
    check_packages()


def install_packages():
    custom_requirements = "requirements.txt"
    command = [PATH_TO_PYTHON, "-m", "pip", "install", "-r", custom_requirements]
    logger.info(f"Starting install packages from {custom_requirements!r}")

    returncode = run_popen(command)
    if returncode != 0:
        logger.error("idk what happened. write to me, maybe i can do something: https://a1ekzfame.t.me")
        exit(returncode)
    logger.info("Packages installed")
    return


def install_package(package: str) -> bool:
    command = [PATH_TO_PYTHON, "-m", "pip", "install", package]
    logger.info(f"Starting install package {package!r}")

    returncode = run_popen(command)
    if returncode != 0:
        logger.error("idk what happened. something goes wrong")
        return False
    logger.info("Package installed")
    return True


def check_packages():
    ignore_list = ["python"]
    with open("requirements.txt") as file: raw = file.read()
    packages_excepted: list[str] = []
    for a in raw.splitlines():
        b = re.match(r"(\w+)==(.+)", a.lower())
        if b is not None:
            packages_excepted.append(f"{b.group(1)}=={b.group(2)}")
    
    packages_actual: list[str] = []
    for a in os.listdir(os.sep.join([_venv_name, "Lib", "site-packages"])):
        b = re.fullmatch(r"(\w+)-([\d.]+)\.dist-info", a.lower())
        if b is not None:
            packages_actual.append(f"{b.group(1)}=={b.group(2)}")

    if not all([a in packages_actual for a in packages_excepted]):
        difference = [a for a in packages_excepted if a not in packages_actual and a not in ignore_list]
        for package in difference:
            install_package(package)


def start_venv():
    command = [PATH_TO_PYTHON, "main.py", "--in-venv"]
    logger.info(f"Starting main.py with {PATH_TO_PYTHON!r}")
    returncode = run_popen(command)
    exit(returncode)


check_platform()
