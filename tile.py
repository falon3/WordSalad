
from random import randint
from kivy.uix.button import Button
from words import Letters
from kivy.animation import Animation
from kivy.properties import ObjectProperty

_Board = None

class Tile(Button):
    """ Represents a tile in the game board.
    """    
    anims_to_complete = 0
    animating = False
    lscore = ObjectProperty()
    
    def __repr__(self):
        return self.text
    
    def __init__(self, board=None, **kwargs):
        """
        
        """
        if board != None and _Board == None:
            global _Board
            _Board = board
            
        # initialize base class
        super(Tile, self).__init__(**kwargs)     
        
        
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
            if self.collide_point(touch.x, touch.y) \
                and not Tile.anims_to_complete:
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
            if self.collide_point(touch.x, touch.y) \
                and not Tile.anims_to_complete: 
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

        if touch.is_touch or touch.button == 'left':
            if touch.grab_current is self:
                word = _Board.complete
                # clear word complete text
                _Board.complete = '_ _ _'
                
                # release grab
                touch.ungrab(self)
                # only check word if on playArea
                if _Board._dictionary.lookup(word) and \
                    _Board.play_area.collide_point(touch.x, touch.y):
                    score = _Board.value
                    _Board.score += score
                    # reset score progress bar every 100 points because reached next level
                    # maybe display a bubble animation when this happens like (level 1, level 2....)
                    _Board.progress.value = (_Board.progress.value + score)%_Board.progress.max
                    _Board.game_timer.seconds += score
                    
                    affected_columns = set()
                    # find columns with tiles to remove
                    for tile in _Board._highlighted:
                        affected_columns.add(tile.parent)
                        
                    # remove and replace tiles 
                    for column in affected_columns:
                        found = False
                        i = 0
                        remove = []
                        # count tiles removed
                        for tile in column.children:
                            if tile in _Board._highlighted:
                                found = True
                                remove.append(tile)
                                column.missing_tiles += 1
                            elif found:                                    
                                Tile.fall(column.children, i)
                            i += 1
                        add = []
                        # build animations
                        for tile in remove:        
                            add.append(tile.remove())
                        # apply animations
                        for new in add:                
                            Tile.add(new[0], new[1], new[2], new[3])
                else:
                    for tile in _Board._highlighted:
                        tile.background_color = [1,1,1,1]
                        
                # clear highlighted list
                _Board._highlighted.clear()
                
                #clear point bubble
                _Board.value = 0
                                    
                return True
        return False
    
    def add(remove, old, add, new):
        column = old.parent
        column.add_widget(new, index=len(column.children))
        column.remove_widget(old)
        _Board.progress.add_widget(old)
        remove.start(old)
        add.start(new)
    
    def add_complete(self, instance):     
        instance.fall_complete(instance)
        
    def remove(self):        
        self.animating = True
        column = self.parent
        window = column.parent.get_parent_window()
        fall_out = Animation(size=self.size,pos=(self.x, -100), \
            t='out_bounce', d = 2)
        
        dest_tile = column.children[len(column.children)-column.missing_tiles]
        fall_in =  Animation(pos=(self.x, dest_tile.y), \
            t='out_bounce', d = 1)
        Tile.anims_to_complete += 1
        new_tile = Tile()
        new_tile.x = self.x
        new_tile.y = window.height + 100
        new_tile.animating = True
        
        fall_out.on_complete = self.remove_complete
        fall_in.on_complete = new_tile.add_complete
        
        column.missing_tiles -= 1 
        
        return fall_out, self, fall_in, new_tile
        
    def remove_complete(self, instance):
        _Board.progress.remove_widget(instance)
    
    def fall(tiles, i):
        tile = tiles[i]
        tile.animating = True
        
        prev_tile = tiles[i-tile.parent.missing_tiles]
        Tile.anims_to_complete += 1
        animation = Animation(pos=(prev_tile.x, prev_tile.y), \
                        t='out_bounce', d = 1)
        animation.on_complete = tile.fall_complete
        animation.start(tile)
        
    def fall_complete(self, instance):
        Tile.anims_to_complete -= 1 
        
        instance.animating = False
        if not Tile.anims_to_complete:
            # rebuild graph
            _Board.update_board()
            pass       
