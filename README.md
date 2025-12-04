======================================================================
🌐 ConnectionCommunity: Plataforma de Intercambio de Habilidades Locales
======================================================================

[Python: 3.x] | [Django: 5.0] | [Licencia: MIT]

======================================================================
🎯 Resumen del Proyecto
======================================================================

ConnectionCommunity es un Marketplace de Habilidades Local cuyo objetivo es fomentar el intercambio de servicios comunitarios utilizando una moneda social digital: los Créditos de Tiempo (CR).

Este repositorio contiene la implementación del Producto Mínimo Viable (MVP), con foco en el desarrollo y la validación de la Integridad Atómica de la Moneda (RF-02) y el Matching Geoespacial (RF-03).

======================================================================
✨ Requerimientos Funcionales Clave Implementados
======================================================================

La arquitectura está diseñada bajo el patrón Modelo-Vista-Template (MVT) de Django.

--- 1. Integridad Atómica de Créditos (RF-02) - El Núcleo ---

Asegura que cada intercambio de 1 CR sea una operación atómica.

* COMMIT: Si el solicitante tiene saldo suficiente, la transferencia de 1 CR es instantánea y se confirma.
* ROLLBACK: Si el solicitante tiene saldo cero (saldo_cr < 1), la operación es abortada automáticamente por el sistema de bases de datos, impidiendo la corrupción de saldos.

--- 2. Geo-Matching y Proximidad (RF-03) ---

* Geolocalización: Las coordenadas Lat/Lon del usuario y del oferente se almacenan en el perfil.
* Ordenamiento por Distancia: Se utiliza la Fórmula de Haversine para calcular la distancia precisa (en kilómetros) y ordenar el listado de publicaciones por el servicio más cercano.

--- 3. Funcionalidades Transversales ---

* Registro y Bono (HU-01): Nuevo usuario recibe un saldo inicial de 2 CR.
* Marketplace (RF-04): CRUD completo para la creación y gestión de publicaciones de servicios.
* Visualización de Saldo (HU-05): El saldo CR es visible de forma constante en el encabezado.

======================================================================
🛠️ Stack Tecnológico
======================================================================

* Backend: Python 3.x
* Framework: Django 5.x (Arquitectura MVT)
* Base de Datos: SQLite3
* Lógica de Negocio: Service Layer (Funciones atómicas encapsuladas en transactions/services.py).

======================================================================
🚀 Instalación y Ejecución Local
======================================================================

### Requisitos
* Python 3.x instalado.

### 1. Clonar el Repositorio
git clone https://github.com/NicoBoost/ProjectCC.git
cd ProjectCC

### 2. Crear y Activar el Entorno Virtual (venv)
# Crear el entorno
python -m venv venv

# Activar el entorno (Windows)
.\venv\Scripts\activate
# Activar el entorno (Linux/macOS)
source venv/bin/activate

### 3. Instalar Dependencias
pip install django

### 4. Aplicar Migraciones
python manage.py migrate

### 5. Crear Superusuario (Admin)
python manage.py createsuperuser

### 6. Ejecutar el Servidor
python manage.py runserver
Accede a la aplicación en: http://127.0.0.1:8000/

======================================================================
🧪 Validación y Pruebas Unitarias
======================================================================

La funcionalidad crítica del RF-02 fue validada mediante pruebas automatizadas.

Para verificar la integridad del sistema:
python manage.py test transactions

El resultado 'OK' valida que:
* TC-CR-001: La transferencia de CR es exitosa (COMMIT).
* TC-CR-002: El intento de pago con saldo insuficiente causa un ROLLBACK.

======================================================================
👨‍💻 Autor y Licencia
======================================================================

* Autor: Nicolás Martínez A.
* Licencia: Este proyecto está bajo la Licencia MIT.
