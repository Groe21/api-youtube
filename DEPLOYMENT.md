# Configuración de Auto-Deployment para api-youtube

Este proyecto está configurado para deployment automático cuando se hace push a GitHub.

## 🚀 Métodos de Deployment

### Opción 1: GitHub Webhook (Automático)

1. **Configurar Webhook en GitHub:**
   - Ve a: `https://github.com/Groe21/api-youtube/settings/hooks`
   - Click en "Add webhook"
   - Payload URL: `http://192.168.1.251/webhook/deploy`
   - Content type: `application/json`
   - Secret: (opcional para mayor seguridad)
   - Selecciona: "Just the push event"
   - Click "Add webhook"

2. **Configurar permisos en el servidor:**
   ```bash
   # Dar permisos al usuario www-data para git pull
   sudo visudo
   # Agregar: www-data ALL=(ALL) NOPASSWD: /bin/systemctl restart youtube-api
   
   # Configurar git en el servidor
   cd /var/www/api-youtube
   sudo chown -R www-data:www-data .git
   sudo -u www-data git config --global --add safe.directory /var/www/api-youtube
   ```

3. **¡Listo!** Cada vez que hagas `git push`, GitHub notificará a tu servidor y se actualizará automáticamente.

---

### Opción 2: Script Manual de Deployment

Copia el archivo `deploy.sh` al servidor y ejecútalo cuando quieras actualizar:

```bash
# En el servidor
sudo chmod +x /var/www/api-youtube/deploy.sh
sudo /var/www/api-youtube/deploy.sh
```

---

### Opción 3: Cron Job (Cada X minutos)

Para revisar automáticamente cada 5 minutos si hay cambios:

```bash
# Editar crontab
sudo crontab -e

# Agregar esta línea:
*/5 * * * * cd /var/www/api-youtube && git fetch origin && [ $(git rev-parse HEAD) != $(git rev-parse @{u}) ] && /var/www/api-youtube/deploy.sh
```

---

## 📋 Logs de Deployment

Los logs se guardan en: `/var/log/api-youtube-deploy.log`

Ver logs en tiempo real:
```bash
sudo tail -f /var/log/api-youtube-deploy.log
```

---

## 🔒 Seguridad (Opcional)

Para agregar autenticación al webhook:

1. Genera un secreto:
   ```bash
   openssl rand -hex 20
   ```

2. Configúralo en GitHub (Secret field)

3. Descomenta las líneas de verificación en `app.py` y agrega:
   ```bash
   export GITHUB_WEBHOOK_SECRET="tu-secreto-aqui"
   ```

---

## ✅ Verificar que funciona

1. Haz un cambio en tu código local
2. Ejecuta:
   ```bash
   git add .
   git commit -m "Test auto-deployment"
   git push
   ```
3. Espera 5-10 segundos
4. Verifica en http://192.168.1.251

---

## 🛠️ Troubleshooting

**Error: Permission denied**
```bash
sudo chown -R www-data:www-data /var/www/api-youtube
```

**Error: Git pull failed**
```bash
cd /var/www/api-youtube
sudo -u www-data git status
sudo -u www-data git pull origin main
```

**Error: Service restart failed**
```bash
sudo systemctl status youtube-api
sudo journalctl -u youtube-api -n 50
```
