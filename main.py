# cmgraff, scheers cmput275 LBL B2, LBL EB1
'''
Wordless
================
A word search game created with kivy.Wordless: a fast-paced word game
Authors: Craig Graff, Falon Scheers Cmput275 LBL B2, LBL EB1

Required software/environment: Kivy 1.9.0

To run the game click on the Wordless.py file and 'open with' kivy-3.4.bat
Alternately, open kivy-3.4.bat and navigate to game folder, then run:
	python3 Wordless.py
    
'''

import kivy
kivy.require('1.9.0')

from kivy.app import App
from board import Board, MenuScreen
from kivy.uix.screenmanager import ScreenManager, Screen


        
class Wordless(App):
    """Base kivy application for game.
    
    """
    def build(self):        
        # add screen manager and primary screens      
        sm = ScreenManager()
        layout = Board(name='game')
        menu = MenuScreen(name='menu')
        sm.add_widget(layout)
        sm.add_widget(menu)
        return sm

    
if __name__ == '__main__':
    
    Wordless().run()
