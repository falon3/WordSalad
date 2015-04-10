
from random import randint, random
from kivy.uix.button import Button
from words import Letters
from kivy.animation import Animation
from kivy.properties import ObjectProperty

_Board = None

class Tile(Button):
    """ Represents a tile in the game board.
    """    
    anims_to_complete = 0
    tiles_being_removed = 0
    lscore = ObjectProperty()
    number = 0
    
    def __repr__(self):
        score = ""
        try:
            score = self.lscore.text
        except:
            pass
        return self.text + "," + score
    
    def __init__(self, number, board=None, **kwargs):
        """
        
        """
        if board != None and _Board == None:
            global _Board
            _Board = board
            
        # initialize base class
        super(Tile, self).__init__(**kwargs)    
        
        # keep tile color updated
        _Board.bind(tile_color=self.update_color) 
        
        
        # populate board with random letters
        # TODO: consider populating board with words and partial words
        
        # set the text of this tile
        rand = randint(0, len(Letters.letters)-1)
    
        letter = Letters.letters[rand]
        self.text = letter
        self.lscore.text = str(Letters.Value[letter])
        self.number = number
    
    def update_color(self, instance, value):
        if self in _Board._highlighted or value == [1,1,1,1]:
            self.background_color = value
                
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
            if touch.grab_current is self and not Tile.anims_to_complete: 
                word = _Board.complete
                # clear word complete text
                _Board.complete = '_ _ _'
                
                # release grab
                touch.ungrab(self)
                # only check word if on playArea
                if _Board._dictionary.lookup(word) and \
                    _Board.play_area.collide_point(touch.x, touch.y) \
                    and _Board._highlighted:
                        
                    
                    # add bubble points indicator
                    bubble = _Board.footer.bubble
                    # get the last element added to highlighted
                    
                    last = next(reversed(_Board._highlighted))
                    bubble.pos = last.pos
                    bubble.text = _Board.header.word_complete.bubble.text[:]
                    score_board = _Board.header.lheader.score
                    timer = _Board.game_timer
                    move_bubble = Animation(pos=(timer.x + 30, timer.y - 20), \
                        t='in_expo', d = 0.7)
                    move_bubble += Animation(pos=(score_board.x + 50, score_board.y), \
                        t='in_out_elastic', d = 0.3)
                    move_bubble.on_progress = self.mid_bubble
                    move_bubble.on_complete = self.done_bubble
                    move_bubble.start(bubble)
                    
                    # mark score bubble as in-progress
                    bubble.working = 1
                    
                                
                    affected_columns = set()
                    # find columns with tiles to remove
                    for tile in _Board._highlighted:
                        affected_columns.add(tile.parent)
            
                    Tile.replace_tiles(affected_columns)
                    

                else:
                    #clear word complete point bubble
                    _Board.value = 0
                    # clear highlight
                    for tile in _Board._highlighted:
                        tile.background_color = [1,1,1,1]
                        
                # clear highlighted list
                _Board._highlighted.clear()
                
                                    
                return True
        return False
        
    def mid_bubble(self, instance, progression):
        if progression >= 0.7 and instance.working < 2:
            instance.working = 2
            _Board.game_timer.seconds += _Board.value
        
    
    def done_bubble(self, instance):
        
        _Board.score += _Board.value

        if _Board.score >= 4 and _Board.level == 0:
            _Board.level = 1
            _Board.progress.max = 100
        
        # level up every 100 points
        if _Board.level > 0 and _Board.score >= 100*_Board.level:
            _Board.level += 1
           
        
        # move bubble back off screen
        instance.pos = -5000, -5000
        
        #clear word complete point bubble
        _Board.value = 0
        
        # reset bubble (allow game to end)
        instance.working = 0
    
    def replace_tiles(affected_columns):
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
        
        _Board._highlighted.clear()
    
    def add(remove, old, add, new):
        # change the parent of the removed tiles
        column = old.parent
        column.add_widget(new, index=len(column.children))
        column.remove_widget(old)
        _Board.footer.add_widget(old, index = 1)
        
        # play animations
        remove.start(old)
        add.start(new)
    
    def add_complete(self, instance):     
        instance.fall_complete(instance)
        
    def remove(self):        
        column = self.parent
        window = column.parent.get_parent_window()
        fall_out = Animation(size=self.size,pos=(self.x, -125), \
            t='out_bounce', d = 1.5)
        
        dest_tile = column.children[len(column.children)-column.missing_tiles]
        fall_in =  Animation(pos=(self.x, dest_tile.y), \
            t='out_bounce', d = 1)
        Tile.anims_to_complete += 1
        Tile.tiles_being_removed += 1
        new_tile = Tile(self.number)
        new_tile.x = self.x
        new_tile.y = window.height + 100
        
        fall_out.on_complete = self.remove_complete
        fall_in.on_complete = new_tile.add_complete
        
        column.missing_tiles -= 1 
        
        return fall_out, self, fall_in, new_tile
        
    def remove_complete(self, instance):
        _Board.footer.remove_widget(instance)
        Tile.tiles_being_removed -= 1
        
    
    def fall(tiles, i):
        tile = tiles[i]
        
        prev_tile = tiles[i-tile.parent.missing_tiles]
        Tile.anims_to_complete += 1
        animation = Animation(pos=(prev_tile.x, prev_tile.y), \
                        t='out_bounce', d = 1)
        animation.on_complete = tile.fall_complete
        animation.start(tile)
        
    def fall_complete(self, instance):
        Tile.anims_to_complete -= 1 
        
        if not Tile.anims_to_complete:
            # rebuild graph
            _Board.update_board()
