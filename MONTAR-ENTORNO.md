# Montar el entorno de desarrollo

Estos pasos levantan una copia completa del sistema en cualquier equipo
Windows, con datos de prueba ficticios y sin tocar producción.

Toma unos 30 minutos, casi todo esperando descargas.

---

## Lo que se copia y lo que se regenera

| | |
|---|---|
| **Se clona de GitHub** | Todo el código, plantillas, imágenes y catálogos |
| **Se regenera** | Entorno virtual, base de datos, datos de prueba |
| **Se escribe a mano** | El archivo `.env` (nunca viaja por git) |

No hay que copiar carpetas entre computadoras. Con clonar el repositorio y
seguir estos pasos, el resultado es idéntico.

---

## 1. Programas necesarios

En PowerShell:

```powershell
winget install --id Git.Git
winget install --id GitHub.cli
winget install --id Python.Python.3.12
winget install --id MariaDB.Server
```

**Cierra PowerShell y abre una ventana nueva** para que reconozca los
comandos recién instalados.

> **Python 3.12 exactamente.** En versiones más nuevas varias dependencias
> no tienen paquete precompilado y pip intenta compilarlas, lo que exige
> Visual Studio.

Verifica:

```powershell
py -3.12 --version
```

---

## 2. Arrancar MariaDB

`winget` instala los archivos pero no registra el servicio. Abre PowerShell
**como administrador** (clic derecho → Ejecutar como administrador):

```powershell
& "C:\Program Files\MariaDB 12.3\bin\mariadbd.exe" --install MariaDB --defaults-file="C:\Program Files\MariaDB 12.3\data\my.ini"
net start MariaDB
```

Crea la base:

```powershell
& "C:\Program Files\MariaDB 12.3\bin\mysql.exe" -u root -e "CREATE DATABASE legalbit CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;"
```

> Si instalaste otra versión, ajusta `MariaDB 12.3` a la que tengas.

---

## 3. Clonar el proyecto

```powershell
gh auth login
```

Elige: `GitHub.com` → `HTTPS` → `Y` → `Login with a web browser`.

```powershell
cd $HOME\Documents
git clone https://github.com/beto-worst/AVALO.git
cd AVALO
```

---

## 4. Entorno virtual y dependencias

```powershell
py -3.12 -m venv env
env\Scripts\python.exe -m pip install --upgrade pip
env\Scripts\python.exe -m pip install -r requirements-local.txt
env\Scripts\python.exe -m pip install playwright
```

> `requirements-local.txt` es igual a `requirements.txt` salvo por unos
> paquetes subidos al mínimo necesario para Python 3.12.
> `requirements.txt` queda intacto como referencia de lo que corre en
> producción.
>
> `playwright` se instala aparte porque el código lo importa pero nadie lo
> declaró en `requirements.txt`.

---

## 5. Configuración

```powershell
copy LegalBit\.env.example LegalBit\.env
```

Abre `LegalBit\.env` y ajusta `DB_USER` y `DB_PASS` según cómo quedó tu
MariaDB. Si root no tiene contraseña, déjalo así:

```
DB_USER=root
DB_PASS=
```

**Deja vacías las llaves de los proveedores.** Es lo que evita que las
pruebas gasten créditos de NUFI o Moffin, o consulten personas reales.

---

## 6. Base de datos

```powershell
env\Scripts\python.exe manage.py migrate
& "C:\Program Files\MariaDB 12.3\bin\mysql.exe" -u root legalbit -e "source MySQL/catalogos.sql"
```

Crea tu usuario:

```powershell
env\Scripts\python.exe manage.py createsuperuser
```

Y genera datos ficticios (50 personas, 30 investigaciones):

```powershell
env\Scripts\python.exe MySQL\generar_datos_prueba.py
```

> El generador espera un usuario llamado `admin`. Si usaste otro nombre,
> ajusta esa línea del script.

---

## 7. Arrancar

```powershell
env\Scripts\python.exe manage.py runserver
```

Abre http://127.0.0.1:8000

---

## Uso diario

Arrancar:

```powershell
cd $HOME\Documents\AVALO
env\Scripts\python.exe manage.py runserver
```

Detener: `Ctrl+C`

Al guardar cualquier archivo `.py` el servidor se reinicia solo.

Empezar con datos limpios:

```powershell
env\Scripts\python.exe MySQL\generar_datos_prueba.py --limpiar
env\Scripts\python.exe MySQL\generar_datos_prueba.py
```

---

## Qué esperar

**Las funciones que llaman a proveedores fallan**, y es a propósito:
consultar buró, escanear INE, validar lista nominal. Sin llaves en el
`.env` no hay forma de gastar dinero ni de tocar datos de personas reales
desde una máquina de desarrollo.

**Los reportes de buró de los datos de prueba son inventados**, pero con
la misma estructura que devuelve Moffin, así que los PDF y las vistas de
reporte se renderizan bien.

---

## Producción, para referencia

Producción **no** usa Docker, a pesar de lo que sugiere el
`docker-compose.yml` del repositorio.

| | |
|---|---|
| Servidor | AWS Lightsail, `sistema.avalo.mx` |
| Ruta | `/home/admin/LegalBit2` |
| Servidor web | nginx → Gunicorn en `127.0.0.1:8000` |
| Reiniciar | `sudo systemctl restart legalbit` |
| Base de datos | MySQL local en el mismo servidor |

El despliegue se hace copiando archivos, no con git.
