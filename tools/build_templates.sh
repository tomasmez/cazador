#!/bin/bash


if [ -z "$1" ]; then
	echo "usage: $0 <base dir to put templates>"
	echo "templates based from ./template_sources/"
	exit 0
fi


BUILD_DIR="$1"

TEMPLATES_DIR="$BUILD_DIR/templates"
SOURCE_DIR="../template_sources"


TEMPLATES=(
	"index_not_running.html"
	"index_running.html"
	"config.html"
	"horas_arranque.html"
	"tiempos_riego.html"
	"registration.html"
	)	

HEADER="$SOURCE_DIR/header.html"

for file in ${TEMPLATES[@]}; do
	echo "writing $file"

	cat "${HEADER%.*}.style" > "$TEMPLATES_DIR/$file"
	cat "$SOURCE_DIR/${file%.*}.style" >> "$TEMPLATES_DIR/$file"
	cat "$HEADER" >> "$TEMPLATES_DIR/$file"

	# special case for all files that start with index_
	if [ "${file%%_*}" == "index" ]; then
		STRING="###ACTIVEindex.html###"
	else
		STRING="###ACTIVE${file}###"
	fi

	sed -i "s/$STRING/class=\"active\"/g" "$TEMPLATES_DIR/$file"
	sed -i "s/###ACTIVE.*###//g"  "$TEMPLATES_DIR/$file"

	cat "$SOURCE_DIR/$file" >> "$TEMPLATES_DIR/$file"
done

