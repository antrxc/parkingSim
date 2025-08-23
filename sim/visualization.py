# Pygame visualization for parking lot
import pygame

SLOT_SIZE = 40
MARGIN = 5
ENTRY_ROAD_WIDTH = 60

COLORS = {
    'free': (0, 200, 0),
    'occupied': (200, 0, 0),
    'car': (0, 0, 200),
    'bg': (30, 30, 30)
}

def draw_parking_lot(screen, lot, cars):
    screen.fill(COLORS['bg'])
    for r in range(lot.rows):
        for c in range(lot.cols):
            color = COLORS['free'] if lot.is_free(r, c) else COLORS['occupied']
            rect = pygame.Rect(ENTRY_ROAD_WIDTH + c*(SLOT_SIZE+MARGIN), r*(SLOT_SIZE+MARGIN), SLOT_SIZE, SLOT_SIZE)
            pygame.draw.rect(screen, color, rect)
    for car in cars:
        if car.slot:
            r, c = car.slot
            rect = pygame.Rect(ENTRY_ROAD_WIDTH + c*(SLOT_SIZE+MARGIN), r*(SLOT_SIZE+MARGIN), SLOT_SIZE, SLOT_SIZE)
            pygame.draw.rect(screen, COLORS['car'], rect)
