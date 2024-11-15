import subprocess
import threading
import tkinter as tk
from tkinter import messagebox, filedialog


def run_command(command, *args, output_widget=None):
    try:
        result = subprocess.run([command, *args], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode('utf-8') + '\n'
        if result.stderr:
            output += result.stderr.decode('utf-8') + '\n'
        if output_widget:
            output_widget.insert(tk.END, output)
        else:
            print(output)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Erro", f"Erro ao executar o comando: {e}")


def select_interface():
    run_command('./wifi_script.sh', 'select_wifi_interface', output_widget=output_text)


def start_capture():
    interface = interface_entry.get()
    bssid = bssid_entry.get()
    channel = channel_entry.get()
    file_name = filedialog.asksaveasfilename(title="Salvar captura como...", defaultextension=".cap")
    if interface and bssid and channel and file_name:
        run_command('./wifi_script.sh', 'start_capture', interface, bssid, channel, file_name, output_widget=output_text)


def select_network():
    interface = interface_entry.get()
    if not interface:
        messagebox.showerror("Erro", "Selecione uma interface de rede primeiro.")
        return
    networks_file = filedialog.asksaveasfilename(title="Salvar redes como...", defaultextension=".csv")
    if networks_file:
        run_command('sudo', 'airodump-ng', '-w', networks_file, '--output-format', 'csv', interface, output_widget=output_text)
        # Aqui você pode adicionar lógica para permitir que o usuário selecione uma rede específica a partir do arquivos de redes


def list_connected_devices_realtime():
    interface = interface_entry.get()
    bssid = bssid_entry.get()
    channel = channel_entry.get()

    if not interface or not bssid or not channel:
        messagebox.showerror("Erro", "Certifique-se de que todos os campos (Interface, BSSID e Canal) estão preenchidos.")
        return

    def capture_devices():
        list_connected_devices(interface, bssid, channel)

    thread = threading.Thread(target=capture_devices)
    thread.start()

def list_connected_devices(interface, bssid, channel):
    try:
        result = subprocess.Popen(['sudo', 'airodump-ng', '-c', channel, '--bssid', bssid, interface],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        for line in iter(result.stdout.readline, b''):
            line = line.decode('utf-8')
            output_text.insert(tk.END, line)
        result.stdout.close()
        result.wait()
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Erro", f"Erro ao executar o comando: {e}")

def start_deauth():
    interface = interface_entry.get()
    target_mac = target_mac_entry.get()
    bssid = bssid_entry.get()
    if interface and target_mac and bssid:
        run_command('./wifi_script.sh', 'start_deauth', interface, target_mac, bssid, output_widget=output_text)


def stop_deauth():
    run_command('./wifi_script.sh', 'stop_deauth', output_widget=output_text)


def decrypt_handshakes():
    bssid = bssid_entry.get()
    cap_files = filedialog.askopenfilenames(title="Selecionar arquivos .cap", filetypes=[("CAP Files", "*.cap")])
    if bssid and cap_files:
        run_command('./wifi_script.sh', 'decrypt_handshakes', bssid, *cap_files, output_widget=output_text)


def cleanup_temp_files():
    file_prefix = filedialog.askstring("Prefixo do Arquivo", "Insira o prefixo do arquivo:")
    if file_prefix:
        run_command('./wifi_script.sh', 'cleanup', file_prefix, output_widget=output_text)


def clear_output():
    output_text.delete('1.0', tk.END)


# Criação da Interface Gráfica
root = tk.Tk()
root.title("CapTool")

tk.Label(root, text="Interface de Rede").grid(row=0, column=0)
interface_entry = tk.Entry(root)
interface_entry.grid(row=0, column=1)
tk.Button(root, text="Selecionar Interface", command=select_interface).grid(row=0, column=2)

tk.Label(root, text="BSSID").grid(row=1, column=0)
bssid_entry = tk.Entry(root)
bssid_entry.grid(row=1, column=1)

tk.Label(root, text="Canal").grid(row=2, column=0)
channel_entry = tk.Entry(root)
channel_entry.grid(row=2, column=1)

tk.Button(root, text="Iniciar Captura", command=start_capture).grid(row=3, column=0)
tk.Button(root, text="Listar Redes", command=select_network).grid(row=3, column=1)
tk.Button(root, text="Listar Dispositivos Conectados", command=list_connected_devices_realtime).grid(row=3, column=2)

tk.Label(root, text="MAC do Alvo").grid(row=4, column=0)
target_mac_entry = tk.Entry(root)
target_mac_entry.grid(row=4, column=1)

tk.Button(root, text="Iniciar Deauth", command=start_deauth).grid(row=5, column=0)
tk.Button(root, text="Parar Deauth", command=stop_deauth).grid(row=5, column=1)

tk.Button(root, text="Descriptografar Handshakes", command=decrypt_handshakes).grid(row=6, column=0, columnspan=2)
tk.Button(root, text="Limpar Arquivos Temporários", command=cleanup_temp_files).grid(row=7, column=0, columnspan=2)

tk.Button(root, text="Limpar Saída", command=clear_output).grid(row=8, column=0)

# Área de texto para exibir a saída dos comandos
output_text = tk.Text(root, height=15, width=80)
output_text.grid(row=9, column=0, columnspan=3, padx=10, pady=10)

# Iniciar o loop principal da interface gráfica
root.mainloop()

