# Main Pygame loop for parking lot simulation
import pygame
from sim.parking_lot import ParkingLot
from sim.car import Car
from sim.metrics import Metrics
from sim.visualization import draw_parking_lot, SLOT_SIZE, MARGIN, ENTRY_ROAD_WIDTH
import random


ROWS, COLS = 5, 10
INFO_HEIGHT = 60  # Height for the info section
SCREEN_W = ENTRY_ROAD_WIDTH + COLS * (SLOT_SIZE + MARGIN)
SCREEN_H = ROWS * (SLOT_SIZE + MARGIN) + INFO_HEIGHT
FPS = 30

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption('Parking Lot Optimizer')
        self.clock = pygame.time.Clock()
        self.lot = ParkingLot(ROWS, COLS)
        self.metrics = Metrics()
        self.cars = []
        self.time = 0
        self.spawn_timer = 0
        # Use JetBrains Mono font, fallback to default if not found
        try:
            self.font = pygame.font.SysFont("JetBrains Mono", 24)
        except:
            self.font = pygame.font.SysFont(None, 24)

    def spawn_car(self):
        car = Car.random_car(self.time)
        free_slots = self.lot.get_free_slots()
        if free_slots:
            slot = random.choice(free_slots)
            self.lot.occupy(*slot)
            car.slot = slot
            # Path: entry road -> row road -> slot
            entry_x = ENTRY_ROAD_WIDTH // 2
            row_y = slot[0] * (SLOT_SIZE + MARGIN) + SLOT_SIZE // 2
            slot_x, slot_y = ENTRY_ROAD_WIDTH + slot[1] * (SLOT_SIZE + MARGIN) + SLOT_SIZE // 2, row_y
            path = [
                (entry_x, row_y),  # move vertically to row
                (slot_x, slot_y)   # move horizontally to slot
            ]
            car.set_path([(entry_x, 0)] + path)
            self.metrics.record_park(car.wait_time)
            leave_time = self.time + car.parking_duration
            self.cars.append({'car': car, 'leave_time': leave_time})
        else:
            self.metrics.record_fail()

    def update(self):
        self.time += 1/FPS
        self.spawn_timer += 1/FPS
        # Poisson process: spawn car on average every 3 seconds
        if self.spawn_timer > random.expovariate(1/3):
            self.spawn_car()
            self.spawn_timer = 0
        # Move cars along their paths
        for c in self.cars:
            c['car'].move_along_path()
        # Remove cars whose time is up
        for c in list(self.cars):
            if c['leave_time'] <= self.time:
                self.lot.free(*c['car'].slot)
                self.cars.remove(c)

    def draw_metrics(self):
        occ = self.lot.occupancy_percent()
        txt = f"Occupancy: {occ:.0f}%  Parked: {self.metrics.parked}  Failed: {self.metrics.failed}  Avg wait: {self.metrics.avg_wait():.1f}  Reward: {self.metrics.rewards}"
        img = self.font.render(txt, True, (255,255,255))
        # Draw a background rectangle for the info section at the bottom
        pygame.draw.rect(self.screen, (20, 20, 20), (0, SCREEN_H-INFO_HEIGHT, SCREEN_W, INFO_HEIGHT))
        self.screen.blit(img, (10, SCREEN_H-INFO_HEIGHT+16))

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            self.update()
            # Draw main game area (excluding info section)
            game_surface = self.screen.subsurface((0, 0, SCREEN_W, SCREEN_H-INFO_HEIGHT))
            draw_parking_lot(game_surface, self.lot, [c['car'] for c in self.cars])
            self.draw_metrics()
            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()

if __name__ == '__main__':
    Game().run()
