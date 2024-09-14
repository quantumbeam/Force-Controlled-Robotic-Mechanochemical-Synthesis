
## Environment Setup
To set up the environment, Docker is required. Running `run.sh` will build a Docker container and launch JupyterLab. You can open JupyterLab through your browser or VSCode. The default port is set to 18888.

## Preparing Files
Place the CIF files and instrument parameter files in the `data/cif_and_instprm` directory.

## Running the Demo
The demo script automatically performs Rietveld analysis every time an XYE file is generated in the `data/XRD` directory. The results are saved in the `results` directory.
