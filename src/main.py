
import tkinter as tk
from tkinter import messagebox, filedialog
from dataclasses import dataclass
import json
import csv
import xml.etree.ElementTree as ET

@dataclass
class Person:
    name: str
    age: int
    email: str

class PersonManager:
    def __init__(self):
        self.persons = []

    def add_person(self, name, age, email):
        self.persons.append(Person(name, age, email))

    def save_to_file(self, filename, file_type):
        try:
            if file_type == "csv":
                with open(filename, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Name", "Alter", "E-Mail"])
                    for p in self.persons:
                        writer.writerow([p.name, p.age, p.email])
            elif file_type == "json":
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump([vars(p) for p in self.persons], f, indent=4, ensure_ascii=False)
            elif file_type == "xml":
                root = ET.Element("Persons")
                for p in self.persons:
                    person = ET.SubElement(root, "Person")
                    ET.SubElement(person, "Name").text = p.name
                    ET.SubElement(person, "Alter").text = str(p.age)
                    ET.SubElement(person, "Email").text = p.email
                tree = ET.ElementTree(root)
                tree.write(filename, encoding="utf-8", xml_declaration=True)
            return True
        except Exception as e:
            messagebox.showerror("Fehler", f"Speichern fehlgeschlagen: {e}")
            return False

    def load_from_file(self, filename):
        try:
            if filename.endswith(".csv"):
                with open(filename, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    self.persons = [Person(r["Name"], int(r["Alter"]), r["E-Mail"]) for r in reader]
            elif filename.endswith(".json"):
                with open(filename, "r", encoding="utf-8") as f:
                    self.persons = [Person(p["name"], p["age"], p["email"]) for p in json.load(f)]
            elif filename.endswith(".xml"):
                tree = ET.parse(filename)
                self.persons = []
                for p in tree.findall(".//Person"):
                    self.persons.append(Person(
                        p.find("Name").text,
                        int(p.find("Alter").text),
                        p.find("Email").text
                    ))
            return True
        except Exception as e:
            messagebox.showerror("Fehler", f"Laden fehlgeschlagen: {e}")
            return False

    def show_persons(self):
        return "\n".join(
            f"Name: {p.name}, Alter: {p.age}, E-Mail: {p.email}"
            for p in self.persons
        ) if self.persons else "Keine Personen vorhanden."

class PersonGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Person Manager")
        self.root.geometry("800x500")
        self.manager = PersonManager()

        # Eingabefelder
        for i, (text, var) in enumerate([("Name:", "name_entry"), ("Alter:", "age_entry"), ("E-Mail:", "email_entry")]):
            tk.Label(root, text=text).grid(row=i, column=0, padx=10, pady=5, sticky="e")
            setattr(self, var, tk.Entry(root, width=30))
            getattr(self, var).grid(row=i, column=1, padx=10, pady=5)

        # Buttons
        for i, (text, cmd) in enumerate([("Hinzufügen", self.add_person), ("Anzeigen", self.show_persons)]):
            tk.Button(root, text=text, command=cmd, width=10).grid(row=3, column=i, pady=10, padx=5)

        # Menü
        menubar = tk.Menu(root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Öffnen", command=self.load_file)
        file_menu.add_command(label="Neu", command=self.clear_all)
        for fmt in [("CSV", "csv"), ("JSON", "json"), ("XML", "xml")]:
            file_menu.add_command(label=f"Speichern als {fmt[0]}", command=lambda f=fmt[1]: self.save_file(f))
        file_menu.add_separator()
        file_menu.add_command(label="Beenden", command=root.quit)
        menubar.add_cascade(label="Datei", menu=file_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Über", command=lambda: messagebox.showinfo("Über", "Person Manager v1.0"))
        menubar.add_cascade(label="Hilfe", menu=help_menu)

        root.config(menu=menubar)

        # Statuslabel
        self.status_label = tk.Label(root, text="Bereit", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.grid(row=4, column=0, columnspan=2, sticky="we", padx=10, pady=5)

        # Textfeld
        self.text = tk.Text(root, width=80, height=15)
        self.text.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

    def add_person(self):
        try:
            name, age, email = self.name_entry.get().strip(), self.age_entry.get().strip(), self.email_entry.get().strip()
            if not name or not email:
                raise ValueError("Name und E-Mail dürfen nicht leer sein!")
            if not age.isdigit() or int(age) <= 0:
                raise ValueError("Alter muss eine positive ganze Zahl sein!")
            if "@" not in email or "." not in email:
                raise ValueError("Ungültige E-Mail-Adresse!")
            self.manager.add_person(name, int(age), email)
            self.status_label.config(text="Person hinzugefügt!")
            self.clear_entries()
        except ValueError as e:
            messagebox.showerror("Fehler", str(e))

    def show_persons(self):
        self.text.delete(1.0, tk.END)
        self.text.insert(tk.END, self.manager.show_persons())

    def clear_entries(self):
        self.name_entry.delete(0, tk.END)
        self.age_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)

    def clear_all(self):
        self.manager.persons = []
        self.text.delete(1.0, tk.END)
        self.status_label.config(text="Alle Daten gelöscht!")

    def save_file(self, file_type):
        filename = filedialog.asksaveasfilename(
            defaultextension=f".{file_type}",
            filetypes=[("CSV", "*.csv"), ("JSON", "*.json"), ("XML", "*.xml")]
        )
        if filename and self.manager.save_to_file(filename, file_type):
            self.status_label.config(text=f"Gespeichert als {file_type.upper()}")

    def load_file(self):
        filename = filedialog.askopenfilename(
            filetypes=[("CSV", "*.csv"), ("JSON", "*.json"), ("XML", "*.xml")]
        )
        if filename and self.manager.load_from_file(filename):
            self.status_label.config(text=f"Geladen: {filename.split('/')[-1]}")
            self.show_persons()

if __name__ == "__main__":
    root = tk.Tk()
    app = PersonGUI(root)
    root.mainloop()
