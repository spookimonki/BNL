#!/usr/bin/env bash

set -e

#Startup script for Prosjektet med både globale variabla og Virtuelt environment handling:

BNL_VENV_PATH="/home/${USER}/.BNL_venv"

clean() {
	exit_code="$?"
	echo "------------ Environment feilet, sletter filer. Feilkode: ${exit_code} ------------"
	rm -rf "${BNL_VENV_PATH}"
}

trap clean ERR

if test -d "${BNL_VENV_PATH}/.venv"; then
	echo -e "\033[32mVirtual environment finnes i ${BNL_VENV_PATH}, skipper..\033[0m"
else
	echo -e "\033[31mFinner ikke Venv mappe, bygger...\033[0m" && mkdir -p "${BNL_VENV_PATH}"
	python3 -m venv "${BNL_VENV_PATH}/.venv" && source "${BNL_VENV_PATH}/.venv/bin/activate"
	pip install --no-cache-dir	cython \
					numpy==1.26.4 \
					cuda-toolkit \
					pillow \
		 			matplotlib \
		 			PyQt5 \
		 			PyYAML \
		 			cocotools \
		 			cuda-toolkit \
		 			torch \
		 			torchvision \
		 			ultralytics-opencv-headless
	deactivate
	
echo -e "Installed venv in ${BNL_VENV_PATH}"

fi

trap - ERR

