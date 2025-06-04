# Salon Booking with Yape

Este proyecto contiene un backend sencillo en FastAPI y un frontend estático para agendar citas en un salón de belleza. Los usuarios reservan una hora e ingresan el código de pago de Yape. Un administrador puede validar el pago.

## Estructura

- `backend/`: código del servidor FastAPI y pruebas.
- `frontend/`: páginas HTML para el cliente y el administrador.

## Uso

1. Instalar dependencias (ya incluidas en la imagen de Codex).
2. Ejecutar el servidor desde la carpeta `backend`:

```bash
uvicorn main:app --reload --port 8000
```

3. Abrir `frontend/index.html` en un navegador para reservar citas y `frontend/admin.html` para validarlas.

## Pruebas

En la carpeta `backend` se encuentran pruebas simples que se ejecutan con:

```bash
pytest -q
```
