#!/bin/bash


if [ -z "$1" ]; then
	echo "usage: $0 <base dir to put templates>"
	echo "templates based from ./template_sources/"
	exit 0
fi


BUILD_DIR="$1"

TEMPLATES_DIR="$BUILD_DIR/templates"
SOURCE_DIR="../template_sources"


TEMPLATES=("index.html"
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
	STRING="###ACTIVE${file}###"
	sed -i "s/$STRING/class=\"active\"/g" "$TEMPLATES_DIR/$file"
	sed -i "s/###ACTIVE.*###//g"  "$TEMPLATES_DIR/$file"

	cat "$SOURCE_DIR/$file" >> "$TEMPLATES_DIR/$file"
done

