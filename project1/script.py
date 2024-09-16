import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((1000, 750))
font = pygame.font.Font(None, 36)

# Define color variables
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (150, 150, 150)  # for grayed out buttons and ships
LIGHT_BLUE = (100, 100, 255)
RED = (255, 0, 0)  # for outlining ships
GRID_BLUE = (10, 150, 210)  # for grid background

# Global variables to store game state
num_ships = 0
player1_ships = None
player2_ships = None
player1_ships_deep = None
player2_ships_deep = None

# Grids to track attacks for each player
player1_attack_grid = [[None for _ in range(10)] for _ in range(10)]
player2_attack_grid = [[None for _ in range(10)] for _ in range(10)]

def draw_button(text, x, y, w, h, color, action=None, enabled=True):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    # Draw the button in dark gray if it's disabled
    if enabled:
        pygame.draw.rect(screen, color, (x, y, w, h))
    else:
        pygame.draw.rect(screen, DARK_GRAY, (x, y, w, h))

    text_surf = font.render(text, True, BLACK)
    screen.blit(text_surf, (x + w // 2 - text_surf.get_width() // 2, y + h // 2 - text_surf.get_height() // 2))

    # Check if the button is clicked and execute the associated action
    if enabled and x < mouse[0] < x + w and y < mouse[1] < y + h:
        if click[0] == 1 and action is not None:
            action()

# Start screen for players to select how many ships to play with
def start_screen():
    global num_ships
    while num_ships == 0:
        screen.fill(WHITE)
        text = font.render("Select number of ships to play with:", True, BLACK)
        screen.blit(text, (250, 200))

        # Draw buttons for selecting the number of ships (1 to 5)
        for i in range(1, 6):
            draw_button(str(i), 150 + 100 * i, 250, 80, 50, LIGHT_GRAY,
                        lambda i=i: setattr(sys.modules[__name__], 'num_ships', i))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.flip()

finished = False

# Screen for each player to place their ships
def placement_screen(player):
    global player1_ships, player2_ships, player1_ships_deep, player2_ships_deep, finished
    grid = [[None] * 10 for _ in range(10)]  # Initialize the grid with None values
    ships = [pygame.Rect(600, 100 + i * 60, (i + 1) * 50, 50) for i in range(num_ships)]
    selected = None # Which ship is currently selected for placement
    vertical = False
    finished = False

    def clear_ship(ship_num):
        # Remove a ship from the grid
        for y in range(10):
            for x in range(10):
                if grid[y][x] == ship_num:
                    grid[y][x] = None

    def is_valid_placement(x, y, size, is_vertical, ship_num):
        # Check if the ship is within the grid bounds
        if is_vertical and y + size > 10:
            return False
        if not is_vertical and x + size > 10:
            return False

        # Check only the cells the ship will occupy
        for i in range(size):
            check_x = x + (0 if is_vertical else i)
            check_y = y + (i if is_vertical else 0)

            if grid[check_y][check_x] is not None and grid[check_y][check_x] != ship_num:
                return False

        return True

    while not finished:
        screen.fill(WHITE)
        text = font.render(f"Player {player} Ship Placement", True, BLACK)
        screen.blit(text, (350, 20))

        # Draw the grid and label it with letters and numbers
        for i in range(10):
            for j in range(10):
                pygame.draw.rect(screen, GRID_BLUE, (50 + i * 50, 100 + j * 50, 50, 50)) # Draw background
                pygame.draw.rect(screen, BLACK, (50 + i * 50, 100 + j * 50, 50, 50), 1) # Draw black outlines
                if grid[j][i] is not None:  # If a ship is placed, draw dark gray over that spot in grid
                    pygame.draw.rect(screen, DARK_GRAY, (50 + i * 50, 100 + j * 50, 50, 50))
                screen.blit(font.render(chr(65 + i), True, BLACK), (65 + i * 50, 70))
                screen.blit(font.render(str(j + 1), True, BLACK), (20, 115 + j * 50))

        # Draw the ships in the sidebar
        for ship in ships:
            pygame.draw.rect(screen, DARK_GRAY, ship)
            if ships.index(ship) == selected:
                pygame.draw.rect(screen, RED, ship, 2)

        # Draw rotate and finish buttons
        rotate_text = "Rotate (V)" if vertical else "Rotate (H)"
        draw_button(rotate_text, 600, 600, 150, 50, LIGHT_GRAY, lambda: globals().update(vertical=not vertical))

        all_ships_placed = all(ship.left < 600 for ship in ships)
        draw_button("Finish", 800, 600, 150, 50, LIGHT_GRAY, lambda: None,
                    enabled=all_ships_placed)

        # Draw a red outline to show where the selected ship will be placed
        mouse_pos = pygame.mouse.get_pos()
        if selected is not None:
            size = max(ships[selected].width, ships[selected].height) // 50
            if vertical:
                indicator = pygame.Rect(mouse_pos[0] - 25, mouse_pos[1] - 25, 50, size * 50)
            else:
                indicator = pygame.Rect(mouse_pos[0] - 25, mouse_pos[1] - 25, size * 50, 50)
            pygame.draw.rect(screen, RED, indicator, 2)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            #Use key h or v to rotate
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    vertical = True
                elif event.key == pygame.K_v:
                    vertical = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Rotate button pressed
                if 600 <= event.pos[0] <= 750 and 600 <= event.pos[1] <= 650:
                    vertical = not vertical
                # All ships have been placed and the finish button is pressed
                elif 800 <= event.pos[0] <= 950 and 600 <= event.pos[1] <= 650 and all_ships_placed:
                    finished = True
                else:
                    x, y = (event.pos[0] - 50) // 50, (event.pos[1] - 100) // 50 # Get grid position of mouse click
                    if 0 <= x < 10 and 0 <= y < 10: # Check if mouse click is within bounds of grid
                        # If a ship is selected, check if the placement is valid and place it if so
                        if selected is not None:
                            size = max(ships[selected].width, ships[selected].height) // 50
                            if is_valid_placement(x, y, size, vertical, selected + 1):
                                # Place the ship on the grid
                                clear_ship(selected + 1)
                                for i in range(size):
                                    if vertical:
                                        grid[y + i][x] = selected + 1
                                    else:
                                        grid[y][x + i] = selected + 1
                                ships[selected] = pygame.Rect(50 + x * 50, 100 + y * 50, 50 if vertical else size * 50,
                                                              size * 50 if vertical else 50)
                                selected = None  # Deselect the ship after placing it
                        else:
                            # Select a ship that's already on the grid
                            for i, ship in enumerate(ships):
                                if ship.collidepoint(event.pos):
                                    selected = i
                                    clear_ship(i + 1)  # Clear the ship from its current position
                                    break
                    else:
                        # Select a ship from the sidebar or pick up a placed ship
                        for i, ship in enumerate(ships):
                            if ship.collidepoint(event.pos):
                                selected = i
                                clear_ship(i + 1)  # Clear the ship from its current position
                                break

        pygame.display.flip()

    # store where the ships are, not just the cells that the ships take
    ships_deep = []
    for ship in ships:
        ship_points = []
        for x in range((ship.left-50)//50, (ship.right-50)//50):
            for y in range((ship.top-100)//50, (ship.bottom-100)//50):
                ship_points.append((x, y))
        ships_deep.append(ship_points)

    # Store the completed ship placement for each player
    if player == 1:
        player1_ships = [[1 if cell is not None else None for cell in row] for row in grid]
        player1_ships_deep = ships_deep
    else:
        player2_ships = [[1 if cell is not None else None for cell in row] for row in grid]
        player2_ships_deep = ships_deep

# Transition screen to prevent players from looking at each other's grid
def pass_screen(player):
    global finished
    finished = False
    while not finished:
        screen.fill(WHITE)
        text = font.render(f"Pass to player {player}", True, BLACK)
        screen.blit(text, (350, 20))
        draw_button("Finish", 400, 600, 150, 50, LIGHT_GRAY, None)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Mouse button press when over finish button
                if 400 <= event.pos[0] <= 550 and 600 <= event.pos[1] <= 650:
                    finished = True
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.flip()


def battle_screen(player, opponent_grid, hits_grid, player_grid, player_ships_deep, opponent_ships_deep):
    global finished
    finished = False
    shot_result = None  # Track if the last shot was a hit or miss
    attack_made = False  # Track if an attack has been made, for preventing multiple attacks in same turn

    def check_ship_sunk(x, y, grid, ships_deep):
        # find the ship that the coordinates x, y are on
        ship_points = None
        for ship in ships_deep:
            for point in ship:
                if x == point[0] and y == point[1]:
                    ship_points = ship

        # If no ship is there, then no ship is sunk there
        if ship_points is None:
            return False

        # A ship is sunk if all cells in the ship are hit
        for point in ship_points:
            if grid[point[1]][point[0]] != 'H':
                return False
        return True

    while not finished:
        screen.fill(WHITE)
        text = font.render(f"Player {player}: Select a cell to attack", True, BLACK)
        screen.blit(text, (300, 20))

        # Draw the opponent's grid
        for i in range(10):
            for j in range(10):
                pygame.draw.rect(screen, GRID_BLUE, (50 + i * 50, 100 + j * 50, 50, 50))
                pygame.draw.rect(screen, BLACK, (50 + i * 50, 100 + j * 50, 50, 50), 1)
                screen.blit(font.render(chr(65 + i), True, BLACK), (65 + i * 50, 70))
                screen.blit(font.render(str(j + 1), True, BLACK), (20, 115 + j * 50))

                if hits_grid[j][i] == 'M':  # Missed shot, draw white circle
                    pygame.draw.circle(screen, WHITE, (75 + i * 50, 125 + j * 50), 20, 2)
                elif hits_grid[j][i] == 'H':  # Hit shot
                    if check_ship_sunk(i, j, opponent_grid, opponent_ships_deep):
                        pygame.draw.rect(screen, RED, (50 + i * 50, 100 + j * 50, 50, 50))
                    else:
                        pygame.draw.line(screen, RED, (60 + i * 50, 110 + j * 50), (90 + i * 50, 140 + j * 50), 3)
                        pygame.draw.line(screen, RED, (90 + i * 50, 110 + j * 50), (60 + i * 50, 140 + j * 50), 3)
        
        # Draw player's own grid
        for i in range(10):
            for j in range(10):
                pygame.draw.rect(screen, LIGHT_BLUE, (600 + i * 30, 100 + j * 30, 30, 30))
                pygame.draw.rect(screen, BLACK, (600 + i * 30, 100 + j * 30, 30, 30), 1)
                
                if player_grid[j][i] == 1:  # Ship
                    pygame.draw.rect(screen, DARK_GRAY, (600 + i * 30, 100 + j * 30, 30, 30))
                elif player_grid[j][i] == 'M':  # Missed attack by opponent
                    pygame.draw.circle(screen, WHITE, (615 + i * 30, 115 + j * 30), 12, 2)
                elif player_grid[j][i] == 'H':  # Hit attack by opponent
                    if check_ship_sunk(i, j, player_grid, player_ships_deep):
                        pygame.draw.rect(screen, RED, (600 + i * 30, 100 + j * 30, 30, 30))
                    else:
                        pygame.draw.rect(screen, DARK_GRAY, (600 + i * 30, 100 + j * 30, 30, 30))
                        pygame.draw.line(screen, RED, (605 + i * 30, 105 + j * 30), (625 + i * 30, 125 + j * 30), 2)
                        pygame.draw.line(screen, RED, (625 + i * 30, 105 + j * 30), (605 + i * 30, 125 + j * 30), 2)

        # Show the result of the last shot
        if shot_result:
            result_text = font.render(shot_result, True, BLACK)
            screen.blit(result_text, (400, 650))

        # Draw a "Finish Turn" button
        draw_button("Finish Turn", 800, 600, 150, 50, LIGHT_GRAY, None,
                    enabled=attack_made)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and attack_made:
                # Mouse button press when over finish button
                if 800 <= event.pos[0] <= 950 and 600 <= event.pos[1] <= 650:
                    finished = True
            if event.type == pygame.MOUSEBUTTONDOWN and not attack_made:
                # Get the grid coordinates the player clicked on
                x, y = (event.pos[0] - 50) // 50, (event.pos[1] - 100) // 50
                if 0 <= x < 10 and 0 <= y < 10:
                    # Check if this cell has already been attacked
                    if hits_grid[y][x] is None:
                        if opponent_grid[y][x] == 1:  # Hit
                            hits_grid[y][x] = 'H'
                            opponent_grid[y][x] = 'H'
                            if check_ship_sunk(x, y, opponent_grid, opponent_ships_deep):
                                shot_result = "Sink!"
                            else:
                                shot_result = "Hit!"
                        else:  # Miss
                            hits_grid[y][x] = 'M'
                            opponent_grid[y][x] = 'M'
                            shot_result = "Miss!"
                        attack_made = True  # Lock out further attacks
                    else:
                        # If the cell has already been attacked, do nothing
                        shot_result = "Already Attacked!"

        pygame.display.flip()

    # Check for game over condition
    def all_ships_sunk(grid):
        return all(cell != 1 for row in grid for cell in row)

    if all_ships_sunk(opponent_grid):
        finished = True
        winner = player
        return winner  # Return the winner
    else:
        return 0  # Continue the game

# Game over screen, displays who won and asks to play again
def winner_screen(player):
    global game_running, restart_game
    screen.fill(WHITE)
    text = font.render(f"Player {player} Wins!", True, BLACK)
    screen.blit(text, (350, 200))

    def new_game():
        global restart_game
        restart_game = True

    def end_game():
        global game_running
        game_running = False

    # Draw "New Game" button
    draw_button("New Game", 300, 400, 150, 50, LIGHT_GRAY, action=new_game)

    # Draw "End Game" button
    draw_button("End Game", 500, 400, 150, 50, LIGHT_GRAY, action=end_game)

    # Wait for user interaction
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                # New game button pressed
                if 300 <= mouse_pos[0] <= 450 and 400 <= mouse_pos[1] <= 450:
                    new_game()
                    return
                # Quit game button pressed
                elif 500 <= mouse_pos[0] <= 650 and 400 <= mouse_pos[1] <= 450:
                    end_game()
                    return

        pygame.display.flip()


def main():
    global num_ships, player1_ships, player2_ships
    global game_running, restart_game

    game_running = True
    restart_game = False

    while game_running:
        if restart_game:
            # Reset game state for a new game
            num_ships = 0
            player1_ships = None
            player2_ships = None
            restart_game = False
            continue  # Go back to the start of the loop

        start_screen()
        # Initialize hits grids for each player
        player1_hits = [[None] * 10 for _ in range(10)]
        player2_hits = [[None] * 10 for _ in range(10)]

        # Player 1 ship placement
        placement_screen(1)
        pass_screen(2)

        # Player 2 ship placement
        placement_screen(2)
        pass_screen(1)

        # Start the battle
        winner = 0
        while winner == 0:
            winner = battle_screen(1, player2_ships, player1_hits, player1_ships, player1_ships_deep, player2_ships_deep)  # Player 1 attacks Player 2
            if winner:
                break
            pass_screen(2)

            winner = battle_screen(2, player1_ships, player2_hits, player2_ships, player2_ships_deep, player1_ships_deep)  # Player 2 attacks Player 1
            if winner:
                break
            pass_screen(1)

        # Display winner and wait for user action
        winner_screen(winner)

        if not game_running:
            break


# Run the main game loop
if __name__ == "__main__":
    main()
