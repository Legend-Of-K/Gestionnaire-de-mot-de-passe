import os
import random
import string
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from cryptography.fernet import Fernet
import platform
import subprocess

# Fichiers cachés pour stocker les mots de passe et la clé de déverrouillage
PASSWORD_FILE = ".passwords.txt"
LOCK_FILE = ".lock.txt"
KEY_FILE = ".secret.key"

# Vérifier si un fichier existe
def file_exists(file_path):
    return os.path.exists(file_path)

# Marquer un fichier comme caché sous Windows
def hide_file_windows(file_path):
    if platform.system() == 'Windows':
        try:
            subprocess.check_call(['attrib', '+h', file_path])
        except subprocess.CalledProcessError:
            messagebox.showerror("Erreur", f"Impossible de cacher le fichier {file_path}")

# Générer et sauvegarder la clé de chiffrement (fait une seule fois)
def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as key_file:
        key_file.write(key)
    hide_file_windows(KEY_FILE)

# Charger la clé de chiffrement
def load_key():
    with open(KEY_FILE, "rb") as key_file:
        return key_file.read()

# Chiffrer un mot de passe
def encrypt_password(password, key):
    fernet = Fernet(key)
    return fernet.encrypt(password.encode()).decode()

# Déchiffrer un mot de passe
def decrypt_password(encrypted_password, key):
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_password.encode()).decode()

# Sauvegarder le code de déverrouillage
def save_unlock_code(code):
    with open(LOCK_FILE, "w") as lock_file:
        lock_file.write(code)
    hide_file_windows(LOCK_FILE)

# Vérifier le code de déverrouillage
def verify_unlock_code(code):
    if not file_exists(LOCK_FILE):
        return False
    with open(LOCK_FILE, "r") as lock_file:
        stored_code = lock_file.read().strip()
    return code == stored_code

# Générer un mot de passe aléatoire
def generate_password(length, use_special_chars):
    if length < 8:
        raise ValueError("Le mot de passe doit comporter au moins 8 caractères.")
    chars = string.ascii_letters + string.digits
    if use_special_chars:
        chars += string.punctuation
    return ''.join(random.choice(chars) for _ in range(length))

# Stocker le mot de passe dans un fichier après chiffrement
def store_password(site, password):
    key = load_key()
    encrypted_password = encrypt_password(password, key)
    with open(PASSWORD_FILE, "a") as f:
        f.write(f"{site}: {encrypted_password}\n")
    hide_file_windows(PASSWORD_FILE)

# Récupérer et déchiffrer le mot de passe pour un site donné
def retrieve_password(site):
    key = load_key()
    if not file_exists(PASSWORD_FILE):
        return None
    with open(PASSWORD_FILE, "r") as f:
        lines = f.readlines()
        for line in lines:
            stored_site, stored_password = line.strip().split(": ")
            if stored_site == site:
                return decrypt_password(stored_password, key)
    return None

# Créer l'interface utilisateur
class PasswordManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Manager")

        # Vérification de la première utilisation et génération de la clé
        if not file_exists(KEY_FILE):
            self.first_time_setup()

        self.unlock_code = None
        self.unlock_dialog()

        # Interface de génération de mot de passe
        self.label_site = tk.Label(root, text="Site:")
        self.label_site.grid(row=0, column=0)
        self.entry_site = tk.Entry(root)
        self.entry_site.grid(row=0, column=1)

        self.label_length = tk.Label(root, text="Taille du mot de passe (min 8):")
        self.label_length.grid(row=1, column=0)
        self.entry_length = tk.Entry(root)
        self.entry_length.grid(row=1, column=1)

        self.use_special_chars = tk.BooleanVar()
        self.check_special_chars = tk.Checkbutton(root, text="Utiliser des caractères spéciaux", variable=self.use_special_chars)
        self.check_special_chars.grid(row=2, columnspan=2)

        self.button_generate = tk.Button(root, text="Générer et stocker", command=self.generate_and_store_password)
        self.button_generate.grid(row=3, columnspan=2)

        self.button_retrieve = tk.Button(root, text="Consulter mot de passe", command=self.retrieve_password_dialog)
        self.button_retrieve.grid(row=4, columnspan=2)

    def first_time_setup(self):
        # Demande du code de déverrouillage et génération de la clé de chiffrement
        code = simpledialog.askstring("Premier lancement", "Créez un code de déverrouillage", show="*")
        if code:
            save_unlock_code(code)
            generate_key()
        else:
            messagebox.showerror("Erreur", "Le code de déverrouillage est requis.")
            self.root.quit()

    def unlock_dialog(self):
        code = simpledialog.askstring("Déverrouillage", "Entrez votre code de déverrouillage", show="*")
        if not verify_unlock_code(code):
            messagebox.showerror("Erreur", "Code incorrect.")
            self.root.quit()
        else:
            self.unlock_code = code

    def generate_and_store_password(self):
        site = self.entry_site.get()
        try:
            length = int(self.entry_length.get())
            if length < 8:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erreur", "La taille du mot de passe doit être un nombre supérieur ou égal à 8.")
            return

        use_special_chars = self.use_special_chars.get()
        try:
            password = generate_password(length, use_special_chars)
        except ValueError as e:
            messagebox.showerror("Erreur", str(e))
            return

        store_password(site, password)
        messagebox.showinfo("Succès", f"Mot de passe pour {site} généré et stocké.")

    def retrieve_password_dialog(self):
        site = simpledialog.askstring("Consulter mot de passe", "Entrez le nom du site")
        if not site:
            messagebox.showerror("Erreur", "Site non renseigné.")
            return

        password = retrieve_password(site)
        if password:
            self.show_password(password)
        else:
            messagebox.showerror("Erreur", "Mot de passe non trouvé pour ce site.")

    def show_password(self, password):
        show_password = messagebox.askyesno("Mot de passe trouvé", "Voulez-vous afficher le mot de passe ?")
        if show_password:
            messagebox.showinfo("Mot de passe", f"Mot de passe: {password}")

# Fonction principale
if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordManagerApp(root)
    root.mainloop()
