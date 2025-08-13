"""Larry plugin to set the wallpaper on MacOS"""

import os
import pathlib
import subprocess
import tempfile

import larry
import larry.config
from larry.color import ColorList

LOGGER = larry.LOGGER.getChild("larry4mac.wallpaper")

HELP = "Set the wallpaper on MacOS"


def plugin(_colors: ColorList, config: larry.config.ConfigType) -> None:
    """Set the wallpaper on MacOS"""
    infile = pathlib.Path(config["input"]).expanduser()

    with tempfile.TemporaryDirectory() as tmpdir:
        link = pathlib.Path(tmpdir) / f"larry4mac.{infile.suffix or 'png'}"
        LOGGER.debug("Linking from %s to %s", link, infile)
        link.symlink_to(infile)
        set_wallpaper(link)
        set_wallpaper(infile)


def set_wallpaper(src: str | os.PathLike) -> None:
    """Set the set the wallpaper given the path

    Uses some wicked AppleScript
    """
    script = f"""\
tell application "System Events"
    tell every desktop
        set picture to "{src}"
    end tell
end tell
"""
    LOGGER.debug("Setting wallpaper to %s", src)
    applescript(script)


def applescript(script: str) -> None:
    """Run the given applescript"""
    with subprocess.Popen(["/usr/bin/osascript"], stdin=subprocess.PIPE) as sp:
        assert sp.stdin
        sp.stdin.write(script.encode("utf8"))
        sp.stdin.close()
