# TFMCyber

This repository contains tools and scripts for graph analysis and model prediction. Obtained from: https://github.com/Daaviid30/TFG

**Prerequisites**
- Python 3.11 (recommended)
- Git (optional)

**Quick setup**

1. Create and activate a virtual environment

	- Windows (PowerShell):

	  ```powershell
	  python -m venv .venv
	  .\.venv\Scripts\Activate.ps1
	  ```

	- Windows (cmd):

	  ```cmd
	  python -m venv .venv
	  .\.venv\Scripts\activate.bat
	  ```

	- macOS / Linux:

	  ```bash
	  python3 -m venv .venv
	  source .venv/bin/activate
	  ```

2. Upgrade pip

	```bash
	python -m pip install --upgrade pip
	```

3. Install project dependencies

	```bash
	python -m pip install -r requirements.txt
	```

	Note: `requirements.txt` already includes `torch` and `torch-geometric`. If installation of `torch-geometric` fails on your platform, follow the official PyG installation guide for platform- and CUDA-specific wheels: https://pytorch-geometric.readthedocs.io/en/latest/notes/installation.html

4. Install Playwright browsers (if you plan to run any web automation)

	```bash
	python -m playwright install
	```

5. Verify key packages

	```bash
	python -c "import sys, torch; import torch_geometric as tg; print('py', sys.version.split()[0]); print('torch', torch.__version__); print('torch-geometric', tg.__version__)"
	```

6. Run the project

	- Typical entry point:

	  ```bash
	  python main.py
	  ```

	  Adjust the command as needed for other scripts (for example, `webGraph.py`).

Troubleshooting
- If `torch` installation is required with a specific CUDA build, install `torch` first using the official PyTorch selector: https://pytorch.org/get-started/locally/ then re-run `pip install -r requirements.txt`.
- If a package fails to install due to binary wheels (common with PyG), consult the PyG installation page linked above for the correct pre-built wheels.

Contact / Notes
- Files of interest: [requirements.txt](requirements.txt), [main.py](main.py)

Enjoy exploring the repository.
