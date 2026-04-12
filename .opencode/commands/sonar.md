---
description: Ejecutar analisis SonarQube del proyecto
agent: build
---
Ejecuta un analisis de codigo con SonarQube Cloud. Sigue estos pasos:

1. Verifica que existe el archivo `sonar-project.properties` en la raiz del proyecto.
2. Verifica que la variable de entorno `SONAR_TOKEN` esta configurada.
3. Ejecuta el comando: `npx @sonar/scan`
4. Espera a que el Quality Gate devuelva el resultado.
5. Muestra un resumen de los issues encontrados (bugs, vulnerabilidades, code smells).
6. Si el Quality Gate falla, sugiere las acciones correctivas prioritarias.
