# Terminal demo shown in README.md, recorded with VHS (https://github.com/charmbracelet/vhs).
# Re-record from the repository root after a CLI change:  vhs docs/readme/demo.tape
# Local commands and made-up input only: no network calls, no keys, no personal files.
# A new project replaces the commands below with its own and keeps the settings.

Output docs/readme/demo.gif

Require uv

Set Shell "bash"
Set FontSize 18
Set Width 1200
Set Height 340
Set Padding 24
Set TypingSpeed 40ms
Set Theme { "name": "Bearing Quest Night", "background": "#10213A", "foreground": "#F4F6F8", "cursor": "#E8894F", "selection": "#2E4A72", "black": "#10213A", "red": "#FF8A80", "green": "#8FD19E", "yellow": "#F2C46B", "blue": "#7DB8F0", "magenta": "#E3A1D6", "cyan": "#7FD6E8", "white": "#C9D3DF", "brightBlack": "#8EA0B5", "brightRed": "#FFB4AB", "brightGreen": "#B5E3C0", "brightYellow": "#F7D99A", "brightBlue": "#A9D0F5", "brightMagenta": "#EFC4E8", "brightCyan": "#A8E6F2", "brightWhite": "#FFFFFF" }

Hide
Type `export PS1='$ ' && clear`
Enter
Sleep 1s
Show

Type `uv run pt version`
Sleep 300ms
Enter
Sleep 2s

Type `uv run pt hello --name Ada`
Sleep 300ms
Enter
Sleep 3s

Type `uv run pt hello --name ''`
Sleep 300ms
Enter
Sleep 3.5s
