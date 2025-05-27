import pygame
import random
import sys
import time
import math
import os

# Initialize pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Memory Card Game")

# AWS corporate colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
AWS_ORANGE = (255, 153, 0)      # AWS Orange
AWS_BLUE = (35, 47, 62)         # AWS Dark Blue
AWS_LIGHT_BLUE = (68, 138, 255) # AWS Light Blue
AWS_DARK_ORANGE = (232, 114, 0) # AWS Dark Orange
AWS_TEAL = (19, 165, 173)       # AWS Teal
AWS_LIGHT_GRAY = (242, 243, 243)# AWS Light Gray
AWS_DARK_GRAY = (84, 91, 100)   # AWS Dark Gray
SUCCESS_GREEN = (0, 200, 0)     # Green color for success mark
RED = (255, 0, 0)               # Red color for Ultra Hard Mode text

# Player territory colors - using AWS corporate colors
PLAYER1_TERRITORY = (255, 240, 220)  # Light orange for Player 1
PLAYER2_TERRITORY = (255, 240, 220)  # Light orange for Player 2
PLAY_AREA_COLOR = (255, 255, 255)    # White for play area

# Card settings - making them square
CARD_SIZE = 80  # Square cards
CARD_MARGIN = 15
CARD_BACK_COLOR = AWS_BLUE

# Card symbols (more types for different difficulty levels)
CARD_TYPES = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M"]
CARD_COLORS = [
    AWS_BLUE, AWS_ORANGE, AWS_TEAL, AWS_DARK_ORANGE, AWS_DARK_GRAY,
    AWS_LIGHT_BLUE, AWS_BLUE, AWS_ORANGE, AWS_TEAL, AWS_DARK_ORANGE,
    AWS_DARK_GRAY, AWS_LIGHT_BLUE, AWS_BLUE
]

# Player settings
PLAYER_1 = 0
PLAYER_2 = 1
player_names = ["Player 1", "Player 2"]
player_colors = [AWS_ORANGE, AWS_ORANGE]  # Both players use orange color
player_scores = [0, 0]
current_player = PLAYER_1

# Game settings
DIFFICULTY_EASY = 0
DIFFICULTY_NORMAL = 1
DIFFICULTY_HARD = 2
DIFFICULTY_ULTRA = 3
difficulty_names = ["Easy", "Normal", "Hard", "Ultra Hard"]
current_difficulty = DIFFICULTY_EASY

# Difficulty settings
difficulty_settings = {
    DIFFICULTY_EASY: {"rows": 2, "cols": 5, "pairs": 5, "time_limit": None, "display_time": 10000, "rotate": False, "custom_layout": False},
    DIFFICULTY_NORMAL: {"rows": 3, "cols": 6, "pairs": 9, "time_limit": None, "display_time": 10000, "rotate": False, "custom_layout": False},
    DIFFICULTY_HARD: {"rows": 5, "cols": 6, "pairs": 13, "time_limit": 15000, "display_time": 10000, "rotate": False, "custom_layout": True},
    DIFFICULTY_ULTRA: {"rows": 5, "cols": 6, "pairs": 13, "time_limit": 15000, "display_time": 5000, "rotate": True, "custom_layout": True}
}

# Game states
STATE_MENU = "menu"
STATE_SHOW_ALL = "show_all"
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"
game_state = STATE_MENU

# Matched cards for each player
player_matched_cards = [[], []]

# Turn timer for hard mode
turn_timer = 0
turn_time_limit = 0

# Load card images
def load_card_images():
    # Load card back image
    card_back_path = './images/card_back.png'
    card_back_img = pygame.image.load(card_back_path)
    
    # Get all PNG files from the images directory (excluding card_back.png)
    image_dir = './images'
    hard_mode_dir = './images/hard_mode'
    
    # Regular card images
    card_images = []
    for file in os.listdir(image_dir):
        if file.lower().endswith('.png') and file != 'card_back.png' and not os.path.isdir(os.path.join(image_dir, file)):
            img_path = os.path.join(image_dir, file)
            img = pygame.image.load(img_path)
            card_images.append((file.split('.')[0], img))  # Store name without extension and image
    
    # Hard mode card images
    hard_mode_images = []
    if os.path.exists(hard_mode_dir):
        for file in os.listdir(hard_mode_dir):
            if file.lower().endswith('.png') and not file.startswith('.'):
                img_path = os.path.join(hard_mode_dir, file)
                img = pygame.image.load(img_path)
                hard_mode_images.append((file.split('.')[0], img))  # Store name without extension and image
    
    return card_back_img, card_images, hard_mode_images

# Load images at the start
CARD_BACK_IMG, CARD_IMAGES, HARD_MODE_IMAGES = load_card_images()

# Card class
class Card:
    def __init__(self, card_type, x, y, image):
        self.card_type = card_type
        self.x = x
        self.y = y
        self.width = CARD_SIZE
        self.height = CARD_SIZE
        self.is_flipped = False
        self.is_matched = False
        self.matched_by = None  # Which player matched this card
        self.rect = pygame.Rect(x, y, CARD_SIZE, CARD_SIZE)
        self.image = image  # Store the card's front image
        self.rotation = 0  # Rotation angle in degrees
        self.show_success_mark = False  # Flag to show success mark
        self.success_mark_timer = 0  # Timer for success mark display
        
    def draw(self):
        if self.is_matched and not self.show_success_mark:
            return
            
        if self.is_flipped:
            # Front side - draw the card image
            # Create a white background
            pygame.draw.rect(screen, WHITE, self.rect)
            
            # Scale the image to fit the card size
            scaled_img = pygame.transform.scale(self.image, (self.width, self.height))
            
            # Apply rotation if needed (for Ultra Hard mode)
            if self.rotation != 0:
                scaled_img = pygame.transform.rotate(scaled_img, self.rotation)
                # Get the rect of the rotated image to center it
                rot_rect = scaled_img.get_rect(center=self.rect.center)
                screen.blit(scaled_img, rot_rect)
            else:
                screen.blit(scaled_img, self.rect)
            
            # Draw border
            pygame.draw.rect(screen, BLACK, self.rect, 2)
            
            # Draw success mark if needed
            if self.show_success_mark:
                # Draw a green circle (success mark)
                circle_radius = min(self.width, self.height) // 3
                pygame.draw.circle(screen, SUCCESS_GREEN, self.rect.center, circle_radius, 5)
                
                # Draw a checkmark inside the circle
                check_size = circle_radius * 0.8
                start_x = self.rect.centerx - check_size * 0.5
                mid_x = self.rect.centerx - check_size * 0.1
                end_x = self.rect.centerx + check_size * 0.5
                start_y = self.rect.centery
                mid_y = self.rect.centery + check_size * 0.5
                end_y = self.rect.centery - check_size * 0.3
                
                pygame.draw.line(screen, SUCCESS_GREEN, (start_x, start_y), (mid_x, mid_y), 5)
                pygame.draw.line(screen, SUCCESS_GREEN, (mid_x, mid_y), (end_x, end_y), 5)
                
        else:
            # Back side - use the card back image
            scaled_back = pygame.transform.scale(CARD_BACK_IMG, (self.width, self.height))
            screen.blit(scaled_back, self.rect)
            pygame.draw.rect(screen, BLACK, self.rect, 2)
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos) and not self.is_flipped and not self.is_matched
        
    def update(self, dt):
        # Update success mark timer if active
        if self.show_success_mark:
            self.success_mark_timer += dt
            if self.success_mark_timer >= 1000:  # 1 second
                self.show_success_mark = False

# Initialize game with selected difficulty
def init_game(difficulty):
    global cards, selected_cards, current_player, player_scores, game_state, player_matched_cards, show_timer, turn_timer, turn_time_limit
    
    # Set difficulty settings
    rows = difficulty_settings[difficulty]["rows"]
    cols = difficulty_settings[difficulty]["cols"]
    pairs = difficulty_settings[difficulty]["pairs"]
    turn_time_limit = difficulty_settings[difficulty]["time_limit"]
    custom_layout = difficulty_settings[difficulty].get("custom_layout", False)
    rotate_cards = difficulty_settings[difficulty].get("rotate", False)
    
    # Create cards based on difficulty
    cards = []
    
    # Select random card images for this game
    if difficulty == DIFFICULTY_ULTRA:
        # Use hard mode images for Ultra Hard difficulty
        available_images = list(HARD_MODE_IMAGES)
    else:
        # Use regular images for other difficulties
        available_images = list(CARD_IMAGES)
    
    random.shuffle(available_images)
    selected_images = available_images[:pairs]
    
    # Create pairs of cards
    card_pairs = []
    for card_type, img in selected_images:
        card_pairs.extend([(card_type, img), (card_type, img)])  # Add each card twice
    
    random.shuffle(card_pairs)  # Shuffle the pairs
    
    # Calculate play area dimensions
    play_area_width = SCREEN_WIDTH * 0.6  # 60% of screen width
    play_area_left = (SCREEN_WIDTH - play_area_width) / 2
    
    # Adjust card size based on grid
    card_width = min(70, (play_area_width - (cols + 1) * CARD_MARGIN) / cols)
    card_height = card_width  # Keep cards square
    
    positions = []
    
    if custom_layout and (difficulty == DIFFICULTY_HARD or difficulty == DIFFICULTY_ULTRA):
        # Custom layout for Hard and Ultra Hard modes:
        # Row 1: 4 cards
        # Row 2: 6 cards
        # Row 3: 6 cards
        # Row 4: 6 cards
        # Row 5: 4 cards
        
        # Calculate total height and width
        total_height = 5 * (card_height + CARD_MARGIN) - CARD_MARGIN
        max_width = 6 * (card_width + CARD_MARGIN) - CARD_MARGIN
        
        # Calculate starting positions
        start_y = (SCREEN_HEIGHT - total_height) / 2
        
        # Row 1: 4 cards (centered)
        row1_width = 4 * (card_width + CARD_MARGIN) - CARD_MARGIN
        row1_start_x = play_area_left + (play_area_width - row1_width) / 2
        for col in range(4):
            x = row1_start_x + col * (card_width + CARD_MARGIN)
            y = start_y
            positions.append((x, y))
        
        # Row 2: 6 cards
        row2_start_x = play_area_left + (play_area_width - max_width) / 2
        for col in range(6):
            x = row2_start_x + col * (card_width + CARD_MARGIN)
            y = start_y + 1 * (card_height + CARD_MARGIN)
            positions.append((x, y))
        
        # Row 3: 6 cards
        row3_start_x = row2_start_x
        for col in range(6):
            x = row3_start_x + col * (card_width + CARD_MARGIN)
            y = start_y + 2 * (card_height + CARD_MARGIN)
            positions.append((x, y))
        
        # Row 4: 6 cards
        row4_start_x = row2_start_x
        for col in range(6):
            x = row4_start_x + col * (card_width + CARD_MARGIN)
            y = start_y + 3 * (card_height + CARD_MARGIN)
            positions.append((x, y))
        
        # Row 5: 4 cards (centered)
        row5_width = 4 * (card_width + CARD_MARGIN) - CARD_MARGIN
        row5_start_x = play_area_left + (play_area_width - row5_width) / 2
        for col in range(4):
            x = row5_start_x + col * (card_width + CARD_MARGIN)
            y = start_y + 4 * (card_height + CARD_MARGIN)
            positions.append((x, y))
    else:
        # Standard grid layout
        # Calculate starting position to center the cards in the play area
        total_width = cols * (card_width + CARD_MARGIN) - CARD_MARGIN
        total_height = rows * (card_height + CARD_MARGIN) - CARD_MARGIN
        
        start_x = play_area_left + (play_area_width - total_width) / 2
        start_y = (SCREEN_HEIGHT - total_height) / 2
        
        for row in range(rows):
            for col in range(cols):
                x = start_x + col * (card_width + CARD_MARGIN)
                y = start_y + row * (card_height + CARD_MARGIN)
                positions.append((x, y))
    
    # Create cards with positions and images
    for i, (card_type, img) in enumerate(card_pairs):
        if i < len(positions):  # Make sure we don't exceed available positions
            x, y = positions[i]
            card = Card(card_type, x, y, img)
            card.width = card_width
            card.height = card_height
            card.rect = pygame.Rect(x, y, card_width, card_height)
            
            # Apply random rotation for Ultra Hard mode
            if rotate_cards:
                # Random rotation: 0, 90, 180, or 270 degrees
                card.rotation = random.choice([0, 90, 180, 270])
            
            cards.append(card)
    
    selected_cards = []
    current_player = PLAYER_1
    player_scores = [0, 0]
    player_matched_cards = [[], []]
    game_state = STATE_SHOW_ALL  # Initially show all cards
    show_timer = 0  # Reset timer for each new game
    turn_timer = 0  # Reset turn timer
    
    # Initially flip all cards face up
    for card in cards:
        card.is_flipped = True

# Draw main menu
def draw_menu():
    screen.fill(WHITE)
    
    # Title
    font = pygame.font.SysFont(None, 72)
    title = font.render("Memory Card Game", True, AWS_BLUE)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80))
    
    # Subtitle
    font = pygame.font.SysFont(None, 36)
    subtitle = font.render("Select Difficulty", True, BLACK)
    screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 160))
    
    # Difficulty buttons
    button_width = 200
    button_height = 60
    button_margin = 30
    button_y = 250
    
    difficulty_rects = []
    
    for i, name in enumerate(difficulty_names):
        button_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - button_width // 2,
            button_y + i * (button_height + button_margin),
            button_width,
            button_height
        )
        difficulty_rects.append(button_rect)
        
        # Draw button
        pygame.draw.rect(screen, AWS_LIGHT_GRAY, button_rect)
        pygame.draw.rect(screen, BLACK, button_rect, 2)
        
        # Draw text
        font = pygame.font.SysFont(None, 36)
        text = font.render(name, True, BLACK)
        screen.blit(text, (button_rect.centerx - text.get_width() // 2, 
                          button_rect.centery - text.get_height() // 2))
    
    # Quit button
    quit_font = pygame.font.SysFont(None, 24)
    quit_text = quit_font.render("Quit", True, BLACK)
    quit_rect = pygame.Rect(SCREEN_WIDTH - 70, 10, 60, 30)
    pygame.draw.rect(screen, AWS_LIGHT_GRAY, quit_rect)
    pygame.draw.rect(screen, BLACK, quit_rect, 2)
    screen.blit(quit_text, (quit_rect.centerx - quit_text.get_width() // 2, 
                           quit_rect.centery - quit_text.get_height() // 2))
    
    pygame.display.flip()
    return difficulty_rects

# Draw game state
def draw_game():
    screen.fill(WHITE)
    
    # Calculate play area dimensions
    play_area_width = SCREEN_WIDTH * 0.6  # 60% of screen width
    play_area_left = (SCREEN_WIDTH - play_area_width) / 2
    territory_width = (SCREEN_WIDTH - play_area_width) / 2  # Each territory gets half of remaining space
    
    # Draw player territories
    p1_territory = pygame.Rect(0, 0, territory_width, SCREEN_HEIGHT)
    p2_territory = pygame.Rect(SCREEN_WIDTH - territory_width, 0, territory_width, SCREEN_HEIGHT)
    pygame.draw.rect(screen, PLAYER1_TERRITORY, p1_territory)
    pygame.draw.rect(screen, PLAYER2_TERRITORY, p2_territory)
    
    # Draw play area
    play_area = pygame.Rect(territory_width, 0, play_area_width, SCREEN_HEIGHT)
    pygame.draw.rect(screen, PLAY_AREA_COLOR, play_area)
    
    # Title
    font = pygame.font.SysFont(None, 36)
    title = font.render(f"Memory Card Game - {difficulty_names[current_difficulty]}", True, BLACK)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 10))
    
    # Quit button
    quit_font = pygame.font.SysFont(None, 24)
    quit_text = quit_font.render("Quit", True, BLACK)
    quit_rect = pygame.Rect(SCREEN_WIDTH - 70, 10, 60, 30)
    pygame.draw.rect(screen, AWS_LIGHT_GRAY, quit_rect)
    pygame.draw.rect(screen, BLACK, quit_rect, 2)
    screen.blit(quit_text, (quit_rect.centerx - quit_text.get_width() // 2, 
                           quit_rect.centery - quit_text.get_height() // 2))
    
    # Menu button
    menu_font = pygame.font.SysFont(None, 24)
    menu_text = menu_font.render("Menu", True, BLACK)
    menu_rect = pygame.Rect(SCREEN_WIDTH - 140, 10, 60, 30)
    pygame.draw.rect(screen, AWS_LIGHT_GRAY, menu_rect)
    pygame.draw.rect(screen, BLACK, menu_rect, 2)
    screen.blit(menu_text, (menu_rect.centerx - menu_text.get_width() // 2, 
                           menu_rect.centery - menu_text.get_height() // 2))
    
    # Player information
    for i, name in enumerate(player_names):
        font = pygame.font.SysFont(None, 36)
        
        # Player name
        text = font.render(name, True, player_colors[i])
        x_pos = 20 if i == PLAYER_1 else SCREEN_WIDTH - 20 - text.get_width()
        screen.blit(text, (x_pos, 60))
        
        # Underline current player
        if i == current_player:
            line_y = 60 + text.get_height() + 2
            line_width = text.get_width()
            pygame.draw.line(screen, player_colors[i], 
                            (x_pos, line_y), 
                            (x_pos + line_width, line_y), 
                            3)
        
        # Score
        score_text = font.render(f"Score: {player_scores[i]}", True, BLACK)
        x_pos = 20 if i == PLAYER_1 else SCREEN_WIDTH - 20 - score_text.get_width()
        screen.blit(score_text, (x_pos, 100))
    
    # Draw matched cards in player territories
    for player in range(2):
        for idx, card_info in enumerate(player_matched_cards[player]):
            # Calculate position for 2-column layout
            col = idx % 2  # 0 for left column, 1 for right column
            row = idx // 2  # Row index
            
            # Card size is 40% of original
            card_size = CARD_SIZE * 0.4
            card_spacing = 10
            
            if player == PLAYER_1:
                # Left territory
                base_x = 20  # Left margin
                if col == 0:
                    card_x = base_x
                else:
                    card_x = base_x + card_size + card_spacing
            else:
                # Right territory
                base_x = SCREEN_WIDTH - territory_width + 20  # Right territory left margin
                if col == 0:
                    card_x = base_x
                else:
                    card_x = base_x + card_size + card_spacing
            
            card_y = 150 + row * (card_size + card_spacing)
            
            # Draw card at 40% of original size
            card_rect = pygame.Rect(card_x, card_y, card_size, card_size)
            pygame.draw.rect(screen, WHITE, card_rect)
            pygame.draw.rect(screen, BLACK, card_rect, 2)
            
            # Find the image for this card type
            card_type, card_img = None, None
            
            # Check in regular images first
            for c_type, img in CARD_IMAGES:
                if c_type == card_info:
                    card_type, card_img = c_type, img
                    break
            
            # If not found, check in hard mode images
            if not card_img:
                for c_type, img in HARD_MODE_IMAGES:
                    if c_type == card_info:
                        card_type, card_img = c_type, img
                        break
            
            if card_img:
                # Scale and draw the image
                scaled_img = pygame.transform.scale(card_img, (card_size, card_size))
                screen.blit(scaled_img, card_rect)
    
    # Draw cards in play area
    for card in cards:
        card.draw()
    
    # Draw turn timer for hard mode
    if (current_difficulty == DIFFICULTY_HARD or current_difficulty == DIFFICULTY_ULTRA) and game_state == STATE_PLAYING:
        time_left = (turn_time_limit - turn_timer) // 1000
        if time_left < 0:
            time_left = 0
        
        timer_font = pygame.font.SysFont(None, 36)
        timer_text = timer_font.render(f"Time: {time_left}s", True, BLACK)
        screen.blit(timer_text, (SCREEN_WIDTH // 2 - timer_text.get_width() // 2, 50))
    
    # Draw Ultra Hard mode indicator
    if current_difficulty == DIFFICULTY_ULTRA and (game_state == STATE_PLAYING or game_state == STATE_SHOW_ALL):
        rot_font = pygame.font.SysFont(None, 30)
        rot_text = rot_font.render("Ultra Hard Mode - Cards are rotated!", True, RED)
        screen.blit(rot_text, (SCREEN_WIDTH // 2 - rot_text.get_width() // 2, 80))
    
    # Game over message
    if game_state == STATE_GAME_OVER:
        font = pygame.font.SysFont(None, 72)
        if player_scores[0] > player_scores[1]:
            result = "Player 1 Wins!"
            color = player_colors[0]
        elif player_scores[1] > player_scores[0]:
            result = "Player 2 Wins!"
            color = player_colors[1]
        else:
            result = "It's a Tie!"
            color = BLACK
            
        text = font.render(result, True, color)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        
        # Semi-transparent background
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        s.fill((255, 255, 255, 200))
        screen.blit(s, (0, 0))
        
        screen.blit(text, text_rect)
        
        # Restart button
        restart_font = pygame.font.SysFont(None, 36)
        restart_text = restart_font.render("Play Again", True, BLACK)
        restart_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50, 140, 50)
        pygame.draw.rect(screen, AWS_LIGHT_GRAY, restart_rect)
        pygame.draw.rect(screen, BLACK, restart_rect, 2)
        screen.blit(restart_text, (restart_rect.centerx - restart_text.get_width() // 2, 
                                  restart_rect.centery - restart_text.get_height() // 2))
        
        # Quit button on game over screen
        quit_game_text = restart_font.render("Quit", True, BLACK)
        quit_game_rect = pygame.Rect(SCREEN_WIDTH // 2 + 10, SCREEN_HEIGHT // 2 + 50, 140, 50)
        pygame.draw.rect(screen, AWS_LIGHT_GRAY, quit_game_rect)
        pygame.draw.rect(screen, BLACK, quit_game_rect, 2)
        screen.blit(quit_game_text, (quit_game_rect.centerx - quit_game_text.get_width() // 2, 
                                   quit_game_rect.centery - quit_game_text.get_height() // 2))
    
    # Instruction text
    if game_state == STATE_SHOW_ALL:
        font = pygame.font.SysFont(None, 36)
        text = font.render("Memorize the cards...", True, BLACK)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT - 50))
    elif game_state == STATE_PLAYING:
        font = pygame.font.SysFont(None, 36)
        # Change text color to black
        text = font.render(f"{player_names[current_player]}'s Turn", True, BLACK)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT - 50))
    
    pygame.display.flip()

# Main game loop
def main():
    global selected_cards, current_player, game_state, show_timer, turn_timer, current_difficulty
    
    clock = pygame.time.Clock()
    show_timer = 0
    turn_timer = 0
    game_state = STATE_MENU
    
    running = True
    while running:
        # Get time elapsed since last frame
        dt = clock.get_time()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Menu state
                if game_state == STATE_MENU:
                    # Check for difficulty selection
                    difficulty_rects = draw_menu()
                    for i, rect in enumerate(difficulty_rects):
                        if rect.collidepoint(event.pos):
                            current_difficulty = i
                            init_game(current_difficulty)
                            break
                    
                    # Check for quit button click
                    quit_rect = pygame.Rect(SCREEN_WIDTH - 70, 10, 60, 30)
                    if quit_rect.collidepoint(event.pos):
                        running = False
                        continue
                
                # Game playing states
                else:
                    # Check for quit button click
                    quit_rect = pygame.Rect(SCREEN_WIDTH - 70, 10, 60, 30)
                    if quit_rect.collidepoint(event.pos):
                        running = False
                        continue
                    
                    # Check for menu button click
                    menu_rect = pygame.Rect(SCREEN_WIDTH - 140, 10, 60, 30)
                    if menu_rect.collidepoint(event.pos):
                        game_state = STATE_MENU
                        continue
                    
                    # Game over screen buttons
                    if game_state == STATE_GAME_OVER:
                        # Restart button
                        restart_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50, 140, 50)
                        if restart_rect.collidepoint(event.pos):
                            init_game(current_difficulty)  # Restart with same difficulty
                            continue
                        
                        # Quit button on game over screen
                        quit_game_rect = pygame.Rect(SCREEN_WIDTH // 2 + 10, SCREEN_HEIGHT // 2 + 50, 140, 50)
                        if quit_game_rect.collidepoint(event.pos):
                            running = False
                            continue
                    
                    # Card selection
                    if game_state == STATE_PLAYING:
                        for card in cards:
                            if card.is_clicked(event.pos) and len(selected_cards) < 2:
                                card.is_flipped = True
                                selected_cards.append(card)
                                
                                # When 2 cards are selected
                                if len(selected_cards) == 2:
                                    # Check if they match
                                    if selected_cards[0].card_type == selected_cards[1].card_type:
                                        # If matched, increase player's score
                                        player_scores[current_player] += 2
                                        
                                        # Mark cards as matched
                                        selected_cards[0].is_matched = True
                                        selected_cards[1].is_matched = True
                                        selected_cards[0].matched_by = current_player
                                        selected_cards[1].matched_by = current_player
                                        
                                        # Show success mark on matched cards
                                        selected_cards[0].show_success_mark = True
                                        selected_cards[1].show_success_mark = True
                                        selected_cards[0].success_mark_timer = 0
                                        selected_cards[1].success_mark_timer = 0
                                        
                                        # Add to player's matched cards
                                        player_matched_cards[current_player].append(selected_cards[0].card_type)
                                        
                                        # Check if all cards are matched
                                        all_matched = all(card.is_matched for card in cards)
                                        if all_matched:
                                            game_state = STATE_GAME_OVER
                                    else:
                                        # If not matched, switch players
                                        current_player = 1 - current_player
                                        # Reset turn timer for hard/ultra mode
                                        if current_difficulty == DIFFICULTY_HARD or current_difficulty == DIFFICULTY_ULTRA:
                                            turn_timer = 0
                                    
                                    # Wait a bit before flipping cards back
                                    draw_game()
                                    pygame.display.flip()
                                    pygame.time.delay(1000)
                                    
                                    # Flip cards back if not matched
                                    if not selected_cards[0].is_matched:
                                        selected_cards[0].is_flipped = False
                                        selected_cards[1].is_flipped = False
                                    
                                    selected_cards = []
        
        # Menu state
        if game_state == STATE_MENU:
            draw_menu()
        
        # Game states
        else:
            # Initial card display time
            if game_state == STATE_SHOW_ALL:
                show_timer += dt
                display_time = difficulty_settings[current_difficulty]["display_time"]
                if show_timer >= display_time:  # Display time based on difficulty
                    # Flip cards face down WITHOUT shuffling positions
                    for card in cards:
                        card.is_flipped = False
                    
                    game_state = STATE_PLAYING
                    turn_timer = 0  # Reset turn timer
            
            # Turn timer for hard/ultra mode
            elif game_state == STATE_PLAYING and (current_difficulty == DIFFICULTY_HARD or current_difficulty == DIFFICULTY_ULTRA):
                turn_timer += dt
                if turn_timer >= turn_time_limit:
                    # Time's up, switch players
                    current_player = 1 - current_player
                    turn_timer = 0
                    
                    # Flip any selected cards back
                    for card in selected_cards:
                        card.is_flipped = False
                    selected_cards = []
            
            # Update card success mark timers
            for card in cards:
                card.update(dt)
            
            draw_game()
        
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
