# Using modules made by other people.
import sys
import pygame as pg

class Tile:
    """
    The smallest of the tiles that are found in the program.
    Parameters:
        game- The main game class that runs the main game loop.
        pos- A tuple containing the x and y co-ordinates of the tile.
        index- A tuple containing the same index as its position on its particular board.

    """
    TILE_GAP = 0
    TILE_SIZE: int = 50

    def __init__(self, game, pos: tuple[int, int], index: tuple[int, int]) -> None:
        self.game: Game = game  # Need this to access the items that are in the game class.
        self.pos: tuple[int, int] = pos
        self.index = index  # Need this to compare the tile with a sub_board later on.
        self.rect: pg.Rect = pg.Rect(*pos, Tile.TILE_SIZE, Tile.TILE_SIZE)  # For the collision detection and drawing on screen.
        self.rect_color = (0, 0, 0)
        self.text = self.game.small_tile_font.render("", True, (0, 0, 0))
        self.value = float("nan")  # NaN in python. Used so that the total becomes NaN while checking for win.

    def update(self) -> bool:
        """
        Updates the value of a tile based on the current player's turn.

        Return: A boolean value depending on if the update was successful or not.
        """
        # Checks if the tile is empty (not occupied by any other player before).
        if self.value not in {0, 1}:
            if self.game.turn == 1:
                symbol = "X"
                self.rect_color = Game.X_COLOR
                self.value = 1
            else:
                symbol = "O"
                self.rect_color = Game.O_COLOR
                self.value = 0

            # Displays the text on the screen.
            self.text = self.game.small_tile_font.render(symbol, True, self.rect_color)
            self.render()
            return True

        return False

    def render(self) -> None:
        """
        Renders the tile on the main display.
        """
        # Draws the current tile's boundaries.
        pg.draw.rect(self.game.screen, self.rect_color, self.rect, 2)
        self.game.screen.blit(self.text, (self.pos[0] + (Tile.TILE_SIZE - self.text.get_width()) / 2,
                                          self.pos[1] + (Tile.TILE_SIZE - self.text.get_height())))


class SubBoard:
    """
   The small board that is contained in the big board and itself contains the smaller tiles.
   Parameters:
       game- The main game class that runs the game loop.
       pos- A tuple containing the sub_board's x and y co-ordinates.
       index- A tuple containing the sub_board's index to reference it with the tiles' index.
    """
    BOARD_GAP: int = 15
    BOARD_SIZE: int = 3 * Tile.TILE_SIZE + 2 * Tile.TILE_GAP

    def __init__(self, game, pos: tuple[int, int], index: tuple[int, int]) -> None:
        self.pos = pos
        self.game: Game = game  # To access the game class items.
        self.index = index  # To compare with its corresponding tile.

        self.rect: pg.Rect = pg.Rect(*pos, SubBoard.BOARD_SIZE, SubBoard.BOARD_SIZE)
        self.rect_color = (0, 0, 0, 0)

        # Stores all the 9 tiles (Tile objects) inside it.
        self.tiles: list[Tile] = []

        self.value = float("nan")

        # Filling in the list 'tiles' with its Tile objects.
        for i in range(3):
            for j in range(3):
                tile_pos = (pos[0] + j * (Tile.TILE_SIZE + Tile.TILE_GAP), pos[1] + i*(Tile.TILE_SIZE + Tile.TILE_GAP))
                tile = Tile(self.game, tile_pos, (i, j))
                self.tiles.append(tile)

                tile.render()

        # Used for transparency.
        self.alpha = 0
        self.winner = None

    def render(self) -> None:
        """
        Renders the tile on the main display.
        """
        # If the tile is not used/ completed, show the tiles, otherwise show the winner of that tile.
        if self not in self.game.used_sub_boards:
            s = pg.Surface((SubBoard.BOARD_SIZE, SubBoard.BOARD_SIZE))
            s.fill((27, 240, 200))
            # s.fill((252, 186, 3))
            s.set_alpha(self.alpha)
            self.game.screen.blit(s, self.pos)

            for tile in self.tiles:
                tile.render()
        else:
            color = Game.X_COLOR if self.winner == "X" else Game.O_COLOR
            winner_text = self.game.big_tile_font.render(self.winner, True,
                                                         color)
            self.game.screen.blit(winner_text,
                                  (self.pos[0] + (SubBoard.BOARD_SIZE - winner_text.get_width()) / 2,
                                   self.pos[1] + (SubBoard.BOARD_SIZE - winner_text.get_height())))
            pg.draw.rect(self.game.screen, color, self.rect, 5)


class Game:
    """
    The main game class that has the game loop.
    """
    OUTSIDE_GAP = 20
    SCREEN_WIDTH: int = 3 * SubBoard.BOARD_SIZE + 2 * SubBoard.BOARD_GAP + 2 * OUTSIDE_GAP
    SCREEN_HEIGHT: int = 3 * SubBoard.BOARD_SIZE + 2 * SubBoard.BOARD_GAP + 2 * OUTSIDE_GAP + 40  # For the turn text.

    X_COLOR = (0, 150, 20)
    O_COLOR = (200, 0, 0)

    def __init__(self) -> None:
        # Setting up the screen and other pygame's important stuff.
        pg.init()
        self.screen: pg.Surface = pg.display.set_mode((Game.SCREEN_WIDTH, Game.SCREEN_HEIGHT))

        pg.display.set_caption("Ultimate Tic-Tac-Toe")
        self.clock: pg.Clock = pg.Clock()

        self.turn = 1

        self.small_tile_font = pg.Font(None, int(1.2 * Tile.TILE_SIZE))
        self.big_tile_font = pg.Font(None, int(1.2 * SubBoard.BOARD_SIZE))

        self.turn_font = pg.Font(None, int(Tile.TILE_SIZE))

        self.sub_boards: list[SubBoard] = []
        self.next_sub_boards = set()
        self.used_sub_boards = set()

        self.winner = None

        # Filling in the list 'sub_boards' with all the 9 sub_boards each of which in turn have 9 tiles in them.
        for i in range(3):
            for j in range(3):
                pos = (Game.OUTSIDE_GAP + j * (SubBoard.BOARD_SIZE + SubBoard.BOARD_GAP),
                       Game.OUTSIDE_GAP + i * (SubBoard.BOARD_SIZE + SubBoard.BOARD_GAP))
                board = SubBoard(self, pos, (i, j))
                self.sub_boards.append(board)
                self.next_sub_boards.add(board)

        # Just draw and render everything.
        self.draw_everything()
        pg.display.flip()

    def draw_everything(self) -> None:
        """
        Renders everything on the screen when called.
        """
        # Rendering everything.
        self.screen.fill((185, 185, 185))

        # Checking which sub_board needs to be highlighted.
        for sub_board in self.sub_boards:
            if sub_board in self.next_sub_boards:
                sub_board.alpha = 128
            else:
                sub_board.alpha = 0

            sub_board.render()

        # Displaying whose turn it is at the bottom.
        move_text = self.turn_font.render(f"It's {'X' if self.turn % 2 else 'O'}'s turn!", True,
                                          Game.X_COLOR if self.turn % 2 else Game.O_COLOR)
        self.screen.blit(move_text, ((Game.SCREEN_WIDTH - move_text.get_width()) / 2, Game.SCREEN_HEIGHT - 45))

    def evaluate(self, board, tiles) -> int:
        """
        Used to check if of the sub_boards or the main game board has been won by a player.
        """
        # All the possible combinations to win.
        combos: set[int] = {
            sum([tiles[0].value, tiles[1].value, tiles[2].value]), sum([tiles[3].value, tiles[4].value, tiles[5].value]),
            sum([tiles[6].value, tiles[7].value, tiles[8].value]), sum([tiles[0].value, tiles[3].value, tiles[6].value]),
            sum([tiles[1].value, tiles[4].value, tiles[7].value]), sum([tiles[2].value, tiles[5].value, tiles[8].value]),
            sum([tiles[0].value, tiles[4].value, tiles[8].value]), sum([tiles[2].value, tiles[4].value, tiles[6].value])
        }

        # Checking for 'X' and 'O' being in a possible combination.
        # Also has these try except blocks because we don't know if the parameter getting
        # passed in is a Game object or a SubBoard object.
        if 3 in combos:
            board.value = 1
            try:
                self.used_sub_boards.add(board)
            except AttributeError:
                pass
            return 3

        elif 0 in combos:
            board.value = 0
            try:
                self.used_sub_boards.add(board)
            except AttributeError:
                pass

            return 1

        # If all the tiles are filled but there is no winner, then reset.
        full = True
        for tile in tiles:
            if tile.value not in {0, 1}:
                full = False

        if full:
            try:
                board.__init__(self, board.pos, board.index)
            except TypeError:
                start_game()

        return 0

    def run(self) -> None:
        """
        The main game loop. All the events happening on the screen and behind the screen are all controlled here.
        """
        i = 0
        # Game Loop
        while True:
            # Event Handler
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

                # Checks if the user presses the left mouse button.
                if event.type == pg.MOUSEBUTTONDOWN and self.winner is None:
                    if event.button == 1:
                        i += 1
                        print(i)
                        mouse_pos = pg.mouse.get_pos()
                        # Iterates through the list sub_boards and then iterates through the tiles in eac of the sub_board.
                        for sub_board in self.sub_boards:
                            for tile in sub_board.tiles:
                                # Checks if the mouse collided with the tile and if yes, also checks if the
                                # sub_board that tile is on is one of the sub_boards that are allowed/unlocked for the next turn.
                                if tile.rect.collidepoint(mouse_pos):
                                    if sub_board in self.next_sub_boards:
                                        self.next_sub_boards.clear()
                                        # Again, iterates through each of the sub_board in all the sub_boards to check
                                        # which one corresponds to the small tile's position to the big main game's
                                        # tile (sub_board) position.
                                        for board in self.sub_boards:
                                            if board.index == tile.index:
                                                next_sub_board = board
                                                self.next_sub_boards.add(next_sub_board)
                                                break
                                        # The next_sub_board will always be defined because there is always a
                                        # sub_board with the same index as a tile.
                                        # So, this warning can be ignored.
                                        self.next_sub_boards.add(next_sub_board)
                                        print(next_sub_board.index, end="\n\n")
                                        if tile.update():
                                            self.turn = (self.turn + 1) % 2
                                            # The 'walrus' operator below will assign sub_board_ret with the value
                                            # returned by the self.evaluate() function.
                                            if sub_board_ret := self.evaluate(sub_board, sub_board.tiles):
                                                sub_board.winner = "X" if sub_board_ret == 3 else "O"

                                                # This warning is dealt with inside the function so not a problem.
                                                if main_ret := self.evaluate(self, self.sub_boards):
                                                    self.winner = "X" if main_ret == 3 else "O"

                                            # If the current targeted board is already completed, then all the other
                                            # boards are unlocked.
                                            if next_sub_board in self.used_sub_boards:
                                                self.next_sub_boards = set(self.sub_boards) - self.used_sub_boards
                                            self.draw_everything()
                                            pg.display.flip()

                # If the winner has been decided, then this will be displayed until the game is restarted by pressing
                # the space key on the keyboard.
                if self.winner is not None:
                    self.screen.fill((185, 185, 185))
                    win_font = pg.Font(None, int(Game.SCREEN_WIDTH / 2.5))
                    win_text = win_font.render(f"     {self.winner}\n Wins!!", True,
                                               Game.X_COLOR if self.winner == "X" else Game.O_COLOR)

                    self.screen.blit(win_text, ((Game.SCREEN_WIDTH - win_text.get_width()) / 2,
                                                (Game.SCREEN_HEIGHT - win_text.get_height()) / 2))

                    pg.display.flip()

                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_SPACE:
                            start_game()

            self.clock.tick(10)


if __name__ == "__main__":
    def start_game():
        Game().run()


    start_game()

