from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.bubble import BubbleButton
from kivy.uix.label import Label
from kivy.properties import StringProperty, ObjectProperty, NumericProperty, \
    ListProperty
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen, RiseInTransition
from kivy.uix.popup import Popup 

from words import Letters, Dictograph
from collections import OrderedDict
from tile import Tile, SearchWord
from graph_v2 import Graph
import math

TILE_ROWS = 7       # number of rows in the game board
TILE_COLUMNS = 11   # number of columns  in the game board

LEVEL_POINTS = 100
LEVEL_1_POINTS = 30

_Board = None

class Board(Screen):   
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
    _game_over = False
    _searchword = StringProperty('')
    play_area = ObjectProperty()
    complete = StringProperty()
    color = ListProperty()
    tile_color = ListProperty([1,1,1,1])
    progress = ObjectProperty()
    score = NumericProperty()
    level = NumericProperty(0)
    
    tiles = []
        
    def complete_word(self, tile):        
        # display current letters selected in sequence selected        
        
        score = 0
        word = ''
        for tile in self._highlighted:
            letter = tile.text
            word += letter
            score = Letters.calc_add_score(word, score, letter)            
        
        self.value = score
        self.complete = word 
        # word is green if found
        word_found = self._dictionary.lookup(word)
        if word_found:
            self.color = [0, .7, .7, 1]
            self.tile_color = [0,1,1,1]
        # yellow if possible
        elif word_found != None:            
            self.color = [.7, .7, 0, 1]
            self.tile_color = [2,2,0,1]
        # red if not possible
        else:
            self.color = [.7, 0, 0, 1]
            self.tile_color = [1,0,0,1]
    
    def highlight(self, tile, touch):           
        # only highlight letter if moving over center.
        border_x = tile.width / 10
        border_y = tile.height / 10
        if tile.x + border_x <= touch.x <= tile.right - border_x \
            and tile.y + border_y <= touch.y <= tile.top - border_y \
            or not touch.px:
            # if not highlighted
            if tile not in self._highlighted:     
                    last = None
                    if self._highlighted:
                    # get the last element added to highlighted
                        last = next(reversed(self._highlighted))
                    
                    # if last exists, get neighbors
                    if last:
                        neighbours = self._board.neighbours(last.number)
                    # allow highlighting if first tile or adjacent tile
                    if not last or tile.number in neighbours:                
                        self._highlighted[tile] = len(self._highlighted)
                        tile.background_color = self.tile_color
            
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
        for i in range(TILE_ROWS * TILE_COLUMNS):
            if i % TILE_ROWS == 0:
                column = Column()
                # swap these conditions if going horizontal
                if i % (2 * TILE_ROWS) == 0:      
                    column.pos_hint = {'top': .915}   
                else:       
                    column.pos_hint = {'top': .98}       
                          
                playArea.add_widget(column)
                self._columns.append(column)

            tile = Tile(i, self)
            tiles.append(tile)
            column.add_widget(tile)

        # build graph from board
        self.update_board()
        

    def update_board(self, tiles = None):
        # rebuild tile list from rows
        if tiles == None:
            tiles = [tile for column in self._columns for tile in \
                    reversed(column.children)]
            self.tiles = tiles
            # get just the numbers
            tiles = [tile.number for tile in tiles]
            
            # create graph representing the board
            self._board = Graph(set(tiles))
        # fill out edges of graph
        edges = []
        
        # check if at board boundaries
        
        for i in tiles:        
            
            left = i % TILE_ROWS == 0
            right = i % TILE_ROWS == TILE_ROWS - 1 
            top = i // TILE_ROWS == 0
            bottom = i // TILE_ROWS == TILE_COLUMNS - 1
            
            
            # offset == 1 for odd rows, 0 for even
            offset = (i // TILE_ROWS) % 2
            # even == True if offset == 0
            even = offset == 0
                        
            # NOTE: effectively the two values above are identical, but 
            #       I've given them different names because they are
            #       used for different purposes
            
            # not left of the board
            if not left:
                self._board.add_edge((i, i-1))
                
            # not right of the board
            if not right:
                self._board.add_edge((i, i+1))
            
            # not top of the board
            if not top:      
                if not right:
                    self._board.add_edge((i, i-TILE_ROWS + 1 - offset))  
                elif not even:  # right and odd
                    self._board.add_edge((i, i-TILE_ROWS))            
                if not left: 
                    self._board.add_edge((i, i-TILE_ROWS - offset))  
                elif even:  # left and even
                    self._board.add_edge((i, i-TILE_ROWS))         
            
                
            # not bottom of the board
            if not bottom:
                if not right:
                    self._board.add_edge((i, i+TILE_ROWS + 1 - offset))
                elif not even:  # right and odd
                    self._board.add_edge((i, i+TILE_ROWS))                      
                if not left:
                    self._board.add_edge((i, i+TILE_ROWS - offset))   
                elif even:  # left and even
                    self._board.add_edge((i, i+TILE_ROWS))    
        
        
        
    def reset_tiles(self, min_time=-float('inf')):
        if  _Board.score == 0 or (_Board.game_timer.seconds >= min_time and 
                            not Tile.anims_to_complete):
            add = []
            for tile in self.tiles:
                tile.background_color = [1,.5,.5,1]
            Tile.replace_tiles(set(self.tiles), self._columns)
            self.complete = '_ _ _'
            self.value = 0
    
    def on_pre_enter(self):
        self.header.lheader.score.displayed_score = 0
        
    def on_enter(self):
        if self.score > 0:     
            self.score = 0
            self.reset_tiles()   
            self.level = 0
            self.progress.value = 0
            self.progress.max = LEVEL_1_POINTS
            self._game_over = False
            self.footer.search.remove()
        
        
class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)
        
        

class Column(BoxLayout):
    missing_tiles = 0

class LeftHeader(BoxLayout):
    pass
    
class Header(BoxLayout):
    pass
    
class Footer(Label):
    pass
    
class PlayArea(BoxLayout):
    pass

class Score(BoxLayout):
    displayed_score = NumericProperty()
    
    def __init__(self, **kwargs):        
        # call parent class init
        super(Score, self).__init__(**kwargs)
        
        Clock.schedule_interval(self.update, .05)
    
    def update(self, time_passed):
        increment = max(int(abs( self.displayed_score - _Board.score) / 50), 1)
        
        if self.displayed_score < _Board.score:
            self.displayed_score += increment
        if self.displayed_score > _Board.score:
            self.displayed_score -= increment
                    
        # reset score progress bar every 100 points because reached next level
        # add seconds to timer when points scored
        _Board.progress.value = self.displayed_score % _Board.progress.max
        

class WordComplete(Label):
    pass 

class GameTimer(BoxLayout):
    seconds = NumericProperty()
    displayed_seconds = NumericProperty()
    cover_timer = -1
    next_tile_to_fall = TILE_ROWS - 1
    
    def __init__(self, **kwargs):        
        # call parent class init
        super(GameTimer, self).__init__(**kwargs)
                
        Clock.schedule_interval(self.update, .05)

    def update(self, time_passed):
        sec = math.ceil(self.seconds)
        increment = max(int(abs(sec - self.displayed_seconds) / 50), 1)
        if self.displayed_seconds < sec:
            self.displayed_seconds += increment
                
        elif self.displayed_seconds > sec:
            self.displayed_seconds -= increment
        
        if _Board.level > 0:
            if self.seconds > 0:
                if _Board.level > 1:
                    time_passed *= (_Board.level*4/9)
                    
                self.seconds = self.seconds - time_passed
                #if Board.level > 
                                            
            # don't end the game if the score bubble is still animating
            # or if tiles are falling
            elif not _Board._game_over and not _Board.footer.bubble.working\
                and not Tile.anims_to_complete and SearchWord.appeared != 1:
                _Board._game_over = True
                GameOver()
                
        
                
    def tile_drop(self, time_passed):
            
        
        # drop the bottom tile out of a row every 20 seconds - levels
        # but never faster than once per second
        self.cover_timer += time_passed
        tile = _Board.tiles[self.next_tile_to_fall]
        drop_time = max(1, 20 - _Board.level)
        if self.cover_timer > drop_time:
            
            if not Tile.anims_to_complete:
                fall = True
                for highlighted in _Board._highlighted:
                    if highlighted.parent == tile.parent:
                        fall = False
                if fall:                 
                    tile.background_color = [1,0,0,1]   
                    _Board.tile_cover.size = tile.width, tile.height / 20
                    self.cover_timer = 0
                    Tile.replace_tiles([tile], [tile.parent])
                    self.next_tile_to_fall += TILE_ROWS 
                    self.next_tile_to_fall %= TILE_ROWS * TILE_COLUMNS  
        else:        
            _Board.tile_cover.size = tile.width, tile.height * self.cover_timer / drop_time
            _Board.tile_cover.background_color = 1,0,0, self.cover_timer / drop_time
            _Board.tile_cover.pos = tile.pos
    

class Bonus(BubbleButton):    
    #disable touch events
    def on_touch_down(self, touch): 
        pass
    def on_touch_up(self, touch): 
        pass
    def on_touch_move(self, touch): 
        pass

class Level(BoxLayout):
    pass
    


def GameOver():
    # save score to file only if higher than rest saved
    # see if got new high score
    
    try: # check that data is initialized
        GameOver.input_text
    except AttributeError: # initialize data
        GameOver.input_text = None
        GameOver.score_list = []
        
    _Board._highlighted.clear()
    Clock.unschedule(_Board.game_timer.tile_drop)
    _Board.game_timer.cover_timer = -1
    _Board.tile_cover.pos = -5000, -5000
    _Board.manager.transition = RiseInTransition(duration=.5)
    _Board.manager.current = 'menu'
    

    box = BoxLayout()
    text_in = TextInput(multiline = False, font_size = 40)
    box.add_widget(text_in)

    popup = Popup(title='NEW HIGH SCORE! Enter Your Name')
    popup.content = box
    popup.auto_dismiss = False
    popup.size_hint = (None, None)
    popup.size=(550, 120)

    text_in.on_text_validate = LastScreen
    
    GameOver.input_text = text_in
    GameOver.input_text.popup = popup
    
    
     # high score file must end with newline
    try:
        file = open('high_scores.txt', 'r')
        for line in file:
            line = line.strip().split(",")
            print("line:", line)
            try:
                GameOver.score_list.append((line[0],line[1])) 
            except:
                # if blank line do nothing
                continue
        file.close()
        print("DEBUG")
    except:
        # dummy score emtry if file was empty
        GameOver.score_list.append((0, 'Falon'))
  

    if int(GameOver.score_list[-1][0]) < _Board.score:
        popup.open()
    else:
        LastScreen()
  
    
def LastScreen():
    input_text = GameOver.input_text
    score_list = GameOver.score_list
    player = input_text.text
       
    end_score = _Board.score 
    input_text.popup.dismiss()

   
    if int(score_list[-1][0]) < end_score:
        # reopen file for appending this time
        file_append = open('high_scores.txt', 'a')

        # new high score!!!
        # PROMPT USER FOR NAME AND SAVE AS name
        score_list.append((end_score, player))
        file_append.write(str(end_score))
        file_append.write(", ")
        file_append.write(player)
        file_append.write("\n")
        file_append.close()
   

    Records = _Board.manager.current_screen  


    Records.champ_score = int(score_list[-1][0])
    Records.your_score = end_score
    Records.champion = score_list[-1][1]
    for i in range(1, len(score_list)):
        try:
            Records.scores[i-1] = int(score_list[-i][0])
            Records.player[i-1] = score_list[-i][1]
        except:
            Records.scores[i-1] = 0
            Records.player[i-1] = 'Falon'
