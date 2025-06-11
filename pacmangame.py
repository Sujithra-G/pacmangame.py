import pygame
import random
import heapq

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 650
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = (HEIGHT - 50) // GRID_SIZE

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
PINK = (255, 184, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 184, 82)

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pac-Man with Best First Search")
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 24)

class Game:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.pacman = PacMan(GRID_WIDTH // 2, GRID_HEIGHT // 2)
        self.ghosts = [
            Ghost(5, 5, RED),
            Ghost(GRID_WIDTH - 5, 5, PINK),
            Ghost(5, GRID_HEIGHT - 5, CYAN),
            Ghost(GRID_WIDTH - 5, GRID_HEIGHT - 5, ORANGE)
        ]
        self.walls = self.create_maze()
        self.dots = self.create_dots()
        self.score = 0
        self.game_over = False
        self.win = False

    def create_maze(self):
        walls = set()

        # Border walls
        for x in range(GRID_WIDTH):
            walls.add((x, 0))
            walls.add((x, GRID_HEIGHT - 1))
        for y in range(GRID_HEIGHT):
            walls.add((0, y))
            walls.add((GRID_WIDTH - 1, y))

        # Add simple maze pattern
        for x in range(5, GRID_WIDTH - 5, 2):
            walls.add((x, 5))
            walls.add((x, GRID_HEIGHT - 6))
        for y in range(5, GRID_HEIGHT - 5, 2):
            walls.add((5, y))
            walls.add((GRID_WIDTH - 6, y))

        return walls

    def create_dots(self):
        dots = set()
        for x in range(1, GRID_WIDTH - 1):
            for y in range(1, GRID_HEIGHT - 1):
                if (x, y) not in self.walls:
                    dots.add((x, y))
        return dots

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and (self.game_over or self.win):
                    self.reset()
                elif event.key == pygame.K_UP:
                    self.pacman.next_direction = (0, -1)
                elif event.key == pygame.K_DOWN:
                    self.pacman.next_direction = (0, 1)
                elif event.key == pygame.K_LEFT:
                    self.pacman.next_direction = (-1, 0)
                elif event.key == pygame.K_RIGHT:
                    self.pacman.next_direction = (1, 0)
        return True

    def update(self):
        if self.game_over or self.win:
            return
            
        # Move Pac-Man
        self.pacman.move(self.walls)
        
        # Check dot collection
        if (self.pacman.x, self.pacman.y) in self.dots:
            self.dots.remove((self.pacman.x, self.pacman.y))
            self.score += 10
            
        # Check win condition
        if not self.dots:
            self.win = True
            
        # Move ghosts using Best First Search
        for ghost in self.ghosts:
            ghost.move(self.pacman, self.walls)
            
            # Check collision
            if ghost.x == self.pacman.x and ghost.y == self.pacman.y:
                self.game_over = True

    def draw(self):
        screen.fill(BLACK)
        
        # Draw walls
        for wall in self.walls:
            pygame.draw.rect(screen, BLUE, (wall[0] * GRID_SIZE, wall[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))
        
        # Draw dots
        for dot in self.dots:
            pygame.draw.circle(screen, WHITE, (dot[0] * GRID_SIZE + GRID_SIZE // 2, dot[1] * GRID_SIZE + GRID_SIZE // 2), GRID_SIZE // 6)
        
        # Draw Pac-Man
        self.pacman.draw(screen)
        
        # Draw ghosts
        for ghost in self.ghosts:
            ghost.draw(screen)
        
        # Draw score
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, HEIGHT - 40))
        
        # Draw game messages
        if self.game_over:
            msg = font.render("GAME OVER! Press R to restart", True, RED)
            screen.blit(msg, (WIDTH // 2 - 150, HEIGHT // 2))
        elif self.win:
            msg = font.render("YOU WIN! Press R to restart", True, YELLOW)
            screen.blit(msg, (WIDTH // 2 - 130, HEIGHT // 2))
        
        pygame.display.flip()

class PacMan:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = (0, 0)
        self.next_direction = (0, 0)
        
    def move(self, walls):
        # Try next direction first
        new_x, new_y = self.x + self.next_direction[0], self.y + self.next_direction[1]
        
        if (new_x, new_y) not in walls:
            self.direction = self.next_direction

        new_x, new_y = self.x + self.direction[0], self.y + self.direction[1]
        if (new_x, new_y) not in walls:
            self.x, self.y = new_x, new_y
    
    def draw(self, screen):
        pygame.draw.circle(screen, YELLOW, (self.x * GRID_SIZE + GRID_SIZE // 2, self.y * GRID_SIZE + GRID_SIZE // 2), GRID_SIZE // 2)

class Ghost:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color

    def move(self, pacman, walls):
        path = best_first_search((self.x, self.y), (pacman.x, pacman.y), walls)
        if path:
            self.x, self.y = path[0]

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x * GRID_SIZE, self.y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

def best_first_search(start, target, walls):
    pq = []
    heapq.heappush(pq, (0, start))
    visited = {start: None}

    while pq:
        _, current = heapq.heappop(pq)
        if current == target:
            break

        x, y = current
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            new_pos = (x + dx, y + dy)
            if new_pos not in walls and new_pos not in visited:
                priority = abs(new_pos[0] - target[0]) + abs(new_pos[1] - target[1])
                heapq.heappush(pq, (priority, new_pos))
                visited[new_pos] = current

    path, step = [], target
    while step in visited and visited[step] is not None:
        path.append(step)
        step = visited[step]
    return path[::-1]

def main():
    game = Game()
    running = True
    
    while running:
        running = game.handle_events()
        game.update()
        game.draw()
        clock.tick(10)
    
    pygame.quit()

if __name__ == "__main__":
    main()
