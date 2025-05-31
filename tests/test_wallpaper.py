# pylint: disable=missing-docstring
import configparser
import subprocess as sp
from pathlib import Path
from unittest import TestCase, mock

from larry.color import ColorList
from larry.config import ConfigType

from larry4mac import wallpaper


@mock.patch.object(wallpaper, "set_wallpaper")
class PluginTests(TestCase):
    def test(self, set_wallpaper: mock.Mock) -> None:
        colors: ColorList = []
        parser = configparser.ConfigParser()
        parser.add_section("larry4mac")
        config = ConfigType(parser, name="larry4mac")
        config["input"] = "/dev/null"

        wallpaper.plugin(colors, config)

        self.assertEqual(2, set_wallpaper.call_count)
        set_wallpaper.assert_called_with(Path("/dev/null"))


@mock.patch.object(wallpaper.subprocess, "Popen")
class SetWallpaperTests(TestCase):
    def test(self, popen_cls: mock.Mock) -> None:
        path = "/dev/null"
        wallpaper.set_wallpaper(path)

        popen_cls.assert_called_once_with(["/usr/bin/osascript"], stdin=sp.PIPE)
        popen = popen_cls.return_value
        context = popen.__enter__.return_value
        stdin = context.stdin
        message = stdin.write.call_args[0][0]
        self.assertIn(b'set picture to "/dev/null"\n', message)
