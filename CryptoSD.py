from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
import codecs
import os
import sys


def my_xor(x, y):
    """
    Xor x et y qui sont deux integer
    """
    return (x | y) & (~x | ~y)


def generate_fernet_key_file(path_cle, nom_cle, path_sd):
    """
    Créer les fichiers contenant les bouts de clé et le fichier contenant la vrai clé hashé (SHA256)

    :param path_cle: Chemin de la clé sur le pc
    :param nom_cle:  Nom du fichier de la clé avec son extension
    :param path_sd:  Chemin de la clé sur la carte SD
    :return:
    """

    try:
        cid = str(find_cid(path_sd)).replace("\\x", "")[2:-1]
    except Exception as e:
        return

    key_pc = str(Fernet.generate_key()).replace("-", "+").replace("_", "/")[2:-1].encode()
    with open(path_cle + nom_cle, "wb")as key_file:
        key_file.write(key_pc)

    key_sd = str(Fernet.generate_key()).replace("-", "+").replace("_", "/")[2:-1].encode()
    with open(path_sd + nom_cle, "wb")as key_file:
        key_file.write(key_sd)

    master_key_hex = generate_master_key_hex(key_pc, key_sd, cid)

    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(master_key_hex.encode())

    master_digest = digest.finalize()
    with open(path_cle + "Master_" + nom_cle, "wb")as key_file:
        key_file.write(master_digest)


def generate_master_key_hex(key_pc, key_sd, cid):
    """
    Encode les bouts de clé en hexadécimal pour les xor et retourne la vraie clé en hexadécimal
    """

    key_pc_hex = codecs.encode(codecs.decode(key_pc, 'base64'), 'hex').decode()
    key_sd_hex = codecs.encode(codecs.decode(key_sd, 'base64'), 'hex').decode()

    master_key = my_xor(my_xor(int(key_pc_hex, 16), int(cid, 16)), int(key_sd_hex, 16))
    master_key_hex = str(hex(master_key))[2:]
    if len(master_key_hex) < len(key_pc_hex):
        master_key_hex = "0" + master_key_hex

    return master_key_hex


def create_master_key_hex(path_cle, nom_cle, path_sd):
    """
    Crée la clé en hexadécimal
    """

    with open(path_cle + nom_cle, "rb")as key_file:
        key_pc = key_file.read()

    with open(path_sd + nom_cle, "rb")as key_file:
        key_sd = key_file.read()

    try:
        cid = str(find_cid(path_sd)).replace("\\x", "")[2:-1]
    except Exception as e:
        raise e

    master_key_hex = generate_master_key_hex(key_pc, key_sd, cid)

    return master_key_hex


def create_master_key(path_cle, nom_cle, path_sd):
    """
    Crée la clé en base64 url_safe

    Fonction utilisé pour créer la clé fonctionnant avec les fonctions encrypt et decrypt

    :param path_cle: Chemin de la clé sur le pc
    :param nom_cle:  Nom du fichier de la clé avec son extension
    :param path_sd:  Chemin de la clé sur la carte SD
    :return: La vraie clé en base64 url_safe
    """

    master_key_hex = create_master_key_hex(path_cle, nom_cle, path_sd)
    master_key = codecs.encode(codecs.decode(master_key_hex, 'hex'), 'base64').decode()
    return master_key.replace("+", "-").replace("/", "_")[:-1].encode()


def check_keys(path_cle, nom_cle, path_sd):
    """
    Assemble les clés, ouvre le fichier SHA256 et compare les valeurs

    :param path_cle: Chemin de la clé sur le pc
    :param nom_cle:  Nom du fichier de la clé avec son extension
    :param path_sd:  Chemin de la clé sur la carte SD
    :return: True si le sha256 correspond bien à cette clé, False sinon
    """

    try:
        master_key_hex = create_master_key_hex(path_cle, nom_cle, path_sd)
    except Exception as e:
        print("Problème de CID")
        return False

    with open(path_cle + "Master_" + nom_cle, "rb")as key_file:
        master_digest = key_file.read()

    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(master_key_hex.encode())
    if digest.finalize() == master_digest:
        return True
    else:
        return False


def encode_fernet(key, message):
    """
    Chiffre un message

    :param key: Clé provenant de la fonction create_master_key
    :param message: Message à chiffrer
    :return:
    """
    fernet_key = Fernet(key)
    token = fernet_key.encrypt(message)
    return token


def decode_fernet(key, token):
    """
    Déchiffre un message

    :param key: Clé provenant de la fonction create_master_key
    :param token: Message à déchiffrer
    :return:
    """
    fernet_key = Fernet(key)
    message = fernet_key.decrypt(token)
    return message


def encrypt_file_fernet(key, path):
    """
    Chiffre un fichier

    :param key: Clé provenant de la fonction create_master_key
    :param path: Chemin du fichier à Chiffrer
    :return:
    """

    with open(path, "rb") as file_read:
        message = file_read.read()

    pass_encrypt = encode_fernet(key, message)

    with open(path, "wb") as file_write:
        file_write.write(pass_encrypt)


def decrypt_file_fernet(key, path):
    """
    Déchiffre un fichier

    :param key: Clé provenant de la fonction create_master_key
    :param path: Chemin du fichier à déchiffrer
    :return:
    """
    with open(path, "rb") as file_read:
        token = file_read.read()

    pass_decrypt = decode_fernet(key, token)

    with open(path, "wb") as file_write:
        file_write.write(pass_decrypt)


def encrypt_directory_fernet(key, path):
    """
    Chiffre complètement un dossier

    :param key: Clé provenant de la fonction create_master_key
    :param path: Chemin du dossier à Chiffrer
    :return:
    """
    for paths, dirs, files in os.walk(path):
        for filename in files:
            encrypt_file_fernet(key, paths + os.sep + filename)


def decrypt_directory_fernet(key, path):
    """
    Déchiffre complètement un dossier

    :param key: Clé provenant de la fonction create_master_key
    :param path: Chemin du dossier à déchiffrer
    :return:
    """
    for paths, dirs, files in os.walk(path):
        for filename in files:
            decrypt_file_fernet(key, paths + os.sep + filename)


def find_cid(path):
    """
    Trouve le CID de la carte SD
    """
    cid = ""

    if sys.platform == "win32":
        try:
            f = open(path[:-1], 'rb')
            cid = f.read(43)[39:]   # Volume ID dans le cas de windows
        except Exception as e:
            print(path[:-1])
            raise e
    elif sys.platform == "linux":
        try:
            f = open("/sys/block/" + str(path) + "device/cid", 'rb')
            cid = f.read()
        except Exception as e:
            return e
    return bytes(cid)





"""     EXEMPLE     """


def testcreer():
    path = "prout"
    path_cle = ""
    nom_cle = "cleSD.txt"
    if not generate_fernet_key_file(path_cle, nom_cle, "H:" + os.sep):
        print("Problème de CID, rien n'est généré")
        return

    key = create_master_key(path_cle, nom_cle, "H:\\")
    encrypt_directory_fernet(key, path)


def testdecrypt():
    path = "prout"
    path_cle = ""
    nom_cle = "cleSD.txt"
    key = create_master_key(path_cle, nom_cle, "H:\\")

    decrypt_directory_fernet(key, path)
