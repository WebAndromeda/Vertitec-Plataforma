# 🚀 Plataforma Vertitec

La **Plataforma Vertitec** es una aplicación web en desarrollo, orientada a empresas de ingeniería (especialmente mantenimiento de ascensores). Está diseñada para facilitar la gestión de reportes técnicos, la comunicación con administraciones de edificios y el seguimiento de servicios realizados.

---

## 📝 Descripción

Esta plataforma permite a técnicos registrar los detalles de mantenimiento realizados en ascensores, mientras que administradores y clientes pueden consultar esa información de forma rápida, organizada y remota.

### 🎯 Propósito

- Digitalizar los reportes técnicos de mantenimiento.
- Agilizar el acceso a la información de los servicios realizados.
- Notificar automáticamente a los clientes sobre el estado de sus equipos y necesidades de repuestos.

### 🧩 Problemas que soluciona

- Elimina la gestión manual en papel.
- Ahorra tiempo en la comunicación entre técnicos y administradores.
- Centraliza el historial de servicios y necesidades técnicas por edificio.

---

## 👥 Roles y funcionalidades

### 👷 Técnico
- Ver agendamientos asignados y pendientes.
- Iniciar agendamientos y diligenciar formularios de servicio.
- Registrar observaciones, recomendaciones y checklist técnico.

### 🏢 Cliente / Edificio
- Ver historial y próximos agendamientos.
- Consultar repuestos instalados o pendientes.

### 🛠️ Administrador
- CRUD completo de:
  - Técnicos
  - Edificios
  - Torres
  - Agendamientos

---
## Diseño de la base de datos
![Diseño de la base de datos](DiseñoDB.png)

## ✅ Funcionalidades actuales

- CRUD de técnicos
- CRUD de administradores
- CRUD de edificios/clientes

---

## 🚧 Funcionalidades pendientes

- Estilos responsive en todos los CRUD
- CRUD de repuestos
- Paginación y filtros en listados
- Campos dependientes (por ejemplo, torres según edificio)
- Buscador de edificios

---

## 🧰 Tecnologías utilizadas

- **Lenguaje:** Python 3.12.3
- **Framework:** Django
- **Frontend:** Bootstrap, HTML, CSS, JavaScript
- **Base de datos:** SQLite (por defecto en Django)

---

## ⚙️ Instalación

Sigue estos pasos para instalar el proyecto localmente:

```bash
# 1. Crear carpeta contenedora
mkdir Contenedor
cd Contenedor/

# 2. Clonar el repositorio
git clone https://github.com/WebAndromeda/Vertitec-Plataforma.git

# 3. Crear y activar entorno virtual
python3 -m venv env
source env/bin/activate

# 4. Instalar dependencias
cd Vertitec-Plataforma/
pip install -r requirements.txt

# 5. Aplicar migraciones
python manage.py migrate

# 6. Crear usuarios, grupos y demo inicial
python manage.py setup_app

# 7. Iniciar servidor
python manage.py runserver

 Instrucciones de uso
Accede a la plataforma desde: http://localhost:8000

Usuarios de prueba creados automáticamente por el comando setup_app:

Superusuario: root / chatgpt22

Administrador: admin / chatgpt22

Técnico: tech / chatgpt22

Cliente: cliente / chatgpt22

