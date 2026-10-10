import platform
import subprocess
import re
import sys

from collections.abc import Sequence
from typing import Any


class CompatibiltyError(Exception):
    """Error raised when devices operating system is not compatible with the script"""

    def __init__(self, message: str, device_os: str) -> None:
        super().__init__()
        self._device_os: str = device_os
        self._message: str = message

    def __str__(self) -> str:
        """Formatted string with information to get logged when error is raised"""
        return f"{self._message}\n(Incompatible Operating System: {self._device_os})"


# Type aliases for system cmmands dictinary
type Pipeline = tuple[str, ...]
type SystemCommands = dict[str, Pipeline]

GPU_COMMANDS: SystemCommands = {
    "Linux": ("lspci",),
    "Darwin": ("system_profiler", "SPDisplaysDataType"),
    "win11": (
        "powershell",
        "-Command",
        "Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name",
    ),
    "win-legacy": ("wmic", "path", "Win32_VideoController", "get", "name"),
}


def _get_device_output() -> str:
    """Calls system to get string of connected GPUs"""
    device_os: str = platform.system()

    if device_os not in ["Linux", "Darwin", "Windows"]:
        raise CompatibiltyError(
            "The GPU info cannot be obtained on this device", device_os
        )

    # use powershell on Windows 11, batch on older Windows versions
    if device_os == "Windows":
        version = platform.release()
        if version != "11":
            device_os = "win-legacy"

        else:
            device_os = "win11"

    cmd: Pipeline = GPU_COMMANDS[device_os]

    return _run_cmd(cmd)


def _run_cmd(cmd: Sequence[str]) -> str:
    """Runs command to get output containing all connected device names"""
    flags: dict[str, Any] = {}

    # flags to hide console window
    if sys.platform.startswith("win"):
        flags["creationflags"] = (
            subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW
        )
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        flags["startupinfo"] = si

    else:
        flags["start_new_session"] = True
    
    try:
        proc = subprocess.run(
            cmd, capture_output=True, check=True, shell=False, text=True, **flags
        )

    except FileNotFoundError as e:
        raise FileNotFoundError("Command not found in PATH") from e

    except PermissionError as e:
        raise PermissionError("Permission denied when running system command") from e

    except subprocess.CalledProcessError as e:
        raise RuntimeError("Subprocess failed") from e

    except OSError as e:
        raise OSError("OS error while running subprocess") from e

    else:
        return proc.stdout


def _parse_linux_output(output: str) -> list[str]:
    gpus = []

    for line in output.splitlines():
        if any(x in line.lower() for x in ("vga", "3d", "video")):
            gpus.append(line.split(": ", 1)[1].split(" (rev")[0])

    return gpus


def _parse_mac_output(output: str) -> list[str]:
    gpus = []

    for line in output.splitlines():
        if "Chipset Model:" in line:
            gpus.append(line.split(":", 1)[1].strip())

    return gpus


def _parse_win_output(output: str) -> list[str]:
    gpus = []

    for line in output.splitlines():
        if line.lower not in ["name", "names"] or line != "":
            gpus.append(line)

    return gpus


def _remove_symbols(gpu_names: list[str]) -> list[str]:
    """ Remove special characters and symbols added to GPU names """
    cleaned_gpus = []

    for string in gpu_names:
        stripped = re.sub(r"[\($@*&?-].*[\)$@*&?-]", "", string).strip()

        if stripped != "":
            cleaned_gpus.append(stripped)

    return cleaned_gpus


def gpu_fullnames() -> list[str]:
    """ Returns fullnames of connected GPU devices """
    output: str = _get_device_output()

    if sys.platform.startswith("win"):
        gpus = _parse_win_output(output)
    elif sys.platform.startswith("linux"):
        gpus = _parse_linux_output(output)
    elif sys.platform.startswith("darwin"):
        gpus = _parse_mac_output(output)
    
    return _remove_symbols(gpus)


def gpu_manufacturers() -> list[str]:
    """
    Returns list of manufacturer names of all connected GPUs

    Possible returns options:
        nvidia - for NVIDIA GPUS
        amd - for AMD for dedicated and integrated GPUs
        intel - for Intel for dedicated and integrated GPUs
        apple - for Macbook M5 GPUs
        adapter - return value for operating systems hosted on virtual machines / containers, 
                  or due to missing drivers
    """
    gpus = gpu_fullnames()    

    manufacturers: list[str] = []

    for gpu in gpus:
        split_name = gpu.split()

        # Linux devices may use Advanced Micro Devices, Inc instead on AMD
        if split_name[0].lower() == "advanced":
            manufacturers.append("amd")
            continue

        # possible options for OS run on virtual machines, and containers
        elif split_name[0].lower in ["microsoft", "vmware", "virtualbox"]:
            manufacturers.append("adapter")
            continue

        manufacturers.append(split_name[0].lower())

    return list(dict.fromkeys(manufacturers))
