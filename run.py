"""
Main entry point for the Marine Audio Classification project.
Run this script to start the application or run the evaluation.
"""
import os
import sys
import subprocess
import time

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    print("====================================================")
    print("   SYSTÈME DE CLASSIFICATION AUDIO - IA HACK 2026   ")
    print("====================================================")
    print()

def start_app():
    print("Démarrage de l'interface Streamlit...")
    try:
        # Check if streamlit is installed
        subprocess.check_call([sys.executable, "-m", "streamlit", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app.py"])
        print("\nL'interface devrait s'ouvrir dans votre navigateur sous peu.")
        print("Si ce n'est pas le cas, ouvrez : http://localhost:8501")
        print("\nAppuyez sur Entrée pour revenir au menu (l'app continuera de tourner)...")
        input()
    except subprocess.CalledProcessError:
        print("Erreur : Streamlit n'est pas installé. Veuillez exécuter 'pip install streamlit'.")
        time.sleep(3)

def run_evaluation():
    clear_screen()
    print_header()
    print("Lancement de l'évaluation du modèle sur les données de test...")
    print("-" * 52)
    try:
        subprocess.run([sys.executable, "evaluate_model.py"])
    except Exception as e:
        print(f"Erreur lors de l'évaluation : {e}")
    print("-" * 52)
    print("\nAppuyez sur Entrée pour revenir au menu...")
    input()

def run_training():
    clear_screen()
    print_header()
    print("ATTENTION : Cela va ré-entraîner le modèle complet (plusieurs minutes).")
    confirm = input("Voulez-vous continuer ? (o/n) : ")
    if confirm.lower() == 'o':
        try:
            subprocess.run([sys.executable, "train_model.py"])
        except Exception as e:
            print(f"Erreur lors de l'entraînement : {e}")
    print("\nAppuyez sur Entrée pour revenir au menu...")
    input()

def check_dependencies():
    print("Vérification des dépendances...")
    deps = ["streamlit", "librosa", "numpy", "pandas", "joblib", "sklearn", "plotly"]
    missing = []
    
    for dep in deps:
        try:
            if dep == "sklearn":
                __import__("sklearn")
            else:
                __import__(dep)
        except ImportError:
            missing.append(dep)
    
    if missing:
        print(f"Dépendances manquantes détectées : {', '.join(missing)}")
        install = input("Voulez-vous tenter de les installer avec pip ? (o/n) : ")
        if install.lower() == 'o':
            subprocess.run([sys.executable, "-m", "pip", "install"] + missing)
    else:
        print("Toutes les dépendances sont installées.")
    time.sleep(1)

def main():
    check_dependencies()
    
    while True:
        clear_screen()
        print_header()
        print("1. Lancer l'interface utilisateur (Streamlit)")
        print("2. Lancer l'évaluation complète (Rapport & Matrice)")
        print("3. Ré-entraîner le modèle (Optionnel)")
        print("4. Quitter")
        print()
        
        choice = input("Votre choix (1-4) : ")
        
        if choice == '1':
            start_app()
        elif choice == '2':
            run_evaluation()
        elif choice == '3':
            run_training()
        elif choice == '4':
            print("Au revoir !")
            break
        else:
            print("Choix invalide.")
            time.sleep(1)

if __name__ == "__main__":
    main()
