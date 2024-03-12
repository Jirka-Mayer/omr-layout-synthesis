.PHONY: download-muscima-pp


download-muscima-pp:
	rm -rf datasets/MUSCIMA-pp_v1.0
	mkdir -p datasets
	wget https://github.com/apacha/OMR-Datasets/releases/download/datasets/MUSCIMA-pp_v1.0.zip
	unzip MUSCIMA-pp_v1.0.zip -d datasets
	rm MUSCIMA-pp_v1.0.zip
	mv datasets/v1.0 datasets/MUSCIMA-pp_v1.0
	wget https://github.com/apacha/OMR-Datasets/releases/download/datasets/CVC_MUSCIMA_PP_Annotated-Images.zip
	unzip CVC_MUSCIMA_PP_Annotated-Images.zip -d datasets/MUSCIMA-pp_v1.0/data/images
	rm CVC_MUSCIMA_PP_Annotated-Images.zip
