import os
import sqlite3
import sys
import pygame
import random
from PIL import Image

# from pgu import gui
# from PyQt5.QtWidgets import QInputDialog


WIDTH = 1000
HEIGHT = 700


def load_screen_im(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def music_play(name):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Звуковой файл '{fullname}' не найден")
        sys.exit()
    pygame.mixer.music.load(fullname)
    pygame.mixer.music.play(-1)


class App:
    def __init__(self):
        self.money = 0
        self.pause = False
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Chasing the Sun')
        self.run = True
        self.design = 'V1'
        self.last_click = None
        self.all_sprites = pygame.sprite.Group()
        self.stars = pygame.sprite.Group()
        self.player_group = pygame.sprite.Group()
        self.prizes = pygame.sprite.Group()
        self.bird = AnimatedSprite(self, load_screen_im("birds5.png"), 8, 3, 1000, 260)
        self.fps = 200.0
        self.clock = pygame.time.Clock()
        self.length = 0
        self.score = 0
        self.all_money = 0
        self.speed = 1
        self.speed_variants = [1, 2, 4, 5, 8, 10]
        self.speed = self.speed_variants[0]
        # self.mus = music_play('music.mp3')

    def terminate(self):
        pygame.quit()
        sys.exit()

    def game(self):
        dog_surf = load_screen_im('pause.png')
        dog_surf2 = load_screen_im('home.png')
        dog_rect = dog_surf.get_rect(bottomright=(60, 690))
        dog_rect2 = dog_surf2.get_rect(bottomright=(120, 690))
        picture = Picture(self.design)
        weather = Weather()
        gift = Gift(self)
        stone = Stones(self)
        player = Player(self)
        coins = Money(self)
        self.pause = False
        is_jump = False
        jump_count = 13

        while self.run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                if event.type == pygame.MOUSEBUTTONUP:
                    x, y = event.pos
                    if (x in range(10, 60)) and (y in range(640, 690)):
                        print('Пауза')
                        if not self.pause:
                            self.pause = True
                            dog_surf = load_screen_im('play.png')
                            dog_rect = dog_surf.get_rect(bottomright=(60, 690))
                            # rect = pygame.Rect(0, 60, 700, 640)
                            # sub = self.screen.subsurface(rect)
                            # pygame.image.save(sub, 'data/screenshot.jpg')
                            # pause_screen = load_screen_im('screenshot.jpg')
                            # pause_rect = pause_screen.get_rect(topleft=(0, 60))
                            # self.screen.blit(pause_screen, pause_rect)
                            pygame.mixer.music.pause()

                            if (x in range(70, 120)) and (y in range(640, 690)):
                                print('Home')
                                self.start_game()
                        else:
                            self.pause = False
                            dog_surf = load_screen_im('pause.png')
                            dog_rect = dog_surf.get_rect(bottomright=(60, 690))
                            pygame.mixer.music.unpause()

                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    is_jump = True

            if is_jump:
                if player.jump(picture):
                    if jump_count >= 13:
                        if jump_count < 0:
                            player.rect.y += jump_count ** 2
                        else:
                            player.rect.y -= jump_count ** 2
                        player.rect.x += 100
                        jump_count -= 1
                    else:
                        is_jump = False
                        jump_count = 10

            self.screen.fill('#99CCFF')
            self.all_sprites.draw(self.screen)
            self.player_group.draw(self.screen)
            self.prizes.draw(self.screen)

            if not self.pause:
                self.length += 0.06

                # пока что раз в 10 метров, но потом можешь изменить на сотку, например
                # if int(self.length) % 1000 == 0 and int(self.length) > 0:
                #     self.length += 1
                #     i = self.speed_variants.index(self.speed)
                #     if i < 5:
                #         self.speed = self.speed_variants[i + 1]
                #         print(self.speed)

                self.fps += 0.5

                self.all_sprites.update(self, player)
                self.player_group.update(picture)
                gift.update(player, picture)
                stone.update(self, player, picture)
                coins.update(self, player, picture)

                font = pygame.font.Font(None, 50)
                length = font.render(str(int(self.length)) + 'м', True, pygame.Color('white'))
                intro_rect = length.get_rect()
                intro_rect.top = 10
                intro_rect.x = 975 - 24 * len(str(int(self.length)))
                self.screen.blit(length, intro_rect)

            else:
                font = pygame.font.Font(None, 120)

                length = font.render(str(int(self.length)) + 'м', True, pygame.Color('white'))
                intro_rect = length.get_rect()
                intro_rect.top = 250
                intro_rect.x = (1000 - 60 * len(str(int(self.length)))) // 2
                self.screen.blit(length, intro_rect)

            font = pygame.font.Font(None, 50)
            score = font.render(str(int(self.score)), True, pygame.Color('white'))
            intro_rect = score.get_rect()
            intro_rect.top = 50
            intro_rect.x = 1000 - 28 * len(str(int(self.score)))
            self.screen.blit(score, intro_rect)

            money = font.render(str(int(self.money)), True, pygame.Color('white'))
            intro_rect = money.get_rect()
            intro_rect.top = 10
            intro_rect.x = 15
            self.screen.blit(money, intro_rect)

            picture.draw_picture(self.screen)

            if weather.sun:
                self.screen.blit(weather.sun_1, weather.rect4)
            if weather.clouds:
                self.screen.blit(weather.clouds_1, weather.rect)
                self.screen.blit(weather.clouds_2, weather.rect2)
                self.screen.blit(weather.clouds_3, weather.rect3)

            if int(self.length) % 120 == 0 and int(self.length) > 2:
                new_weather = random.choice(['clouds', 'sun'])
                self.bird.new_bird()
                weather.change_weather(new_weather)

            if int(self.length) % 130 == 0 and int(self.length) > 0:
                gift.new_gift()

            if int(self.length) % 90 == 0 and int(self.length) > 0:
                print('new stone spawned')
                stone.new_stone()
                coins.new_stone()

            if gift.prize == 'ускорение':
                i = self.speed_variants.index(self.speed)
                if i < 5:
                    self.speed = self.speed_variants[i + 1]
                print(self.speed)

            if gift.prize == 'замедление':
                i = self.speed_variants.index(self.speed)
                if i > 0:
                    self.speed = self.speed_variants[i - 1]
                # if self.speed > 3:
                #     self.speed -= 2
                # elif 2 < self.speed <= 3:
                #     self.speed -= 1
                # else:
                #     self.speed -= 0.01

            if gift.prize == 'щит':
                print('Пока не реализовано')

            if gift.prize == 'очки':
                self.score += random.randrange(15, 201, 5)

            if gift.prize == 'монеты':
                self.money += random.randrange(10, 101, 10)

            picture.update(self.pause, self.speed)
            weather.update(self.pause)
            self.screen.blit(dog_surf, dog_rect)
            self.screen.blit(dog_surf2, dog_rect2)
            pygame.display.flip()
            self.clock.tick(int(self.fps))

    def start_game(self):
        intro_text = ["CHASING THE SUN", "",
                      "Правила игры",
                      "Начало игры",
                      "Достижения",
                      "Выбрать дизайн"]

        levels = ['Выберите уровень']

        fon = pygame.transform.scale(load_screen_im('fon.jpg'), (WIDTH, HEIGHT))
        self.screen.blit(fon, (0, 0))
        font = pygame.font.Font(None, 30)

        text_coord = 50
        for line in intro_text:
            string_rendered = font.render(line, True, pygame.Color('white'))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.right = 890
            text_coord += intro_rect.height
            self.screen.blit(string_rendered, intro_rect)

        string_rendered = font.render(levels[0], True, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        intro_rect.right = 890
        intro_rect.top = text_coord + 70
        self.screen.blit(string_rendered, intro_rect)

        coin = load_screen_im("coin_start.png", -1)
        coin_rect = coin.get_rect()
        coin_rect.top = 40
        coin_rect.left = 10
        self.screen.blit(coin, coin_rect)
        font = pygame.font.Font(None, 50)
        money = font.render(str(self.all_money), True, pygame.Color('white'))
        money_rect = money.get_rect()
        money_rect.top = 50
        money_rect.left = 70
        self.screen.blit(money, money_rect)

        rec = True
        dis = True
        spe = True
        run = True
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                if event.type == pygame.MOUSEBUTTONUP:
                    x, y = event.pos
                    if (x in range(781, 890)) and (y in range(60, 80)):
                        print('Заставка')
                        self.last_click = 'Заставка'
                    if (x in range(751, 890)) and (y in range(120, 140)):
                        print('Правила')
                        self.last_click = 'Правила'
                    if (x in range(763, 890)) and (y in range(150, 170)):
                        self.game()
                    if (x in range(765, 890)) and (y in range(180, 200)):
                        print('Достижения')
                        if rec:
                            rec = False
                            records = []
                            font = pygame.font.Font(None, 30)
                            for n in range(3):
                                length, score = self.get_records(n + 1)
                                records.append([length[0], score[0]])

                            text_coord = 110
                            level = 1
                            for line in records:
                                if line[0]:
                                    text = f'На уровне {level} Вы прошли {line[0]} метров и набрали {line[1]} очков'
                                    level += 1
                                    string_rendered = font.render(text, True, pygame.Color('white'))
                                    record_rect = string_rendered.get_rect()
                                    text_coord += 10
                                    record_rect.top = text_coord
                                    record_rect.left = 20
                                    text_coord += record_rect.height
                                    self.screen.blit(string_rendered, record_rect)
                                else:
                                    string_rendered = font.render(f'У Вас нет досстижений на уровне {level}', True, pygame.Color('white'))
                                    level += 1
                                    record_rect = string_rendered.get_rect()
                                    text_coord += 10
                                    record_rect.top = text_coord
                                    record_rect.left = 20
                                    text_coord += record_rect.height
                                    self.screen.blit(string_rendered, record_rect)
                        else:
                            self.start_game()
                    if (x in range(725, 890)) and (y in range(210, 230)):
                        if dis:
                            dis = False
                            text_coord = 230
                            choice = [' Пиксельный o', ' Классика o']
                            for line in choice:
                                string_rendered = font.render(line, True, pygame.Color('white'))
                                intro_rect = string_rendered.get_rect()
                                text_coord += 10
                                intro_rect.top = text_coord
                                intro_rect.right = 890
                                text_coord += intro_rect.height
                                self.screen.blit(string_rendered, intro_rect)
                        else:
                            self.start_game()
                        print('Дизайн')
                    if (x in range(744, 890)) and (y in range(240, 260)) and not dis:
                        self.design = 'V2'
                        self.last_click = ''
                        self.start_game()
                    if (x in range(773, 890)) and (y in range(270, 290)) and not dis:
                        self.design = 'V1'
                        self.last_click = ''
                        self.start_game()
                    if (x in range(706, 890)) and (y in range(300, 320)):
                        print('Выберите скорость')
                        if spe:
                            spe = False
                            coord = 320
                            choice = [load_screen_im('star1.png'), load_screen_im('star2.png'),
                                      load_screen_im('star3.png')]
                            for n, line in enumerate(choice):
                                rect = line.get_rect()
                                rect.x = 840
                                rect.y = coord + n * 50
                                self.screen.blit(line, rect)
                        else:
                            self.start_game()
                    if (x in range(840, 890)) and (y in range(320, 370)) and not spe:
                        self.speed = 1
                        self.start_game()
                    if (x in range(840, 890)) and (y in range(370, 420)) and not spe:
                        self.speed = 2
                        self.start_game()
                    if (x in range(840, 890)) and (y in range(420, 470)) and not spe:
                        self.speed = 4
                        self.start_game()
                    # print(self.speed)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.game()

            pygame.display.flip()
            self.clock.tick(int(self.fps))

    #    def choose_design(self):
    #        design, ok_pressed = QInputDialog.getItem(
    #            self, "Выберите дизайн игры", "Готовы выбрать?",
    #            ("Простой дизайн", "Красивый дизайн"), 1, False)
    #        if ok_pressed:
    #            if design == "Простой дизайн":
    #                self.design = 'V2'
    #            elif design == "Красивый дизайн":
    #                self.design = 'V1'

    def update_records(self):
        con = sqlite3.connect('info.sqlite')
        cur = con.cursor()
        length = cur.execute(f"""SELECT num from records
                                    WHERE type = 'length'""").fetchall()
        score = cur.execute(f"""SELECT num from records
                                    WHERE type = 'score'""").fetchall()
        con.close()

        if self.length > length[0]:
            con = sqlite3.connect('info.sqlite')
            cur = con.cursor()
            data = ('length', int(self.length))
            query = 'INSERT INTO records VALUES (?, ?)'
            cur.execute(query, data)
            con.commit()
            con.close()
        if self.score > score[0]:
            con = sqlite3.connect('info.sqlite')
            cur = con.cursor()
            data = ('score', int(self.score))
            query = 'INSERT INTO records VALUES (?, ?)'
            cur.execute(query, data)
            con.commit()
            con.close()

    def get_records(self, level):
        con = sqlite3.connect('info.sqlite')
        cur = con.cursor()
        length = cur.execute(f"""SELECT num from records
                                            WHERE type = 'length' and level = '{level}'""").fetchall()
        score = cur.execute(f"""SELECT num from records
                                            WHERE type = 'score' and level = '{level}'""").fetchall()
        con.close()
        return length[0], score[0]

    def finish_game(self, money, score):
        mon = money
        leng = score
        self.run = True
        fon = pygame.transform.scale(load_screen_im('fon.jpg'), (WIDTH, HEIGHT))
        self.screen.blit(fon, (0, 0))
        font = pygame.font.Font(None, 30)
        self.all_money += self.money

        self.money = 0

        levels = [f'Собранные вами монеты: {mon}', f'Расстояние, которое вы преодолели: {int(leng)}']
        string_rendered = font.render(levels[0], True, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        intro_rect.right = 700
        intro_rect.top = 300
        self.screen.blit(string_rendered, intro_rect)

        string_rendered = font.render(levels[1], True, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        intro_rect.right = 700
        intro_rect.top = 330
        self.screen.blit(string_rendered, intro_rect)

        choice = [load_screen_im('home.png'), load_screen_im('return.png')]
        coords = [(450, 375), (500, 375)]
        for n, line in enumerate(choice):
            rect = line.get_rect()
            rect.x = coords[n][0]
            rect.y = coords[n][1]
            self.screen.blit(line, rect)

        while self.run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                if event.type == pygame.MOUSEBUTTONUP:
                    x, y = event.pos
                    print(x, y)

            pygame.display.flip()


class Player(pygame.sprite.Sprite):
    def __init__(self, app):
        super().__init__(app.player_group)
        self.image = load_screen_im("doll.png", -1)
        self.app = app
        self.app.screen.fill('#99CCFF')
        self.picture = Picture(app.design)
        self.pic_rect = self.picture.mask.outline(every=1)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = 100
        self.rect.y = 250

    def jump(self, picture):
        if pygame.sprite.collide_mask(self, picture):
            return True
        else:
            return False

    def update(self, picture):
        y_now = []
        y_later = []
        for coord in self.pic_rect:
            if coord[0] == 137:
                y_now.append(coord[1])
            if coord[0] == 138:
                y_later.append(coord[1])

        distance = max(y_later) - max(y_now)
        # вместо +-1 нужно будет подставить +-distance, но пока что не знаю, как

        if not pygame.sprite.collide_mask(self, picture):
            if max(y_now) < (self.rect.top - 200):
                self.rect = self.rect.move(0, -2)
            elif max(y_now) >= (self.rect.top - 300):
                self.rect = self.rect.move(0, 1)
            if self.rect.top > 600:
                self.rect = self.rect.move(0, 5)
        else:
            self.rect = self.rect.move(0, -1)


class Picture:
    def __init__(self, design):
        MAPS_V1 = ['data/hills1.png', 'data/hills2.png', 'data/hills3.png']
        MAPS_V2 = ['data/map1_v2.png', 'data/map2_v2.png', 'data/map3_v2.png']
        maps = None
        if design == 'V1':
            maps = MAPS_V1
            self.x, self.y = 1000, 400
        elif design == 'V2':
            maps = MAPS_V2
            self.x, self.y = 1714, 400

        self.image1 = pygame.image.load(random.choice(maps))
        self.rect1 = self.image1.get_rect()
        self.rect1.left = 1
        self.rect1.top = 700 - self.y

        self.image2 = pygame.image.load(random.choice(maps))
        self.rect2 = self.image2.get_rect()
        self.rect2.left = self.x
        self.rect2.top = 700 - self.y

        self.first_im = True
        self.second_im = False
        self.pause = False
        self.mask_time = 1

        self.image = self.image1
        self.rect = self.rect1
        self.mask = pygame.mask.from_surface(self.image)

    def choice_image(self, flag):
        if flag:
            self.image = self.image2
            self.rect = self.rect2
            self.mask = pygame.mask.from_surface(self.image)
            self.rect1.left = 1000

        else:
            self.image = self.image1
            self.rect = self.rect1
            self.mask = pygame.mask.from_surface(self.image)
            self.rect2.left = 1000

    def draw_picture(self, screen):
        screen.blit(self.image, self.rect)
        if self.first_im:
            screen.blit(self.image2, self.rect2)

        if self.second_im:
            screen.blit(self.image1, self.rect1)

    def update(self, pause, speed):
        x = speed * -1 + 1
        if not pause:
            if self.first_im:
                self.rect = self.rect.move(-1 * int(speed), 0)
                self.rect2 = self.rect2.move(-1 * int(speed), 0)

            if self.second_im:
                self.rect = self.rect.move(-1 * int(speed), 0)
                self.rect1 = self.rect1.move(-1 * int(speed), 0)

            if self.rect.left == -1000 + x and self.first_im:
                self.first_im = False
                self.second_im = True
                self.choice_image(True)
            if self.rect.left == -1000 + x and self.second_im:
                self.second_im = False
                self.first_im = True
                self.choice_image(False)


class Gift(pygame.sprite.Sprite):
    def __init__(self, app):
        super().__init__(app.prizes)
        self.image = load_screen_im("prize.png", -1)
        self.rect = self.image.get_rect()
        self.rect.x = -200
        self.rect.y = 0
        self.mask = pygame.mask.from_surface(self.image)
        self.prizes = ['ускорение', 'замедление', 'очки', 'монеты', 'щит']
        self.prize = ''

    def new_gift(self):
        self.rect.x = 1000
        self.rect.y = 0

    def update(self, player, picture):
        if pygame.sprite.collide_mask(self, player):
            self.prize = random.choice(self.prizes)
            self.rect.x = -200
            self.rect.y = 0
            print(self.prize)
        elif pygame.sprite.collide_mask(self, picture):
            self.prize = ''
            self.rect = self.rect.move(-1, 0)
        else:
            self.prize = ''
            self.rect = self.rect.move(-3, 5)


class Stones(pygame.sprite.Sprite):
    def __init__(self, app):
        super().__init__(app.prizes)
        self.image = load_screen_im("stone.png", -1)
        self.rect = self.image.get_rect()
        self.rect.x = 800 # -200
        self.rect.y = 400
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, app, player, picture):
        if pygame.sprite.collide_mask(self, player):
            self.rect.x = -200
            self.rect.y = 0
            app.finish_game(app.money, app.length)
            print('врезался в камень')
        elif pygame.sprite.collide_mask(self, picture):
            self.rect = self.rect.move(-1, 0)
        else:
            self.rect = self.rect.move(0, 1)

    def new_stone(self):
        self.rect.x = 980
        self.rect.y = 400


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, app, sheet, columns, rows, x, y):
        super().__init__(app.all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.counter = 0
        self.counter_of_fly = 0

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self, app, player):
        if not pygame.sprite.collide_mask(self, player):
            self.counter += 1
            self.counter_of_fly += 1
            if self.counter == 8:
                self.counter = 0
                self.cur_frame = (self.cur_frame + 1) % len(self.frames)
                self.image = self.frames[self.cur_frame]
            if self.counter_of_fly % 2 == 0:
                self.rect = self.rect.move(-3, 0)
        else:
            score = app.score
            if score > 10:
                score -= 10
            else:
                app.finish_game(app.money, app.length)  # (app.score, app.length, app.money)

    def new_bird(self):
        self.rect.top = 350
        self.rect.left = 1000


class Weather:
    def __init__(self):
        self.clouds_1 = load_screen_im('cloud.png')
        self.clouds_2 = load_screen_im('cloud2.png')
        self.clouds_3 = load_screen_im('cloud3.png')
        self.rect = self.clouds_1.get_rect()
        self.rect.left, self.rect.top = 400, 0
        self.rect2 = self.clouds_1.get_rect()
        self.rect2.left, self.rect2.top = 100, -50
        self.rect3 = self.clouds_1.get_rect()
        self.rect3.left, self.rect3.top = 300, 50

        self.sun_1 = load_screen_im('sun.png')
        self.rect4 = self.sun_1.get_rect()
        self.rect4.left, self.rect4.top = 850, 100

        self.weather = 'sun'
        self.clouds = False
        self.sun = True
        self.catch_clouds = False
        self.catch_sun = False

        self.counter = 0

    def update(self, pause):
        self.counter += 1
        self.counter %= 200
        if not pause and self.counter % 3 == 0:
            if self.catch_clouds:
                if self.rect.left > -300:
                    self.rect = self.rect.move(-3, 0)
                if self.rect2.left > -300:
                    self.rect2 = self.rect2.move(-4, 0)
                if self.rect3.left > -300:
                    self.rect3 = self.rect3.move(-5, 0)
                if self.rect.left <= -300 and self.rect2.left <= -300 and self.rect3.left <= -300:
                    self.catch_clouds = False
                    self.clouds = False

            if self.catch_sun:
                if self.rect4.left > -300:
                    self.rect4 = self.rect4.move(-2, 0)
                if self.rect4.left <= -300:
                    self.catch_sun = False
                    self.sun = False

            if self.clouds and not self.catch_clouds:
                self.rect = self.rect.move(-2, 0)
                if self.rect.left <= -300:
                    self.rect.left = 1000
                self.rect2 = self.rect2.move(-3, 0)
                if self.rect2.left <= -300:
                    self.rect2.left = 1000
                self.rect3 = self.rect3.move(-4, 0)
                if self.rect3.left <= -300:
                    self.rect3.left = 1000
            elif self.sun and not self.catch_sun:
                self.rect4 = self.rect4.move(-1, 0)
                if self.rect4.left <= -300:
                    self.rect4.left = 850

    def change_weather(self, weather):
        if self.weather != weather:
            if weather == 'sun':
                self.weather = 'sun'
                self.rect4.left, self.rect.top = 700, 0
                self.sun = True
                self.catch_clouds = True
            else:
                self.weather = 'clouds'
                self.rect.left, self.rect.top = 700, 0
                self.rect2.left, self.rect2.top = 850, -50
                self.rect3.left, self.rect3.top = 900, 50
                self.clouds = True
                self.catch_sun = True


class Money(pygame.sprite.Sprite):
    def __init__(self, app):
        super().__init__(app.prizes)
        self.image = load_screen_im("coin.png")
        self.rect = self.image.get_rect()
        self.rect.x = 700 # -200
        self.rect.y = 300
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, app, player, picture):
        if pygame.sprite.collide_mask(self, player):
            self.rect.x = -200
            self.rect.y = 0
            # здесь надо прибавлять монетки
            print('+10 монеток')
            app.money += 10
        elif pygame.sprite.collide_mask(self, picture):
            self.rect = self.rect.move(-1, 0)
        else:
            self.rect = self.rect.move(0, 1)

    def new_stone(self):
        self.rect.x = 500
        self.rect.y = 450


if __name__ == '__main__':
    app = App()
    app.start_game()