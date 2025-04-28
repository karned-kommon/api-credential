# Deploying to GitHub Pages

This guide explains how to deploy the API Credential documentation to GitHub Pages.

## Automatic Deployment

The documentation is automatically deployed to GitHub Pages whenever changes are pushed to the `main` branch that modify files in the `docs/` directory or the `mkdocs.yml` file. This is handled by a GitHub Actions workflow.

### How It Works

1. The GitHub Actions workflow is defined in `.github/workflows/deploy-docs.yml`
2. When changes are pushed to the `main` branch, the workflow:
   - Sets up a Python environment
   - Installs MkDocs and required dependencies
   - Builds the documentation
   - Deploys it to the `gh-pages` branch
3. GitHub Pages serves the content from the `gh-pages` branch

### Viewing the Deployment Status

You can check the status of the deployment in the "Actions" tab of the GitHub repository.

## Manual Deployment

If you need to deploy the documentation manually, you can do so using the MkDocs `gh-deploy` command.

### Prerequisites

- Python 3.8 or higher
- MkDocs and required dependencies installed

### Deployment Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/Karned/Kommon/api-credential.git
   cd api-credential
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Deploy to GitHub Pages:
   ```bash
   mkdocs gh-deploy
   ```

This command builds the documentation and pushes it to the `gh-pages` branch of the repository.

### Forcing Deployment

If you need to force the deployment (overwriting existing content), use:

```bash
mkdocs gh-deploy --force
```

## Accessing the Documentation

Once deployed, the documentation is available at:

[https://karned.github.io/Kommon/api-credential/](https://karned.github.io/Kommon/api-credential/)

## Troubleshooting

### Documentation Not Updating

If the documentation is not updating after a push:

1. Check the GitHub Actions workflow in the "Actions" tab
2. Ensure the repository has GitHub Pages enabled in the repository settings
3. Verify that the GitHub Pages source is set to the `gh-pages` branch

### Local Testing

To test the documentation locally before deployment:

```bash
mkdocs serve
```

This starts a local server at `http://localhost:8000` where you can preview the documentation.