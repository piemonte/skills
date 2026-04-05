# Installing swift-concurrency for Codex

## Install

### macOS / Linux

```bash
# Clone the skills repository
git clone https://github.com/piemonte/skills.git ~/.codex/piemonte-skills

# Create the skills directory if it doesn't exist
mkdir -p ~/.agents/skills

# Symlink the individual skill
ln -s ~/.codex/piemonte-skills/swift-concurrency ~/.agents/skills/swift-concurrency
```

### Windows

```powershell
git clone https://github.com/piemonte/skills.git "$env:USERPROFILE\.codex\piemonte-skills"
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agents\skills"
cmd /c mklink /J "$env:USERPROFILE\.agents\skills\swift-concurrency" "$env:USERPROFILE\.codex\piemonte-skills\swift-concurrency"
```

## Update

```bash
cd ~/.codex/piemonte-skills && git pull
```

## Uninstall

```bash
rm ~/.agents/skills/swift-concurrency
```
