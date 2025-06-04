# Salon Booking with Yape

Este proyecto contiene un backend sencillo en FastAPI y un frontend estático para agendar citas en un salón de belleza. Los usuarios reservan una hora e ingresan el código de pago de Yape. Un administrador puede validar el pago.

## Estructura

- `backend/`: código del servidor FastAPI y pruebas.
- `frontend/`: páginas HTML para el cliente, el administrador y el registro de usuarios.

## Uso

1. Instalar dependencias desde el archivo `requirements.txt`:

   ```bash
   pip install -r requirements.txt
   ```
2. Ejecutar el servidor desde la carpeta `backend`:

```bash
uvicorn main:app --reload --port 8000
```

Asegúrate de que el backend esté disponible en `http://localhost:8000`, ya que
 todas las páginas del frontend realizan sus solicitudes a esa dirección.

3. Abrir `frontend/index.html` en un navegador para reservar citas y `frontend/admin.html` para validarlas.
4. Para registrar nuevos usuarios se puede utilizar `frontend/register.html`, que ofrece una interfaz moderna basada en Bootstrap.

### Registro de usuarios

El backend permite registrar usuarios enviando un `POST` a `/users` con un nombre y al menos un correo electrónico o número de WhatsApp. La información se almacena en el archivo `users.db` usando SQLite, por lo que no se necesita ninguna base de datos externa.

## Pruebas

En la carpeta `backend` se encuentran pruebas simples que se ejecutan con:

```bash
pytest -q
```
