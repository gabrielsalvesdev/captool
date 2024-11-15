import subprocess
import unittest
from unittest.mock import patch
import logging
import os

# Configurar o logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestCaptool(unittest.TestCase):
    def test_capture_handshake(self):
        # Configurar o ambiente de teste
        capture_file = "capture.cap"
        
        logger.info(f"Iniciando o teste de captura de handshake com o arquivo de captura {capture_file}")
        
        # Simular a interação com a interface gráfica do captool
        with patch('subprocess.run') as mock_run:
            # Configurar o mock para retornar um valor específico
            mock_run.return_value = subprocess.CompletedProcess([], 0)
            
            # Executar o captool através da interface gráfica
            captool_command = "captool"
            result = subprocess.run(captool_command, shell=True, capture_output=True, text=True)
            
            logger.info(f"Comando do captool executado: {captool_command}")
            logger.info(f"Resultado da execução do comando: {result}")
            
            # Verificar se o comando foi executado corretamente
            mock_run.assert_called_once_with(captool_command, shell=True, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0)
        
        # Verificar se o arquivo de captura foi gerado
        self.assertTrue(os.path.exists(capture_file), f"O arquivo de captura {capture_file} não foi gerado.")
        
        # Verificar a integridade do arquivo de captura
        with open(capture_file, "rb") as file:
            capture_data = file.read()
            
            logger.info(f"Arquivo de captura {capture_file} lido com sucesso")
            
            # Realizar verificações específicas na captura
            self.assertIn(b"EAPOL", capture_data)  # Verificar a presença de pacotes EAPOL
            self.assertGreater(len(capture_data), 100)  # Verificar se a captura tem tamanho mínimo
            
            logger.info("Verificações de integridade do arquivo de captura concluídas com sucesso")
        
        # Executar análise adicional usando o Claude (opcional)
        claude_analysis = analyze_capture(capture_file)
        logger.info(f"Análise do Claude: {claude_analysis}")
        self.assertIn("handshake", claude_analysis)  # Verificar a análise do Claude
        
        # Limpar o arquivo de captura após o teste
        os.remove(capture_file)
        logger.info(f"Arquivo de captura {capture_file} removido após o teste")
        
        logger.info("Teste de captura de handshake concluído com sucesso")

if __name__ == '__main__':
    unittest.main()
