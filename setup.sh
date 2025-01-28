#!/bin/bash

echo "AIRFLOW_UID=$(id -u)" > .env

export AIRFLOW_PROJ_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

folders=("$AIRFLOW_PROJ_DIR/jars" "$AIRFLOW_PROJ_DIR/logs" "$AIRFLOW_PROJ_DIR/plugins") 

for folder in "${folders[@]}"; do
    if [ ! -d "$folder" ]; then
        mkdir -p "$folder"
        echo "📁 Carpeta creada: $folder"
    else
        echo "✅ La carpeta ya existe: $folder"
    fi
done


curl https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar -o aws-java-sdk-bundle-1.12.262.jar
curl https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-core/1.12.262/aws-java-sdk-core-1.12.262.jar -o aws-java-sdk-core-1.12.262.jar
curl https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar -o hadoop-aws-3.3.4.jar
curl https://repo1.maven.org/maven2/com/databricks/spark-xml_2.12/0.14.0/spark-xml_2.12-0.14.0.jar -o spark-xml_2.12-0.14.0.jar

mv $AIRFLOW_PROJ_DIR/*.jar $AIRFLOW_PROJ_DIR/jars/
