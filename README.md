# 3button_tstick

Raspberry Pi 5 desktop application for the 3-button and T-stick test station. The app uses a PyQt5 interface, reads force data from an Arduino over serial, and controls the test fixture through a separate GRBL serial connection. The code also includes GPIO button checks, calibration, local SQLite logging, and ERP job-card integration.

## Project files

| File | Purpose |
| --- | --- |
| `main.py` | Desktop launcher entry point, test interface, fixture communication, and calibration |
| `erp.py` | ERP integration and local job-card records |
| `config.py` | Required station configuration imported by both Python files |

Keep a working `config.py` on the Pi alongside `main.py` and `erp.py`. Before starting, verify `ARDUINO_PORT`, `GRBL_PORT`, `SERIAL_BAUDRATE`, `GPIO_BUTTON_PINS`, and the station's ERP configuration. Keep live credentials and production databases off GitHub.

## One-time setup on Raspberry Pi 5

Use Raspberry Pi OS with a desktop session. Open Terminal as the user who will operate the station.

```bash
sudo apt update
sudo apt install -y git python3-pyqt5 python3-serial python3-matplotlib \
  python3-websocket python3-reportlab python3-requests python3-flask \
  python3-dotenv python3-gpiozero python3-lgpio python3-pymysql

mkdir -p "$HOME/apps"
cd "$HOME/apps"
git clone https://github.com/prathamaptener-creator/3button_tstick.git
cd 3button_tstick
```

For a private repository, authenticate with read access to this repo before cloning. If the project is already cloned, open the existing checkout instead. Add the station's `config.py` if it is supplied separately.

Connect the Arduino and GRBL controller and check their device paths.

```bash
ls -l /dev/serial/by-id/
groups
```

If the USB serial devices belong to `dialout` and your account is missing that group, run `sudo usermod -aG dialout "$USER"` and log out and back in. Use the actual Arduino and GRBL device paths in `config.py`. When available, distinct `/dev/serial/by-id/` paths are preferable to numbered USB device paths.

## Launch and verify

From a terminal in the Pi desktop session, run:

```bash
cd "$HOME/apps/3button_tstick"
/usr/bin/python3 main.py
```

Confirm the employee entry window opens. Verify the Arduino and GRBL connections, the configured GPIO inputs, and ERP connectivity on the station before production use. Run from the project directory so relative database and output paths resolve there.

## Add a one-click app shortcut

After the terminal launch works, run these commands as the same desktop user. They assume the checkout is in `$HOME/apps/3button_tstick`.

```bash
mkdir -p "$HOME/.local/bin" "$HOME/.local/share/applications"

cat > "$HOME/.local/bin/start-3button-tstick" <<'LAUNCHER'
#!/bin/sh
cd "$HOME/apps/3button_tstick" || exit 1
exec /usr/bin/python3 main.py
LAUNCHER
chmod +x "$HOME/.local/bin/start-3button-tstick"

cat > "$HOME/.local/share/applications/3button-tstick.desktop" <<DESKTOP
[Desktop Entry]
Type=Application
Name=3 Button / T-Stick
Exec="$HOME/.local/bin/start-3button-tstick"
Terminal=false
Categories=Utility;
DESKTOP
```

Open **3 Button / T-Stick** from the Pi application menu. If it closes immediately, run the terminal launch command again to see the error.

## Publish this README

In Windows Command Prompt, from your existing local `3button_tstick` folder, save this file as `README.md` and run:

```cmd
git add -- README.md
git diff --cached --name-only
git commit -m "Document Raspberry Pi setup and launcher"
git push github main
```

Before committing, confirm the staged list contains only `README.md`. These commands assume the `github` remote is already set to `prathamaptener-creator/3button_tstick`.
