# CLOUDING-DDNS-FW

Control firewall del VPS en Clouding con notificación a Telegram o Discord.

En su primera ejecución nos añade las reglas de firewall en nuestro VPS de Clouding teniendo en cuenta el nombre del firewall que le pasamos en la variable CLOUDING_FW_NAME y los datos introducidos en el fichero registros_fw.json.

En las siguientes ejecuciones que se realizarán según definamos en la variable CRON, chequeará si ha habido cambio de IP con referencia a lo que tenemos en las reglas de firewall en Clouding y si ha habido cambio de IP, actualizará la IP en el registro del firewall de Clouding.

Explicación del fichero registros_fw.json mas abajo. 

### Configuración variables de entorno en fichero .env (renombrar el env-example a .env)

| VARIABLE                | NECESARIA | VERSIÓN | VALOR |
|:----------------------- |:---------:| :------:| :-------------|
| CLOUDING_API_URL        |     ✅    | v0.1.0  | Por defecto: https://api.clouding.io/v1                                     |
| CLOUDING_API_TOKEN      |     ✅    | v0.1.0  | Token para el acceso a Clouding a través de la API. (lo generas desde el panel de control de Clouding) |
| CLOUDING_FW_NAME        |     ✅    | v0.1.0  | Nombre del firewall en tu VPS de Clouding.                                  |
| CLIENTE_NOTIFICACION    |     ❌    | v0.1.0  | Cliente de notificaciones. (telegram o discord)                             |
| TELEGRAM_BOT_TOKEN      |     ❌    | v0.1.0  | Token del bot de Telegram.                                                  |
| TELEGRAM_CHAT_ID        |     ❌    | v0.1.0  | ID del chat de Telegram.                                                    |
| DISCORD_WEBHOOK         |     ❌    | v0.1.0  | Discord Webhook.                                                            |
| CRON                    |     ✅    | v0.1.0  | Hora / fecha de ejecución. (formato crontab. ej., */10 * * * * = cada 10 minutos, visita https://crontab.guru para más info.) |
| DEBUG                   |     ✅    | v0.1.0  | Habilita el modo Debug en el log. (0 = No / 1 = Si)                         |
| TZ                      |     ✅    | v0.1.0  | Timezone (Por ejemplo: Europe/Madrid)                                       |

La VERSIÓN indica cuando se añadió esa variable o cuando sufrió alguna actualización. Consultar https://github.com/unraiders/clouding-ddns-fw/releases

---

  > [!IMPORTANT]
  > Debemos descargar 2 ficheros del repositorio que son necesarios para el funcionamiento de este Docker y colocarlos en la carpeta que mapeamos como volumen en nuestro docker-compose:
  > - check_ip.txt que contiene las url's donde consultar la dirección IP pública de tu conexión a Internet.
  > - registros_ejemplo_fw.json que renombraremos a registros_fw.json que es el fichero de configuración para añadir las reglas en el firewall del VPS en Clouding. 

---

### Explicación del fichero registros_fw.json

 La estructura del fichero es la siguiente:

```json
[
    {
        "firewall_id": "",
        "sourceIp": "",
        "protocol": "",
        "description": "",
        "portRangeMin": "",
        "portRangeMax": "",
        "id": ""
    },
    {
        "firewall_id": "",
        "sourceIp": "",
        "protocol": "",
        "description": "",
        "portRangeMin": "",
        "portRangeMax": "",
        "id": ""
    }
]

```
- **firewall_id**: Utilizado internamente, no rellenar.  
- **sourceIp**: Utilizado internamente, no rellenar.
- **protocol**: Protocolo en esta regla de firewall (usualmente tcp o udp).
- **description**: Descripción que le quieres poner a esta regla de firewall.
- **portRangeMin**: Puerto desde que quieres abrir en el firewall (por ejemplo: 22)
- **portRangeMax**: Puerto hasta que quieres abrir en el firewall (por ejemplo: 22)
- **id**: Utilizado internamente, no rellenar.

---

Te puedes descargar la imagen del icono desde aquí: https://raw.githubusercontent.com/unraiders/clouding-ddns-fw/master/imagenes/clouding-ddns-fw.png

---

### Ejemplo docker-compose.yml (con fichero .env aparte)
```yaml
services:
  clouding-ddns-fw:
    image: unraiders/clouding-ddns-fw
    container_name: clouding-ddns-fw
    env_file:
        - .env
    volume:
        - tu_ruta_local_del_host:/app/data
    network_mode: bridge
    restart: unless-stopped
```

---

### Ejemplo docker-compose.yml (con variables incorporadas)
```yaml
services:
  clouding-ddns-fw:
    image: unraiders/clouding-ddns-fw
    container_name: clouding-ddns-fw
    environment:
        - CLOUDING_API_URL=https://api.clouding.io/v1
        - CLOUDING_API_TOKEN=
        - CLOUDING_FW_NAME=
        - CLIENTE_NOTIFICACION=
        - TELEGRAM_BOT_TOKEN=
        - TELEGRAM_CHAT_ID=
        - DISCORD_WEBHOOK=
        - CRON=*/10 * * * *
        - DEBUG=0
        - TZ=Europe/Madrid
    volume:
        - tu_ruta_local_del_host:/app/data
    network_mode: bridge
    restart: unless-stopped
```

---

## Instalación plantilla en Unraid.

- Nos vamos a una ventana de terminal en nuestro Unraid, pegamos esta línea y enter:
```sh
wget -O /boot/config/plugins/dockerMan/templates-user/my-clouding-ddns-fw.xml https://raw.githubusercontent.com/unraiders/clouding-ddns-fw/refs/heads/main/my-clouding-ddns-fw.xml
```
- Nos vamos a DOCKER y abajo a la izquierda tenemos el botón "AGREGAR CONTENEDOR" hacemos click y en seleccionar plantilla seleccionamos clouding-ddns-fw y rellenamos las variables de entorno necesarias, tienes una explicación en cada variable en la propia plantilla.

---

Este proyecto se hace a nivel personal y se comparte con la comunidad por si puede ser de utilidad.

Unraiders no tiene ningún vinculo con Clouding.io