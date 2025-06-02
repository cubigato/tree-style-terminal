# 4K Display Quick Start Guide

## TL;DR - Just Want It to Work?

For most 4K displays, this should give you properly sized fonts:

```bash
python -m tree_style_terminal --dpi 192
```

## Finding Your Optimal DPI Setting

### Step 1: Check Your Current System

```bash
python -m tree_style_terminal --test-fonts
```

This will show your system's current DPI detection and font scaling.

### Step 2: Test Different DPI Values

Try these common 4K settings:

```bash
# Conservative scaling (1.5x)
python -m tree_style_terminal --test-fonts --dpi 144

# Standard 4K scaling (2x) - most popular
python -m tree_style_terminal --test-fonts --dpi 192

# High scaling (2.5x) - for very high DPI or poor eyesight
python -m tree_style_terminal --test-fonts --dpi 240
```

### Step 3: Launch with Your Preferred Setting

Once you find a DPI that gives comfortable font sizes:

```bash
python -m tree_style_terminal --dpi 192
```

## Common 4K Display Configurations

| Display Type | Recommended DPI | Font Sizes (UI/Terminal) |
|--------------|-----------------|---------------------------|
| 27" 4K Monitor | 144-160 | 14-16px / 16-18px |
| 32" 4K Monitor | 120-144 | 12-14px / 14-16px |
| 15" 4K Laptop | 192-240 | 20-25px / 22-28px |
| 13" 4K Laptop | 240-288 | 25-30px / 28-33px |

## Making It Permanent

### Option 1: Shell Alias (Recommended)

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
alias tst='python -m tree_style_terminal --dpi 192'
```

### Option 2: Environment Variable

Add to your shell profile:

```bash
export TST_DPI=192
```

Then launch normally:

```bash
python -m tree_style_terminal
```

### Option 3: Desktop Entry

Create `~/.local/share/applications/tree-style-terminal.desktop`:

```ini
[Desktop Entry]
Name=Tree Style Terminal
Exec=python -m tree_style_terminal --dpi 192
Icon=terminal
Type=Application
Categories=System;TerminalEmulator;
```

## Troubleshooting

### Fonts Still Too Small?

Try higher DPI values:

```bash
python -m tree_style_terminal --dpi 240
python -m tree_style_terminal --dpi 288
```

### Fonts Too Large?

Try lower DPI values:

```bash
python -m tree_style_terminal --dpi 144
python -m tree_style_terminal --dpi 120
```

### System Not Detecting DPI Correctly?

Check your system information:

```bash
python -m tree_style_terminal --show-info
```

Look for:
- **Calculated DPI**: Physical display DPI
- **GTK XFT DPI**: System font scaling DPI
- **Effective DPI**: What the app will actually use

### Quick Test Without GUI

```bash
python -m tree_style_terminal --test-fonts --dpi YOUR_VALUE
```

This shows the calculated font sizes without starting the full application.

## Advanced: Multiple Monitor Setups

If you have mixed DPI displays (e.g., 4K + 1080p), the app will detect the primary monitor. You may need to:

1. Set your 4K display as primary in system settings
2. Use the manual `--dpi` override for your 4K display's optimal setting
3. Move the application to your 4K monitor after launch

## Getting Help

- `python -m tree_style_terminal --help` - Full command reference
- `python font_test.py` - Quick system font check
- Check the main README.md for complete documentation