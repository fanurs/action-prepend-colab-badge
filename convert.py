#!/usr/bin/env python3
import argparse
import json
import os
import urllib.parse

def parse_args():
    parser = argparse.ArgumentParser(
        description="Prepend Google Colab badge to Jupyter Notebooks."
    )
    parser.add_argument(
        "files", 
        metavar="FILE", 
        nargs="+", 
        help="One or more .ipynb files to update"
    )
    parser.add_argument(
        "--repo",
        required=True,
        help="Target GitHub repository (e.g., username/repo)"
    )
    parser.add_argument(
        "--branch",
        required=True,
        help="Target git branch (e.g., main, feature-x)"
    )
    return parser.parse_args()

def is_badge_line(line):
    """
    Checks if a line contains a Google Colab badge image.
    This heuristic allows us to detect badges even if the repo/branch is different.
    """
    return "colab-badge.svg" in line

def clean_notebook_cells(cells):
    """
    Removes existing Colab badges from all markdown cells.
    If a cell becomes empty after removing the badge, it is discarded.
    """
    cleaned_cells = []
    
    for cell in cells:
        # We only care about Markdown cells for badges
        if cell.get("cell_type") != "markdown":
            cleaned_cells.append(cell)
            continue
        
        source = cell.get("source", [])
        # Handle case where source is a single string (uncommon but valid JSON)
        if isinstance(source, str):
            source = source.splitlines(keepends=True)
            
        # Filter out lines that look like a badge
        new_source = [line for line in source if not is_badge_line(line)]
        
        # LOGIC:
        # If the cell had content but now has none (meaning it was ONLY a badge),
        # we drop the cell entirely to avoid leaving empty cells at the top.
        # If it was already empty, or still has content (like a title), we keep it.
        was_badge_only = (len(source) > 0) and (len(new_source) == 0) and (len(source) != len(new_source))
        
        if not was_badge_only:
            cell["source"] = new_source
            cleaned_cells.append(cell)
            
    return cleaned_cells

def create_badge_cell(repo, branch, file_path):
    """
    Creates a new Markdown cell containing ONLY the badge.
    """
    # Encode branch for URL safety (e.g. 'feature/x' -> 'feature%2Fx')
    encoded_branch = urllib.parse.quote(branch, safe='')

    # Construct the dynamic URL
    colab_url = f"https://colab.research.google.com/github/{repo}/blob/{encoded_branch}/{file_path}"
    image_url = "https://colab.research.google.com/assets/colab-badge.svg"
    
    # HTML format as requested
    badge_html = f'<a href="{colab_url}" target="_parent"><img src="{image_url}" alt="Open In Colab"/></a>'
    
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [badge_html] # No trailing newline needed for single line cell
    }

def update_notebook(file_path, repo, branch):
    print(f"Updating badge for {file_path} -> {branch}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    # 1. Clean existing badges (Idempotency Step)
    if "cells" in data:
        data["cells"] = clean_notebook_cells(data["cells"])
    else:
        data["cells"] = []

    # 2. Create the new badge cell
    badge_cell = create_badge_cell(repo, branch, file_path)

    # 3. Insert at the very beginning
    data["cells"].insert(0, badge_cell)
    
    # 4. Save
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            # indent=1 matches convert.py style
            json.dump(data, f, indent=1, ensure_ascii=False)
            f.write("\n") # Match convert.py trailing newline
    except Exception as e:
        print(f"Error writing {file_path}: {e}")

def main():
    args = parse_args()
    
    for file_path in args.files:
        # Basic check if file exists (shell glob expansion might pass non-existent patterns as strings)
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue
            
        update_notebook(file_path, args.repo, args.branch)

if __name__ == "__main__":
    main()