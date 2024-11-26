# Standalons Script for OBS Shortcuts

# Why?

This is useful for Wayland where global shortcuts do not work out of the box.

This also allows you to script and automate OBS, for instance you can write a bash daemon to start Replay Buffer as soon as you launch a particular program or game.

# How to use

## Enable Websocket in OBS

Open OBS, and enable Websockets in Tools --> Websocket Server Settings.

Note: If you don't have Tools --> Websocket Server Settings in your OBS menu, you may be runng a OBS which is not compiled with Websocket support. In that case, you'll need to either find a OBS binary for your system which has OBS support, or compile it yourself with the right flag. For Arch, you can download a precompiled package [from Chaotic AUR here](https://pkgs.org/download/obs-studio-stable), or install `obs-studio-stable` if you have [Chaotic AUR](https://aur.chaotic.cx/) [enabled](https://aur.chaotic.cx/docs).

## Setup this script
- Clone this repo or just download the python script and put it somewhere in your system. This script has no dependencies other than standard python libraries, which you should have if your system has python.
- Add a file named `obs-password.txt` to the same directory as the .py script, and put your OBS Websockets password there. You can find or set the password in OBS, Tools --> Websocket Server Settings.

## How to invoke

With OBS running, you can now control it from command line like this -

```sh
# Example: Start or stop streaming.
python obs-control.py --request ToggleStream
```

This supports all commands officially supported by the OBS Websocket plugin. You can see a full list in [OBS Websockets official documentation here](https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md).

I recommend the following shortcuts to be set up -

| Shortcut    | Command                            | Comment                                                    |
| ----------- | ---------------------------------- | ---------------------------------------------------------- |
| Alt+Shift+S | `... --request ToggleStream`       | Starts or stops streaming.                                 |
| Alt+F8      | `... --request ToggleReplayBuffer` | Enables saving last x minutes replay with Alt+F10.         |
| Alt+F10     | `... --request SaveReplayBuffer`   | Save the last x minuts, assuming replay buffer is enabled. |
