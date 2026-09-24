# quiz-skill

One question about the repository you're working in, with four brief choices. Reply `a`, `b`, `c`, or `d`.

- Right answer: `Correct.`
- Wrong answer: the correct letter and 1–2 short lines explaining why.
- Each invocation ends after grading. Invoke again for a new random question.
- No question history, scores, learner profiles, or sampling state are saved by this skill. Your coding agent still manages its normal chat history.

## Why we built this

As we develop more projects and let coding agents write more of the code, it becomes easier to lose track of how our own software works. Returning to a project after weeks or months can reveal gaps in our understanding of its concepts, architecture, and behavior.

We built quiz-skill to make checking that understanding a small, repeatable habit. A question asks you to retrieve what you know before seeing the answer, and brief feedback helps correct misunderstandings. Practicing that recall over time can strengthen long-term memory.

For example, revisiting code you wrote a month ago with a few questions each week gives you repeated opportunities to remember how it works. The aim is understanding you can retain and use when you return to the project much later.

## Install

Requires Python 3.9+, Git, and Codex or OpenCode with local skill support. No Python packages, API keys, or MCP servers are needed by the skill itself. Your coding agent uses its existing model connection.

Download or clone this repository to a permanent local folder, then run from its root:

```sh
python3 scripts/install.py
python3 scripts/install.py --check
```

The installer links this checkout into `~/.agents/skills/quiz` for both tools, and installs an OpenCode `/quiz` command in `~/.config/opencode/commands/quiz.md`. It respects `XDG_CONFIG_HOME` and `OPENCODE_CONFIG_DIR` for OpenCode. Existing conflicting files are never overwritten. Keep the checkout in place because the installation uses symlinks. Supported installer platforms: macOS and Linux.

No extra Codex plugin manifest is necessary for this local skill installation. `agents/openai.yaml` supplies optional Codex display metadata; the shared behavior is in `SKILL.md`.

## Discover and use

Open the repository you want to learn in your coding agent, then start a new session if the installation isn't visible yet.

| Tool | Find it | Start a question |
| --- | --- | --- |
| Codex | Type `$` and search for `quiz`; CLI/IDE also support `/skills` | `$quiz` |
| OpenCode | Type `/` and search for `quiz` | `/quiz` |

Codex invocation UI varies by client; `$quiz` is the documented skill mention. This package supplies the exact `/quiz` command for OpenCode. Reply to the resulting question in the same conversation with one letter. It accepts uppercase too. No second question is asked automatically.

To check the installed files, run `python3 scripts/install.py --check` from this checkout. This checks links, not an already-running agent's cached skill list. OpenCode can also list discovered skills with `opencode debug skill`. If discovery fails, restart the agent, check skill permissions, and check for another skill or command named `quiz` in the current project.

## How randomness works

`scripts/sample.py` uses Python's OS-backed `SystemRandom` for fresh choices every invocation. It enumerates Git-tracked and nonignored untracked files, filters common dependency, generated, binary, minified, oversized, credential, and build files, and avoids symlinks. It never runs the target project's code.

It chooses an area uniformly (the first two parent directories, or the root), then a file uniformly within that area. This gives smaller areas a chance instead of letting the largest directory dominate. For Python it samples a function/class when available; other languages use a nonblank, noncomment line as an anchor for the agent to locate a meaningful block. It supplies a shuffled category order and random answer position. The agent reads enough surrounding code to verify a question, using the first suitable category.

Categories: concepts, architecture, code interpretation, data flow, control flow, edge cases, error handling, state changes, async behavior, dependencies, testing, performance, security, configuration, and change impact.

The sampler reads sampled source but outputs only paths, line ranges, and selection metadata. Filters are heuristics; the agent still checks suitability and follows the repository's instructions. Random repeats are possible, especially in small repositories. No history is used to suppress them. The target must be a Git repository; source inside a submodule is sampled when that submodule is opened as the target repository.

## Share on GitHub

This is an ordinary Git repository. `SKILL.md` at its root is the entrypoint; share the entire repository so users get the sampler and installer too.

1. Review the files, then commit them locally.
2. Create an empty GitHub repository named `quiz-skill` (public if anyone should be able to download it). Do not initialize it with a separate README.
3. Add that repository as the `origin` remote and push your local commit to `main`.
4. Share the repository URL. Recipients clone it and run the installer above, or ask their agent to read this README and install it.

With GitHub CLI installed and authenticated, from a fresh checkout without an origin remote:

```sh
git status --short
git add .gitignore SKILL.md README.md LICENSE agents integrations scripts tests
git commit -m "Add portable repository quiz skill"
gh repo create quiz-skill --public --source=. --remote=origin
git push -u origin HEAD:main
```

Change `--public` to `--private` for an invite-only repository. If GitHub CLI isn't authenticated, run `gh auth login` first. If the repo or origin already exists, use it rather than repeating repository creation. The commands publish the current feature branch to remote `main`.

After installation, pulling updates into this checkout updates the linked skill. Start a fresh agent session if needed. To uninstall, remove only the symlinks created by the installer; the checkout can remain on disk.

## Development and checks

```sh
python3 -B -m unittest discover -s tests -v
python3 scripts/sample.py --repo .
```

The tests use temporary synthetic Git repositories. They check exclusion behavior, sampling variation, empty-repository handling, and that sampling leaves repository contents unchanged. They do not prove every model follows the conversational instructions. To check those, invoke the skill, answer once correctly and once incorrectly, and verify the exact feedback and stopping behavior.

Sources for installation conventions: [Codex skills](https://learn.chatgpt.com/docs/build-skills), [OpenCode skills](https://opencode.ai/docs/skills), [OpenCode commands](https://opencode.ai/docs/commands).
