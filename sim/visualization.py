# Pygame visualization for parking lot
import pygame

SLOT_SIZE = 50
SLOT_WIDTH = 80
SLOT_HEIGHT = 40
LANE_WIDTH = 40
ENTRY_ROAD_WIDTH = 100

COLORS = {
    'asphalt': (45, 45, 45),
    'lane_marking': (255, 255, 255),
    'slot_line': (255, 255, 255),
    'car': (0, 100, 200),
    'car_red': (200, 50, 50),
    'car_green': (50, 150, 50),
    'car_yellow': (200, 200, 50),
    'grass': (40, 120, 40),
    'entrance': (200, 200, 200),
    'text': (255, 255, 255),
    'occupied_tint': (255, 100, 100, 100)
}

def get_slot_center(row, col):
    # Calculate position based on realistic parking lot layout
    x = ENTRY_ROAD_WIDTH + col * (SLOT_WIDTH + 10) + SLOT_WIDTH // 2
    y = 60 + row * (SLOT_HEIGHT + LANE_WIDTH) + SLOT_HEIGHT // 2
    return x, y

def get_slot_rect(row, col):
    x = ENTRY_ROAD_WIDTH + col * (SLOT_WIDTH + 10)
    y = 60 + row * (SLOT_HEIGHT + LANE_WIDTH)
    return pygame.Rect(x, y, SLOT_WIDTH, SLOT_HEIGHT)

def draw_parking_space(screen, row, col, is_occupied=False):
    rect = get_slot_rect(row, col)
    
    # Draw parking space outline (white lines)
    pygame.draw.rect(screen, COLORS['slot_line'], rect, 2)
    
    # Add diagonal lines for better visual
    pygame.draw.line(screen, COLORS['slot_line'], 
                    (rect.left, rect.top), 
                    (rect.left + 15, rect.top), 2)
    pygame.draw.line(screen, COLORS['slot_line'], 
                    (rect.right - 15, rect.top), 
                    (rect.right, rect.top), 2)

def draw_lanes(screen, lot):
    # Draw main driving lanes between parking rows
    for r in range(lot.rows + 1):
        y = 60 + r * (SLOT_HEIGHT + LANE_WIDTH) - LANE_WIDTH // 2
        lane_rect = pygame.Rect(ENTRY_ROAD_WIDTH, y, lot.cols * (SLOT_WIDTH + 10), LANE_WIDTH)
        pygame.draw.rect(screen, COLORS['asphalt'], lane_rect)
        
        # Draw lane center line (dashed)
        center_y = y + LANE_WIDTH // 2
        for x in range(ENTRY_ROAD_WIDTH, ENTRY_ROAD_WIDTH + lot.cols * (SLOT_WIDTH + 10), 30):
            pygame.draw.line(screen, COLORS['lane_marking'], 
                           (x, center_y), (x + 15, center_y), 2)

def draw_entry_road(screen, lot):
    # Draw main entry road
    entry_rect = pygame.Rect(0, 0, ENTRY_ROAD_WIDTH, 60 + lot.rows * (SLOT_HEIGHT + LANE_WIDTH))
    pygame.draw.rect(screen, COLORS['asphalt'], entry_rect)
    
    # Draw entry road markings
    for y in range(50, entry_rect.height, 40):
        pygame.draw.line(screen, COLORS['lane_marking'], 
                        (ENTRY_ROAD_WIDTH - 20, y), (ENTRY_ROAD_WIDTH - 20, y + 20), 2)
    
    # Draw entrance/exit markers
    font = pygame.font.SysFont("Arial", 16)
    entrance_text = font.render("ENTRANCE", True, COLORS['text'])
    screen.blit(entrance_text, (10, 10))
    
    exit_text = font.render("EXIT", True, COLORS['text'])
    screen.blit(exit_text, (10, entry_rect.height - 40))

def draw_realistic_car(screen, x, y, parking_duration=None, color=None):
    if color is None:
        import random
        colors = [COLORS['car'], COLORS['car_red'], COLORS['car_green'], COLORS['car_yellow']]
        color = random.choice(colors)
    
    car_width, car_height = 60, 30
    car_rect = pygame.Rect(int(x) - car_width//2, int(y) - car_height//2, car_width, car_height)
    
    # Car body
    pygame.draw.rect(screen, color, car_rect)
    pygame.draw.rect(screen, (0, 0, 0), car_rect, 2)
    
    # Windows (darker rectangle)
    window_rect = pygame.Rect(car_rect.x + 8, car_rect.y + 5, car_width - 16, car_height - 10)
    pygame.draw.rect(screen, (100, 150, 200), window_rect)
    
    # Headlights/taillights
    pygame.draw.circle(screen, (255, 255, 200), (car_rect.right - 5, car_rect.y + 8), 3)
    pygame.draw.circle(screen, (255, 255, 200), (car_rect.right - 5, car_rect.bottom - 8), 3)
    
    # Display parking duration above the car
    if parking_duration is not None:
        font = pygame.font.SysFont("Arial", 14)
        duration_text = font.render(f"{parking_duration:.0f}s", True, (255, 255, 255))
        text_rect = duration_text.get_rect(center=(int(x), int(y) - car_height//2 - 15))
        # Add background for better readability
        bg_rect = text_rect.copy()
        bg_rect.inflate(6, 2)
        pygame.draw.rect(screen, (0, 0, 0, 128), bg_rect)
        screen.blit(duration_text, text_rect)

def draw_parking_lot(screen, lot, cars):
    # Fill background with grass/ground
    screen.fill(COLORS['grass'])
    
    # Draw asphalt base for parking area
    parking_area = pygame.Rect(ENTRY_ROAD_WIDTH - 20, 40, 
                              lot.cols * (SLOT_WIDTH + 10) + 40, 
                              lot.rows * (SLOT_HEIGHT + LANE_WIDTH) + 40)
    pygame.draw.rect(screen, COLORS['asphalt'], parking_area)
    
    # Draw entry road
    draw_entry_road(screen, lot)
    
    # Draw driving lanes
    draw_lanes(screen, lot)
    
    # Draw parking spaces
    for r in range(lot.rows):
        for c in range(lot.cols):
            is_occupied = not lot.is_free(r, c)
            draw_parking_space(screen, r, c, is_occupied)
    
    # Draw cars
    for car in cars:
        if hasattr(car, 'x') and hasattr(car, 'y') and car.x > 0 and car.y > 0:
            # Use fixed car color to prevent blinking
            car_color = getattr(car, 'color', COLORS['car'])
            # Show remaining parking time only if car is parked (not leaving)
            if car.parked and not car.leaving and car.park_start_time is not None:
                current_time = getattr(car, 'current_time_ref', 0)
                elapsed = current_time - car.park_start_time
                remaining = max(0, car.parking_duration - elapsed)
                draw_realistic_car(screen, car.x, car.y, remaining, car_color)
            else:
                draw_realistic_car(screen, car.x, car.y, None, car_color)
