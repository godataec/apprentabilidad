# GoData Financial Dashboard - Deployment

## Opción 1: Deploy a Render (Recomendado - Gratis)

1. **Crear cuenta en Render**
   - Ve a https://render.com y crea una cuenta gratuita

2. **Subir código a GitHub**
   - Crea un repositorio en GitHub
   - Sube todo el proyecto (dashboard.py, processing.py, requirements.txt, Procfile)

3. **Crear Web Service en Render**
   - En Render, click "New +" → "Web Service"
   - Conecta tu repositorio de GitHub
   - Configuración:
     - **Name**: godata-dashboard
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn dashboard:server`
     - **Instance Type**: Free
   - Click "Create Web Service"

4. **Variables de entorno (opcional)**
   - En Render, ve a "Environment"
   - Agrega: `DASH_DEBUG=False`

5. **Acceder a tu app**
   - URL: https://godata-dashboard.onrender.com

---

## Opción 2: Deploy a Azure Web Apps

1. **Instalar Azure CLI**
   ```bash
   az login
   ```

2. **Crear recursos**
   ```bash
   az group create --name godata-rg --location eastus
   az webapp up --name godata-dashboard --resource-group godata-rg --runtime "PYTHON:3.11"
   ```

3. **Configurar variables**
   ```bash
   az webapp config appsettings set --name godata-dashboard --resource-group godata-rg --settings DASH_DEBUG=False
   ```

4. **Acceder**
   - URL: https://godata-dashboard.azurewebsites.net

---

## Opción 3: Deploy Manual con Gunicorn (Local/VPS)

1. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

2. **Ejecutar con Gunicorn**
   ```bash
   gunicorn dashboard:server --bind 0.0.0.0:8050 --workers 4
   ```

---

## Archivos creados para deployment:

- ✅ **requirements.txt** - Dependencias de Python
- ✅ **Procfile** - Configuración para servidores (Render/Heroku)
- ✅ **dashboard.py** - Actualizado con `server` para deployment

## Notas importantes:

- La app generará datos simulados cada vez que se reinicie
- El tier gratuito de Render se duerme después de 15 min de inactividad
- Para producción real, considera usar una base de datos en lugar de generar datos en memoria
