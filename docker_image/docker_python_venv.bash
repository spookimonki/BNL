python3 -m "venv" "${BNL_VENV_PATH}/.venv" && source "${BNL_VENV_PATH}/.venv/bin/activate"
	pip install	cython \
			numpy==1.26.4 \
			cuda-toolkit \
			pillow \
		 	nvidia-cudnn-cu11 \
		 	matplotlib \
		 	PyQt5 \
		 	PyYAML \
		 	cocotools \
		 	cuda-toolkit \
		 	torch \
		 	torchvision \
		 	ultralytics-opencv-headless
