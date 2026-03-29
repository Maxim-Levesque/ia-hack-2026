"""
evaluate_model.py — Évaluation du modèle sur le jeu de test
===========================================================
Charge le modèle entraîné et affiche la matrice de confusion.

Usage: python evaluate_model.py
"""

import os
import joblib
import numpy as np
from pathlib import Path
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import plotly.figure_factory as ff

# Importer les configurations et fonctions de train_model
from train_model import (
    DATA_SOURCES,
    MODEL_DIR,
    SPECIES_NAMES,
    build_dataset,
)

def evaluate():
    print("\n" + "=" * 60)
    print("  EVALUATION DU MODELE SUR LE JEU DE TEST")
    print("=" * 60)

    # 1. Vérifier si le modèle existe
    clf_path = MODEL_DIR / "classifier.pkl"
    scaler_path = MODEL_DIR / "scaler.pkl"
    meta_path = MODEL_DIR / "metadata.pkl"

    if not all([p.exists() for p in [clf_path, scaler_path, meta_path]]):
        print(f"Erreur: Modele non trouve dans {MODEL_DIR}.")
        print("Veuillez d'abord lancer: python train_model.py")
        return

    # 2. Charger le modèle et le scaler
    print("Chargement du modele...")
    clf = joblib.load(clf_path)
    scaler = joblib.load(scaler_path)
    metadata = joblib.load(meta_path)
    
    # 3. Charger le dataset de test
    X_test, y_test = build_dataset(DATA_SOURCES, subset="test")
    print(f"\nJeu de test charge (Shape: {X_test.shape})")

    # 4. Normalisation et Prédiction
    X_test_scaled = scaler.transform(X_test)
    y_pred = clf.predict(X_test_scaled)
    
    # 5. Métriques
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\nAccuracy globale : {accuracy:.2%}")
    print("\nRapport de classification :")
    print(
        classification_report(
            y_test,
            y_pred,
            target_names=SPECIES_NAMES,
            zero_division=0,
        )
    )

    # 6. Matrice de confusion (Console)
    cm = confusion_matrix(y_test, y_pred)
    print("\nMatrice de confusion (Console) :")
    
    # Header formaté
    header = " " * 20 + " ".join([f"{n[:12]:>12}" for n in SPECIES_NAMES])
    print(header)
    for i, row in enumerate(cm):
        row_str = " ".join([f"{v:12d}" for v in row])
        print(f"{SPECIES_NAMES[i][:20]:20s}{row_str}")

    # 7. Matrice de confusion (Optionnel: Plotly figure si nécessaire, mais ici on reste en console comme demandé)
    # On pourrait générer une image si on voulait, mais le user a dit "dans le code" (console).
    
    print("\n" + "=" * 60)
    print("  Fin de l'évaluation")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    evaluate()
