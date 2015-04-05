
from random import randint
from kivy.uix.button import Button
from words import Letters
from kivy.animation import Animation

_Board = None

class Tile(Button):
    """ Represents a tile in the game board.
    """    
    anims_to_complete = 0
    
    def __repr__(self):
        return self.text
    
    def __init__(self, board=None, **kwargs):
        """
        
        """
        if board != None and _Board == None:
            global _Board
            _Board = board
            
        # initialize base class
        super().__init__(**kwargs)     
        
        
        # populate board with random letters
        # TODO: consider populating board with words and partial words
        
        # set the text of this tile
        rand = randint(0, len(Letters.letters)-1)
    
        letter = Letters.letters[rand]
        self.text = letter
        self.lscore.text = str(Letters.Value[letter])
        self.font_size = 50
                
    def on_touch_down(self, touch):  
        """Base kivy method inherited from Button.
        
        This method is called on all buttons at once, so we need to 
        return True for only the currently touched button.

        Note:
          We are not currently passing this up to super(), but 
          we could consider doing so.

        Args:
          touch: A kivy motion event

        Returns:
          True if for currently touched button, False otherwise.

        """      
        touch.multitouch_sim = False
        if touch.is_touch or touch.button == 'left':
            if self.collide_point(touch.x, touch.y):
                _Board.highlight(self, touch)
                
                
                # set grab to catch release off of tiles
                touch.grab(self)
                return True
        return False
            
    def on_touch_move(self, touch):        
        """Base kivy method inherited from Button.
        
        This method is called on all buttons at once, so we need to 
        return True for only the currently touched button.

        Note:
          We are not currently passing this up to super(), but 
          we could consider doing so.

        Args:
          touch: A kivy motion event

        Returns:
          True if for currently touched button, False otherwise.

        """
        
        if touch.is_touch or touch.button == 'left':
            if self.collide_point(touch.x, touch.y):                
                _Board.highlight(self, touch)
                return True
        return False
            
    def on_touch_up(self, touch):        
        """Base kivy method inherited from Button.
        
        This method is called on all buttons at once, so we need to 
        return True for only the currently touched button.

        Note:
          We are not currently passing this up to super(), but 
          we could consider doing so.

        Args:
          touch: A kivy motion event

        Returns:
          True if for currently touched button, False otherwise.

        """
        # clear word complete text
        _Board.complete.text = '_ _ _'

        if touch.is_touch or touch.button == 'left':
            if touch.grab_current is self:
                # release grab
                touch.ungrab(self)
                score = 0
                word = ''
                for tile in _Board._highlighted:
                    letter = tile.text
                    score = score + Letters.Value[letter]
                    word = word + letter
                # only check word if on playArea
                if _Board._dictionary.lookup(word) and \
                    _Board.play_area.collide_point(touch.x, touch.y):
                    # word length bonus of (addtional letter)*2 times the score
                    # for each letter over 3
                    score += int(score*((len(word)-3)/2))
                    _Board.score += score
                    _Board.progress.value += score
                    # remove and replace tiles 


                    # right now we remove and replace but nothing fancy happens
                    # with jumbling up an entire area of the board when they are being replaced
                    # and the graph class properties are not carried onto the new tiles
                    # or the moved tiles
                    for tile in _Board._highlighted:
                        new = _Board._highlighted[tile]
                        root = tile.parent
                        #root.remove_widget(tile)
                        new_tile = Tile()
                        root.add_widget(new_tile)
                        tile.remove()
					
                    #_Board.update_board()
                        
                
                else:
                    for tile in _Board._highlighted:
                        tile.background_color = [1,1,1,1]
                        
                # clear highlighted list
                _Board._highlighted.clear()
                    
                return True
        return False
        
    def remove_complete(self, instance):
        self.parent.remove_widget(self)
        Tile.anims_to_complete -= 1
        
        # all tiles removed, update board
        if not Tile.anims_to_complete:
            # rebuild graph
            _Board.update_board()
        
    def remove(self):
        # create an animation object. 
        animation = Animation(pos=(self.x, -100), t='out_bounce', d = .3)
        Tile.anims_to_complete += 1
        animation.on_complete = self.remove_complete

        # apply the animation on the tile
        animation.start(self) 
