import numpy as np
import random as rd
import pygame

# Define constants
GRID_SIZE = 30
BLOCK_SIZE = 18
WIDTH = HEIGHT = GRID_SIZE * BLOCK_SIZE
WALL_BORDER = 3

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0,0,255)

ODD = .05

class Block():
    def __init__(self,coord):
        self.prev = None
        self.is_visited = False
        self.x = coord[0]
        self.y = coord[1]
        self.walls = [1,1,1,1] #index 0,1,2,3 -> up,right,down,left

    def visit(self):
        self.is_visited = True

    def clear_wall(self,side):
        self.walls[side] = 0

    def add_wall(self,side):
        self.walls[side] = 1

class Stack():
    def __init__(self,v):
        self.head = v

    def add(self,v):
        v.prev = self.head
        self.head = v

    def remove(self):
        if self.head:
            self.head = self.head.prev
            return True
        else:
            return False

    def coords(self):
        return self.head.x,self.head.y

def generate_start_position(grid_size):
    position = rd.randint(0,grid_size-1)
    return 0,position

def generate_end_position(grid_size):
    side = rd.choice(('U','D','R'))
    position = rd.randint(0,grid_size-1)
    if side=='R':
        x=grid_size-1
        y=position
    else:
        x=position
        if side=='U':
            y=grid_size-1
        else:
            y=0

    return x,y

def create_full_maze(grid,start):
    #maze starts as a grid full of walls
    #begin at starting point and select a random wall to break and move to the block you broke into
    #if no unvisited blocks around, go back one block and check again
    #repeat until every block has been visited and is reachable
    stack = Stack(grid[GRID_SIZE-1-start[1],start[0]])
    stack.head.visit()
    visited = 1
    x,y = stack.coords()

    while visited < GRID_SIZE**2:
        #only break into unvisited blocks
        sides = available(grid,x,y)
        if sides:
            enter(stack,sides)
            visited += 1
            x,y = stack.coords()
        else:
            if stack.remove():
                x,y = stack.coords()
            else:
                break
    remove_quadrants(grid)

def remove_quadrants(grid):
    #fill 2x2 empty blocks with a random wall
    for row in range(GRID_SIZE-1):
        for col in range(GRID_SIZE-1):
            if not (grid[row,col].walls[1] or grid[row,col].walls[2] or grid[row+1,col+1].walls[0] or grid[row+1,col+1].walls[3]):
                wall = rd.randint(0,3)
                match wall:
                    case 0:
                        close_wall(grid[row,col],grid[row,col+1],1)
                    case 1:
                        close_wall(grid[row,col+1],grid[row+1,col+1],2)
                    case 2:
                        close_wall(grid[row+1,col],grid[row+1,col+1],1)
                    case 3:
                        close_wall(grid[row,col],grid[row+1,col],2)


def available(grid,x,y):
    #check which sides have not been visited
    TOP = GRID_SIZE-1-(y+1),x
    BOT = GRID_SIZE-1-(y-1),x
    RIGHT = GRID_SIZE-1-y,x+1
    LEFT = GRID_SIZE-1-y,x-1

    choice_dict = {}

    if y < GRID_SIZE-1 and not grid[TOP].is_visited:
        choice_dict[0] = grid[TOP]
    if x < GRID_SIZE-1 and not grid[RIGHT].is_visited:
        choice_dict[1] = grid[RIGHT]
    if y > 0 and not grid[BOT].is_visited:
        choice_dict[2] = grid[BOT]
    if x > 0 and not grid[LEFT].is_visited:
        choice_dict[3] = grid[LEFT]
    if len(choice_dict.keys()) > 0:
        return choice_dict
    else:
        return None

def enter(stack,sides):
    choice = rd.choice(list(sides.keys()))
    new = sides[choice]
    new.visit()
    open_wall(stack.head,new,choice)
    if rd.random()< ODD:

        if len(sides.keys())>1:
            del sides[choice]
            choice = rd.choice(list(sides.keys()))
            open_wall(stack.head,sides[choice],choice)

    stack.add(new)

def open_wall(current,next,side):
    current.clear_wall(side)
    next.clear_wall(opposite(side))

def close_wall(current,next,side):
    current.add_wall(side)
    next.add_wall(opposite(side))

def opposite(x):
    #Returns number refering to the number of the opposite side
    if x < 2:
        return x+2
    else:
        return x-2

def draw_maze(screen, grid):
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if grid[i,j].walls[0]:
                pygame.draw.rect(screen, BLACK, (j * BLOCK_SIZE-WALL_BORDER, i * BLOCK_SIZE, BLOCK_SIZE+WALL_BORDER*2, WALL_BORDER))
            if grid[i,j].walls[1]:
                pygame.draw.rect(screen, BLACK, ((j+1) * BLOCK_SIZE-WALL_BORDER, i * BLOCK_SIZE, WALL_BORDER, BLOCK_SIZE+WALL_BORDER))
            if grid[i,j].walls[2]:
                pygame.draw.rect(screen, BLACK, (j * BLOCK_SIZE-WALL_BORDER, (i+1) * BLOCK_SIZE-WALL_BORDER, BLOCK_SIZE+WALL_BORDER*2, WALL_BORDER))      
            if grid[i,j].walls[3]:
                pygame.draw.rect(screen, BLACK, (j * BLOCK_SIZE, i * BLOCK_SIZE, WALL_BORDER, BLOCK_SIZE+WALL_BORDER))

                
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    grid = np.array([[Block((x,GRID_SIZE-1-y)) for x in range(GRID_SIZE)] for y in range(GRID_SIZE)],dtype=Block)
    start_position = generate_start_position(GRID_SIZE)

    create_full_maze(grid,start_position)

    block_x = start_position[0]
    block_y = start_position[1]

    stop = False
    while True:
        #draw background
        screen.fill(WHITE)
        draw_maze(screen, grid)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stop = True
        if stop:
            break

        pygame.draw.rect(screen, RED, (block_x * BLOCK_SIZE+4, (GRID_SIZE-1-block_y) * BLOCK_SIZE+4, BLOCK_SIZE-8, BLOCK_SIZE-8)) #draw player
        keys = pygame.key.get_pressed()

        #inputs
        if keys[pygame.K_RIGHT]:
            if not grid[GRID_SIZE-1-block_y,block_x].walls[1]:
                block_x+=1
        elif keys[pygame.K_LEFT]:
            if not grid[GRID_SIZE-1-block_y,block_x].walls[3]:
                block_x-=1
        elif keys[pygame.K_UP]:
            if not grid[GRID_SIZE-1-block_y,block_x].walls[0]:
                block_y+=1
        elif keys[pygame.K_DOWN]:
            if not grid[GRID_SIZE-1-block_y,block_x].walls[2]:
                block_y-=1

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()