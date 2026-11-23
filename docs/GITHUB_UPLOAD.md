# Upload ICT Risk Copilot to your GitHub portfolio

Your existing GitHub portfolio is at `https://github.com/yadu732`. This project is **not** yet published there; download the ZIP and follow one of the options below using an account with write access.

## Option A: Separate repository (recommended)

A separate repository makes the project easy for recruiters to discover and evaluate.

1. Extract `ict-risk-copilot.zip` to a folder called `ict-risk-copilot`.
2. On GitHub, create a **new empty repository** called `ict-risk-copilot` under your intended GitHub account. Do **not** tick "Add a README", because this project already has one.
3. Open VS Code inside the extracted `ict-risk-copilot` folder.
4. Run these commands in the VS Code PowerShell terminal:

```powershell
git init
git branch -M main
git add .
git commit -m "Add ICT Risk Copilot local LLM portfolio project"
git remote add origin https://github.com/yadu732/ict-risk-copilot.git
git push -u origin main
```

If your GitHub username differs from `yadu732`, change the remote URL before pushing.

If `git remote add origin` reports an existing remote, run `git remote -v`, and use `git remote set-url origin YOUR_REPO_URL` if needed.

If `git commit` requests your identity, run the following with your own details:

```powershell
git config --global user.name "Your GitHub Name"
git config --global user.email "your-public-or-noreply-email@example.com"
```

Never enter your GitHub password directly into a remote URL or publish credentials in code.

## Option B: Add to your IdentityGuard repository

If you prefer to keep the prototype inside `identityguard-IAM-analytics`:

1. Clone your repository:

```powershell
git clone https://github.com/yadu732/identityguard-IAM-analytics.git
```

2. In File Explorer, copy the extracted `ict-risk-copilot` project folder into the cloned `identityguard-IAM-analytics` directory. Do **not** copy a nested `.git` directory from the standalone project.
3. Open the cloned repository in VS Code and run:

```powershell
git add ict-risk-copilot
git commit -m "Add local LLM ICT risk reporting prototype"
git push origin main
```

Note: the standalone project has its own `pyproject.toml`. After adding it as a subfolder, open a terminal in that subfolder to install dependencies and run `streamlit run app.py`.

## Verify after publishing

- Open GitHub and check that `README.md`, `app.py`, `data/`, `src/` and `tests/` are visible.
- Open the **Actions** tab to confirm CI tests pass.
- Put the repository URL in your CV only after it is live.
- Never upload `.venv`, API keys, real company tickets, private personal data or credentials.
