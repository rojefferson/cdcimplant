#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para executar todos os extratores em sequência.

Exemplos de uso:

    python run_extractors.py dev
    python run_extractors.py hml
    python run_extractors.py prod

No CRON, algo como:

    */30 * * * * /usr/bin/python3 /caminho/para/seu/projeto/run_extractors.py prod >> /caminho/para/seu/projeto/cron_log.txt 2>&1
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

def run_script(script_name, env_name):
    """Executa um script Python individualmente, passando o env como parâmetro."""
    print(f"--- Iniciando {script_name} (env={env_name}) ---")
    start_time = time.time()
    
    try:
        # Chama: python script_name <env>
        result = subprocess.run(
            [sys.executable, script_name, env_name],
            check=True,
            capture_output=False,  # deixa a saída ir para stdout/stderr padrão
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
    # Lê o env da linha de comando: python run_extractors.py dev
    if len(sys.argv) > 1:
        env_name = sys.argv[1]
    else:
        # Default se não passar nada
        env_name = "dev"

    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)  # Garante que estamos no diretório correto
    
    print(f"Iniciando execução sequencial de {len(SCRIPTS)} extratores...")
    print(f"Diretório de trabalho: {base_dir}")
    print(f"Ambiente (env): {env_name}\n")

    for script in SCRIPTS:
        if os.path.exists(script):
            success = run_script(script, env_name)
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
