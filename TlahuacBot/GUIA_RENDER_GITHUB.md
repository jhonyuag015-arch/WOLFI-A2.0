# Publicar TláhuacBot/WOLFI-A con IA en Render

## 1. Crear una clave de Groq

Crea tu cuenta en GroqCloud y genera una API key desde su consola. La disponibilidad gratuita y sus límites dependen del plan y del modelo; consulta los límites vigentes en la consola.

**No compartas la clave en el chat, capturas, GitHub ni archivos del proyecto.**

## 2. Subir el proyecto a GitHub

Sube el contenido de esta carpeta al repositorio, conservando esta estructura. El archivo `Procfile` indica a Render cómo iniciar Flask con Gunicorn.

## 3. Configurar Render

En tu servicio de Render:

1. Abre **Environment**.
2. Agrega `GROQ_API_KEY` y pega ahí la clave privada.
3. Agrega `GROQ_MODEL` con valor `llama-3.1-8b-instant`.
4. Guarda los cambios.
5. En **Settings**, confirma que el servicio use la rama correcta de GitHub y que el comando de inicio sea `gunicorn app:app --workers 1 --threads 4 --timeout 120` (si Render toma el Procfile, no hace falta duplicarlo).
6. Ejecuta un nuevo deploy.

## 4. Probar

Abre la URL pública y prueba primero una pregunta sobre una carrera, por ejemplo: `¿Qué se estudia en Ingeniería en Sistemas Computacionales?`.

Las respuestas institucionales fijas (por ejemplo, costos, becas, fechas y trámites) siguen saliendo del motor de datos para evitar que la IA invente información. Si la API no está configurada o falla, se conserva el respaldo del motor.

## 5. Si falla

Consulta **Render > Logs**. Si aparece un error 401, revisa la clave; si aparece 429, se alcanzó un límite de uso temporal; si aparece un error de modelo, revisa que `GROQ_MODEL` siga disponible en la consola de Groq.
