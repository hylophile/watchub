![image](https://user-images.githubusercontent.com/3336264/230327809-3de6f530-3363-466d-93fd-131f37db8ce6.png)

# Watchub

A simple webpage which...
- shows a file tree of media files in a given directory (which is just the URL path)
- shows the progress of each file/folder (i.e. how far the content has been watched) in a `<meter>`
- opens `mpv` when a file is clicked
- has live search for file paths (supports Regex)
- saves search per path in localStorage

For showing the progress, logging functionality needs to be added to `mpv`. This is thankfully very easy thanks to it being scriptable with Lua. Just put `main.lua` in `~/.config/mpv/scripts/log/main.lua`.

## SystemD

To start watchub at system startup, create a service file in `~/.config/systemd/user/watchub.service`:

``` ini
[Unit]
Description=Watchub service

[Service]
Type=simple
WorkingDirectory=%h/code/watchub
ExecStart=python app.py

[Install]
WantedBy=default.target
```

Then:

``` sh
systemctl --user daemon-reload
```

``` sh
systemctl --user enable --now watchub
```

And visit `http://localhost:5959`

## Docker
The app can also be run in Docker. In that case we can't open `mpv` without other means though. We can use a named pipe for that.

Create the pipe:
``` sh
mkfifo /data/watchub/mpvpipe
```

Example service file to listen to the pipe on system startup:
``` ini
[Unit]
Description=mpvpipe service

[Service]
ExecStart=/bin/bash -c 'while true; do mpv "$(cat /data/mpv/mpvpipe) &"; done'

[Install]
WantedBy=multi-user.target
```

Example `docker-compose.yml`:

``` yaml
version: "3"
services:
  watchub:
    container_name: watchub
    build: .
    environment:
      - WH_PIPE_PATH=/data/media/mpvpipe
      - WH_ROOT_PATH=/data
      - WH_MPV_LOG=/data/media/mpv.log
    volumes:
      - /data/media:/data/media
    restart: unless-stopped
    ports:
      - 5959:5959
```
