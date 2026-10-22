# Spider robot

A four-legged spider robot with 12 servos, three per leg, being designed in simulation first and built as real hardware later. Almost all of the work is done by AI agents (Claude Code sub-agents) under one human's direction, and the repo keeps every decision, review and mistake along the way.

**Design journal:** https://katan-chan.github.io/robot/journal/ — the story of the project. It covers the ideas, the problems the agents and the human ran into, and how each one was solved.

![MuJoCo render of the G1 model](docs/journal/media/g1/mujoco/iso.png)

## Status

- **Phase 1** is in progress. Its goal is a robot built from simple shapes that walks in an accurate physics simulation. It is driven by hand from a web controller on phone or laptop, and AI agents drive it through the same API from a CLI.
- **Gate G1** has a working 3D model:
  - Blender is the source of the model.
  - The model is exported to MuJoCo with 12 position servos.
  - A parts table is read from the physics engine.
- G1 is being revised so the robot can carry a 2 kg payload (decision step 19).
- **Later stages** run up to a real robot. They are listed in [docs/decisions/07-trinh-tu-task.md](docs/decisions/07-trinh-tu-task.md).

## How it is built

```
models/spider.blend --tools/blender export--> build/model/ --Python MjSpec + physics TOML--> MuJoCo
```

- **Blender** holds the geometry: links, joint positions and axes, joint limits, and which servo sits at which joint. Agents edit it only through a headless CLI, `tools/blender`.
- **MuJoCo** does all the physics: mass, inertia, torque, contact. Project code never re-computes any of these.
- **Python 3.12 via `uv`.** The `mujoco` version is pinned.
- **Platform:** developed on a MacBook Pro M1 Max with macOS, and no NVIDIA GPU.

## Quick start

Requirements: [uv](https://docs.astral.sh/uv/), Blender 5.x, and `ffmpeg` (for videos).

```sh
git config core.hooksPath .githooks          # pre-commit: knowledge-graph check
tools/blender export                          # models/spider.blend -> build/model/
uv run python -m spider.sim.view              # open the MuJoCo viewer
uv run python -m spider.sim.view --parts      # parts table, masses read from MuJoCo
uv run python -m spider.sim.view --video out.mp4   # orbit video, render only
uv run pytest -q                              # full test suite
```

The full command list is in [AGENTS.md](AGENTS.md#lệnh).

## Repo map

| Path | What |
|---|---|
| `models/spider.blend` | Source 3D model |
| `blender/`, `tools/` | Blender scripts, CLI wrapper, knowledge-graph tool |
| `spider/` | Model building (`model/`) and simulation (`sim/`) |
| `tests/` | pytest suite |
| `docs/decisions/` | Every design decision. Rows are never deleted; replaced ones are marked "Đã thay → N" |
| `docs/journal/` | The blog: notes, media per gate, drafts, posts |
| `docs/harness/` | How the agents are organised: roles, who may write which files, lessons learned |
| `docs/kb/` | Knowledge graph linking decisions, components, tasks and checks |
| `docs/superpowers/` | Specs and implementation plans |

## Working with agents

[AGENTS.md](AGENTS.md) holds the rules every agent follows, and [CLAUDE.md](CLAUDE.md) adds the Claude Code specifics. The main points:
- The main session only coordinates. Code is written by sub-agents, each in its own git worktree.
- Separate verifier agents check physics, determinism and security.
- Hard-to-undo actions wait for the human.

The project docs are written in Vietnamese. The journal is written in English.
