# cmgraff, scheers cmput275 LBL B2, LBL EB1
'''
Wordless
================

A word search game created with kivy.

TODO: add game description here, including specifics of assignment 
    (e.g. where to look for interesting algorithms)
'''

import kivy
kivy.require('1.9.0')

from kivy.app import App
from board import Board


        
class Wordless(App):
    """Base kivy application for game.
    
    """
    def build(self):                    
        layout = Board()
        counter = Game_Timer()
        Clock.schedule_interval(counter.update, 1.0)
        return layout

    
if __name__ == '__main__':
    
    Wordless().run()
