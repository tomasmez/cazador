
# Proyecto Cazador del Delta

Este repositorio contiene los archivos fuente necesarios para el desarrollo del proyecto SCR. Aquí encontrarás tanto el código fuente como los binarios precompilados.

## Estructura de archivos

- **/src**: Contiene todos los archivos fuente del proyecto Cazador del Delta.
- **/bin**: Aquí se encuentran los binarios precompilados. Es importante destacar que estos binarios se generan a partir de los archivos fuente ubicados en la carpeta /src.
  
## Compilación

Es necesario tener en tools/ el compilador para micropython **mpy-cross**. El mismo se obtiene del source situado en https://github.com/micropython/micropython

Para compilar el proyecto desde cero, simplemente ejecuta el comando `make`. Esto generará todos los binarios a partir de los archivos fuente disponibles en la carpeta /src.

```bash
make
```

## Instalación

Para instalar, se requiere de ampy de adafruit: https://github.com/scientifichackers/ampy

El puerto por default es /dev/ttyUSB0.

Una vez que los binarios están compilados, puedes instalar el proyecto ejecutando `make install`. Esto transferirá todos los archivos necesarios al dispositivo objetivo.

```bash
make install
```


