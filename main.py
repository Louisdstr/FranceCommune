import requests
import tkinter as tk
from tkinter import messagebox

def fetch_communes():
    code_departement = entry.get()
    if not code_departement:
        messagebox.showwarning("Erreur", "Veuillez entrer un code de département.")
        return

    url = f"https://geo.api.gouv.fr/communes?codeDepartement={code_departement}&fields=codesPostaux,nom"
    response = requests.get(url)

    if response.status_code == 200:
        communes = response.json()
        values = []
        for commune in communes:
            codes_postaux = commune['codesPostaux']
            if codes_postaux:
                code_postal = codes_postaux[0]  # Prendre uniquement le premier code postal
            else:
                code_postal = 'NULL'

            nom_commune = commune['nom'].replace("'", "''")  # Échappe les apostrophes pour SQL
            values.append(f"INTO AB_COMMUNES (CPOST, COMMUNE) VALUES ('{code_postal}', '{nom_commune}')")
        
        query = "INSERT ALL\n" + "\n".join(values) + "\nSELECT * FROM dual;"
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, query)
        copy_button.config(state=tk.NORMAL)
    else:
        messagebox.showerror("Erreur", f"Erreur: {response.status_code}")

def copy_to_clipboard():
    root.clipboard_clear()
    root.clipboard_append(output_text.get("1.0", tk.END))
    messagebox.showinfo("Copié", "La requête SQL a été copiée dans le presse-papiers.")

# Interface graphique
root = tk.Tk()
root.title("Générateur de requêtes SQL pour les communes")

frame = tk.Frame(root)
frame.pack(pady=10)

label = tk.Label(frame, text="Entrez le code du département :")
label.pack(side=tk.LEFT, padx=5)

entry = tk.Entry(frame)
entry.pack(side=tk.LEFT)

fetch_button = tk.Button(frame, text="Générer la requête", command=fetch_communes)
fetch_button.pack(side=tk.LEFT, padx=5)

output_text = tk.Text(root, height=15, width=80)
output_text.pack(pady=10)

copy_button = tk.Button(root, text="Copier dans le presse-papiers", command=copy_to_clipboard, state=tk.DISABLED)
copy_button.pack()

root.mainloop()
