# -*- coding: utf-8 -*-
import random
from pygame import Rect

TILE_SIZE = 32
MAP_W = 25
MAP_H = 14

WIDTH = MAP_W * TILE_SIZE
HEIGHT = MAP_H * TILE_SIZE

PLAYER_COOLDOWN = 0.18
ENEMY_COOLDOWN = 0.6

game_state = "menu"
music_on = True

map_grid = []

def generate_map():
    global map_grid
    map_grid = []

    for y in range(MAP_H):
        row = []
        for x in range(MAP_W):
            if x == 0 or y == 0 or x == MAP_W - 1 or y == MAP_H - 1:
                row.append(1)
            else:
                row.append(1 if random.random() < 0.15 else 0)
        map_grid.append(row)

    map_grid[1][1] = 0


def is_wall(x, y):
    if x < 0 or y < 0 or x >= MAP_W or y >= MAP_H:
        return True
    return map_grid[y][x] == 1

def play_music():
    if music_on:
        music.play("bg_music")
        music.set_volume(0.5)


def stop_music():
    music.stop()

class AnimatedEntity:
    def __init__(self, grid_x, grid_y, animations, speed):
        self.grid_x = grid_x
        self.grid_y = grid_y

        self.x = grid_x * TILE_SIZE
        self.y = grid_y * TILE_SIZE
        self.target_x = self.x
        self.target_y = self.y

        self.animations = animations
        self.state = "idle_down"
        self.frame = 0
        self.anim_timer = 0

        self.speed = speed
        self.actor = Actor(self.animations[self.state][0])
        self.actor.pos = (
            self.x + TILE_SIZE // 2,
            self.y + TILE_SIZE // 2,
        )

    def move_to(self, grid_x, grid_y):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.target_x = grid_x * TILE_SIZE
        self.target_y = grid_y * TILE_SIZE

    def update_position(self, dt):
        self.x += (self.target_x - self.x) * self.speed * dt
        self.y += (self.target_y - self.y) * self.speed * dt

        self.actor.pos = (
            self.x + TILE_SIZE // 2,
            self.y + TILE_SIZE // 2,
        )

    def update_animation(self, dt):
        self.anim_timer += dt
        if self.anim_timer >= 0.15:
            self.frame = (self.frame + 1) % len(self.animations[self.state])
            self.actor.image = self.animations[self.state][self.frame]
            self.anim_timer = 0

    def draw(self):
        self.actor.draw()

PLAYER_ANIMATIONS = {
    "idle_down": [
        "player_idle_down_0",
        "player_idle_down_1",
    ],
    "walk_down": [
        "player_walk_down_0",
    ],
}



class Player(AnimatedEntity):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_ANIMATIONS, speed=10)
        self.cooldown = 0

    def update(self, dt):
        self.cooldown += dt
        dx = dy = 0

        if keyboard.up:
            dy = -1
        elif keyboard.down:
            dy = 1
        elif keyboard.left:
            dx = -1
        elif keyboard.right:
            dx = 1

        if dx or dy:
            self.state = "walk_down"
            if self.cooldown >= PLAYER_COOLDOWN:
                if not is_wall(self.grid_x + dx, self.grid_y + dy):
                    self.move_to(self.grid_x + dx, self.grid_y + dy)
                    self.cooldown = 0
        else:
            self.state = "idle_down"

        self.update_position(dt)
        self.update_animation(dt)

ENEMY_ANIMATIONS = {
    "idle_down": ["enemy_0"],
    "walk": [
        "roach_walk_0",
        "roach_walk_1",
    ],
}
class Enemy(AnimatedEntity):
    def __init__(self, x, y):
        super().__init__(x, y, ENEMY_ANIMATIONS, speed=6)
        self.cooldown = 0
        self.home_x = x
        self.home_y = y
        self.radius = 4

    def update(self, dt):
        self.cooldown += dt
        self.state = "walk"

        if self.cooldown >= ENEMY_COOLDOWN:
            self.cooldown = 0
            dx, dy = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])

            nx = self.grid_x + dx
            ny = self.grid_y + dy

            if (
                not is_wall(nx, ny)
                and abs(nx - self.home_x) <= self.radius
                and abs(ny - self.home_y) <= self.radius
            ):
                self.move_to(nx, ny)

        self.update_position(dt)
        self.update_animation(dt)

class Coin:
    def __init__(self, x, y):
        self.grid_x = x
        self.grid_y = y

        self.actor = Actor("coin_0")
        self.actor.pos = (
            x * TILE_SIZE + TILE_SIZE // 2,
            y * TILE_SIZE + TILE_SIZE // 2,
        )

        self.frame = 0
        self.timer = 0

    def update(self, dt):
        self.timer += dt
        if self.timer >= 0.3:
            self.frame = 1 - self.frame
            self.actor.image = f"coin_{self.frame}"
            self.timer = 0

    def draw(self):
        self.actor.draw()

player = None
enemies = []
coins = []

coins_collected = 0
total_coins = 8

btn_start = Rect((WIDTH // 2 - 100, 160), (200, 40))
btn_music = Rect((WIDTH // 2 - 100, 220), (200, 40))
btn_exit = Rect((WIDTH // 2 - 100, 280), (200, 40))

def draw_button(rect, text):
    screen.draw.filled_rect(rect, (70, 90, 140))
    screen.draw.rect(rect, "white")
    screen.draw.text(text, center=rect.center, fontsize=26)

def update(dt):
    global game_state, coins_collected

    if game_state != "playing":
        return

    player.update(dt)

    for enemy in enemies:
        enemy.update(dt)
        if enemy.grid_x == player.grid_x and enemy.grid_y == player.grid_y:
            stop_music()
            game_state = "game_over"

    for coin in coins[:]:
        coin.update(dt)
        if coin.grid_x == player.grid_x and coin.grid_y == player.grid_y:
            coins.remove(coin)
            coins_collected += 1
            if music_on:
                sounds.coin.play()


            if coins_collected == total_coins:
                stop_music()
                game_state = "win"


def draw():
    screen.clear()

    if game_state == "menu":
        screen.fill((30, 30, 60))
        screen.draw.text("TESTE KODLAND", center=(WIDTH // 2, 80), fontsize=50)
        draw_button(btn_start, "COMECAR")
        draw_button(btn_music, f"MUSICA: {'ON' if music_on else 'OFF'}")
        draw_button(btn_exit, "FECHAR")

    elif game_state == "playing":
        for y in range(MAP_H):
            for x in range(MAP_W):
                if map_grid[y][x] == 1:
                    screen.blit("wall", (x * TILE_SIZE, y * TILE_SIZE))

        for coin in coins:
            coin.draw()

        for enemy in enemies:
            enemy.draw()

        player.draw()

        screen.draw.text(
            f"Coins: {coins_collected}/{total_coins}",
            topleft=(10, 10),
            fontsize=26,
            color="white",
        )

    elif game_state == "game_over":
        screen.fill((60, 10, 10))
        screen.draw.text("GAME OVER", center=(WIDTH // 2, HEIGHT // 2), fontsize=60)
        screen.draw.text("Click to return", center=(WIDTH // 2, HEIGHT // 2 + 50), fontsize=22)

    elif game_state == "win":
        screen.fill((10, 60, 20))
        screen.draw.text("YOU WIN!", center=(WIDTH // 2, HEIGHT // 2), fontsize=60)
        screen.draw.text("Click to return", center=(WIDTH // 2, HEIGHT // 2 + 50), fontsize=22)


def on_mouse_down(pos):
    global game_state, music_on

    if game_state == "menu":
        if btn_start.collidepoint(pos):
            reset_game()
            game_state = "playing"
            play_music()

        elif btn_music.collidepoint(pos):
            music_on = not music_on
            play_music() if music_on else stop_music()

        elif btn_exit.collidepoint(pos):
            stop_music()
            quit()

    elif game_state in ("game_over", "win"):
        game_state = "menu"

def reset_game():
    global player, enemies, coins, coins_collected

    generate_map()
    player = Player(1, 1)

    enemies = []
    for _ in range(4):
        while True:
            x = random.randint(3, MAP_W - 4)
            y = random.randint(3, MAP_H - 4)
            if not is_wall(x, y):
                enemies.append(Enemy(x, y))
                break

    coins = []
    coins_collected = 0

    for _ in range(total_coins):
        while True:
            x = random.randint(1, MAP_W - 2)
            y = random.randint(1, MAP_H - 2)
            if not is_wall(x, y):
                coins.append(Coin(x, y))
                break


generate_map()
