# Publish this project on GitHub

## Before you publish

- Keep `.env` private. It contains your local PostgreSQL password and is excluded by `.gitignore`.
- Keep `.venv/`, local logs, and cache files out of the repository.
- Keep `data/raw/sales.csv` only if you are comfortable publishing the bundled synthetic sample data. It contains generated data, not real customer records.
- Run the ETL pipeline and dashboard locally, then capture a clean dashboard screenshot for the README.

## 1. Create a GitHub repository

On GitHub, create a **public** repository named `sales-data-etl-pipeline`. Do not initialize it with a README, licence, or `.gitignore` because this project already contains those files.

## 2. Check what will be committed

Run these commands in PowerShell from the project root:

```powershell
git status --short
git check-ignore .env .venv
```

If `.env` exists, `git check-ignore .env` should report it as ignored. If it does not, add `.env` to `.gitignore` before continuing. Never paste the password into README, screenshots, source code, or GitHub issues.

## 3. Commit and push

Replace `YOUR_USERNAME` with your GitHub username:

```powershell
git init
git add .
git status
git commit -m "Build sales ETL pipeline and analytics dashboard"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/sales-data-etl-pipeline.git
git push -u origin main
```

Review the output of `git status` before committing. If Git says the remote already exists, use `git remote -v` to inspect it rather than adding a second remote.

## 4. Add a dashboard screenshot

1. Run `streamlit run dashboard\app.py` and open the local dashboard.
2. Set the browser to a useful width and scroll to the top.
3. Take a screenshot that does not expose your terminal, `.env`, or database password.
4. Save it as `docs/dashboard-preview.png`.
5. Add this near the top of `README.md`:

   ```markdown
   ## Dashboard preview
   ![Sales Intelligence dashboard](docs/dashboard-preview.png)
   ```

6. Commit the screenshot and README update:

   ```powershell
   git add README.md docs/dashboard-preview.png
   git commit -m "Add dashboard preview to README"
   git push
   ```

## 5. Keep the repository reproducible

The README should explain that PostgreSQL must be installed locally, `.env` must be created from `.env.example`, and the schema/ETL steps must be run before the dashboard. The app is a local Streamlit dashboard; GitHub stores the source but does not host the running app.
