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
