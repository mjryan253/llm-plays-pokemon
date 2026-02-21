#!/usr/bin/env bash
# Build mGBA from source with Python bindings (-DBUILD_PYTHON=ON).
# Run from anywhere: bash pygba/setup_mgba.sh
set -euo pipefail

MGBA_REPO="https://github.com/mgba-emu/mgba.git"
BUILD_DIR="${MGBA_BUILD_DIR:-/tmp/mgba-build}"

echo "=== mGBA Python Bindings Setup ==="
echo ""

# ── dependencies ────────────────────────────────────────────────────
echo "Installing build dependencies (requires sudo)..."
if command -v apt-get &>/dev/null; then
    sudo apt-get update -qq
    sudo apt-get install -y -qq \
        cmake build-essential git \
        libelf-dev libzip-dev libpng-dev libsqlite3-dev \
        qt6-base-dev qt6-multimedia-dev libsdl2-dev \
        python3-dev swig
elif command -v dnf &>/dev/null; then
    sudo dnf install -y \
        cmake gcc-c++ git \
        elfutils-libelf-devel libzip-devel libpng-devel sqlite-devel \
        qt6-qtbase-devel qt6-qtmultimedia-devel SDL2-devel \
        python3-devel swig
elif command -v pacman &>/dev/null; then
    sudo pacman -Sy --noconfirm \
        cmake base-devel git \
        libelf libzip libpng sqlite \
        qt6-base qt6-multimedia sdl2 \
        python swig
else
    echo "Unsupported package manager. Install cmake, libelf-dev, swig, python3-dev manually."
fi

# ── clone ───────────────────────────────────────────────────────────
echo ""
echo "Cloning mGBA into ${BUILD_DIR}..."
rm -rf "${BUILD_DIR}"
git clone --depth 1 "${MGBA_REPO}" "${BUILD_DIR}"

# ── build ───────────────────────────────────────────────────────────
echo ""
echo "Building mGBA with Python bindings..."
cd "${BUILD_DIR}"
mkdir -p build && cd build
cmake .. -DBUILD_PYTHON=ON -DCMAKE_INSTALL_PREFIX=/usr/local
make -j"$(nproc)"

# ── install ─────────────────────────────────────────────────────────
echo ""
echo "Installing (requires sudo)..."
sudo make install
sudo ldconfig

# ── verify ──────────────────────────────────────────────────────────
echo ""
if python3 -c "import mgba.core; print('mgba.core imported successfully')" 2>/dev/null; then
    echo "SUCCESS: mGBA Python bindings installed."
    echo "You can now run: python -m pygba"
else
    echo "WARNING: 'import mgba' still fails."
    echo "The bindings may have installed to a path Python cannot find."
    echo "Try: export PYTHONPATH=/usr/local/lib/python3/dist-packages:\$PYTHONPATH"
    echo "Or link the mgba package into your venv's site-packages."
fi
