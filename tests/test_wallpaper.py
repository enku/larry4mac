# pylint: disable=missing-docstring
import configparser
import contextlib
import io
import pathlib
import subprocess as sp
import tempfile
from unittest import IsolatedAsyncioTestCase, mock

from larry.config import ConfigType

from larry4mac import wallpaper


@mock.patch.object(wallpaper, "set_wallpaper")
class PluginTests(IsolatedAsyncioTestCase):
    async def test(self, set_wallpaper: mock.Mock) -> None:
        parser = configparser.ConfigParser()
        parser.add_section("larry4mac")
        config = ConfigType(parser, name="larry4mac")
        config["input"] = "/dev/null"

        with tempfile.TemporaryDirectory() as output:
            config["output"] = output
            await wallpaper.plugin([], config)

        self.assertEqual(1, set_wallpaper.call_count)
        path = set_wallpaper.call_args[0][0]
        self.assertTrue(path.startswith(f"{output}/larry4mac-"))

    async def test_removes_previous_wallappers(self, set_wallpaper: mock.Mock) -> None:
        parser = configparser.ConfigParser()
        parser.add_section("larry4mac")
        config = ConfigType(parser, name="larry4mac")
        config["input"] = "/dev/null"

        with tempfile.TemporaryDirectory() as output:
            config["output"] = output
            await wallpaper.plugin([], config)

            path = set_wallpaper.call_args[0][0]
            self.assertTrue(pathlib.Path(path).exists())

            await wallpaper.plugin([], config)
            self.assertFalse(pathlib.Path(path).exists())


class PluginOutputTests(IsolatedAsyncioTestCase):
    async def test_warn_if_output_is_not_directory(self) -> None:
        parser = configparser.ConfigParser()
        parser.add_section("larry4mac")
        config = ConfigType(parser, name="larry4mac")
        config["input"] = "/dev/null"
        config["output"] = "/dev/null"
        stderr = io.StringIO()

        with contextlib.redirect_stderr(stderr):
            await wallpaper.plugin([], config)

        self.assertEqual(
            stderr.getvalue(),
            "larry4mac.wallpaper: /dev/null does not exist or is not a directory.\n",
        )


@mock.patch.object(wallpaper.subprocess, "Popen")
class SetWallpaperTests(IsolatedAsyncioTestCase):
    async def test(self, popen_cls: mock.Mock) -> None:
        path = "/dev/null"
        await wallpaper.set_wallpaper(path)

        popen_cls.assert_called_once_with([wallpaper.APPLESCRIPT], stdin=sp.PIPE)
        popen = popen_cls.return_value
        context = popen.__enter__.return_value
        stdin = context.stdin
        message = stdin.write.call_args[0][0]
        self.assertIn(b'set picture to "/dev/null"\n', message)
