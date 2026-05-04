import pygame
import random

pygame.init()
WIDTH, HEIGHT = 1000, 800
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Turn-based Board Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)

FONT = pygame.font.Font(None, 24)

class Dice:
    @staticmethod
    def roll():
        return random.randint(1, 4)

class Point:
    def __init__(self, x, y, radius=10):
        self.x = x
        self.y = y
        self.radius = radius

    def draw(self, screen, color=BLACK):
        pygame.draw.circle(screen, color, (self.x, self.y), self.radius)

    def is_clicked(self, pos):
        return (pos[0] - self.x) ** 2 + (pos[1] - self.y) ** 2 <= self.radius ** 2

class Unit:
    def __init__(self, name, x, y, camp_id, hp=10, attack_power=1):
        self.name = name
        self.point = Point(x, y, 15)
        self.camp_id = camp_id
        self.hp = hp
        self.max_hp = hp
        self.attack_power = attack_power
        self.alive = True
        self.color = [RED, BLUE, GREEN, YELLOW][camp_id]

    def draw(self, screen, selected=False):
        if not self.alive:
            return
        if self.name == "Gate":
            pygame.draw.rect(screen, self.color, (self.point.x - self.point.radius - 5, self.point.y - self.point.radius, self.point.radius * 2 + 10, self.point.radius * 2))
            if selected:
                pygame.draw.rect(screen, WHITE, (self.point.x - self.point.radius - 8, self.point.y - self.point.radius - 3, self.point.radius * 2 + 16, self.point.radius * 2 + 6), 2)
        elif self.name == "General":
            pygame.draw.rect(screen, self.color, (self.point.x - self.point.radius, self.point.y - self.point.radius, self.point.radius * 2, self.point.radius * 2))
            if selected:
                pygame.draw.rect(screen, WHITE, (self.point.x - self.point.radius - 3, self.point.y - self.point.radius - 3, self.point.radius * 2 + 6, self.point.radius * 2 + 6), 2)
        elif self.name == "King":
            pygame.draw.polygon(screen, self.color, [
                (self.point.x, self.point.y - self.point.radius),
                (self.point.x - self.point.radius, self.point.y + self.point.radius),
                (self.point.x + self.point.radius, self.point.y + self.point.radius)
            ])
            if selected:
                pygame.draw.polygon(screen, WHITE, [
                    (self.point.x, self.point.y - self.point.radius - 3),
                    (self.point.x - self.point.radius - 3, self.point.y + self.point.radius + 3),
                    (self.point.x + self.point.radius + 3, self.point.y + self.point.radius + 3)
                ], 2)
        else:
            pygame.draw.circle(screen, self.color, (self.point.x, self.point.y), self.point.radius)
            if selected:
                pygame.draw.circle(screen, WHITE, (self.point.x, self.point.y), self.point.radius + 3, 2)
        hp_width = (self.hp / self.max_hp) * 30
        pygame.draw.rect(screen, RED, (self.point.x - 15, self.point.y - 25, 30, 5))
        pygame.draw.rect(screen, GREEN, (self.point.x - 15, self.point.y - 25, hp_width, 5))

    def is_clicked(self, pos):
        return self.point.is_clicked(pos)

    def move_to(self, point):
        self.point.x = point.x
        self.point.y = point.y

    def get_adjacent_points(self, camps, battlefield):
        adjacent = []
        try:
            for bf_point in battlefield.points:
                if bf_point.x == self.point.x and bf_point.y == self.point.y:
                    i = battlefield.points.index(bf_point)
                    for conn in battlefield.connections:
                        if conn[0] == i:
                            adjacent.append((battlefield.points[conn[1]].x, battlefield.points[conn[1]].y))
                        elif conn[1] == i:
                            adjacent.append((battlefield.points[conn[0]].x, battlefield.points[conn[0]].y))
                    if i == 1:  # Top side midpoint
                        adjacent.append((camps[0].points[0].x, camps[0].points[0].y))
                    elif i == 2:  # Right side midpoint
                        adjacent.append((camps[1].points[0].x, camps[1].points[0].y))
                    elif i == 3:  # Bottom side midpoint
                        adjacent.append((camps[2].points[0].x, camps[2].points[0].y))
                    elif i == 4:  # Left side midpoint
                        adjacent.append((camps[3].points[0].x, camps[3].points[0].y))
                    break
            
            for camp in camps:
                for i, camp_point in enumerate(camp.points):
                    if camp_point.x == self.point.x and camp_point.y == self.point.y:
                        for conn in camp.connections:
                            if conn[0] == i:
                                adjacent.append((camp.points[conn[1]].x, camp.points[conn[1]].y))
                            elif conn[1] == i:
                                adjacent.append((camp.points[conn[0]].x, camp.points[conn[0]].y))
                        if i == 4:
                            adjacent.append((camp.points[5].x, camp.points[5].y))
                        elif i == 5:
                            adjacent.append((camp.points[4].x, camp.points[4].y))
                            adjacent.append((camp.points[6].x, camp.points[6].y))
                        elif i == 6:
                            adjacent.append((camp.points[5].x, camp.points[5].y))
                        if camp.camp_id == 0:
                            adjacent.append((battlefield.points[1].x, battlefield.points[1].y))
                        elif camp.camp_id == 1:
                            adjacent.append((battlefield.points[2].x, battlefield.points[2].y))
                        elif camp.camp_id == 2:
                            adjacent.append((battlefield.points[3].x, battlefield.points[3].y))
                        else:
                            adjacent.append((battlefield.points[4].x, battlefield.points[4].y))
                        break
        except Exception as e:
            print(f"Get adjacent error: {e}")
        
        unique = []
        for coord in adjacent:
            if coord not in unique:
                unique.append(coord)
        return unique

    def can_move_to(self, point, camps, battlefield):
        if not self.alive:
            return False
        for camp in camps:
            for unit in camp.units:
                if unit != self and unit.alive:
                    if unit.point.x == point.x and unit.point.y == point.y:
                        if unit.name == "Gate":  # Gate is not a real fighter!
                            if unit.camp_id == self.camp_id:  # 己方Gate 不阻挡己方单位！
                                continue
                        return False
        adjacent = self.get_adjacent_points(camps, battlefield)
        for coord in adjacent:
            if coord[0] == point.x and coord[1] == point.y:
                return True
        return False

    def attack(self, target):
        if self.alive and target and target.alive:
            target.hp -= self.attack_power
            print(f"{self.name} attacks {target.name}, dealing {self.attack_power} damage")
            if target.hp <= 0:
                target.alive = False
                print(f"{target.name} is defeated!")

class Camp:
    def __init__(self, camp_id):
        self.camp_id = camp_id
        self.color = [RED, BLUE, GREEN, YELLOW][camp_id]
        self.points = []
        self.connections = []
        self.units = []
        self.gate = None
        self.king = None
        self.create_points()
        self.create_units()

    def create_points(self):
        if self.camp_id == 0:  # Top
            positions = [
                (500, 225),  # Point 0: Gate (顶点)
                (450, 175), (500, 175), (550, 175),  # Base line
                (400, 100), (500, 100), (600, 100)   # Bottom line (将军向外扩展，形成三角形)
            ]
        elif self.camp_id == 1:  # Right
            positions = [
                (775, 400),  # Point 0: Gate (顶点)
                (825, 350), (825, 400), (825, 450),  # Base line
                (950, 325), (950, 400), (950, 475)   # Bottom line (将军向外扩展，形成三角形)
            ]
        elif self.camp_id == 2:  # Bottom
            positions = [
                (500, 575),  # Point 0: Gate (顶点)
                (450, 625), (500, 625), (550, 625),  # Base line
                (400, 700), (500, 700), (600, 700)   # Bottom line (将军向外扩展，形成三角形)
            ]
        else:  # Left
            positions = [
                (225, 400),  # Point 0: Gate (顶点)
                (175, 350), (175, 400), (175, 450),  # Base line
                (50, 325), (50, 400), (50, 475)      # Bottom line (将军向外扩展，形成三角形)
            ]
        
        self.points = [Point(x, y) for x, y in positions]
        self.connections = [
            (0, 1), (0, 2), (0, 3),
            (1, 2), (2, 3),
            (1, 4), (1, 5),
            (2, 4), (2, 5), (2, 6),
            (3, 5), (3, 6),
            (4, 5), (5, 6)
        ]

    def create_units(self):
        self.gate = Unit("Gate", self.points[0].x, self.points[0].y, self.camp_id, hp=20, attack_power=0)
        self.units.append(self.gate)
        self.units.append(Unit("Soldier", self.points[1].x, self.points[1].y, self.camp_id, hp=3, attack_power=1))
        self.units.append(Unit("Soldier", self.points[2].x, self.points[2].y, self.camp_id, hp=3, attack_power=1))
        self.units.append(Unit("Soldier", self.points[3].x, self.points[3].y, self.camp_id, hp=3, attack_power=1))
        self.units.append(Unit("General", self.points[4].x, self.points[4].y, self.camp_id, hp=5, attack_power=2))
        self.king = Unit("King", self.points[5].x, self.points[5].y, self.camp_id, hp=10, attack_power=1)
        self.units.append(self.king)
        self.units.append(Unit("General", self.points[6].x, self.points[6].y, self.camp_id, hp=5, attack_power=2))

    def draw(self, screen, selected_unit=None):
        for conn in self.connections:
            p1 = self.points[conn[0]]
            p2 = self.points[conn[1]]
            pygame.draw.line(screen, GRAY, (p1.x, p1.y), (p2.x, p2.y), 2)
        for point in self.points:
            point.draw(screen, self.color)
        for unit in self.units:
            unit.draw(screen, selected_unit == unit)

class Battlefield:
    def __init__(self):
        self.points = []
        self.connections = []
        self.create_points()

    def create_points(self):
        # Square battlefield with 9 points: center, 4 sides midpoints, and 4 corners
        self.points = [
            Point(500, 400), Point(500, 250), Point(750, 400),
            Point(500, 550), Point(250, 400),
            Point(250, 250), Point(750, 250),
            Point(750, 550), Point(250, 550)
        ]
        self.connections = [
            (0, 1), (0, 2), (0, 3), (0, 4),
            (1, 5), (1, 6),
            (2, 6), (2, 7),
            (3, 7), (3, 8),
            (4, 5), (4, 8),
            (5, 6), (6, 7), (7, 8), (8, 5),
            (0, 5), (0, 6), (0, 7), (0, 8)
        ]

    def draw(self, screen):
        for conn in self.connections:
            p1 = self.points[conn[0]]
            p2 = self.points[conn[1]]
            pygame.draw.line(screen, GRAY, (p1.x, p1.y), (p2.x, p2.y), 3)
        for point in self.points:
            point.draw(screen, BLACK)

class Button:
    def __init__(self, x, y, width, height, text, text_color, bg_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.text_color = text_color
        self.bg_color = bg_color

    def draw(self, screen):
        pygame.draw.rect(screen, self.bg_color, self.rect)
        text_surface = FONT.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class Game:
    def __init__(self):
        self.turn = 0
        self.action_points = 0
        self.battlefield = Battlefield()
        self.camps = [Camp(i) for i in range(4)]
        self.dice = Dice()
        self.running = True
        self.selected_unit = None
        self.game_over = False
        self.winner = None
        self.skip_button = Button(WIDTH - 150, 10, 140, 50, "Skip Turn", BLACK, WHITE)

    def check_game_over(self):
        for i, camp in enumerate(self.camps):
            if not camp.king.alive:
                self.game_over = True
                for j in range(4):
                    if self.camps[j].king.alive:
                        self.winner = j
                        break
                return True
        return False

    def find_point_by_coord(self, x, y):
        for bf_point in self.battlefield.points:
            if bf_point.x == x and bf_point.y == y:
                return bf_point
        for camp in self.camps:
            for camp_point in camp.points:
                if camp_point.x == x and camp_point.y == y:
                    return camp_point
        return Point(x, y)

    def find_unit_at_point(self, point):
        for camp in self.camps:
            for unit in camp.units:
                if unit.alive and unit.point.x == point.x and unit.point.y == point.y:
                    return unit
        return None

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                pos = pygame.mouse.get_pos()
                
                if self.skip_button.is_clicked(pos):
                    self.next_turn()
                    return
                
                if event.button == 1:  # Left click - select unit
                    for camp in self.camps:
                        for unit in camp.units:
                            if unit.is_clicked(pos) and unit.name != "Gate" and unit.camp_id == self.turn and unit.alive:
                                self.selected_unit = unit
                                return
                
                elif event.button == 3 and self.selected_unit and self.action_points > 0:
                    try:
                        clicked_point = None
                        clicked_location = None
                        
                        for point in self.battlefield.points:
                            if point.is_clicked(pos):
                                clicked_point = point
                                clicked_location = "battlefield"
                                break
                        
                        if not clicked_point:
                            for camp in self.camps:
                                for point in camp.points:
                                    if point.is_clicked(pos):
                                        clicked_point = point
                                        clicked_location = "camp"
                                        break
                        
                        if not clicked_point:
                            return
                        
                        target = self.find_unit_at_point(clicked_point)
                        
                        if target and target.camp_id != self.selected_unit.camp_id and target.alive:
                            adjacent = self.selected_unit.get_adjacent_points(self.camps, self.battlefield)
                            if (clicked_point.x, clicked_point.y) in adjacent:
                                self.selected_unit.attack(target)
                                self.action_points -= 1
                                self.check_game_over()
                                return
                        elif not target:
                            if self.selected_unit.can_move_to(clicked_point, self.camps, self.battlefield):
                                self.selected_unit.move_to(clicked_point)
                                self.action_points -= 1
                                return
                    except Exception as e:
                        print(f"Handle event error: {e}")
                        import traceback
                        traceback.print_exc()
                        print(f"selected_unit: {self.selected_unit}")
                        print(f"target: {target if 'target' in locals() else 'N/A'}")
                        print(f"clicked_point: {clicked_point if 'clicked_point' in locals() else 'N/A'}")
                        return

    def ai_move(self):
        if self.turn == 0 or self.game_over:
            return False
        
        camp = self.camps[self.turn]
        available = [u for u in camp.units if u.alive and u.name != "Gate"]
        if not available:
            return False
        
        unit = random.choice(available)
        try:
            adjacent = unit.get_adjacent_points(self.camps, self.battlefield)
            
            for coord in adjacent:
                temp_point = Point(coord[0], coord[1])
                target = self.find_unit_at_point(temp_point)
                if target and target.alive and target.camp_id != unit.camp_id:
                    print(f"AI {unit.name} attacks {target.name}")
                    unit.attack(target)
                    self.action_points -= 1
                    self.check_game_over()
                    return True
            
            valid = []
            for coord in adjacent:
                temp = Point(coord[0], coord[1])
                if unit.can_move_to(temp, self.camps, self.battlefield):
                    valid.append(coord)
            
            if valid:
                target = random.choice(valid)
                target_point = self.find_point_by_coord(target[0], target[1])
                if target_point:
                    unit.move_to(target_point)
                    self.action_points -= 1
                    return True
        except Exception as e:
            print(f"AI move error: {e}")
        return False

    def next_turn(self):
        if self.game_over:
            return
        
        self.turn = (self.turn + 1) % 4
        self.selected_unit = None
        self.action_points = self.dice.roll()
        print(f"Faction {self.turn + 1} starts with {self.action_points} action points")
        
        while self.turn != 0 and not self.game_over:
            while self.action_points > 0 and not self.game_over:
                moved = self.ai_move()
                if not moved:
                    break
            
            if self.game_over:
                break
                
            self.turn = (self.turn + 1) % 4
            self.action_points = self.dice.roll()
            print(f"Faction {self.turn + 1} starts with {self.action_points} action points")

    def update(self):
        if not self.game_over and self.turn == 0 and self.action_points <= 0:
            self.next_turn()

    def draw(self):
        SCREEN.fill(WHITE)
        self.battlefield.draw(SCREEN)
        for camp in self.camps:
            camp.draw(SCREEN, self.selected_unit)
        
        action_text = FONT.render(f"Action Points: {self.action_points}", True, BLACK)
        SCREEN.blit(action_text, (10, 10))
        turn_text = FONT.render(f"Turn: Faction {self.turn + 1}", True, BLACK)
        SCREEN.blit(turn_text, (10, 50))
        self.skip_button.draw(SCREEN)
        
        if self.game_over:
            game_over_text = FONT.render(f"Game Over! Faction {self.winner + 1} Wins!", True, RED)
            SCREEN.blit(game_over_text, (WIDTH // 2 - 170, HEIGHT // 2))
        
        pygame.display.flip()

def main():
    game = Game()
    game.action_points = game.dice.roll()
    print(f"Faction 1 starts with {game.action_points} action points")
    clock = pygame.time.Clock()
    
    while game.running:
        game.handle_events()
        game.update()
        game.draw()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()
