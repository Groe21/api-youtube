#!/bin/bash
# Script de actualización manual para api-youtube

echo "🚀 Actualizando api-youtube..."

# Ir al directorio del proyecto
cd /var/www/api-youtube

# Hacer backup
echo "💾 Haciendo backup..."
sudo -u www-data git stash

# Obtener últimos cambios
echo "📥 Descargando cambios..."
sudo -u www-data git pull origin main

# Verificar si requirements.txt cambió
if git diff HEAD@{1} --name-only 2>/dev/null | grep -q "requirements.txt"; then
    echo "📦 Actualizando dependencias..."
    sudo /var/www/api-youtube/venv/bin/pip install -r requirements.txt
fi

# Reiniciar servicio
echo "🔄 Reiniciando servicio..."
sudo systemctl restart youtube-api

# Verificar estado
sleep 2
if systemctl is-active --quiet youtube-api; then
    echo "✅ Actualización completada exitosamente!"
    echo "🌐 App disponible en http://192.168.1.251"
else
    echo "❌ Error: El servicio no está activo"
    sudo systemctl status youtube-api
fi
