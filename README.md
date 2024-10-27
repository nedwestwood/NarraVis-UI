# Narrative Analysis User Interface

_Last modified: 1 August 2024_

## Introduction

This repository provides a user interface for the multimodal narrative analysis [pipeline](https://github.com/AndrewTham/studious-octo-funicular).

Please note that this repository is still a work in progress.

### Project Structure

```
studious-octo-funicular-ui/
├── studious-octo-funicular-ui/
│   └── tabs/
│       ├── constants.py               # Specifies constants for the project
│       ├── graph.py
│       ├── narrative_visualiser.py    # Entry point for the repository
│       ├── parser.py
│       └── sidebar.py
├── docs/                              # Miscellaneous documents
├── data/                              # Input data
│   ├── graphs/                        # Contains graphs generated from the pipeline
│   ├── images/                        # Contains images associated with the graphs
│   └── videos/                        # Contains videos associated with the graphs
├── pyproject.toml                     # Manage packages used for this project
└── README.md                          # Project documentation
```

## Software Requirements

To develop on this repository, you need the following tools installed on your system:

- [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- [Poetry](https://python-poetry.org/docs/)
- [Python 3.10 or newer](https://www.python.org/downloads/)

## Usage

### 1. Set Up the Data Directory

Create a `data/` directory with subdirectories `output` and `videos`.

- `data/output/`: Contains output folder obtained from a pipeline run.
- `data/videos/`: Contains folders of videos used to initiate a pipeline run

E.g.

```
data/
├── output/
  ├── <Datetime for pipeline run>/              # Feel free to rename this, but make sure directory containing the corresponding videos (in `data/videos/`) is similarly named
    ├── scenes/                                 # Directory of images obtained from scene detection. Also contains `detected_objects.csv` with object detection information.
    ├── intermediate_graph_data<N>.csv          # Series of checkpoint files with similar name except a number N denoting the checkpoint step order number.
    ├── final_graph_data.csv/                   # Main data (result) obtained from the pipeline.`detected_objects.csv` with object detection information.
    ├── final_graph_data.json                   # Main data from the pipeline, formatted for use in the UI.
    ├── pipeline.log                            # Log file for debugging/error handling.
    ├── ...
    └── topics.csv                              # Output from video topic classification
  ├── ...
  └── ...
└── videos/
  ├── <Datetime for pipeline run>/              # Videos used for a pipeline run. Should have the corresponding pipeline results in `data/output/`
  ├── video_1.mp4                               # Directory of images obtained
  ├── ...
  └── metadata.json                             # Contains metadata of videos in this folder. This file must be called `metadata.json`. And the video ids in the file MUST correspond with the filenames in the folder, and the information used to execute the pipeline.
```

### 2. Start the Interface

Run the following command in your terminal to start the interface:

```bash
streamlit run studious_octo_funicular_ui/narrative_visualiser.py
```

A browser window should open with the interface. If it does not, navigate to `http://localhost:8501` in your browser.

## Development

### Preparation

#### 1. Install the Environment and Pre-commit Hooks

Run this command in a terminal to set up the development environment and pre-commit hooks:

```bash
make install
```

#### 2. Activate the Environment

Activate the virtual environment with all necessary packages by running:

##### MacOS

```bash
source .venv/bin/activate
```

##### Windows

```bash
.venv\Scripts\activate
```

Add or remove packages using `poetry add <PYTHON PACKAGE>` and `poetry remove <PYTHON PACKAGE>`, respectively.

#### 3. Run Pre-commit Checks

Run the pre-commit checks with the following command:

```bash
pre-commit run --all-files
```

#### 4. Commit Code Changes

Stage your code changes with:

```bash
git add .
```

- **A. With Pre-commit Hooks**
  To run the pre-commit hooks, use:

  ```bash
  git commit -m "<COMMIT MESSAGE>"
  git push
  ```

- **B. Skip Pre-commit Hooks**
  To skip the pre-commit hooks, use:

  ```bash
  git commit --no-verify
  git push --no-verify
  ```

## Installation

TODO

## Publishing

- To finalize the setup for publishing to PyPi or Artifactory, see [this guide](https://fpgmaas.github.io/cookiecutter-poetry/features/publishing/#set-up-for-pypi).
- For activating automatic documentation with MkDocs, see [this guide](https://fpgmaas.github.io/cookiecutter-poetry/features/mkdocs/#enabling-the-documentation-on-github).
- To enable code coverage reports, see [this guide](https://fpgmaas.github.io/cookiecutter-poetry/features/codecov/).

---

This repository was initiated with [fpgmaas/cookiecutter-poetry](https://github.com/fpgmaas/cookiecutter-poetry).
