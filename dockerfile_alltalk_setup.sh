#!/bin/bash

# Navigate to the script's directory
cd "$(dirname "$0")"

install_custom_standalone() {
    cd "$(dirname "${BASH_SOURCE[0]}")"

    if [[ "$(pwd)" =~ " " ]]; then
        echo "This script relies on Miniconda which can not be silently installed under a path with spaces."
        exit
    fi

    # Deactivate existing conda envs as needed to avoid conflicts
    { conda deactivate && conda deactivate && conda deactivate; } 2> /dev/null

    OS_ARCH=$(uname -m)
    case "${OS_ARCH}" in
        x86_64*)    OS_ARCH="x86_64" ;;
        arm64* | aarch64*) OS_ARCH="aarch64" ;;
        *)          echo "Unknown system architecture: $OS_ARCH! This script runs only on x86_64 or arm64" && exit ;;
    esac

    # Config
    INSTALL_DIR="$(pwd)/alltalk_environment"
    CONDA_ROOT_PREFIX="${INSTALL_DIR}/conda"
    INSTALL_ENV_DIR="${INSTALL_DIR}/env"
    MINICONDA_DOWNLOAD_URL="https://repo.anaconda.com/miniconda/Miniconda3-py311_24.4.0-0-Linux-${OS_ARCH}.sh"
    if [ ! -x "${CONDA_ROOT_PREFIX}/bin/conda" ]; then
        echo "Downloading Miniconda from $MINICONDA_DOWNLOAD_URL to ${INSTALL_DIR}/miniconda_installer.sh"
        mkdir -p "${INSTALL_DIR}"
        curl -L "${MINICONDA_DOWNLOAD_URL}" -o "${INSTALL_DIR}/miniconda_installer.sh"
        chmod +x "${INSTALL_DIR}/miniconda_installer.sh"
        bash "${INSTALL_DIR}/miniconda_installer.sh" -b -p "${CONDA_ROOT_PREFIX}"
        echo "Miniconda installed."
    fi

    if [ ! -d "${INSTALL_ENV_DIR}" ]; then
        "${CONDA_ROOT_PREFIX}/bin/conda" create -y --prefix "${INSTALL_ENV_DIR}" -c conda-forge python=3.11.9
        echo "Conda environment created at ${INSTALL_ENV_DIR}."
    fi

    # Activate the environment and install requirements
    source "${CONDA_ROOT_PREFIX}/etc/profile.d/conda.sh"
    conda activate "${INSTALL_ENV_DIR}"
    # pip install torch==2.2.1+cu121 torchaudio==2.2.1+cu121 --upgrade --force-reinstall --extra-index-url https://download.pytorch.org/whl/cu121 --no-cache-dir
    conda install -y pytorch=2.2.1 torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia
    conda install -y nvidia/label/cuda-12.1.0::cuda-toolkit=12.1
    conda install -y pytorch::faiss-cpu
    conda install -y conda-forge::ffmpeg
    echo
    echo
    echo
    echo "    Fix Nvidia's broken symlinks in the /env/lib folder"
    echo
    # Define the environment path
    env_path="${INSTALL_ENV_DIR}/lib"

    # List of broken symlinks and their correct targets
    declare -A symlinks=(
        ["libcufile.so"]="libcufile.so.1.10.0"
        ["libcufile_rdma.so"]="libcufile_rdma.so.1.10.0"
        ["libcudart.so"]="libcudart.so.12"
        ["libnvjpeg.so"]="libnvjpeg.so.12.1.1.14"
        ["libcurand.so"]="libcurand.so.10.3.6.39"
        ["libnvJitLink.so"]="libnvJitLink.so.12.1.105"
        ["libnvrtc-builtins.so"]="libnvrtc-builtins.so.12.1.105"
        ["libnvrtc.so"]="libnvrtc.so.12.1.105"
    )

    # Function to fix broken symlinks
    fix_broken_symlinks() {
        echo "Fixing broken symlinks..."
        for link in "${!symlinks[@]}"; do
            target="${symlinks[$link]}"
            if [ -L "$env_path/$link" ] && [ ! -e "$env_path/$link" ]; then
                echo "Removing broken link: $env_path/$link"
                rm "$env_path/$link"
            fi

            if [ -e "$env_path/$target" ]; then
                echo "Creating new symlink: $env_path/$link -> $env_path/$target"
                ln -s "$env_path/$target" "$env_path/$link"
            else
                echo "Target file does not exist: $env_path/$target"
            fi
        done
        echo "Verification of symbolic links:"
        ls -l $env_path | grep -E "libcufile.so|libcudart.so|libcufile_rdma.so|libnvjpeg.so|libcurand.so|libnvJitLink.so|libnvrtc-builtins.so|libnvrtc.so"
    }

    # Call the function to fix broken symlinks
    fix_broken_symlinks
    echo "    Installing additional requirements."
    echo
    pip install -r system/requirements/requirements_standalone.txt
    curl -LO https://github.com/erew123/alltalk_tts/releases/download/DeepSpeed-14.0/deepspeed-0.14.2+cu121torch2.2-cp311-cp311-manylinux_2_24_x86_64.whl
    pip install --upgrade gradio==4.32.2
    echo Installing DeepSpeed...
    pip install deepspeed-0.14.2+cu121torch2.2-cp311-cp311-manylinux_2_24_x86_64.whl
    rm deepspeed-0.14.2+cu121torch2.2-cp311-cp311-manylinux_2_24_x86_64.whl
    conda clean --all --force-pkgs-dirs -y
    # Create start_environment.sh to run AllTalk
    cat << EOF > start_environment.sh
#!/bin/bash
cd "$(dirname "${BASH_SOURCE[0]}")"
if [[ "$(pwd)" =~ " " ]]; then echo This script relies on Miniconda which can not be silently installed under a path with spaces. && exit; fi
# deactivate existing conda envs as needed to avoid conflicts
{ conda deactivate && conda deactivate && conda deactivate; } 2> /dev/null
# config
CONDA_ROOT_PREFIX="$(pwd)/alltalk_environment/conda"
INSTALL_ENV_DIR="$(pwd)/alltalk_environment/env"
# environment isolation
export PYTHONNOUSERSITE=1
unset PYTHONPATH
unset PYTHONHOME
export CUDA_PATH="$INSTALL_ENV_DIR"
export CUDA_HOME="$CUDA_PATH"
# activate env
bash --init-file <(echo "source \"$CONDA_ROOT_PREFIX/etc/profile.d/conda.sh\" && conda activate \"$INSTALL_ENV_DIR\"")
EOF
    cat << EOF > start_alltalk.sh
#!/bin/bash
source "${CONDA_ROOT_PREFIX}/etc/profile.d/conda.sh"
conda activate "${INSTALL_ENV_DIR}"
python script.py
EOF
    cat << EOF > start_finetune.sh
#!/bin/bash
export TRAINER_TELEMETRY=0
source "${CONDA_ROOT_PREFIX}/etc/profile.d/conda.sh"
conda activate "${INSTALL_ENV_DIR}"
python finetune.py
EOF
    cat << EOF > start_diagnostics.sh
#!/bin/bash
source "${CONDA_ROOT_PREFIX}/etc/profile.d/conda.sh"
conda activate "${INSTALL_ENV_DIR}"
python diagnostics.py
EOF
    chmod +x start_alltalk.sh
    chmod +x start_environment.sh
    chmod +x start_finetune.sh
    chmod +x start_diagnostics.sh
    echo
    echo
    echo -e "    Run ${L_YELLOW}./start_alltalk.sh${NC} to start AllTalk."
    echo -e "    Run ${L_YELLOW}./start_diagnostics.sh${NC} to start Diagnostics."
    echo -e "    Run ${L_YELLOW}./start_finetune.sh${NC} to start Finetuning."
    echo -e "    Run ${L_YELLOW}./start_environment.sh${NC} to start the AllTalk Python environment."
    echo
    echo -e "    To install ${L_YELLOW}DeepSpeed${NC} on Linux, there are additional"
    echo -e "    steps required. Please see the Github or documentation on DeepSeed."
    echo
}

install_custom_standalone
