#!/bin/bash

# ==============================================================================
# LightBerry OS - Instalador Robusto y Funcional
# Este script instala todo lo necesario para que funcione correctamente
# Si la app falla, creará un log en ~/lightberry-os/app.log
# ==============================================================================

# Colores para la salida
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # Sin Color

# Funciones de ayuda para los logs
print_status() { echo -e "$GREEN✅ $NC $1"; }
print_warning() { echo -e "$YELLOW⚠️ $NC $1"; }
print_error() { echo -e "$RED❌ $NC $1"; }
print_info() { echo -e "$BLUE🔍 $NC $1"; }

set -e

# --- Variables ---
APP_DIR="$HOME/lightberry-os1"
APP_DIR1="$HOME/lightberry-os1/modules"
APP_DIR2="$HOME/lightberry-os1/utils"
OPENBOX_DIR="$HOME/.config/openbox"
BASH_PROFILE="$HOME/.bash_profile"

# --- Inicio ---
print_info "Iniciando la instalación de LightBerry OS..."

# Verificar que no se ejecute como root
if [ "$EUID" -eq 0 ]; then
  print_error "Este script no debe ejecutarse como root. Pedirá la contraseña de sudo cuando sea necesario."
  exit 1
fi

print_info "-> 1. Actualizando sistema e instalando dependencias..."
sudo apt-get update -qq > /dev/null
sudo apt-get install -y python3-pygame xserver-xorg xinit openbox unclutter neomutt python3-requests
print_status "Dependencias instaladas (incluyendo neomutt para correo)."

print_info "-> 2. Creando directorio de aplicación..."
mkdir -p "$APP_DIR"
print_status "Directorio de aplicación creado."

print_info "-> 3. Copiando archivos de aplicación..."
cp "$(dirname "$0")/lightberry_os.py" "$APP_DIR/"
cp "$(dirname "$0")/light_phone_kiosk.py" "$APP_DIR/"
cp "$(dirname "$0")/utils/data_manager.py" "$APP_DIR/"
cp "$(dirname "$0")/utils/hardware_manager.py" "$APP_DIR/"
cp "$(dirname "$0")/utils/notification_manager.py" "$APP_DIR/"
cp "$(dirname "$0")/modules/calculator.py" "$APP_DIR/"
cp "$(dirname "$0")/modules/calendar_module.py" "$APP_DIR/"
cp "$(dirname "$0")/modules/converter.py" "$APP_DIR/"
cp "$(dirname "$0")/modules/mail.py" "$APP_DIR/"
cp "$(dirname "$0")/modules/notes.py" "$APP_DIR/"
cp "$(dirname "$0")/modules/quit.py" "$APP_DIR/"
cp "$(dirname "$0")/modules/settings.py" "$APP_DIR/"
cp "$(dirname "$0")/modules/terminal.py" "$APP_DIR/"
cp "$(dirname "$0")/modules/system_info.py" "$APP_DIR/"
cp "$(dirname "$0")/modules/timer.py" "$APP_DIR/"
cp "$(dirname "$0")/modules/weather.py" "$APP_DIR/"
cp "$(dirname "$0")/modules/world_clock.py" "$APP_DIR/"
chmod +x "$APP_DIR"/*.py
chmod +x "$APP_DIR"/*.sh
print_status "Archivos de aplicación copiados."

print_info "-> 4. Configurando entorno gráfico..."

# Crear .xinitrc
cat > "$HOME/.xinitrc" << 'EOF'
#!/bin/sh
# Configuración básica de X
xset s off
xset -dpms
xset s noblank

# Ocultar cursor
unclutter -idle 1 -root &

# Iniciar Openbox
exec openbox-session
EOF
chmod +x "$HOME/.xinitrc"
print_status ".xinitrc configurado."

# Crear directorio de Openbox
mkdir -p "$OPENBOX_DIR"
print_status "Directorio de Openbox creado."

# Crear autostart de Openbox
cat > "$OPENBOX_DIR/autostart" << EOF
#!/bin/bash
# Esperar un momento para que X se estabilice
sleep 2

# Cambiar al directorio de la aplicación y ejecutar
cd "$APP_DIR"
python3 lightberry_os.py > app.log 2>&1 &
EOF
chmod +x "$OPENBOX_DIR/autostart"
print_status "Autostart de Openbox configurado."

print_info "-> 5. Configurando inicio automático..."

# Crear o modificar .bash_profile
touch "$BASH_PROFILE"

# Limpiar entradas previas
sed -i '/# LightBerry OS/d' "$BASH_PROFILE"
sed -i '/startx/d' "$BASH_PROFILE"

# Añadir inicio automático
cat >> "$BASH_PROFILE" << 'EOF'

# LightBerry OS - Inicio automático
if [ -z "$DISPLAY" ] && [ "$(tty)" = "/dev/tty1" ]; then
    startx
fi
EOF
print_status "Inicio automático configurado."

print_info "-> 6. Creando script de desinstalación..."
cat > "$APP_DIR/uninstall.sh" << 'EOF'
#!/bin/bash
echo "Desinstalando LightBerry OS..."
# Limpiar .bash_profile
sed -i '/# LightBerry OS/d' "$HOME/.bash_profile"
sed -i '/startx/d' "$HOME/.bash_profile"
# Eliminar archivos
rm -rf "$HOME/.config/openbox"
rm -rf "$HOME/lightberry-os"
rm -f "$HOME/.xinitrc"
echo "Desinstalación completa. Reinicia el sistema."
EOF
chmod +x "$APP_DIR/uninstall.sh"
print_status "Script de desinstalación creado."

print_info "-> 7. Configurando permisos adicionales..."
# Añadir usuario a grupos necesarios
sudo usermod -a -G video,audio,input,dialout "$USER"
print_status "Permisos adicionales configurados."

echo ""
print_status "--- INSTALACIÓN COMPLETADA ---"
print_warning "Por favor, reinicia el sistema para que los cambios surtan efecto."
echo "Ejecuta: sudo reboot"
echo "Para desinstalar: $APP_DIR/uninstall.sh"
echo ""
