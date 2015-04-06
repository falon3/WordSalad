
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.bubble import BubbleButton
from kivy.uix.label import Label
from kivy.properties import StringProperty, ObjectProperty, NumericProperty, \
    ListProperty

from words import Letters, Dictograph
from collections import OrderedDict
from tile import Tile
from graph_v2 import Graph
import time
from kivy.clock import Clock

TILE_COLUMNS = 6    # number of columns in the game board
TILE_ROWS = 9       # number of rows in the game board

_Board = None

class Board(BoxLayout):   
    """Represents the game board.
    
    Currently this class encompasses both the data for the board and the  
    display for the same. 
    
    TODO: We may want to break this functionality up into
    a couple different classes for easier development and maintenance.
    
    Attributes:
      _highlighted (OrderedDict): An ordered collection of highlighted tiles.
      _dictionary (Dictograph): A word list used for checking words 
        and populating the board.
      play_area (ObjectProperty): the box layout of the play area
      progress (ObjectProperty): the progress bar object
      score (NumericProperty): the score
      complete (StringProperty): the word completion text
    
    
    """    
    _highlighted = OrderedDict()
    _dictionary = Dictograph("us_cad_dict.txt")
    _columns = []
    play_area = ObjectProperty()
    complete = StringProperty()
    color = ListProperty()
    progress = ObjectProperty()
    score = NumericProperty()
    tiles = []
    
    def check_neighbors(self, tile, word):
        neighbors = self._board.neighbours(tile)
        for neighbor in neighbors:
            if self._dictionary.in_trie(word + neighbor.text):
                return True
        return False
    
    def complete_word(self, tile):        
        # display current letters selected in sequence selected        
        
        score = 0
        word = ''
        for tile in self._highlighted:
            letter = tile.text
            score += Letters.Value[letter]
            word += letter
            
        # word length bonus of (addtional letter)*2 times the score
        # for each letter over 3
        if len(word) > 2:
            score += int(score*((len(word)-3)/2))
        
        self.value = score
        self.complete = word 
        # word is green if found
        word_found = self._dictionary.lookup(word)
        if word_found:
            self.color = [0, .7, .7, 1]
        # yellow if possible
        elif word_found != None:            
            #if _Board.check_neighbors(tile, word):
            self.color = [.7, .7, 0, 1]
            #else:
            #    _Board.word_complete.color = [.7, 0, 0, 1]    
        else:
            self.color = [.7, 0, 0, 1]
    
    def highlight(self, tile, touch):    
        # if not highlighted
        if tile not in self._highlighted:            
            # only highlight letter if moving over center.
            border_x = tile.width / 10
            border_y = tile.height / 10
            if tile.x + border_x <= touch.x <= tile.right - border_x \
                and tile.y + border_y <= touch.y <= tile.top - border_y \
                or not touch.px:
                last = None
                if self._highlighted:
                # get the last element added to highlighted
                    last = next(reversed(self._highlighted))
                
                # if last exists, get neighbors
                if last:
                    neighbours = self._board.neighbours(last)
                # allow highlighting if first tile or adjacent tile
                if not last or tile in neighbours:                
                    self._highlighted[tile] = len(self._highlighted)
                    tile.background_color = [0,1,1,1]
        
        # if already highlighted
        elif self._highlighted[tile] == len(self._highlighted) - 2:
            # unhighlight last tile if going backward
            last = self._highlighted.popitem(last=True)
            last[0].background_color = [1,1,1,1]
        
        # display current letters selected in sequence selected
        self.complete_word(tile)
        
    def __init__(self, **kwargs):
        
        # call parent class init
        super(Board, self).__init__(**kwargs)
        # set global instance
        tiles = []  
        playArea = self.play_area      
        global _Board
        _Board = self  
        
        # add all the tiles to the board
        for i in range(TILE_COLUMNS * TILE_ROWS):
            if i % TILE_COLUMNS == 0:
                column = Column()
                # swap these conditions if going horizontal
                if i % (2 * TILE_COLUMNS) == 0:      
                    column.pos_hint = {'top': .9}   
                else:       
                    column.pos_hint = {'top': .975}       
                          
                playArea.add_widget(column)
                self._columns.append(column)

            tile = Tile(self)
            tiles.append(tile)
            column.add_widget(tile)

        # build graph from board
        self.update_board()
        

    def update_board(self):
        # rebuild tile list from rows
        tiles = [tile for column in self._columns for tile in \
                reversed(column.children)]
        self.tiles = tiles
        # fill out edges of graph
        edges = []
        
        # check if at board boundaries
        
        for i in range(len(tiles)):           
            
            left = i % TILE_COLUMNS == 0
            right = i % TILE_COLUMNS == TILE_COLUMNS - 1 
            top = i // TILE_COLUMNS == 0
            bottom = i // TILE_COLUMNS == TILE_ROWS - 1
            
            
            # offset == 1 for odd rows, 0 for even
            offset = (i // TILE_COLUMNS) % 2
            # even == True if offset == 0
            even = offset == 0
                        
            # NOTE: effectively the two values above are identical, but 
            #       I've given them different names because they are
            #       used for different purposes
            
            # not left of the board
            if not left:
                edges.append((tiles[i], tiles[i-1]))
                
            # not right of the board
            if not right:
                edges.append((tiles[i], tiles[i+1]))
            
            # not top of the board
            if not top:      
                if not right:
                    edges.append((tiles[i], tiles[i-TILE_COLUMNS + 1 - offset]))  
                elif not even:  # right and odd
                    edges.append((tiles[i], tiles[i-TILE_COLUMNS]))            
                if not left: 
                    edges.append((tiles[i], tiles[i-TILE_COLUMNS - offset]))  
                elif even:  # left and even
                    edges.append((tiles[i], tiles[i-TILE_COLUMNS]))         
            
                
            # not bottom of the board
            if not bottom:
                if not right:
                    edges.append((tiles[i], tiles[i+TILE_COLUMNS + 1 - offset]))
                elif not even:  # right and odd
                    edges.append((tiles[i], tiles[i+TILE_COLUMNS]))                      
                if not left:
                    edges.append((tiles[i], tiles[i+TILE_COLUMNS - offset]))   
                elif even:  # left and even
                    edges.append((tiles[i], tiles[i+TILE_COLUMNS]))    
        
        # create graph representing the board
        self._board = Graph(set(tiles), edges)

    def reset_tiles(self):
        add = []
        for tile in self.tiles:
            # add tiles to _highlighted for Tile.replaceTiles
            self._highlighted[tile] = len(Board._highlighted)
            tile.background_color = [1,.5,.5,1]
        Tile.replace_tiles(self._columns)
        
        


class Column(BoxLayout):
    missing_tiles = 0
    pass

class LeftHeader(BoxLayout):
    pass
    
class Header(BoxLayout):
    pass
    
class PlayArea(BoxLayout):
    pass

class Score(BoxLayout):
    pass

class WordComplete(Label):
    pass 

class GameTimer(BoxLayout):
    seconds = NumericProperty()
    game_over = False
    
    def __init__(self, **kwargs):        
        # call parent class init
        super(GameTimer, self).__init__(**kwargs)
        
        Clock.schedule_interval(self.update, .05)

    def update(self, time_passed):
        if self.seconds > 0:
            self.seconds = self.seconds - time_passed
        elif not self.game_over:
            self.game_over = True
            GameOver(_Board.score)
    

class Bonus(BubbleButton):    
    def on_touch_down(self, touch): 
        pass
    def on_touch_up(self, touch): 
        pass
    def on_touch_move(self, touch): 
        pass
    
def GameOver(end_score):
    print(end_score)
    #_Board.reset_tiles()
    #exit()
