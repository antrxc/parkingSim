# Main Pygame loop for parking lot simulation
import pygame
from sim.parking_lot import ParkingLot
from sim.car import Car
from sim.metrics import Metrics
from sim.visualization import draw_parking_lot, get_slot_center, SLOT_WIDTH, SLOT_HEIGHT, LANE_WIDTH, ENTRY_ROAD_WIDTH
import random

ROWS, COLS = 5, 10
INFO_HEIGHT = 100  # Increased height for separate sections
SCREEN_W = ENTRY_ROAD_WIDTH + COLS * (SLOT_WIDTH + 10) + 40
SCREEN_H = 60 + ROWS * (SLOT_HEIGHT + LANE_WIDTH) + 40 + INFO_HEIGHT
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
            # Path: entry road -> lane -> slot
            entry_x = ENTRY_ROAD_WIDTH // 2
            entry_y = 30  # Start from top of entry road
            lane_y = 60 + slot[0] * (SLOT_HEIGHT + LANE_WIDTH) - LANE_WIDTH // 2 + LANE_WIDTH // 2
            slot_x, slot_y = get_slot_center(slot[0], slot[1])
            
            path = [
                (entry_x, entry_y),    # Start at entry
                (entry_x, lane_y),     # Move down to correct lane
                (ENTRY_ROAD_WIDTH - 10, lane_y),  # Move to lane entrance
                (slot_x - 30, lane_y), # Drive along lane
                (slot_x, slot_y)       # Turn into parking space
            ]
            car.set_path(path)
            self.metrics.record_park(car.wait_time)
            # Don't set leave_time here - it will be set when car actually parks
            self.cars.append({'car': car, 'leave_time': None})
        else:
            self.metrics.record_fail()

    def start_car_exit(self, car):
        """Create exit path for a car leaving its parking spot"""
        if not car.slot:
            return
            
        slot_x, slot_y = get_slot_center(car.slot[0], car.slot[1])
        lane_y = 60 + car.slot[0] * (SLOT_HEIGHT + LANE_WIDTH) - LANE_WIDTH // 2 + LANE_WIDTH // 2
        exit_x = ENTRY_ROAD_WIDTH // 2
        exit_y = 60 + ROWS * (SLOT_HEIGHT + LANE_WIDTH) + 20  # Exit at bottom
        
        # Exit path: slot -> lane -> entry road -> exit
        exit_path = [
            (slot_x, slot_y),          # Current position
            (slot_x - 30, lane_y),     # Move to lane
            (ENTRY_ROAD_WIDTH - 10, lane_y),  # Drive to entry road
            (exit_x, lane_y),          # Enter main road
            (exit_x, exit_y)           # Exit at bottom
        ]
        
        car.start_leaving(exit_path)

    def update(self):
        self.time += 1/FPS
        self.spawn_timer += 1/FPS
        # Poisson process: spawn car on average every 8 seconds (slowed down from 3)
        if self.spawn_timer > random.expovariate(1/8):
            self.spawn_car()
            self.spawn_timer = 0
        
        # Move cars along their paths
        for c in list(self.cars):  # Use list() to allow modification during iteration
            car = c['car']
            still_moving = car.move_along_path(current_time=self.time)
            
            # Update car's current time reference for visualization
            car.current_time_ref = self.time
            
            # Set leave time when car becomes parked
            if car.parked and c['leave_time'] is None and not car.leaving:
                c['leave_time'] = self.time + car.parking_duration
            
            # Start leaving process when parking time is up
            elif (c['leave_time'] is not None and 
                  c['leave_time'] <= self.time and 
                  car.parked and 
                  not car.leaving):
                self.start_car_exit(car)
            
            # Remove car when it has completed exit path
            elif car.leaving and not still_moving:
                if car.slot:
                    self.lot.free(*car.slot)
                self.cars.remove(c)

    def draw_metrics(self):
        occ = self.lot.occupancy_percent()
        
        # Draw background for info section
        pygame.draw.rect(self.screen, (20, 20, 20), (0, SCREEN_H-INFO_HEIGHT, SCREEN_W, INFO_HEIGHT))
        pygame.draw.line(self.screen, (100, 100, 100), (0, SCREEN_H-INFO_HEIGHT), (SCREEN_W, SCREEN_H-INFO_HEIGHT), 2)
        
        # Metrics section
        metrics_text = f"Occupancy: {occ:.0f}%  Parked: {self.metrics.parked}  Failed: {self.metrics.failed}  Avg wait: {self.metrics.avg_wait():.1f}s  Reward: {self.metrics.rewards}"
        metrics_img = self.font.render(metrics_text, True, (255,255,255))
        self.screen.blit(metrics_img, (10, SCREEN_H-INFO_HEIGHT+10))
        
        # Separator line between metrics and legend
        pygame.draw.line(self.screen, (80, 80, 80), (10, SCREEN_H-INFO_HEIGHT+40), (SCREEN_W-10, SCREEN_H-INFO_HEIGHT+40), 1)
        
        # Legend section
        legend_title = self.font.render("Legend:", True, (200, 200, 200))
        self.screen.blit(legend_title, (10, SCREEN_H-INFO_HEIGHT+50))
        
        legend_y = SCREEN_H-INFO_HEIGHT+75
        legend_items = [
            ("Free Space", (255, 255, 255)),
            ("Car", (0, 100, 200)),
            ("Lane", (45, 45, 45))
        ]
        
        x_offset = 10
        for text, color in legend_items:
            pygame.draw.rect(self.screen, color, (x_offset, legend_y, 15, 10))
            legend_text = pygame.font.SysFont("Arial", 18).render(text, True, (200, 200, 200))
            self.screen.blit(legend_text, (x_offset + 20, legend_y - 3))
            x_offset += 120

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
