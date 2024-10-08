from setuptools import setup, find_packages

setup(
    name="PasswordManagerApp",
    version="1.0",
    description="Application de gestion de mots de passe avec interface utilisateur",
    author="Legend_Of_K",
    packages=find_packages(),
    install_requires=[
        "cryptography==3.4.7",
        # Ajouter d'autres dépendances ici si nécessaire
    ],
    entry_points={
        "console_scripts": [
            "passwordmanager = pwg:main",  # Point d'entrée pour démarrer l'application
        ]
    },
    include_package_data=True,
)
