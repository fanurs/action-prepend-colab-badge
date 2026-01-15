# GitHub Action to Prepend Colab Badge

A lightweight GitHub Action to automatically prepend (or update) a "Open in Colab" badge to the first cell of your Jupyter Notebooks (`.ipynb`).

## Why this exists?

We know and love tools like [colab-badge-action](https://github.com/trsvchn/colab-badge-action). However, we wanted something optimized for **speed and minimalism**.

* **Composite Action**: This runs directly on the runner shell without the overhead of building a Docker container, making it significantly faster for quick CI jobs.
* **Smart Idempotency**: It detects existing badges (looking for `colab-badge.svg`) and removes them before adding the new one. If a cell contained *only* a badge, the entire cell is removed to keep your notebook clean.
* **Flexible Context**: It works out-of-the-box for any branch (including feature branches) but allows you to lock badges to specific branches (like `main`) if needed.

## Usage

This action is designed to be used directly from the repository source.

### 1. Standard Usage (Context Aware)

By default, the action uses the current repository and the current branch/ref. This is ideal for feature branches, ensuring the badge links to the version of the code currently being viewed or reviewed.

```yaml
steps:
  - uses: actions/checkout@v4

  - name: Prepend Colab Badges
    uses: fanurs/action-prepend-colab-badge@main
    with:
      # Optional: Glob pattern or list of files (defaults to '*.ipynb')
      files: 'examples/*.ipynb'

  - name: Commit changes
    uses: stefanzweifel/git-auto-commit-action@v5
    with:
      commit_message: "chore: update colab badges"

```

### 2. Fixed Usage (Explicit Overrides)

If you want your badges to **always** point to a specific stable branch (e.g., `main`), or if you are generating badges for a different repository entirely, you can override the defaults.

```yaml
steps:
  - uses: actions/checkout@v4

  - name: Prepend Colab Badges (Fixed Target)
    uses: fanurs/action-prepend-colab-badge@main
    with:
      files: 'examples/*.ipynb'
      
      # Force the badge to always point to the 'main' branch
      # regardless of which branch this workflow is running on.
      branch: 'main'
      
      # Optional: Force the badge to point to a different repository
      # repository: 'other-user/other-repo'

  - name: Commit changes
    uses: stefanzweifel/git-auto-commit-action@v5
    with:
      commit_message: "chore: update colab badges"

```

## Inputs

| Input | Description | Default |
| --- | --- | --- |
| `files` | Glob pattern or list of `.ipynb` files to update. | `*.ipynb` |
| `repository` | The target GitHub repository (username/repo). | `${{ github.repository }}` |
| `branch` | The target git branch. | `${{ github.head_ref \|\| github.ref_name }}` |

## How it Works

The action runs a Python script that processes the JSON structure of your `.ipynb` files.

1. **Scans**: It looks through all Markdown cells for lines containing `colab-badge.svg`.
2. **Cleans**: It removes those lines. If a cell becomes empty because it *only* contained a badge, the cell is deleted.
3. **Inserts**: It generates a new badge with the correct URL format:
`https://colab.research.google.com/github/{repo}/blob/{branch}/{file}`
4. **Saves**: The badge is inserted as the very first cell in the notebook.

## Versioning

⚠️ **Note on Versioning:**
We currently do not publish specific release tags. Please use the `@main` branch to ensure you have the latest updates and fixes.

```yaml
- uses: fanurs/action-prepend-colab-badge@main

```

## Contributing

Contributions are welcome! If you find a bug or have an idea for an improvement, feel free to:

* Open an [issue](https://www.google.com/search?q=https://github.com/fanurs/action-prepend-colab-badge/issues)
* Submit a Pull Request
* Star the repository if you find it useful! ⭐️

## License

This project is licensed under the MIT License - see the [LICENSE](https://www.google.com/search?q=LICENSE) file for details.

```