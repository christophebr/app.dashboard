import pickle
from pathlib import Path
import bcrypt
import streamlit_authenticator as stauth


names = ['Christophe Brichet', 'Miguel Pecqueux']
usernames = ['cbri', 'mpec']
passwords = []

# Générer les mots de passe hachés et les stocker dans un dictionnaire
hashed_passwords = {username: bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode() for username, password in zip(usernames, passwords)}

# Enregistrer les mots de passe hachés dans un fichier
file_path = Path(__file__).parent / 'hashed_pw.pkl'
with file_path.open('wb') as file:
    pickle.dump(hashed_passwords, file)


