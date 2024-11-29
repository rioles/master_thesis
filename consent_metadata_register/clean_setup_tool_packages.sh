#!/bin/bash

# Check if the directories exist before attempting to remove them
if [ -d "build" ]; then
    rm -r build/
fi

if [ -d "dist" ]; then
    rm -r dist/
fi

if [ -d "consent_register.egg-info" ]; then
    rm -r consent_register.egg-info/
fi

# Determine the site-packages directory dynamically for Python 3
PYTHON3_SITE_PACKAGES=$(python3 -c "import site; print(site.getsitepackages()[0])")

# Navigate to the site-packages directory for Python 3
cd "$PYTHON3_SITE_PACKAGES" || {
    echo "Failed to navigate to $PYTHON3_SITE_PACKAGES directory"
    exit 1
}

# Check if any of the vid_stream egg files exist before attempting to remove them for Python 3
# Remove all vid_stream egg files for Python 3
for file in consent_register.egg-info-*.egg; do
    if [ -e "$file" ]; then
        rm -r "$file"
    fi
done

# Determine the site-packages directory dynamically for Python 2
PYTHON2_SITE_PACKAGES=$(python -c "import site; print(site.getsitepackages()[0])")

# Navigate to the site-packages directory for Python 2
cd "$PYTHON2_SITE_PACKAGES" || {
    echo "Failed to navigate to $PYTHON2_SITE_PACKAGES directory"
    exit 1
}

# Check if any of the vid_stream egg files exist before attempting to remove them for Python 2
# Remove all vid_stream egg files for Python 2
for file in consent_register.egg-info-*.egg; do
    if [ -e "$file" ]; then
        rm -r "$file"
    fi
done
