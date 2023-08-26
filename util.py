import os

def trimUrlArguments(url):
    return url.split('?')[0]

def clearConsole():
    os.system('cls' if os.name == 'nt' else 'clear')
