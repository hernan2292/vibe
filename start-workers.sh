#!/bin/bash
# Script para iniciar múltiples workers de Laravel Queue en Linux/macOS
# Para sincronización LDAP paralela

echo "========================================"
echo " Laravel Queue Workers - LDAP Sync"
echo "========================================"
echo ""

# Configuración
WORKERS=8
PHP_PATH="php"
ARTISAN_PATH="$(dirname "$0")/artisan"
LOG_DIR="$(dirname "$0")/storage/logs"

echo "Iniciando $WORKERS workers paralelos..."
echo ""

# Crear directorio de logs si no existe
mkdir -p "$LOG_DIR"

# Iniciar workers en background (sin --name, no existe en Laravel 7)
for i in $(seq 1 $WORKERS)
do
   $PHP_PATH "$ARTISAN_PATH" queue:work --timeout=180 --tries=3 --sleep=1 > "$LOG_DIR/worker-$i.log" 2>&1 &
   PID=$!
   echo "[OK] Worker $i iniciado (PID: $PID)"
   sleep 0.5
done

echo ""
echo "========================================"
echo " $WORKERS workers iniciados exitosamente!"
echo "========================================"
echo ""
echo "Para monitorear el progreso:"
echo "  php artisan ldap:sync-status {batch_id}"
echo ""
echo "Para ver logs en tiempo real:"
echo "  tail -f storage/logs/worker-1.log"
echo ""
echo "Para detener todos los workers:"
echo "  php artisan queue:restart"
echo "  O: pkill -f 'queue:work'"
echo ""
echo "Para ver workers activos:"
echo "  ps aux | grep 'queue:work'"
echo ""
