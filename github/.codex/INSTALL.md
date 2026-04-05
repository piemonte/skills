# Installing github for Codex

## Install

### macOS / Linux

```bash
git clone https://github.com/piemonte/skills.git ~/.codex/piemonte-skills
mkdir -p ~/.agents/skills
ln -s ~/.codex/piemonte-skills/github ~/.agents/skills/github
```

### Windows

```powershell
git clone https://github.com/piemonte/skills.git "$env:USERPROFILE\.codex\piemonte-skills"
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agents\skills"
cmd /c mklink /J "$env:USERPROFILE\.agents\skills\github" "$env:USERPROFILE\.codex\piemonte-skills\github"
```

## Update

```bash
cd ~/.codex/piemonte-skills && git pull
```

## Uninstall

```bash
rm ~/.agents/skills/github
```
