# Enable the unified study dashboard

The static dashboard is committed at [docs/index.html](index.html), and the deployment workflow is available at [the Pages GitHub Action](../.github/workflows/deploy-pages.yml).

**Current state:** The workflow failed at `actions/configure-pages` because GitHub Pages has not yet been enabled for this newly created repository. The dashboard HTML passed a JavaScript syntax check and successfully references the SHA-verified progress JSON at:

`99. Reference Materials/Legacy Journey Snapshot/progress/daily-progress.json`

## One-time GitHub configuration

1. Open [Settings → Pages](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry-Journey/settings/pages).
2. Under **Build and deployment → Source**, select **GitHub Actions**.
3. Open [Actions → Deploy Data Engineering Progress Dashboard](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry-Journey/actions/workflows/deploy-pages.yml).
4. Choose **Run workflow** (main), or push a change under `docs/`.
5. Verify the successful deployment URL reported by the run, ordinarily `https://mulikshrikantdattatray14.github.io/Data-Engineering-Mastry-Journey/`.

No new progress is credited merely by changing the dashboard. Any verified new study completion should be recorded in the **single canonical progress JSON** in the preserved Journey data, followed by a dashboard refresh.

**Important:** The original historical dashboard remains preserved in the Legacy Journey Snapshot and the existing Pages site is left unchanged until the new deployment is verified.
