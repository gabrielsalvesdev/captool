#!/bin/bash

# Atualiza o sistema
sudo apt-get update
sudo apt-get upgrade -y

# Instala Python3 e pip3
sudo apt-get install -y python3 python3-pip

# Instala tkinter para a interface gráfica
sudo apt-get install -y python3-tk

# Instala iw para gerenciamento de redes sem fio
sudo apt-get install -y iw

# Instala aircrack-ng para captura de pacotes Wi-Fi
sudo apt-get install -y aircrack-ng

# Instala John the Ripper para quebra de senhas
sudo apt-get install -y john

# Instala outras ferramentas úteis (opcional)
sudo apt-get install -y git vim

# Mensagem de conclusão
echo "Instalação das dependências concluída com sucesso!"
