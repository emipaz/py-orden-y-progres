Genial idea usar watchdog para automatizar cosas, es una librería muy potente y poco conocida.

**1. ¿Qué es watchdog (muy corto)?**  
- Es una librería que “escucha” una carpeta y te avisa cuando se crean, modifican, mueven o borran archivos.  
- Con eso puedes disparar scripts automáticos sin tener que estar mirando tú.

**2. Script de ejemplo que ya tienes creado**  
Acabo de crear el archivo:  
- 5-librerias/01_watchdog_basico.py  

Este script:  
- Crea (si no existe) una carpeta llamada `carpeta_a_vigilar` al lado del script.  
- Muestra por pantalla cada vez que se crea, modifica, borra o mueve un archivo/carpeta dentro de `carpeta_a_vigilar`.  

**3. Pasos para probarlo (en tu Windows)**  
1) Instalar watchdog (una vez):  
   - Abre la terminal (PowerShell) en la carpeta 5-librerias.  
   - Ejecuta:  
     - `python -m pip install watchdog`  

2) Ejecutar el script:  
   - En la misma carpeta:  
     - `python 01_watchdog_basico.py`  

3) Probar eventos:  
   - En el Explorador de archivos, abre la carpeta `carpeta_a_vigilar` (se habrá creado sola).  
   - Crea un archivo de texto, modifícalo, cámbiale el nombre, bórralo.  
   - Verás en la terminal mensajes como:  
     - `[CREADO ARCHIVO] ...`  
     - `[MODIFICADO ARCHIVO] ...`  
     - `[ELIMINADO ARCHIVO] ...`  
     - `[MOVIDO] origen -> destino`  

Si quieres, el siguiente paso puede ser:  
- Que cualquier cambio en esa carpeta dispare otro script (por ejemplo, copiar archivos, procesar PDFs, convertir imágenes, etc.).  
Dime qué tipo de tarea te gustaría automatizar y lo montamos usando watchdog.

Made changes.