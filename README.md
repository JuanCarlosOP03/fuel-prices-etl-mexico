# 🚗 Proyecto ETL sobre Precios de Combustibles en México ⛽

Este proyecto es un pipeline ETL (Extracción, Transformación y Carga) diseñado para obtener, procesar y almacenar datos sobre los precios de combustibles en México. Utiliza Apache Airflow para la orquestación 🔄 y Apache Spark para el procesamiento de los datos ⚡. Los datos provienen de fuentes oficiales disponibles en el portal de Datos Abiertos de México 🌐 (https://datos.gob.mx/).

## Características 🌟
- **Fuente de Datos**: Los datos provienen de la Comisión Reguladora de Energía (CRE) 📊, los cuales se actualizan periódicamente y están disponibles para consulta pública.
- **Ingesta**: Se extraen los datos en formato XML desde el portal de Datos Abiertos de México 📥, que proporcionan los precios actuales de combustibles.
- **Transformación**: Se realiza la limpieza y estructuración de los datos mediante Apache Spark 🔧 para asegurar su calidad y facilidad de análisis.
- **Almacenamiento**: Los datos procesados se cargan en AWS Redshift 📦, una base de datos en la nube optimizada para el análisis de grandes volúmenes de datos.
- **Orquestación**: Apache Airflow se encarga de gestionar la ejecución del pipeline ETL ⛅, garantizando la automatización y la programación de las tareas dentro de contenedores Docker 🐳.

A continuación se muestra el diagrama del pipeline:

![Diagram](https://github.com/JuanCarlosOP03/fuel-prices-etl-mexico/blob/main/diagram.jpg)


## 📊 Modelo de Datos

El modelo de datos de este proyecto está compuesto por tres tablas principales que almacenan información relacionada con las estaciones de combustible, los precios y los detalles de las estaciones. A continuación, se describen las tablas y sus columnas, junto con las fuentes de donde provienen los datos.

### 1. **Tabla `places`** 🏪
Esta tabla almacena la información básica sobre las estaciones de servicio.

```sql
CREATE TABLE "mx_prices_fuel"."places" (
    "place_id" INT PRIMARY KEY NOT NULL,
    "cre_id" VARCHAR(25) NOT NULL,
    "longitude" DOUBLE PRECISION NOT NULL, 
    "latitude" DOUBLE PRECISION NOT NULL,  
    "place_name" VARCHAR(150)                
);
```

- **place_id**: Identificador único de la estación de servicio.
- **cre_id**: Identificador del permiso.
- **longitude**: Longitud de la estación de servicio en grados.
- **latitude**: Latitud de la estación de servicio en grados.
- **place_name**: Nombre de la estación de servicio.

**Fuente**: [Datos sobre estaciones de servicio](https://publicacionexterna.azurewebsites.net/publicaciones/places)

---

### 2. **Tabla `prices`** 💰
Esta tabla almacena los precios de los combustibles en las estaciones de servicio.

```sql
CREATE TABLE "mx_prices_fuel"."prices" (
    "place_id" INT NOT NULL REFERENCES "mx_prices_fuel"."places" ("place_id"),  
    "fuel_type" VARCHAR(30) NOT NULL,
    "type_product" VARCHAR(30) NOT NULL,
    "price" DOUBLE PRECISION NOT NULL
);
```

- **place_id**: Referencia a la estación de servicio.
- **fuel_type**: Tipo de combustible (por ejemplo, gasolina o diésel).
- **type_product**: Tipo de producto (por ejemplo, premium, magna, o diésel).
- **price**: Precio del combustible en la estación de servicio.

**Fuente**: [Precios de combustibles](https://publicacionexterna.azurewebsites.net/publicaciones/prices)

---

### 3. **Tabla `places_details`** 🏠
Esta tabla contiene detalles adicionales sobre las estaciones de servicio, como su ubicación y fecha de entrada.

```sql
CREATE TABLE "mx_prices_fuel"."places_details" (
    "turn_code" VARCHAR(10) NOT NULL,
    "cre_id" VARCHAR(25) NOT NULL,
    "place_name" VARCHAR(150),
    "place_code" VARCHAR(10) NOT NULL,
    "date_entry" DATE,
    "plenary_date" DATE,
    "address" VARCHAR(200),
    "colony" VARCHAR(100),
    "cp" INT,
    "city" VARCHAR(80) NOT NULL,
    "state" VARCHAR(50) NOT NULL
);
```

- **turn_code**: Código del turno de la estación de servicio.
- **cre_id**: Identificador del permiso.
- **place_name**: Nombre de la estación de servicio.
- **place_code**: Código del lugar.
- **date_entry**: Fecha de entrada en la base de datos.
- **plenary_date**: Fecha plenaria.
- **address**: Dirección de la estación de servicio.
- **colony**: Colonia de la estación de servicio.
- **cp**: Código postal de la estación de servicio.
- **city**: Ciudad de la estación de servicio.
- **state**: Estado de la estación de servicio.

**Fuente**: [Informe de Expendio en Estaciones de Servicio - CRE](https://www.cre.gob.mx/documento/Expendioenestacionesdeservici.pdf)


## Tecnologías Utilizadas 🖥️
- **Docker & Docker Compose** 🐳: Para la contenerización de los servicios y su configuración.
- **Apache Airflow** 🌬️: Para la gestión y orquestación de las tareas del pipeline ETL.
- **Apache Spark** ⚡: Para el procesamiento y transformación de los datos.
- **AWS Redshift** 🌐: Para el almacenamiento de los datos procesados.
- **Python** 🐍: Lenguaje utilizado para la implementación de la lógica ETL.

## Instalación y Configuración ⚙️
### Prerrequisitos 📋
Asegúrate de tener los siguientes requisitos instalados:
- Docker y Docker Compose 🐳
- Python 3.x 🐍

### Pasos de instalación 🛠️
1. Clona el repositorio:
   ```bash
   export LOCAL_USER="$(whoami)"
   sudo mkdir /opt/airflow
   sudo chown -R $LOCAL_USER:root /opt/airflow
   chmod g+w /opt/airflow

   git clone https://github.com/JuanCarlosOP03/fuel-prices-etl-mexico.git /opt/airflow

   cd /opt/airflow
   
   source ./setup.sh
   ```
2. Configura las variables de entorno en `config/airflow.env`. Asegúrate de completar las siguientes variables:
   ```
   AWS_REGION=
   AWS_ACCESS_KEY_ID=
   AWS_SECRET_ACCESS_KEY=
   AWS_S3_ENDPOINT=
   ```
3. Construye y levanta los contenedores:
   ```bash
   docker-compose up -d --build
   ```
4. Accede a la interfaz de Airflow en `http://localhost:8080` y activa el DAG 🔄.
5. Crea las siguientes conexiones en Airflow para asegurar el funcionamiento del pipeline:
   - `aws_default` 🌍
   - `spark_default` ⚡
   - `redshift_default` 💾

Se recomienda almacenar el proyecto en `/opt/spark` para un rendimiento óptimo 🚀.

## Uso 🛠️
- La ejecución del pipeline se gestiona desde la interfaz de Airflow 🖥️.
- Los datos procesados y transformados se cargan en la base de datos Redshift y están listos para análisis posteriores 📊.

## Estructura del Proyecto 📁
```
├── Dockerfile.Airflow
├── Dockerfile.Spark
├── README.md
├── bd
│   └── crate_tables.sql
├── config
│   ├── airflow.env
│   ├── spark-defaults.conf
│   └── spark.env
├── dags
│   ├── pyspark_scripts
│   │   ├── process_places.py
│   │   ├── process_places_details.py
│   │   └── process_prices.py
│   ├── scr
│   │   ├── config
│   │   │   ├── __init__.py
│   │   │   └── conf.py
│   │   └── utils
│   │       ├── __init__.py
│   │       └── extractor.py
│   └── test.py
├── data
│   └── data
│       └── ext
│           ├── places.xml
│           ├── places_detail.pdf
│           └── prices.xml
├── docker-compose.yaml
├── entrypoint.sh
├── jars
│   ├── aws-java-sdk-bundle-1.12.262.jar
│   ├── aws-java-sdk-core-1.12.262.jar
│   ├── hadoop-aws-3.3.4.jar
│   ├── postgresql-42.7.4.jar
│   └── spark-xml_2.12-0.14.0.jar
├── logs
├── plugins
├── requirements.txt
├── setup.sh
```
