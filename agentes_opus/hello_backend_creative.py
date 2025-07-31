# ⚙️ PERSONA: backend_dev
import time
from persona_markers import PersonaMarker

def print_slow(text, delay=0.03):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

@PersonaMarker.wrap_function_with_persona("backend_dev", "Demonstração Backend Criativa")
def main():
    banner = [
        "  _   _      _ _         __        __         _     _ _ ",
        " | | | | ___| | | ___    \\ \\      / /__  _ __| | __| | |",
        " | |_| |/ _ \\ | |/ _ \\    \\ \\ /\\ / / _ \\| '__| |/ _` | |",
        " |  _  |  __/ | | (_) |    \\ V  V / (_) | |  | | (_| |_|",
        " |_| |_|\\___|_|_|\\___/      \\_/\\_/ \\___/|_|  |_|\\__,_(_)",
        "",
        ">>> Backend says: Hello, World! 🚀 <<<"
    ]
    for line in banner:
        print_slow(line, delay=0.01)
    print_slow("\nBem-vindo ao universo Python backend, onde a criatividade encontra a robustez!\n", delay=0.04)
    
    # ⚙️ PERSONA: backend_dev - Demonstração de funcionalidades backend
    PersonaMarker.print_persona_output(
        "backend_dev",
        "Sistema backend inicializado com sucesso!\n" +
        "✅ Servidor configurado\n" +
        "✅ Database conectada\n" +
        "✅ APIs disponíveis\n" +
        "✅ Logs habilitados",
        "Sistema Operacional"
    )

if __name__ == "__main__":
    main()
