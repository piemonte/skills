# Installing swiftui-architecture for Codex

## Install

### macOS / Linux

```bash
# Clone the skills repository
git clone https://github.com/piemonte/skills.git ~/.codex/piemonte-skills

# Create the skills directory if it doesn't exist
mkdir -p ~/.agents/skills

# Symlink the individual skill
ln -s ~/.codex/piemonte-skills/swiftui-architecture ~/.agents/skills/swiftui-architecture
```

### Windows

```powershell
git clone https://github.com/piemonte/skills.git "$env:USERPROFILE\.codex\piemonte-skills"
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agents\skills"
cmd /c mklink /J "$env:USERPROFILE\.agents\skills\swiftui-architecture" "$env:USERPROFILE\.codex\piemonte-skills\swiftui-architecture"
```

## Update

```bash
cd ~/.codex/piemonte-skills && git pull
```

## Uninstall

```bash
rm ~/.agents/skills/swiftui-architecture
```
