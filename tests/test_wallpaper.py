# pylint: disable=missing-docstring
import subprocess as sp
from unittest import TestCase, mock

from larry4mac import wallpaper


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
