import os

IGNORE_DIRS = {"venv", "__pycache__", ".git", "node_modules", "x64", "dependencies", ".vs", "Resources", "imgui"}
# ========== CONFIGURAÇÕES ==========
VALID_EXTENSIONS = {".cpp", ".h", ".hpp", ".java", ".py", ".yml"}
OUTPUT_FILE = "project.txt"
# ===================================

ROOT_PATH = os.getcwd()
OUTPUT_PATH = os.path.join(ROOT_PATH, OUTPUT_FILE)
# Obtém o caminho absoluto deste script para evitar auto-inclusão
CURRENT_SCRIPT_PATH = os.path.abspath(__file__)

def should_ignore_dir(dir_name):
    return dir_name in IGNORE_DIRS

def main():
    try:
        with open(OUTPUT_PATH, "w", encoding="utf-8", errors="ignore") as out:
            for root, dirs, files in os.walk(ROOT_PATH):
                
                # Modifica a lista 'dirs' in-place para impedir que o os.walk entre em pastas ignoradas
                dirs[:] = [d for d in dirs if not should_ignore_dir(d)]

                for file in files:
                    file_path = os.path.join(root, file)
                    abs_file_path = os.path.abspath(file_path)

                    # 1. Ignorar o arquivo de saída (project.txt)
                    if file == OUTPUT_FILE:
                        continue

                    # 2. Ignorar este script (Auto-ignorar)
                    if abs_file_path == CURRENT_SCRIPT_PATH:
                        continue

                    # 3. Checar extensão permitida
                    ext = os.path.splitext(file)[1].lower()
                    if ext not in VALID_EXTENSIONS:
                        continue

                    # Ler arquivo
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                        
                        out.write(f"\n=== {file_path} ===\n")
                        out.write(content)
                        out.write("\n")
                    except Exception as e:
                        print(f"Erro ao ler {file_path}: {e}")
                        out.write(f"\n[ERRO AO LER ARQUIVO: {file_path} - {e}]\n")

        print(f"✔ Arquivo gerado com sucesso: {OUTPUT_PATH}")

    except IOError as e:
        print(f"Erro fatal ao criar arquivo de saída: {e}")

if __name__ == "__main__":
    main()