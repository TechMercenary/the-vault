# the-vault

Software de contabilidad financiera personal orientado a Argentina

## Modo de uso

Ejecutar `src/main.py`

## Desarrollo

Crear un archivo `.env` en la raiz del proyecto y agregar:

- `PYTHONPATH=<ruta al proyecto>;<ruta a proyecto/src>`
- `DEBUG=True`
- `SQLALQUEMY_ECHO=False`

Usar `python >= 3.11`

Para crear la UI se puede usar `pygubu-designer`:

- `pip install pygubu-designer`
- Ejecutar `<virtual env>/Scripts/pygubu-designer.exe`
