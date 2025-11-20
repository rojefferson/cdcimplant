#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para executar todos os extratores em sequência.

CONFIGURAÇÃO DE AUTOMAÇÃO NO LINUX (CRON):

1. Abra o terminal e digite: crontab -e
2. Adicione uma linha para agendar a execução. 
   Exemplo para rodar todo dia às 03:00 da manhã:

   0 3 * * * /usr/bin/python3 /caminho/para/seu/projeto/run_extractors.py >> /caminho/para/seu/projeto/cron_log.txt 2>&1

   Onde:
   - /usr/bin/python3: Caminho para o executável do Python (verifique com `which python3`)
   - /caminho/para/seu/projeto/: Caminho absoluto onde este arquivo está salvo
   - >> cron_log.txt: Salva a saída (logs) em um arquivo de texto para conferência
   - 2>&1: Redireciona erros para o mesmo arquivo de log

3. Salve e feche o editor.

DICA: Certifique-se de que o arquivo run_extractors.py tem permissão de execução:
      chmod +x /caminho/para/seu/projeto/run_extractors.py
"""

import subprocess
import sys
import os
import time

# Lista de scripts na ordem de execução
SCRIPTS = [
    "1_armazem_v2.py",
    "2_Extrator_grupo_v2.py",
    "3_extratorUnidademedida.py",
    "4_Extrator_produtos_v2.py",
    "5_extrator_requisicoes_v2.py",
]

def run_script(script_name):
    """Executa um script Python individualmente."""
    print(f"--- Iniciando {script_name} ---")
    start_time = time.time()
    
    try:
        # Executa o script usando o mesmo interpretador Python atual
        result = subprocess.run(
            [sys.executable, script_name],
            check=True,
            capture_output=False, # Deixar a saída ir para o stdout/stderr padrão
            text=True
        )
        elapsed = time.time() - start_time
        print(f"--- {script_name} concluído com sucesso em {elapsed:.2f} segundos ---\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"!!! ERRO ao executar {script_name} !!!")
        print(f"Código de saída: {e.returncode}")
        return False
    except Exception as e:
        print(f"!!! ERRO inesperado ao executar {script_name}: {e}")
        return False

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir) # Garante que estamos no diretório correto
    
    print(f"Iniciando execução sequencial de {len(SCRIPTS)} extratores...")
    print(f"Diretório de trabalho: {base_dir}\n")

    for script in SCRIPTS:
        if os.path.exists(script):
            success = run_script(script)
            if not success:
                print("Interrompendo a sequência devido a erro no script anterior.")
                sys.exit(1)
        else:
            print(f"!!! ARQUIVO NÃO ENCONTRADO: {script} !!!")
            print("Verifique se o arquivo existe no diretório.")
            sys.exit(1)

    print("Todos os extratores foram executados com sucesso!")

if __name__ == "__main__":
    main()
