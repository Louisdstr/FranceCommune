def open_request_window():
    request_window = tk.Toplevel(root)
    request_window.title("Éditeur de Requête") 
    request_window.geometry("400x400")
    
    label = tk.Label(request_window, text="Sélectionnez le dialecte SQL :")
    label.pack(pady=5)

    dialect_combobox = ttk.Combobox(request_window, textvariable=dialect_var, state="readonly")
    dialect_combobox['values'] = ("MySQL", "SQLite", "PL/SQL", "Autre")
    dialect_combobox.current(0)  
    dialect_combobox.pack(pady=5)

    label = tk.Label(request_window, text="Sélectionnez les champs souhaités :")
    label.pack(pady=5)

    checkbutton_vars = {}
    data = json.loads(response_json)
    field_names = list(data.keys())
    
    for field in field_names:
        var = tk.BooleanVar()
        checkbutton = tk.Checkbutton(request_window, text=field, variable=var)
        checkbutton.pack(anchor="w", padx=10)
        checkbutton_vars[field] = var

    id_var = tk.BooleanVar()
    id_checkbutton = tk.Checkbutton(request_window, text="Inclure ID", variable=id_var)
    id_checkbutton.pack(pady=5)

    label = tk.Label(request_window, text="A partir de quel nombre (si ID inclus) :")
    label.pack(pady=5)

    id_spinbox = tk.Spinbox(request_window, from_=1)
    id_spinbox.pack(pady=5)

    def create_request():
        selected_dialect = dialect_var.get()
        selected_fields = {field: value.get() for field, value in checkbutton_vars.items() if value.get()}
        
        if not selected_fields and not id_var.get():
            messagebox.showwarning("Erreur", "Veuillez sélectionner au moins un champ.")
            return
        
        table_name = "commune"  
        columns = []
        values = []

        if id_var.get():
            id_start = int(id_spinbox.get())
            columns.append("ID")
            values.append(f"{id_start}")

        columns += selected_fields.keys()
        values += [f"'{data[field]}'" for field in selected_fields.keys()]

        columns_str = ", ".join(columns)
        values_str = ", ".join(values)

        if selected_dialect == "MySQL" or selected_dialect == "SQLite":
            query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({values_str});"
        elif selected_dialect == "PL/SQL":
            query = f"BEGIN INSERT INTO {table_name} ({columns_str}) VALUES ({values_str}); END;"
        else:
            query = f"-- SQL pour un dialecte personnalisé --\nINSERT INTO {table_name} ({columns_str}) VALUES ({values_str});"

        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, query)

    generate_button = tk.Button(request_window, text="Générer", command=create_request)
    generate_button.pack(pady=5)

    output_text = tk.Text(request_window, height=10, width=50)
    output_text.pack(pady=10, padx=5, fill="x")

    copy_button = tk.Button(request_window, text="Copier", command=lambda: copy_to_clipboard(output_text))
    copy_button.pack(pady=5)

    root.wait_window(request_window)


import tkinter as tk
from tkinter import messagebox, simpledialog
import requests

def get_info_town(entry):
    global output_text, copy_button

    nom_commune = entry.get()
    if not nom_commune:
        messagebox.showwarning("Erreur", "Veuillez entrer un nom de commune.")
        return

    # URL de l'API avec les champs requis
    url = f"https://geo.api.gouv.fr/communes?nom={nom_commune}&fields=departement,codesPostaux,population,siren,codeEpci"
    response = requests.get(url)

    if response.status_code == 200:
        communes = response.json()
        if not communes:
            messagebox.showinfo("Information", "Aucune commune trouvée pour ce nom.")
            return

        # Si plus d'une commune est trouvée, on affiche une boîte de dialogue pour choisir
        if len(communes) > 1:
            commune_names = [commune['nom'] for commune in communes]
            selected_commune = simpledialog.askstring(
                "Sélectionnez une commune", 
                f"Plusieurs communes ont été trouvées pour '{nom_commune}'.\nVeuillez entrer le nom exact de la commune parmi ces choix :\n{', '.join(commune_names)}"
            )

            # Si l'utilisateur annule ou n'entre rien, on arrête la fonction
            if not selected_commune:
                messagebox.showinfo("Information", "Aucune commune sélectionnée.")
                return

            # Filtrer la commune sélectionnée
            communes = [commune for commune in communes if commune['nom'].lower() == selected_commune.lower()]
            if not communes:
                messagebox.showerror("Erreur", f"Aucune commune trouvée correspondant à '{selected_commune}'.")
                return

        # Une fois la commune sélectionnée, on extrait les informations
        commune = communes[0]
        nom_commune = commune['nom']
        code_postal = commune['codesPostaux'][0] if commune['codesPostaux'] else 'Non disponible'
        population = commune.get('population', 'Non disponible')
        siren = commune.get('siren', 'Non disponible')
        code_epci = commune.get('codeEpci', 'Non disponible')
        nom_departement = commune['departement']['nom']
        code_departement = commune['departement']['code']

        # Affichage des informations dans la zone de texte
        text = (f"Nom de la commune : {nom_commune}\n"
                f"Code Postal : {code_postal}\n"
                f"Population : {population}\n"
                f"SIREN : {siren}\n"
                f"Code EPCI : {code_epci}\n"
                f"Département : {nom_departement} ({code_departement})\n")

        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, text)
        copy_button.config(state="normal")

    else:
        messagebox.showerror("Erreur", f"Erreur lors de la récupération des données : {response.status_code}")


