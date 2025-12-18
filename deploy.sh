#!/bin/bash

# Script de auto-deployment para api-youtube
# Este script se ejecutará cuando GitHub envíe una notificación

echo "🚀 Iniciando deployment automático..."
echo "⏰ $(date)"

# Directorio del proyecto
PROJECT_DIR="/var/www/api-youtube"
LOG_FILE="/var/log/api-youtube-deploy.log"

# Función de logging
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Cambiar al directorio del proyecto
cd "$PROJECT_DIR" || exit 1

log "📂 Directorio: $PROJECT_DIR"

# Hacer backup del estado actual
log "💾 Creando backup..."
git stash

# Obtener cambios del repositorio
log "📥 Descargando cambios de GitHub..."
if git pull origin main; then
    log "✅ Git pull exitoso"
else
    log "❌ Error en git pull"
    exit 1
fi

# Actualizar dependencias si requirements.txt cambió
if git diff HEAD@{1} --name-only | grep -q "requirements.txt"; then
    log "📦 Actualizando dependencias..."
    source venv/bin/activate
    pip install -r requirements.txt
fi

# Reiniciar el servicio
log "🔄 Reiniciando servicio..."
if systemctl restart youtube-api; then
    log "✅ Servicio reiniciado exitosamente"
else
    log "❌ Error al reiniciar servicio"
    exit 1
fi

# Verificar estado del servicio
sleep 2
if systemctl is-active --quiet youtube-api; then
    log "✅ Deployment completado exitosamente"
    log "🌐 Aplicación disponible en http://192.168.1.251"
else
    log "❌ El servicio no está activo después del deployment"
    systemctl status youtube-api
    exit 1
fi

echo "🎉 Deployment finalizado!"
