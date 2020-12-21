import pygame
import random


pygame.init()
width = 700
height = 700
DIS = pygame.display.set_mode((width, height))
pygame.display.set_caption("ASAS")


BG = pygame.transform.scale(pygame.image.load("back.png"), (width, height))
menu1 = pygame.transform.scale(pygame.image.load("menu2.jpg"), (width, height))

SPACESHIP1 = pygame.image.load("pixel_ship_red_small.png")
SPACESHIP2 = pygame.image.load("pixel_ship_blue_small.png")
SPACESHIP3 = pygame.image.load("pixel_ship_green_small.png")
Playership = pygame.image.load("pixel_ship_yellow.png")


bullet_r = pygame.image.load("pixel_laser_red.png")
bullet_b = pygame.image.load("pixel_laser_blue.png")
bullet_g = pygame.image.load("pixel_laser_green.png")
my_bullet = pygame.image.load("pixel_laser_yellow.png")


class Ship:
    time_coll = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(height):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.time_coll:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Bullet(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def g_w(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = Playership
        self.laser_img = my_bullet
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(-vel)
            if laser.off_screen(height):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(DIS)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.get_height() + 10, self.g_w(), 10))
        pygame.draw.rect(window, (0, 255, 0), (
        self.x, self.y + self.get_height() + 10, int(self.g_w() * (self.health / self.max_health)), 10))


class Enemy(Ship):
    COLOR_MAP = {"red": (SPACESHIP1, bullet_r), "blue": (SPACESHIP2, bullet_b),
        "green": (SPACESHIP3, bullet_g)}

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img = self.COLOR_MAP[color][0]
        self.laser_img = self.COLOR_MAP[color][1]
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Bullet(self.x - 20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1




class Bullet:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, laser_velo):
        self.y += laser_velo

    def off_screen(self, height):
        return self.y > height or self.y < 0

    def collision(self, obj):
        return collide(self, obj)


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None



def main():
    run = True
    lost = False
    lost_count = 0
    FPS = 60
    level = 0
    lives = 5
    PLAYER_VEL = 5
    ENEMY_VEL = 1
    LASER_VELO = 5
    enemies = []
    wave_length = 0
    main_font = pygame.font.SysFont("comicsans", size=50)
    player = Player(300, 630)

    clock = pygame.time.Clock()

    def redraw_window():

        DIS.blit(BG, (0, 0))

        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))
        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))
        DIS.blit(lives_label, (10, 10))
        DIS.blit(level_label, (width - level_label.get_width() - 10, 10))


        for enemy in enemies:
            enemy.draw(DIS)

        player.draw(DIS)


        if lost:
            asas = "Game over"
            asas1 = '''Authors: Aizhigit and Nursultan
                           Game over                  '''
            qw = main_font.render(asas, 1, (255, 255, 255))
            DIS.blit(qw, ((width - qw.get_width()) // 2,
                          (height - qw.get_height()) // 2))


        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1
        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue


        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for _ in range(wave_length):
                enemy = Enemy(random.randrange(50, width - 100), random.randrange(-1500 * (1 + level // 4), -100),
                              random.choice(["red", "green", "blue"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and player.x - PLAYER_VEL > 0:
            player.x -= PLAYER_VEL
        if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and player.x + PLAYER_VEL + player.g_w() < width:
            player.x += PLAYER_VEL
        if (keys[pygame.K_w] or keys[pygame.K_UP]) and player.y - PLAYER_VEL > 0:
            player.y -= PLAYER_VEL
        if (keys[pygame.K_s] or keys[
            pygame.K_DOWN]) and player.y + PLAYER_VEL + player.get_height() + 15 < height:
            player.y += PLAYER_VEL
        if keys[pygame.K_SPACE]:
            player.shoot()

        mouse_press = pygame.mouse.get_pressed()
        if mouse_press[0]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(ENEMY_VEL)
            enemy.move_lasers(LASER_VELO, player)
            if random.randrange(0, 2 * FPS) == 1:
                enemy.shoot()
            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > height:
                lives -= 1
                enemies.remove(enemy)
        player.move_lasers(LASER_VELO, enemies)


def main_menu():
    title_font = pygame.font.SysFont("comicsans", 40)
    run = True
    while run:
        title_label = title_font.render("Press the mouse to begin...", 1, (255, 255, 255))
        title_labe2 = title_font.render("Authors: Nursultan and Aizhigit", 1, (255, 255, 255))
        DIS.blit(menu1, (0, 0))
        DIS.blit(title_label, ((width - title_label.get_width()) // 2, (height - title_label.get_height()) // 2))
        DIS.blit(title_labe2, ((width - title_label.get_width()) // 3, (height - title_label.get_height()) // 1.1))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()

