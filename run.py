# starts the program

from dbot.app import example
from app import MainApp

#print(example())
#link is a twitch Clip as a placeholder for now
link = 'https://www.twitch.tv/lucypyre/clip/BigAgitatedRadishRickroll-ZGx1a1Y5-oXkypwj'
print(MainApp.GrabInfo(link))