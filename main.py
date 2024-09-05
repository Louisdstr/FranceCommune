import requests
import tkinter as tk
from tkinter import ttk, messagebox

output_text = None
copy_button = None

def department_window():
    global output_text, copy_button
    
    for widget in frame2.winfo_children():
        widget.destroy()

    frame_department = tk.Frame(frame2)
    frame_department.pack(fill="both")

    label = tk.Label(frame_department, text="Entrez le code du département :")
    label.pack(side="left")

    entry = tk.Entry(frame_department)
    entry.pack(side="left")

    fetch_button = tk.Button(frame_department, text="Valider", command=lambda: get_info_department(entry))
    fetch_button.pack(side="left")

    output_text = tk.Text(frame_department, height=15, width=80)
    output_text.pack(fill="x", padx=5)

    request_button = tk.Button(frame_department, text="Générer une requete", command=copy_to_clipboard)
    request_button.pack(side="left")

def get_info_department(entry):
    global output_text, copy_button
    
    code_departement = entry.get()
    if not code_departement:
        messagebox.showwarning("Erreur", "Veuillez entrer un code de département.")
        return

    url = f"https://geo.api.gouv.fr/communes?codeDepartement={code_departement}&fields=codesPostaux,nom"
    response = requests.get(url)

    if response.status_code == 200:
        communes = response.json()
        if not communes:
            messagebox.showinfo("Information", "Aucune commune trouvée pour ce département.")
            return
        
        text = f"Ce département possède {len(communes)} communes\n"
        values = []
        for commune in communes:
            codes_postaux = commune.get('codesPostaux', [])
            code_postal = codes_postaux[0] if codes_postaux else 'NULL'
            nom_commune = commune['nom'].replace("'", "''")
            values.append(f"Code Postal: {code_postal}, Nom: {nom_commune}")
        
        text += "\n".join(values)
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, text)
        copy_button.config(state="normal")
    else:
        messagebox.showerror("Erreur", f"Erreur: {response.status_code}")

def town_window():
    global output_text, copy_button
    
    for widget in frame2.winfo_children():
        widget.destroy()

    frame_town = tk.Frame(frame2)
    frame_town.pack(fill="both")

    label = tk.Label(frame_town, text="Entrez le nom d'une commune :")
    label.pack(side="left")

    entry = tk.Entry(frame_town)
    entry.pack(side="left")

    fetch_button = tk.Button(frame_town, text="Valider", command=lambda: get_info_town(entry))
    fetch_button.pack(side="left")

    output_text = tk.Text(frame_town, height=15, width=80)
    output_text.pack(fill="x", padx=5)

    copy_button = tk.Button(frame_town, text="Copier", state="disabled", command=copy_to_clipboard)
    copy_button.pack(side="left")

    request_button = tk.Button(frame_town, text="Générer une requete", command=copy_to_clipboard)
    request_button.pack(side="left")

def get_info_town(entry):
    global output_text, copy_button

    nom_commune = entry.get()
    if not nom_commune:
        messagebox.showwarning("Erreur", "Veuillez entrer un nom de commune.")
        return
    
    url = f"https://geo.api.gouv.fr/communes?nom={nom_commune}&fields=departement,codesPostaux,population,siren,codeEpci"
    response = requests.get(url)

    if response.status_code == 200:
        communes = response.json()
        if not communes:
            messagebox.showinfo("Information", "Aucune commune trouvée pour ce nom.")
            return
        
        if len(communes) > 1:
            array_town = [commune['nom'] for commune in communes]
            show_disclaimer_town(array_town)

        values = []
        for commune in communes:
            nom_commune = commune['nom']
            code_postal = commune['codesPostaux'][0] if commune['codesPostaux'] else 'Non disponible'
            population = commune.get('population', 'Non disponible')
            siren = commune.get('siren', 'Non disponible')
            code_epci = commune.get('codeEpci', 'Non disponible')
            nom_departement = commune['departement']['nom']
            code_departement = commune['departement']['code']

            values.append(f"Nom de la commune : {nom_commune}\n"
                          f"Code Postal : {code_postal}\n"
                          f"Population : {population}\n"
                          f"SIREN : {siren}\n"
                          f"Code EPCI : {code_epci}\n"
                          f"Département : {nom_departement} ({code_departement})\n")

        text = "Informations sur la commune :\n\n"
        text += "\n".join(values)

        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, text)
        copy_button.config(state="normal")
    else:
        messagebox.showerror("Erreur", f"Erreur lors de la récupération des données : {response.status_code}")

def copy_to_clipboard():
    global output_text
    root.clipboard_clear()
    root.clipboard_append(output_text.get("1.0", tk.END))
    messagebox.showinfo("Information", "Texte copié dans le presse-papiers.")

def show_disclaimer():
    disclaimer_window = tk.Toplevel(root)
    disclaimer_window.title("Information")
    disclaimer_window.geometry("400x200")
    
    label = tk.Label(disclaimer_window, text="Veuillez lire ce message avant d'utiliser l'application.", wraplength=380)
    label.pack(pady=10)

    disclaimer_text = """\
Cette application récupère ses données grâce à l'API officielle du gouvernement français, 
qui regroupe les communes de France ainsi que leurs informations associées. 
Si certaines informations vous semblent incorrectes, nous vous invitons à les signaler directement sur le site officiel.
https://geo.api.gouv.fr/decoupage-administratif
"""
    text = tk.Label(disclaimer_window, text=disclaimer_text, wraplength=380, justify=tk.LEFT)
    text.pack(pady=10)

    agree_button = tk.Button(disclaimer_window, text="Ok", command=disclaimer_window.destroy)
    agree_button.pack(pady=20)

    root.wait_window(disclaimer_window)

def show_disclaimer_town(array_town):
    disclaimer_window = tk.Toplevel(root)
    disclaimer_window.title("Information") 
    disclaimer_window.geometry("400x200")
    
    label = tk.Label(disclaimer_window, text="Choisir la commune.", wraplength=380)
    label.pack(pady=10)

    disclaimer_text = """\
Plusieurs communes possèdent le même nom ou sont composées de caractères identiques. Veuillez choisir la commune souhaitée.
"""
    text = tk.Label(disclaimer_window, text=disclaimer_text, wraplength=380, justify=tk.LEFT)
    text.pack(pady=10)

    liste = tk.Listbox(disclaimer_window)
    for i, commune in enumerate(array_town, start=1):
        liste.insert(i, commune)

    liste.pack(pady=5)

    agree_button = tk.Button(disclaimer_window, text="Ok", command=disclaimer_window.destroy)
    agree_button.pack(pady=20)

    root.wait_window(disclaimer_window)

def open_request_window(communes):
    request_window = tk.Toplevel(root)
    request_window.title("Editeur Requete") 
    request_window.geometry("400x200")
    
    label = tk.Label(request_window, text="Sélectionnez le dialecte SQL :", wraplength=380)
    label.pack(side="left")

    dialect_combobox = ttk.Combobox(request_window, textvariable=dialect_var, state="readonly")
    dialect_combobox['values'] = ("MySQL", "SQLite", "PL/SQL", "Autre")
    dialect_combobox.current(0) 
    dialect_combobox.pack(side="left")

    fetch_button = tk.Button(request_window, text="Generer", command=lambda: get_info_department(communes))
    fetch_button.pack(side="left")
    
    output_text = tk.Text(request_window, height=15, width=80)
    output_text.pack(fill="x", padx=5)

    request_button = tk.Button(request_window, text="copier", command=copy_to_clipboard)
    request_button.pack(side="bottom")

    agree_button = tk.Button(request_window, text="Ok", command=request_window.destroy)
    agree_button.pack(pady=20)

    root.wait_window(request_window)


root = tk.Tk()
root.title("Commune de France")
root.minsize(500, 500)

frame1 = tk.Frame(root)
frame1.config(width=200, height=300)
frame1.pack(side="left", expand=True, fill="both")

frame2 = tk.Frame(root)
frame2.config(width=300, height=300)
frame2.pack(side="right", expand=True, fill="both")

button1 = tk.Button(frame1, text="Info Département", command=department_window)
button1.pack(fill="X", padx=10)

button2 = tk.Button(frame1, text="Info Commune", command=town_window)
button2.pack(fill="X", padx=10)

button_quit = tk.Button(frame1, text="Quitter", command=root.quit)
button_quit.pack(fill="X", padx=10, side="bottom")

show_disclaimer()

root.mainloop()
