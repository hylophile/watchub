# Watchhub

A simple webpage which...
- shows a file tree of media files in a given directory
- shows the progress of each file/folder (i.e. how far the content has been watched) in a `<meter>`
- unfolds directories which are "in progress", i.e. `0 < progress < 100`
- opens `mpv` when a file is clicked

For showing the progress, logging functionality needs to be added to `mpv`. This is thankfully very easy thanks to it scriptable with Lua. Just put `main.lua` in `~/.config/mpv/scripts/log/main.lua`.
