# larry4mac

larry4mac is a set of [larry](https://github.com/enku/larry) plugins for
MacOS.

### Plugins

#### wallpaper

Thus far there is only the wallpaper plugin. To enable it add the following to
your config file:

```
[larry]
output = ~/Pictures/larry

plugins =
   larry4mac.wallpaper

[plugins:larry4mac.wallpaper]
input = ~/Pictures/larry
```

> [!NOTE]
> The `input` for larry4mac.wallpaper (normally) should be the `output` for
> larry.

> Note: The default location for the config file on MacOS is
> `~/Library/Application Support/larry.cfg`.
