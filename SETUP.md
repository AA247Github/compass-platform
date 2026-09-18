# Month 1 setup, step by step

Work through this in order. Each step ends with a **check** (how you know it
worked) and an **evidence** note (what to screenshot for your portfolio). Expect
this to take three to four evenings, not one. Where something is likely to go
wrong, there is a "If it breaks" note.

Tick these off in your Jira board as you go, one ticket per step.

---

## Step 1 — Install the tools

Install these, in this order. Restart VS Code after each install so it picks up
new commands.

| Tool | Windows | Mac |
|---|---|---|
| Git | `winget install Git.Git` | `brew install git` |
| Python 3.11+ | `winget install Python.Python.3.11` | `brew install python@3.11` |
| VS Code | already installed | already installed |
| Terraform | `winget install Hashicorp.Terraform` | `brew install terraform` |
| Azure CLI | `winget install Microsoft.AzureCLI` | `brew install azure-cli` |

**Check:** open a *new* terminal in VS Code (`Ctrl+`` `) and run each of these.
All four must print a version number:

```bash
git --version
python --version
terraform -version
az --version
```

**If it breaks:** "not recognised as a command" is almost always a PATH problem,
and almost always fixed by closing every terminal window and opening a new one.
If it persists on Windows, search "edit environment variables for your account",
open Path, and confirm the tool's folder is listed.

---

## Step 2 — Open the project in VS Code

Unzip `compass-platform` somewhere sensible (not in Downloads, and not inside a
OneDrive folder that syncs constantly — sync conflicts with `.venv` are a
well-known source of confusing errors).

Then: **File → Open Folder →** select `compass-platform`.

When VS Code asks *"Do you want to install the recommended extensions?"*, say
yes. That installs Python, Pylance, Ruff, Terraform, GitLens, dbt Power User and
YAML — they are listed in `.vscode/extensions.json`.

**Check:** the Explorer sidebar shows `src`, `tests`, `config`, `infra`.

---

## Step 3 — Create the virtual environment

A virtual environment is a private copy of Python for this project, so package
versions here cannot break anything else on your machine.

In the VS Code terminal, from the project root:

```bash
python -m venv .venv
```

Activate it:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# Mac / Linux
source .venv/bin/activate
```

Your prompt should now start with `(.venv)`.

Then tell VS Code to use it: `Ctrl+Shift+P` → "Python: Select Interpreter" →
choose the one inside `.venv`.

**If it breaks:** on Windows, if PowerShell refuses with a script execution error,
run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` and try again.

---

## Step 4 — Install the package and run the tests

```bash
pip install -e ".[dev]"
pytest
```

`-e` means "editable install": Python treats `src/compass` as a real installed
package, but changes to your code take effect immediately without reinstalling.

**Check:** 36 tests pass, and the coverage table shows around 99%.

**Evidence:** screenshot the passing test run. This is your first K6 artefact and
it exists before you have written a single line of pipeline code — that ordering
is the point.

Now break something on purpose: open `src/compass/cleaning.py`, change `"Female"`
to `"female"` in the `_SEX_LOOKUP` dictionary, and run `pytest` again. Watch it
fail, read the failure message, then undo the change. You now know what a failing
test looks like before it matters.

---

## Step 5 — Initialise git and push to GitHub

```bash
git init -b main
git add .
git commit -m "Initial project scaffolding: package, tests, terraform, CI"
```

Create an **empty private repository** on github.com named `compass-platform` —
no README, no .gitignore, since you already have both. Then:

```bash
git remote add origin https://github.com/<your-username>/compass-platform.git
git push -u origin main
```

**Check:** refresh GitHub; your files are there. The `.venv` folder is *not* — it
is gitignored, and that is correct.

**Evidence:** screenshot the repository with its first commit.

---

## Step 6 — Log in to Azure and set up state storage

```bash
az login
az account show --query id -o tsv
```

Copy that subscription ID; you need it in the next step.

**Set a budget alert now, before creating anything.** In the Azure portal:
Cost Management → Budgets → Add. Set £10, monthly, alert at 50% and 90%. Do not
skip this. It costs nothing and prevents the single worst outcome of this project.

Terraform's *state file* records what it created. It contains secrets, so it must
live in Azure rather than in git. Create that storage by hand, once:

```bash
az group create --name rg-compass-tfstate --location uksouth

az storage account create \
  --name stcompasstfstate<yourinitials> \
  --resource-group rg-compass-tfstate \
  --location uksouth \
  --sku Standard_LRS

az storage container create \
  --name tfstate \
  --account-name stcompasstfstate<yourinitials>
```

Replace `<yourinitials>` everywhere; storage account names must be globally
unique across all of Azure, lowercase, no hyphens.

**Evidence:** screenshot the budget alert. Assessors and managers both like this.

---

## Step 7 — Configure your Terraform variables

```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars   # Windows: copy terraform.tfvars.example terraform.tfvars
```

Open `terraform.tfvars` and fill in your real subscription ID and initials. This
file is gitignored on purpose — it identifies your subscription.

---

## Step 8 — Your first Terraform run

Still in `infra/terraform`:

```bash
terraform init      # downloads the azurerm and databricks plugins
terraform fmt       # formats the .tf files
terraform validate  # checks the syntax is coherent
terraform plan      # shows what WOULD be created - creates nothing
```

Read the plan output properly. `+` means create, `-` means destroy, `~` means
change in place. You should see roughly eight resources to add and nothing to
destroy.

When the plan looks right:

```bash
terraform apply     # type 'yes' when prompted
```

This takes five to ten minutes, mostly waiting for the Databricks workspace.

**Check:** `terraform output` prints your workspace URL, storage account name and
Key Vault name. Open the Azure portal and see them.

**Evidence:** screenshot the plan output *and* the portal showing the created
resources. This pair is strong K13/S4 evidence.

**If it breaks:** the most common failure is a storage account name that is
already taken globally — change `storage_account_suffix` in `terraform.tfvars`
and rerun. The second most common is a subscription that has not registered the
Databricks resource provider; fix with
`az provider register --namespace Microsoft.Databricks`.

---

## Step 9 — Unity Catalog (do this second, deliberately)

Unity Catalog needs a *metastore* attached to your workspace, and on a personal
Azure account that step is done once through the Databricks account console at
`accounts.azuredatabricks.net`, not through Terraform.

So: open your workspace URL, confirm you can log in, attach a metastore via the
account console, and only then uncomment the `databricks_catalog` and
`databricks_schema` blocks at the bottom of `main.tf` and run `terraform apply`
again.

Doing infrastructure in two passes like this is normal and worth saying out loud
in your report: it shows you understand provider dependencies rather than
treating Terraform as magic.

**Check:** in Databricks, Catalog Explorer shows a `compass` catalog containing
`bronze`, `silver` and `gold` schemas.

---

## Step 10 — Destroy it again

```bash
terraform destroy
```

Yes, really. You will rebuild it in month 2 with one command, and until you have
proved you can rebuild, you do not actually have infrastructure as code — you
have a very expensive script you ran once.

**Evidence:** note in your journal how long the rebuild took. That number is your
disaster-recovery answer if an assessor asks.

---

## Step 11 — Watch CI run

Make a branch, change something small, and open a pull request:

```bash
git checkout -b chore/verify-ci
# edit README.md - add a line
git add -A
git commit -m "COMPASS-1: verify CI pipeline runs on pull requests"
git push -u origin chore/verify-ci
```

Open the PR on GitHub. The Actions tab shows two jobs: **Python quality gate**
and **Terraform validation**.

Now deliberately break it: on the same branch, add a badly formatted line to a
Python file (for example `x=1` with no spaces, and an unused import). Push again.
Watch the ruff step fail and the PR show a red X.

Fix it (`ruff format .` and remove the import), push, watch it go green, then
merge.

**Evidence:** screenshot the red failing check *and* the green passing one. This
is the single most useful CI/CD image in your whole portfolio.

---

## Step 12 — Turn on branch protection

On GitHub: **Settings → Branches → Add branch protection rule**.

- Branch name pattern: `main`
- Tick "Require a pull request before merging"
- Tick "Require status checks to pass before merging", then select the CI jobs

From now on you physically cannot push broken code to main, including by
accident at 11pm.

**Evidence:** screenshot the protection settings.

---

## Step 13 — Wire up Jira

Create the free Jira project `COMPASS` as a Scrum board, then:

- Create eight epics, one per month of the plan.
- Under the Month 1 epic, create one story per step in this file, each with
  acceptance criteria in Given/When/Then form.
- Install the GitHub for Jira integration so commit messages containing
  `COMPASS-1` link automatically to the ticket.
- Start Sprint 1.

**Evidence:** screenshot the board, and one ticket showing acceptance criteria
plus its linked pull request.

---

## Step 14 — Write your second ADR

`docs/decisions/001-configuration-driven-architecture.md` is written for you as a
worked example. Write `002-cloud-and-platform-choice.md` yourself, covering: why
Azure, why Databricks over Synapse, why UK South, and your estimated monthly cost.

Writing these while the reasoning is fresh is far easier than reconstructing it in
month 7, and these files become the backbone of the design section of your report.

---

## Month 1 exit checklist

- [ ] Repository on GitHub with protected main branch
- [ ] 36 tests passing locally and in CI
- [ ] CI blocking merges when it fails (proved, with screenshots)
- [ ] Terraform applies and destroys cleanly
- [ ] Databricks workspace reachable, Unity Catalog with three schemas
- [ ] Budget alert configured
- [ ] Jira board with eight epics and Sprint 1 running
- [ ] Two ADRs written
- [ ] Journal entries for every session, including what confused you

When all of these are ticked, you have finished month 1 of the scoping form's
project plan, and month 2 is only ingestion code on top of working foundations.
