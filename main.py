import pygame
import random
import sys
import json
import os

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter PRO")

clock = pygame.time.Clock()
FPS = 60

# Load Assets
player_img = pygame.image.load("assets/player.png")
enemy_img = pygame.image.load("assets/enemy.png")
boss_img = pygame.image.load("assets/boss.png")
bullet_img = pygame.image.load("assets/bullet.png")
powerup_img = pygame.image.load("assets/powerup.png")

shoot_sound = pygame.mixer.Sound("assets/shoot.wav")
explosion_sound = pygame.mixer.Sound("assets/explosion.wav")
pygame.mixer.music.load("assets/bg_music.wav")
pygame.mixer.music.play(-1)

font = pygame.font.SysFont("arial", 25)

# ----------------- Animated Stars -----------------
stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT)] for _ in range(80)]

def draw_stars():
    for star in stars:
        pygame.draw.circle(screen, (255,255,255), star, 2)
        star[1] += 2
        if star[1] > HEIGHT:
            star[0] = random.randint(0, WIDTH)
            star[1] = 0

# ----------------- Classes -----------------

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(player_img,(60,50))
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT-50))
        self.speed = 6
        self.health = 100
        self.powered = False

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)
        shoot_sound.play()

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(enemy_img,(50,40))
        self.rect = self.image.get_rect(x=random.randint(0,WIDTH-50), y=random.randint(-100,-40))
        self.speed = random.randint(3,5)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(boss_img,(150,120))
        self.rect = self.image.get_rect(center=(WIDTH//2,100))
        self.health = 300
        self.direction = 1

    def update(self):
        self.rect.x += 3 * self.direction
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.direction *= -1

class Bullet(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        self.image = pygame.transform.scale(bullet_img,(8,20))
        self.rect = self.image.get_rect(center=(x,y))
        self.speed = -8

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(powerup_img,(30,30))
        self.rect = self.image.get_rect(x=random.randint(0,WIDTH-30), y=0)
        self.speed = 3

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

# ----------------- Save / Highscore -----------------

def save_game(score, health):
    data = {"score": score, "health": health}
    with open("savegame.json","w") as f:
        json.dump(data,f)

def load_game():
    if os.path.exists("savegame.json"):
        with open("savegame.json") as f:
            return json.load(f)
    return None

def save_highscore(score):
    high = 0
    if os.path.exists("highscore.txt"):
        with open("highscore.txt") as f:
            high = int(f.read())
    if score > high:
        with open("highscore.txt","w") as f:
            f.write(str(score))

def get_highscore():
    if os.path.exists("highscore.txt"):
        with open("highscore.txt") as f:
            return int(f.read())
    return 0

# ----------------- Game Start -----------------

all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

boss = None
score = 0
level = 1

spawn_enemy = pygame.USEREVENT + 1
spawn_power = pygame.USEREVENT + 2
pygame.time.set_timer(spawn_enemy, 1000)
pygame.time.set_timer(spawn_power, 8000)

running = True
while running:
    clock.tick(FPS)
    screen.fill((0,0,20))
    draw_stars()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_game(score, player.health)
            running = False
        if event.type == spawn_enemy and not boss:
            enemy = Enemy()
            all_sprites.add(enemy)
            enemies.add(enemy)
        if event.type == spawn_power:
            power = PowerUp()
            all_sprites.add(power)
            powerups.add(power)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

    all_sprites.update()

    # Bullet hits
    hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
    for hit in hits:
        explosion_sound.play()
        score += 10

    # Boss Spawn
    if score >= 200 and not boss:
        boss = Boss()
        all_sprites.add(boss)

    # Bullet hits boss
    if boss:
        boss_hits = pygame.sprite.spritecollide(boss, bullets, True)
        for hit in boss_hits:
            boss.health -= 10
            if boss.health <= 0:
                boss.kill()
                score += 500
                boss = None

    # Player collision
    if pygame.sprite.spritecollide(player, enemies, True):
        player.health -= 10

    if pygame.sprite.spritecollide(player, powerups, True):
        player.health += 20
        if player.health > 100:
            player.health = 100

    if player.health <= 0:
        save_highscore(score)
        running = False

    all_sprites.draw(screen)

    screen.blit(font.render(f"Score: {score}",True,(255,255,255)),(10,10))
    screen.blit(font.render(f"Health: {player.health}",True,(255,0,0)),(10,40))
    screen.blit(font.render(f"HighScore: {get_highscore()}",True,(255,255,0)),(10,70))

    pygame.display.update()

pygame.quit()
sys.exit()