#!/bin/bash

THEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd ${THEDIR}
VDIR="botenv"

if [ ! -d "${VDIR}" ]; then
	virtualenv ${VDIR}
fi

# Install libraries
${VDIR}/bin/pip install -r requirements.pip

# Download corpora for nltk
# TODO: figure out which ones we actually need and just download those
#${VDIR}/bin/python -m nltk.downloader -d botenv/nltk_data/

