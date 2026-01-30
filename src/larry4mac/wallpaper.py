"""Larry plugin to set the wallpaper on MacOS"""

import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

import larry
import larry.config
from larry import pool
from larry.color import ColorList

APPLESCRIPT = "/usr/bin/osascript"
HELP = "Set the wallpaper on MacOS"
LOGGER = larry.LOGGER.getChild("larry4mac.wallpaper")
WALLPAPER_SCRIPT = """\
tell application "System Events"
    tell every desktop
        set picture to "{src}"
    end tell
end tell
"""


async def plugin(_colors: ColorList, config: larry.config.ConfigType) -> None:
    """Set the wallpaper on MacOS"""
    infile = pathlib.Path(config["input"]).expanduser()
    output = pathlib.Path(config.get("output", fallback=".")).expanduser()

    if not ensure_path_is_dir(output):
        return

    fd, output_path = tempfile.mkstemp(
        suffix=f".{infile.suffix or 'png'}", prefix="larry4mac-", dir=str(output)
    )
    os.close(fd)
    await pool.run(shutil.copyfile, infile, output_path)
    await set_wallpaper(output_path)
    await purge_old_wallappers(output, output_path)


def ensure_path_is_dir(path: pathlib.Path) -> bool:
    """Return True iff output_dir is a directory"""
    if not path.is_dir():
        errmsg = f"larry4mac.wallpaper: {path} does not exist or is not a directory."
        print(errmsg, file=sys.stderr)
        return False

    return True


async def set_wallpaper(src: str | os.PathLike) -> None:
    """Set the set the wallpaper given the path

    Uses some wicked AppleScript
    """
    LOGGER.debug("Setting wallpaper to %s", src)
    await pool.run(applescript, WALLPAPER_SCRIPT.format(src=src))


def applescript(script: str) -> None:
    """Run the given applescript"""
    with subprocess.Popen([APPLESCRIPT], stdin=subprocess.PIPE) as sp:
        assert sp.stdin
        sp.stdin.write(script.encode("utf8"))
        sp.stdin.close()


async def purge_old_wallappers(directory: pathlib.Path, current: str) -> None:
    """Given the directory and current wallpaper, purge other wallappers

    Remove other files in the directory with the pattern "larry4mac-*".
    """
    for path in directory.glob("larry4mac-*"):
        if str(path) != current and path.is_file():
            path.unlink()
