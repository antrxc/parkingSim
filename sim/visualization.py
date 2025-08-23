# Pygame visualization for parking lot
import pygame


SLOT_SIZE = 40
MARGIN = 18  # Increased margin for more space between shapes
ENTRY_ROAD_WIDTH = 60

COLORS = {
    'free': (0, 200, 0),
    'occupied': (200, 0, 0),
    'car': (0, 0, 200),
    'bg': (30, 30, 30),
    'road': (80, 80, 80),
    'entry': (180, 180, 0)
}

def get_slot_center(row, col):
    x = ENTRY_ROAD_WIDTH + col * (SLOT_SIZE + MARGIN) + SLOT_SIZE // 2
    y = row * (SLOT_SIZE + MARGIN) + SLOT_SIZE // 2
    return x, y

def draw_roads(screen, lot):
    # Draw entry road
    pygame.draw.rect(screen, COLORS['road'], (0, 0, ENTRY_ROAD_WIDTH, lot.rows * (SLOT_SIZE + MARGIN)))
    # Draw horizontal roads in front of each row
    for r in range(lot.rows):
        y = r * (SLOT_SIZE + MARGIN) + SLOT_SIZE // 2
        pygame.draw.line(screen, COLORS['road'], (ENTRY_ROAD_WIDTH, y), (ENTRY_ROAD_WIDTH + lot.cols * (SLOT_SIZE + MARGIN), y), 12)

def draw_parking_lot(screen, lot, cars):
    screen.fill(COLORS['bg'])
    draw_roads(screen, lot)
    for r in range(lot.rows):
        for c in range(lot.cols):
            color = COLORS['free'] if lot.is_free(r, c) else COLORS['occupied']
            rect = pygame.Rect(ENTRY_ROAD_WIDTH + c*(SLOT_SIZE+MARGIN), r*(SLOT_SIZE+MARGIN), SLOT_SIZE, SLOT_SIZE)
            pygame.draw.rect(screen, color, rect)
    for car in cars:
        if car.slot:
            # Draw moving car at its (x, y)
            pygame.draw.rect(screen, COLORS['car'], pygame.Rect(int(car.x)-SLOT_SIZE//2, int(car.y)-SLOT_SIZE//2, SLOT_SIZE, SLOT_SIZE))
