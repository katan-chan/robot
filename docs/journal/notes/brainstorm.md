# Notes: brainstorm

Version: brainstorm (2026-10-20, one day of design talk before any code). Source docs are in Vietnamese; every beat below is self-contained. Decision codes like 3.1 are `docs/decisions/` entries (step 3, decision 1). Commit hashes are 7 characters.

Setup, for readers new to the project: one human and Claude (an AI coding agent) are designing a four-legged spider robot with twelve servo motors, simulated in MuJoCo (a physics engine) on a MacBook. The 3D shape is modelled in Blender. No hardware exists yet.

## Beat: The tool chain changed twice before the first line of code

- **Type:** human-problem
- **What happened:** On the first day Claude proposed a stack of Blender, then an XML robot description (MJCF), then MuJoCo (decision 3.1). During an independent review of the plan (step 9) this was rewritten as decision 3.2: robot parameters live in a text file, a Python script generates the MJCF, and Blender only exports display meshes. The user confirmed that. Later the same day the user reversed it (decision 18.1): Blender is the main place where the robot's 3D shape is edited, and the model is exported from Blender into MuJoCo. So the stack went Blender-first, then parameters-first, then Blender-first again. The user's reason is not written down beyond the decision itself, so this note does not guess at it. Decision 3.2 was marked superseded, not deleted, which is why the history is still readable.
- **How it was solved:** Decision 18.1 gave a clear split of responsibilities. Blender keeps shape, joint positions, joint axes, joint limits and which servo sits at which joint. A TOML file in the repo keeps physics that is not geometry: servo catalogue, masses, friction, solver settings (18.4). MuJoCo does all the physics (18.2). Old lines were kept and labelled "replaced by 18.1" instead of being erased, and the implementation plan for the first gate had to be rewritten (commit 7e476c6).
- **Evidence:** 3.1, 3.2, 18.1, 18.2, 18.4; commits ef2aea5 (brainstorm log), 6960d7e (Blender becomes the main editor), 7e476c6 (G1 plan rewritten)
- **Media:** none

## Beat: "It is a small project, chat is enough" did not survive the day

- **Type:** human-problem
- **What happened:** In step 5 Claude proposed a minimal first version and wrote decision 5.5: the job is small, a description in chat and one file is enough, no separate design document. By the end of the same day the project had 18 numbered decision files, a review by two sub-agents, a physics and security rulebook, a web controller design and a task graph. Nobody planned that growth; each answer from the user opened new questions (remote control over a VPN, safety stops, agent access to the robot).
- **How it was solved:** Decision 5.5 was marked "replaced: the project is bigger than expected, the design document is the `docs/decisions/` folder" (commit f197fbd, "retire stale decisions 5.5"). The cheap lesson: a size estimate made at the start of a brainstorm was wrong within hours, and the cost was only a stale line in a table, because decisions are never deleted, only replaced. Evidence is thin on the exact moment the estimate flipped; the record shows the result (decision steps 6 to 18 all dated the same day), not the moment of realisation.
- **Evidence:** 5.5, 5.4 (also replaced); commits ef2aea5, f197fbd
- **Media:** none

## Beat: Where should the human look at the robot, MuJoCo or Blender?

- **Type:** idea
- **What happened:** The first review gate, G1 ("the user can look at the 3D model and its parts before anything else is built"), was set by the user in decision 16.2. Claude chose how to show it (16.4, labelled "Claude decides, small point"): open the model in MuJoCo's own viewer, with a parts table read from the MuJoCo model and a few snapshot images. Then the user decided Blender is the main editor (18.1), so the gate was redefined (18.3, user confirmed): view the model in Blender, plus a check that the exported model opens in MuJoCo and that the parts table read from MuJoCo matches Blender. At the real G1 review on 2026-10-22 the user settled it the other way (decision 19.10): to view or check the model, open only MuJoCo; Blender is for editing geometry only. The agent keeps this as a standing memory note: "to show the model, open MuJoCo viewer, not Blender".
- **How it was solved:** Not by arguing in advance but by building both views: a MuJoCo viewer command with snapshots, and Blender render commands. The preference only became clear when the human used them. The G1 review page shows the same four camera angles from both programs side by side (commit bdc3c21).
- **Evidence:** 16.2, 16.4, 18.3, 19.10; commits b679835 (gate G1 added), 6960d7e, bdc3c21 (G1 review page)
- **Media:** none yet (G1 images are in `docs/reference/g1/`; journal copies come with the g1 media folder)

## Beat: The main agent may only coordinate, and a hook enforces it

- **Type:** agent-problem
- **What happened:** The user decided that the main Claude session must not write product code (decision 17.2). It only plans, hands out work, calls verifier sub-agents, merges and records decisions. All code goes to sub-agents, each in its own git worktree, even for tasks that must run one after another (17.3, 17.4). A written rule alone is easy for an agent to forget or rationalise away, so Claude added a `PreToolUse` hook (17.5, `coordinator-guard.sh`) that blocks Edit and Write on `spider/`, `tests/`, `tools/`, `web/`, `blender/`, `models/`, `pyproject.toml` and `uv.lock` in the main checkout. Editing inside a worktree is not blocked.
- **How it was solved:** Two limits were written into the decision file instead of being hidden. The hook only sees the Edit and Write tools; a shell command that edits a file bypasses it, so rule 7 in `AGENTS.md` still forbids that by words only. Codex, another agent tool the user may use, has no equivalent hook, so for it the rule is guidance only. The next day the design also hit the agent platform itself: its "auto mode" safety classifier blocked delegating to sub-agents (it read "main session barred from code, work goes to sub-agents" as bypassing a rule) and blocked the agent from editing its own permission settings. That became lesson L-003: run the plan in normal mode, or the human adds the permission by hand, because an agent may never raise its own permissions (17.11, still waiting for the human). A later session was not blocked, so the classifier's behaviour varies between sessions.
- **Evidence:** 17.2, 17.3, 17.4, 17.5, 17.11, L-003; commit b755ee7 (harness: main session orchestrates only)
- **Media:** none
