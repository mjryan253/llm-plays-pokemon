#!/usr/bin/env bash
# Build mGBA from source with Python bindings only (no GUI frontends).
# Run: bash pygba/setup_mgba.sh
set -euo pipefail

MGBA_VERSION="${MGBA_VERSION:-master}"
TARBALL_URL="https://github.com/mgba-emu/mgba/archive/refs/heads/${MGBA_VERSION}.tar.gz"
BUILD_DIR="${MGBA_BUILD_DIR:-/tmp/mgba-build}"

echo "=== mGBA Python Bindings Setup ==="
echo ""
echo "  Version : ${MGBA_VERSION}"
echo "  Build in: ${BUILD_DIR}"
echo ""

# ── dependencies ────────────────────────────────────────────────────
echo "Installing build dependencies (requires sudo)..."
if command -v apt-get &>/dev/null; then
    sudo apt-get update -qq
    sudo apt-get install -y -qq \
        cmake build-essential \
        libelf-dev libzip-dev zipcmp zipmerge ziptool libpng-dev \
        python3-dev python3-cffi swig
elif command -v dnf &>/dev/null; then
    sudo dnf install -y \
        cmake gcc-c++ \
        elfutils-libelf-devel libzip-devel libpng-devel \
        python3-devel python3-cffi swig
elif command -v pacman &>/dev/null; then
    sudo pacman -Sy --noconfirm \
        cmake base-devel \
        libelf libzip libpng \
        python python-cffi swig
else
    echo "Unsupported package manager."
    echo "Install: cmake, build tools, libelf-dev, libzip-dev, libpng-dev, python3-dev, python3-cffi, swig"
    exit 1
fi

# ── download ────────────────────────────────────────────────────────
echo ""
rm -rf "${BUILD_DIR}"
mkdir -p "${BUILD_DIR}"

echo "Downloading mGBA (${MGBA_VERSION})..."
curl -sL "${TARBALL_URL}" | tar xz --strip-components=1 -C "${BUILD_DIR}"

# ── build ───────────────────────────────────────────────────────────
echo "Building libmgba + Python bindings..."
mkdir -p "${BUILD_DIR}/build"
cmake -S "${BUILD_DIR}" -B "${BUILD_DIR}/build" \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=/usr/local \
    -DBUILD_PYTHON=ON \
    -DBUILD_QT=OFF \
    -DBUILD_SDL=OFF \
    -DBUILD_GL=OFF \
    -DBUILD_GLES2=OFF \
    -DBUILD_GLES3=OFF \
    -Wno-dev

make -C "${BUILD_DIR}/build" -j"$(nproc)"

# ── install ─────────────────────────────────────────────────────────
echo ""
echo "Installing (requires sudo)..."
sudo make -C "${BUILD_DIR}/build" install
sudo ldconfig

# ── verify ──────────────────────────────────────────────────────────
echo ""
if python3 -c "import mgba.core; print('mgba.core imported successfully')" 2>/dev/null; then
    echo "SUCCESS: mGBA Python bindings installed."
    echo "You can now run: python -m pygba"
else
    echo "WARNING: 'import mgba.core' failed."
    echo "The bindings may have installed to a non-default path."
    echo "Try: export PYTHONPATH=/usr/local/lib/python3/dist-packages:\$PYTHONPATH"
fi
