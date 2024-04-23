
SRC_DIR=.
BUILD_DIR=../bin/
MPY=../tools/mpy-cross

mdot_microdot.mpy: $(SRC_DIR)/microdot/microdot.py
	$(MPY) "$(SRC_DIR)/microdot/microdot.py" -o "$(BUILD_DIR)/microdot/microdot.mpy"

mdot___init__.mpy: $(SRC_DIR)/microdot/__init__.py
	$(MPY) "$(SRC_DIR)/microdot/__init__.py" -o "$(BUILD_DIR)/microdot/__init__.mpy"


boot.mpy: $(SRC_DIR)/boot.py
	$(MPY) "$(SRC_DIR)/boot.py" -o "$(BUILD_DIR)/boot.mpy"

main.mpy: $(SRC_DIR)/main.py
	$(MPY) "$(SRC_DIR)/main.py" -o "$(BUILD_DIR)/main.mpy"

programa_riego.mpy: $(SRC_DIR)/programa_riego.py
	$(MPY) "$(SRC_DIR)/programa_riego.py" -o "$(BUILD_DIR)/programa_riego.mpy"

cazador_del_delta.mpy: $(SRC_DIR)/cazador_del_delta.py
	$(MPY) "$(SRC_DIR)/cazador_del_delta.py" -o "$(BUILD_DIR)/cazador_del_delta.mpy"
	

calculate_sunrise_sunset.mpy: $(SRC_DIR)/calculate_sunrise_sunset.py
	$(MPY) "$(SRC_DIR)/calculate_sunrise_sunset.py" -o "$(BUILD_DIR)/calculate_sunrise_sunset.mpy"

ds___init__.mpy: $(SRC_DIR)/lib/ds1307/__init__.py
	$(MPY) "$(SRC_DIR)/lib/ds1307/__init__.py" -o "$(BUILD_DIR)/lib/ds1307/__init__.mpy"

ds_ds1307.mpy:  $(SRC_DIR)/lib/ds1307/ds1307.py 
	$(MPY) "$(SRC_DIR)/lib/ds1307/ds1307.py" -o "$(BUILD_DIR)/lib/ds1307/ds1307.mpy"

ds_version.mpy: $(SRC_DIR)/lib/ds1307/version.py
	$(MPY) "$(SRC_DIR)/lib/ds1307/version.py" -o "$(BUILD_DIR)/lib/ds1307/version.mpy"

templates:
	../tools/build_templates.sh "$(BUILD_DIR)"

ds1307: ds_ds1307.mpy ds___init__.mpy ds_version.mpy

microdot: mdot_microdot.mpy mdot___init__.mpy

cazador: main.mpy boot.mpy microdot ds1307 programa_riego.mpy calculate_sunrise_sunset.mpy cazador_del_delta.mpy

all: cazador templates

install: cazador templates
	#killall picocom 2> /dev/null
	cd $(BUILD_DIR) && ../tools/copy_files_to_esp32.sh 

