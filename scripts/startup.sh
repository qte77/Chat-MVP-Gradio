#!/bin/bash
# Custom Azure Web App start-up script
# Ensures proper unpacking and dependency installation for Gradio app
set -ex

SYS_ROOT_PATH="${SYS_ROOT_PATH:-/home/site/wwwroot}"
VENV_PATH="${VENV_PATH:-${SYS_ROOT_PATH}/antenv}"
LOGS_PATH="${LOGS_PATH:-${SYS_ROOT_PATH}/logs}"
REQS_FILE="${SYS_ROOT_PATH}/requirements.txt"
APP_FILE="${SYS_ROOT_PATH}/src/app.py"
APP_EXEC="src.app"
APP_LOG="${LOGS_PATH}/app_startup.log"
INSTALL_LOG="${LOGS_PATH}/pip_install.log"
STARTUP_LOG="${LOGS_PATH}/startup.log"
STARTFAIL_LOG="${SYS_ROOT_PATH}/startup_fail.log"

TIMESTAMP() { echo -e "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"; }

mkdir -p "${LOGS_PATH}" 2>&1 || {
        echo "$(TIMESTAMP) Failed to create log directory" \
            >> $STARTFAIL_LOG && exit 101
    }

echo "$(TIMESTAMP) Starting setup ..." > $STARTUP_LOG

# Check OS
OS_VER=$(cat /etc/os-release | grep PRETTY_NAME)
echo "$(TIMESTAMP) OS: ${OS_VER}" >> $STARTUP_LOG
echo "$(TIMESTAMP) User: $(whoami)" >> $STARTUP_LOG

# Test for app and requirements presence
for f in "${APP_FILE}" "${REQS_FILE}"; do
    [ ! -f "${f}" ] && echo "$(TIMESTAMP) Error: '$f' does not exist" \
        >> $STARTUP_LOG && exit 100
done

# Install pandoc and tex
PANDOC_VER=$(pandoc --version | head -n 1 2>/dev/null)
MAKE_VER=$(make --version | head -n 1 2>/dev/null)
if [ -n "$PANDOC_VER" ]; then
    echo "$(TIMESTAMP) '${PANDOC_VER}' installed." >> $STARTUP_LOG
else
    if [ -n "$MAKE_VER" ]; then
        echo "$(TIMESTAMP) '${MAKE_VER}' installed." >> $STARTUP_LOG
    else
        echo "$(TIMESTAMP) make is not installed. Installing..." >> $STARTUP_LOG
        apt-get update -qq >> $STARTUP_LOG
        apt-get install -y -qq make >> $STARTUP_LOG
    fi
    echo "$(TIMESTAMP) Calling 'make install_pandoc_tex' ..." >> $STARTUP_LOG
    make install_pandoc_tex >> $STARTUP_LOG 2>&1 || {
        echo "$(TIMESTAMP) Failed to 'make install_pandoc_tex'." >> $STARTUP_LOG
        exit 99
    }
fi

# Log Python and pip versions
echo "$(TIMESTAMP) Python version: $(python3 --version)" >> $STARTUP_LOG
echo "$(TIMESTAMP) System pip version: $(pip3 --version)" >> $STARTUP_LOG

# Create virtual environment
echo "$(TIMESTAMP) Creating virtual environment ..." >> $STARTUP_LOG
python3 -m venv $VENV_PATH >> $STARTUP_LOG 2>&1 || {
    echo "$(TIMESTAMP) Failed to create virtual environment" >> $STARTUP_LOG
    exit 1
}

# Activate virtual environment
echo "$(TIMESTAMP) Activating virtual environment ..." >> $STARTUP_LOG
source ${VENV_PATH}/bin/activate >> $STARTUP_LOG 2>&1 || {
    echo "$(TIMESTAMP) Failed to activate virtual environment" >> $STARTUP_LOG
    exit 2
}

# Verify virtual environment Python and pip
echo "$(TIMESTAMP) Virtual env Python version: $(python3 --version)" >> $STARTUP_LOG
echo "$(TIMESTAMP) Virtual env pip version: $(pip --version)" >> $STARTUP_LOG

# Upgrade pip and install requirements
reqstart="$(TIMESTAMP) Installing requirements ..."
echo $reqstart > $INSTALL_LOG
echo $reqstart >> $STARTUP_LOG
pip install --no-cache-dir --disable-pip-version-check pip >> $INSTALL_LOG 2>&1 || {
    echo "$(TIMESTAMP) Failed to upgrade pip" >> $STARTUP_LOG
    exit 3
}
pip install --no-cache-dir -r $REQS_FILE >> $INSTALL_LOG 2>&1 || {
    echo "$(TIMESTAMP) Failed to install requirements. Check '${INSTALL_LOG}' for errors" \
        >> $STARTUP_LOG
    cat $INSTALL_LOG >> $STARTUP_LOG
    exit 4
}

# Verify gradio installation
echo "$(TIMESTAMP) Verifying gradio installation ..." >> $STARTUP_LOG
pip show gradio >> $STARTUP_LOG 2>&1 || {
    echo "$(TIMESTAMP) Gradio not installed. Check '${INSTALL_LOG}' for errors" \
        >> $STARTUP_LOG
    exit 5
}

# Run app
appstart="$(TIMESTAMP) Starting app ..."
echo $appstart > $APP_LOG
echo $appstart >> $STARTUP_LOG
python3 -m $APP_EXEC >> $APP_LOG 2>&1 || {
    echo "$(TIMESTAMP) Failed to start app. Showing '${APP_LOG}' ..." >> $STARTUP_LOG
    cat $APP_LOG >> $STARTUP_LOG
    exit 6
}