import arcade
import random

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Batalla Naval"

GRID_SIZE = 10
CELL_SIZE = 40
MARGIN = 100

# Colores
BLUE = arcade.color.DARK_BLUE
WHITE = arcade.color.WHITE
RED = arcade.color.RED
GREEN = arcade.color.GREEN
GRAY = arcade.color.GRAY
LIGHT_BLUE = arcade.color.LIGHT_BLUE

SHIPS = [4, 3, 2]  # Tamaños de los barcos: uno de 4, uno de 3 y uno de 2

class ImprovedComputerAI:
    def __init__(self, grid_size):
        self.grid_size = grid_size
        self.last_hit = None
        self.hit_streak = []
        self.direction = None
        self.tried_directions = set()

    def get_attack_coordinates(self, player_grid):
        if self.last_hit:
            return self.smart_attack(player_grid)
        else:
            return self.random_attack(player_grid)

    def smart_attack(self, player_grid):
        if not self.direction:
            return self.choose_direction(player_grid)
        
        next_coord = self.get_next_coordinate()
        if self.is_valid_coordinate(next_coord) and player_grid[next_coord[1]][next_coord[0]] == 0:
            return next_coord
        else:
            self.direction = None
            self.tried_directions = set()
            return self.choose_direction(player_grid)

    def choose_direction(self, player_grid):
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        for dx, dy in directions:
            if (dx, dy) not in self.tried_directions:
                next_x = self.last_hit[0] + dx
                next_y = self.last_hit[1] + dy
                if self.is_valid_coordinate((next_x, next_y)) and player_grid[next_y][next_x] == 0:
                    self.direction = (dx, dy)
                    self.tried_directions.add((dx, dy))
                    return next_x, next_y
        
        self.last_hit = None
        self.hit_streak = []
        self.direction = None
        self.tried_directions = set()
        return self.random_attack(player_grid)

    def get_next_coordinate(self):
        return (self.last_hit[0] + self.direction[0], self.last_hit[1] + self.direction[1])

    def random_attack(self, player_grid):
        while True:
            x = random.randint(0, self.grid_size - 1)
            y = random.randint(0, self.grid_size - 1)
            if player_grid[y][x] == 0:  # Not attacked yet
                return x, y

    def is_valid_coordinate(self, coord):
        x, y = coord
        return 0 <= x < self.grid_size and 0 <= y < self.grid_size

    def update(self, x, y, hit):
        if hit:
            if not self.last_hit:
                self.last_hit = (x, y)
            self.hit_streak.append((x, y))
        else:
            if self.direction:
                self.direction = None
            if not self.hit_streak:
                self.last_hit = None

class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.background = arcade.load_texture("background.jpg")
        
    def on_show(self):
        arcade.set_background_color(arcade.color.WHITE)

    def on_draw(self):
        self.clear()
        arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.background)
        arcade.draw_text("Batalla Naval", SCREEN_WIDTH/2, SCREEN_HEIGHT - 100,
                         arcade.color.WHITE, font_size=50, anchor_x="center")
        arcade.draw_text("Clic para comenzar", SCREEN_WIDTH/2, SCREEN_HEIGHT/2,
                         arcade.color.WHITE, font_size=20, anchor_x="center")

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        game_view = BatallaNaval()
        game_view.setup()
        self.window.show_view(game_view)

class BatallaNaval(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(BLUE)
        self.player_name = "Jugador"
        self.reset_game()
        
    def setup(self):
        self.shot_sound = arcade.load_sound("shot.wav")
        self.hit_sound = arcade.load_sound("hit.wav")
        self.miss_sound = arcade.load_sound("miss.wav")
        self.victory_sound = arcade.load_sound("victory.wav")
        self.defeat_sound = arcade.load_sound("defeat.wav")
            
    def reset_game(self):
        self.player_grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.computer_grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.player_guess_grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.computer_guess_grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        
        self.current_ship_index = 0
        self.current_ship_size = SHIPS[self.current_ship_index]
        self.is_horizontal = True
        self.ghost_ship_position = None
        
        self.game_state = "placing_ships"
        self.message = ""
        
        self.computer_ai = ImprovedComputerAI(GRID_SIZE)
        self.score = 0
        self.turns = 0
        
        self.player_ships_remaining = sum(SHIPS)
        self.computer_ships_remaining = sum(SHIPS)
        
    def on_draw(self):
        self.clear()
        self.draw_grids()
        self.draw_ships()
        self.draw_guesses()
        if self.game_state == "placing_ships":
            self.draw_ghost_ship()
        self.draw_instructions()
        self.draw_score()
        
        if self.game_state == "game_over":
            self.draw_game_over()
            
    def draw_grids(self):
        vertical_offset = (SCREEN_HEIGHT - (GRID_SIZE * CELL_SIZE)) // 2
        
        for row in range(GRID_SIZE):
            for column in range(GRID_SIZE):
                # Jugador
                x = MARGIN + column * CELL_SIZE + CELL_SIZE // 2
                y = vertical_offset + row * CELL_SIZE + CELL_SIZE // 2
                arcade.draw_rectangle_outline(x, y, CELL_SIZE, CELL_SIZE, WHITE, 2)
                
                # Computadora
                x = SCREEN_WIDTH - MARGIN - (GRID_SIZE - column) * CELL_SIZE + CELL_SIZE // 2
                y = vertical_offset + row * CELL_SIZE + CELL_SIZE // 2
                arcade.draw_rectangle_outline(x, y, CELL_SIZE, CELL_SIZE, WHITE, 2)
        
        arcade.draw_text("Tu Flota", MARGIN, SCREEN_HEIGHT - MARGIN // 2, 
                         WHITE, 24, anchor_x="left", anchor_y="center")
        arcade.draw_text("Flota Enemiga", SCREEN_WIDTH - MARGIN, SCREEN_HEIGHT - MARGIN // 2, 
                         WHITE, 24, anchor_x="right", anchor_y="center")

    def draw_ships(self):
        vertical_offset = (SCREEN_HEIGHT - (GRID_SIZE * CELL_SIZE)) // 2
        for row in range(GRID_SIZE):
            for column in range(GRID_SIZE):
                x = MARGIN + column * CELL_SIZE + CELL_SIZE // 2
                y = vertical_offset + row * CELL_SIZE + CELL_SIZE // 2
                if self.player_grid[row][column] == 1:
                    arcade.draw_rectangle_filled(x, y, CELL_SIZE - 2, CELL_SIZE - 2, GRAY)
                elif self.player_grid[row][column] == 2:  # Barco impactado
                    arcade.draw_rectangle_filled(x, y, CELL_SIZE - 2, CELL_SIZE - 2, RED)
                elif self.player_grid[row][column] == 3:  # Fallo de la computadora
                    arcade.draw_circle_filled(x, y, CELL_SIZE // 4, LIGHT_BLUE)
                    
    def draw_ghost_ship(self):
        if self.ghost_ship_position and self.game_state == "placing_ships":
            x, y = self.ghost_ship_position
            vertical_offset = (SCREEN_HEIGHT - (GRID_SIZE * CELL_SIZE)) // 2
            color = GREEN if self.can_place_ship(x, y) else RED
            for i in range(self.current_ship_size):
                if self.is_horizontal:
                    draw_x = MARGIN + (x + i) * CELL_SIZE + CELL_SIZE // 2
                    draw_y = vertical_offset + y * CELL_SIZE + CELL_SIZE // 2
                else:
                    draw_x = MARGIN + x * CELL_SIZE + CELL_SIZE // 2
                    draw_y = vertical_offset + (y + i) * CELL_SIZE + CELL_SIZE // 2
                if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
                    arcade.draw_rectangle_outline(draw_x, draw_y, CELL_SIZE, CELL_SIZE, color, 3)

    def draw_guesses(self):
        vertical_offset = (SCREEN_HEIGHT - (GRID_SIZE * CELL_SIZE)) // 2
        for row in range(GRID_SIZE):
            for column in range(GRID_SIZE):
                x = SCREEN_WIDTH - MARGIN - (GRID_SIZE - column) * CELL_SIZE + CELL_SIZE // 2
                y = vertical_offset + row * CELL_SIZE + CELL_SIZE // 2
                if self.player_guess_grid[row][column] == 1:  # Fallo
                    arcade.draw_circle_filled(x, y, CELL_SIZE // 4, LIGHT_BLUE)
                elif self.player_guess_grid[row][column] == 2:  # Acierto
                    arcade.draw_circle_filled(x, y, CELL_SIZE // 4, RED)

    def draw_game_over(self):
        overlay = arcade.create_rectangle_filled(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                                                 SCREEN_WIDTH, SCREEN_HEIGHT, arcade.color.BLACK + (200,))
        overlay.draw()
        arcade.draw_text(self.message, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50,
                         arcade.color.WHITE, 36, anchor_x="center")
        arcade.draw_text(f"Puntuación final: {self.score}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                         arcade.color.WHITE, 24, anchor_x="center")
        arcade.draw_text("Presiona R para reiniciar o Q para salir", 
                         SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50,
                         arcade.color.WHITE, 24, anchor_x="center")

    def draw_instructions(self):
        if self.game_state == "placing_ships":
            if self.current_ship_index < len(SHIPS):
                instructions = f"Coloca tu barco de tamaño {self.current_ship_size}. " \
                               f"Presiona ESPACIO para rotar. " \
                               f"Clic para colocar. " \
                               f"Barcos restantes: {len(SHIPS) - self.current_ship_index}"
            else:
                instructions = "Todos los barcos colocados. ¡Listo para jugar!"
        elif self.game_state == "player_turn":
            instructions = "Tu turno. Haz clic en el tablero enemigo para atacar."
        elif self.game_state == "computer_turn":
            instructions = "Turno de la computadora. Espera..."
        else:
            instructions = self.message
        
        arcade.draw_text(instructions, SCREEN_WIDTH // 2, 20, WHITE, 16, anchor_x="center")

    def draw_score(self):
        arcade.draw_text(f"Puntuación: {self.score}", 10, SCREEN_HEIGHT - 30, WHITE, 14)
        arcade.draw_text(f"Turnos: {self.turns}", 10, SCREEN_HEIGHT - 50, WHITE, 14)

    def can_place_ship(self, x, y):
        if self.is_horizontal:
            if x + self.current_ship_size > GRID_SIZE:
                return False
            return all(self.player_grid[y][x+i] == 0 for i in range(self.current_ship_size))
        else:
            if y + self.current_ship_size > GRID_SIZE:
                return False
            return all(self.player_grid[y+i][x] == 0 for i in range(self.current_ship_size))

    def place_ship(self, x, y):
        if self.can_place_ship(x, y):
            for i in range(self.current_ship_size):
                if self.is_horizontal:
                    self.player_grid[y][x+i] = 1
                else:
                    self.player_grid[y+i][x] = 1
            self.current_ship_index += 1
            if self.current_ship_index < len(SHIPS):
                self.current_ship_size = SHIPS[self.current_ship_index]
            else:
                print("Todos los barcos colocados")
                self.place_computer_ships()
                self.game_state = "player_turn"

    def place_computer_ships(self):
        for ship_size in SHIPS:
            while True:
                x = random.randint(0, GRID_SIZE - 1)
                y = random.randint(0, GRID_SIZE - 1)
                is_horizontal = random.choice([True, False])
                if self.can_place_computer_ship(x, y, ship_size, is_horizontal):
                    self.place_computer_ship(x, y, ship_size, is_horizontal)
                    break

    def can_place_computer_ship(self, x, y, ship_size, is_horizontal):
        if is_horizontal:
            if x + ship_size > GRID_SIZE:
                return False
            return all(self.computer_grid[y][x+i] == 0 for i in range(ship_size))
        else:
            if y + ship_size > GRID_SIZE:
                return False
            return all(self.computer_grid[y+i][x] == 0 for i in range(ship_size))

    def place_computer_ship(self, x, y, ship_size, is_horizontal):
        for i in range(ship_size):
            if is_horizontal:
                self.computer_grid[y][x+i] = 1
            else:
                self.computer_grid[y+i][x] = 1

    def on_mouse_motion(self, x, y, dx, dy):
        if self.game_state == "placing_ships":
            grid_x = (x - MARGIN) // CELL_SIZE
            grid_y = (y - (SCREEN_HEIGHT - (GRID_SIZE * CELL_SIZE)) // 2) // CELL_SIZE
            if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
                self.ghost_ship_position = (grid_x, grid_y)
            else:
                self.ghost_ship_position = None

    def on_mouse_press(self, x, y, button, modifiers):
        if self.game_state == "placing_ships":
            if self.ghost_ship_position:
                grid_x, grid_y = self.ghost_ship_position
                self.place_ship(grid_x, grid_y)
        elif self.game_state == "player_turn":
            grid_x = (x - (SCREEN_WIDTH - MARGIN - GRID_SIZE * CELL_SIZE)) // CELL_SIZE
            grid_y = (y - (SCREEN_HEIGHT - (GRID_SIZE * CELL_SIZE)) // 2) // CELL_SIZE
            if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
                if self.player_guess_grid[grid_y][grid_x] == 0:  # No se ha disparado aquí antes
                    arcade.play_sound(self.shot_sound)
                    self.turns += 1
                    if self.computer_grid[grid_y][grid_x] == 1:  # Hay un barco
                        self.player_guess_grid[grid_y][grid_x] = 2  # Acierto
                        self.message = "¡Impacto!"
                        self.score += 100
                        arcade.play_sound(self.hit_sound)
                        self.computer_ships_remaining -= 1
                    else:
                        self.player_guess_grid[grid_y][grid_x] = 1  # Fallo
                        self.message = "Agua"
                        self.score -= 10
                        arcade.play_sound(self.miss_sound)
                    if not self.check_game_over():
                        self.game_state = "computer_turn"
                        self.computer_turn()

    def on_key_press(self, key, modifiers):
        if self.game_state == "placing_ships":
            if key == arcade.key.SPACE:
                self.is_horizontal = not self.is_horizontal
        elif self.game_state == "game_over":
            if key == arcade.key.R:
                self.reset_game()
            elif key == arcade.key.Q:
                arcade.close_window()

    def computer_turn(self):
        x, y = self.computer_ai.get_attack_coordinates(self.player_grid)
        arcade.play_sound(self.shot_sound)
        if self.player_grid[y][x] == 1:  # Hay un barco del jugador
            self.player_grid[y][x] = 2  # Marcar como golpeado
            self.message = "La computadora ha acertado"
            arcade.play_sound(self.hit_sound)
            self.computer_ai.update(x, y, True)
            self.player_ships_remaining -= 1
        elif self.player_grid[y][x] == 0:  # Agua
            self.player_grid[y][x] = 3  # Marcar como fallo
            self.message = "La computadora ha fallado"
            arcade.play_sound(self.miss_sound)
            self.computer_ai.update(x, y, False)
        self.check_game_over()
        if self.game_state != "game_over":
            self.game_state = "player_turn"

    def check_game_over(self):
        if self.player_ships_remaining == 0:
            self.game_state = "game_over"
            self.message = f"¡{self.player_name}, has perdido!"
            arcade.play_sound(self.defeat_sound)
            return True
        elif self.computer_ships_remaining == 0:
            self.game_state = "game_over"
            self.message = f"¡Felicidades {self.player_name}! ¡Has ganado!"
            self.score += 1000  # Bonus por ganar
            arcade.play_sound(self.victory_sound)
            return True
        
        if self.game_state == "game_over":
            self.score -= self.turns  # Penalización por número de turnos
            print(self.message)  # Para debug
        return False

    def draw_game_over(self):
        overlay = arcade.create_rectangle_filled(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                                                 SCREEN_WIDTH, SCREEN_HEIGHT, arcade.color.BLACK + (200,))
        overlay.draw()
        arcade.draw_text(self.message, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50,
                         arcade.color.WHITE, 36, anchor_x="center")
        arcade.draw_text(f"Puntuación final: {self.score}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                         arcade.color.WHITE, 24, anchor_x="center")
        arcade.draw_text("Presiona R para reiniciar o Q para salir", 
                         SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50,
                         arcade.color.WHITE, 24, anchor_x="center")

    def on_draw(self):
        self.clear()
        self.draw_grids()
        self.draw_ships()
        self.draw_guesses()
        if self.game_state == "placing_ships":
            self.draw_ghost_ship()
        self.draw_instructions()
        self.draw_score()
        
        if self.game_state == "game_over":
            self.draw_game_over()
            
def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game_view = BatallaNaval()
    game_view.setup()
    window.show_view(game_view)
    arcade.run()

if __name__ == "__main__":
    main()
            