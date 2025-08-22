import pygame
import json


def save():
    data = {
        "points": points,
        "total_cookies": total_cookies_earned,
        "music_volume": music_volume,
        "sound_volume": sound_volume,
        "upgrades": {
            "clicker": {"amount": up_clicker.amount, "price": up_clicker.price},
            "grandma": {"amount": up_grandma.amount, "price": up_grandma.price},
            "plant": {"amount": up_plant.amount, "price": up_plant.price},
            "bakery": {"amount": up_bakery.amount, "price": up_bakery.price},
            "farm": {"amount": up_farm.amount, "price": up_farm.price},
            "mine": {"amount": up_mine.amount, "price": up_mine.price},
            "factory": {"amount": up_factory.amount, "price": up_factory.price},
            "laboratory": {"amount": up_laboratory.amount, "price": up_laboratory.price},
        }
    }
    with open("save_data.json", "w") as file:
        json.dump(data, file)


def load():
    try:
        with open("save_data.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {
            "points": 0,
            "total_cookies": 0,
            "music_volume": 0.7,
            "sound_volume": 0.3,
            "upgrades": {
                "clicker": {"amount": 0, "price": 15},
                "grandma": {"amount": 0, "price": 100},
                "plant": {"amount": 0, "price": 1100},
                "bakery": {"amount": 0, "price": 12000},
                "farm": {"amount": 0, "price": 130000},
                "mine": {"amount": 0, "price": 1400000},
                "factory": {"amount": 0, "price": 20000000},
                "laboratory": {"amount": 0, "price": 330000000}
            }
        }


def format_number(num):
    if num < 1000:
        return str(int(num))
    elif num < 1000000:
        return f"{num / 1000:.1f}K"
    elif num < 1000000000:
        return f"{num / 1000000:.1f}M"
    elif num < 1000000000000:
        return f"{num / 1000000000:.1f}B"
    elif num < 1000000000000000:
        return f"{num / 1000000000000:.1f}T"
    elif num < 1000000000000000000:
        return f"{num / 1000000000000000:.1f}Qa"
    else:
        return f"{num / 1000000000000000000:.1f}Qi"


auto_save_time1 = pygame.time.get_ticks()


def auto_save():
    global auto_save_time1
    time2 = pygame.time.get_ticks()
    if time2 - auto_save_time1 > 30000:
        save()
        auto_save_time1 = time2


loaded_data = load()

points = loaded_data["points"]
total_cookies_earned = loaded_data.get("total_cookies", 0)
music_volume = loaded_data.get("music_volume", 0.7)
sound_volume = loaded_data.get("sound_volume", 0.3)
time1 = pygame.time.get_ticks()
shown_cps = 0
cps1 = 0
cps2 = 0
Mouse_pressed = False
scroll_offset = 0
max_scroll = 0

floating_texts = []


class FloatingText:
    def __init__(self, x, y, text, color=(255, 255, 255)):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.alpha = 255
        self.font = pygame.font.Font("freesansbold.ttf", 24)

    def update(self):
        self.y -= 2
        self.alpha -= 5
        return self.alpha > 0

    def draw(self, window):
        if self.alpha > 0:
            text_surface = self.font.render(self.text, True, self.color)
            text_surface.set_alpha(self.alpha)
            window.blit(text_surface, (self.x, self.y))


def add_floating_text(x, y, text, color=(255, 255, 255)):
    floating_texts.append(FloatingText(x, y, text, color))


def update_floating_texts(window):
    global floating_texts
    floating_texts = [text for text in floating_texts if text.update()]
    for text in floating_texts:
        text.draw(window)


def cookie_points(window):
    points_font = pygame.font.Font("freesansbold.ttf", 50)
    points_text = points_font.render(format_number(points), True, (255, 255, 255))

    shadow_text = points_font.render(format_number(points), True, (100, 100, 100))
    window.blit(shadow_text, (437, 37))
    window.blit(points_text, (435, 35))

    window.blit(pygame.image.load("images/cookie_small.png"), (360, 38))


def show_cps_text(window):
    cps_font = pygame.font.Font("freesansbold.ttf", 30)
    cps_text = cps_font.render(f"{format_number(shown_cps)}/sec", True, (200, 200, 200))
    window.blit(cps_text, (440, 90))


def show_stats(window):
    stats_font = pygame.font.Font("freesansbold.ttf", 20)
    stats_text = stats_font.render(f"Total cookies baked: {format_number(total_cookies_earned)}", True, (220, 220, 220))

    shadow_text = stats_font.render(f"Total cookies baked: {format_number(total_cookies_earned)}", True,
                                    (100, 100, 100))
    window.blit(shadow_text, (12, 537))
    window.blit(stats_text, (10, 535))


def cps_update():
    global time1, shown_cps, cps1, cps2
    time2 = pygame.time.get_ticks()
    if time2 - time1 > 1000:
        time1 = time2
        cps3 = cps1
        shown_cps = cps3 - cps2
        cps2 = cps1


class Cookie:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image
        self.scale = 1.0
        self.target_scale = 1.0

    def draw(self, window):
        if abs(self.scale - self.target_scale) > 0.01:
            self.scale += (self.target_scale - self.scale) * 0.3

        if self.scale != 1.0:
            scaled_image = pygame.transform.scale(
                self.image,
                (int(self.image.get_width() * self.scale),
                 int(self.image.get_height() * self.scale))
            )
            offset_x = (self.image.get_width() - scaled_image.get_width()) // 2
            offset_y = (self.image.get_height() - scaled_image.get_height()) // 2
            window.blit(scaled_image, (self.x + offset_x, self.y + offset_y))
        else:
            window.blit(self.image, (self.x, self.y))

    def clicked(self):
        global points, cps1, total_cookies_earned
        try:
            click_sound = pygame.mixer.Sound("sounds/click_sound.wav")
            click_sound.set_volume(sound_volume)
        except:
            click_sound = None

        mouse_pos = pygame.mouse.get_pos()
        cookie_rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        if cookie_rect.collidepoint(mouse_pos):
            if click_sound:
                click_sound.play()

            click_power = 1 + up_clicker.amount
            points += click_power
            cps1 += click_power
            total_cookies_earned += click_power

            self.target_scale = 1.1
            add_floating_text(mouse_pos[0], mouse_pos[1], f"+{format_number(click_power)}", (255, 255, 100))
            return True


normal_cookie = Cookie(383, 250, pygame.image.load("images/cookie_normal.png"))
clicked_cookie = Cookie(395, 260, pygame.image.load("images/cookie_clicked.png"))
shown_cookie = normal_cookie


class Upgrades:
    def __init__(self, name, x, y, price, cookie_gain, amount, time, image, dark_image=None):
        self.name = name
        self.x = x
        self.y = y
        self.base_price = price
        self.price = price
        self.cookie_gain = cookie_gain
        self.amount = amount
        self.time = time
        self.image = image
        self.dark_image = dark_image
        self.hover = False

    def print_upgrade(self, window):
        global Mouse_pressed
        mouse_pos = pygame.mouse.get_pos()

        draw_y = self.y + scroll_offset
        upgrade_rect = pygame.Rect(self.x, draw_y, self.image.get_width(), self.image.get_height())

        if draw_y < -120 or draw_y > 510:
            return

        self.hover = upgrade_rect.collidepoint(mouse_pos)

        if points >= self.price:
            if self.hover and Mouse_pressed:
                window.blit(self.dark_image, (self.x, draw_y))
            else:
                window.blit(self.image, (self.x, draw_y))
                if self.hover:
                    glow_surface = pygame.Surface((self.image.get_width() + 4, self.image.get_height() + 4))
                    glow_surface.fill((255, 255, 255))
                    glow_surface.set_alpha(50)
                    window.blit(glow_surface, (self.x - 2, draw_y - 2))
                    window.blit(self.image, (self.x, draw_y))
        else:
            window.blit(self.dark_image, (self.x, draw_y))

        cost_font = pygame.font.Font("freesansbold.ttf", 16)
        upgrade_price_text = cost_font.render(format_number(self.price), True,
                                              (255, 255, 255) if points >= self.price else (150, 150, 150))
        if self.name == "plant":
            window.blit(upgrade_price_text, (self.x + 10, draw_y + 95))
        else:
            window.blit(upgrade_price_text, (self.x + 10, draw_y + 82))

        amount_font = pygame.font.Font("freesansbold.ttf", 18)
        amount_text = amount_font.render(str(self.amount), True, (255, 255, 100))
        window.blit(amount_text, (self.x - 15, draw_y + 5))

        if self.hover and points >= self.price:
            self.show_tooltip(window, mouse_pos)

    def show_tooltip(self, window, mouse_pos):
        tooltip_font = pygame.font.Font("freesansbold.ttf", 16)
        tooltip_lines = [
            f"{self.name.capitalize()}",
            f"Cost: {format_number(self.price)}",
        ]

        if self.name == "clicker":
            tooltip_lines.append(f"Click power: +{self.amount + 1}")
            tooltip_lines.append("")
            tooltip_lines.append("Bonus: Each clicker adds")
            tooltip_lines.append("+1 cookie per click")
        else:
            tooltip_lines.append(f"Produces: {format_number(self.cookie_gain)} cookies/sec")

        tooltip_lines.append(f"Owned: {self.amount}")

        tooltip_height = len(tooltip_lines) * 20 + 10
        tooltip_width = max([tooltip_font.size(line)[0] for line in tooltip_lines]) + 20

        tooltip_x = mouse_pos[0] + 15
        tooltip_y = mouse_pos[1] - tooltip_height // 2

        if tooltip_x + tooltip_width > 900:
            tooltip_x = mouse_pos[0] - tooltip_width - 15
        if tooltip_y < 0:
            tooltip_y = 0
        elif tooltip_y + tooltip_height > 560:
            tooltip_y = 560 - tooltip_height

        tooltip_surface = pygame.Surface((tooltip_width, tooltip_height))
        tooltip_surface.fill((50, 50, 50))
        tooltip_surface.set_alpha(220)
        window.blit(tooltip_surface, (tooltip_x, tooltip_y))

        pygame.draw.rect(window, (255, 255, 255), (tooltip_x, tooltip_y, tooltip_width, tooltip_height), 2)

        for i, line in enumerate(tooltip_lines):
            text_surface = tooltip_font.render(line, True, (255, 255, 255))
            window.blit(text_surface, (tooltip_x + 10, tooltip_y + 5 + i * 20))

    def buy_upgrade(self):
        global points, total_cookies_earned
        try:
            upgrade_sound = pygame.mixer.Sound("sounds/upgrade_sound.mp3")
            upgrade_sound.set_volume(sound_volume)
        except:
            upgrade_sound = None

        mouse_pos = pygame.mouse.get_pos()
        draw_y = self.y + scroll_offset
        upgrade_rect = pygame.Rect(self.x, draw_y, self.image.get_width(), self.image.get_height())
        if upgrade_rect.collidepoint(mouse_pos):
            if points >= self.price:
                if upgrade_sound:
                    upgrade_sound.play()
                points -= self.price
                self.amount += 1
                self.price = int(self.base_price * (1.15 ** self.amount))
                add_floating_text(self.x + 40, draw_y, f"+1 {self.name}", (100, 255, 100))
                return True

    def gain_upgrades(self):
        global points, cps1, total_cookies_earned
        time2 = pygame.time.get_ticks()
        if time2 - self.time > 1000:
            gain = self.cookie_gain * self.amount
            if gain > 0:
                points += gain
                cps1 += gain
                total_cookies_earned += gain
            self.time = time2


upgrade_spacing = 110
start_y = 50

up_clicker = Upgrades("clicker", 30, start_y, 100, 0, 0, pygame.time.get_ticks(),
                      pygame.image.load("images/up_cursor.png"),
                      pygame.image.load("images/cursor_darker.png"))

up_grandma = Upgrades("grandma", 30, start_y + upgrade_spacing, 100, 1, 0, pygame.time.get_ticks(),
                      pygame.image.load("images/grandma.png"),
                      pygame.image.load("images/grandma_dark.png"))

up_plant = Upgrades("plant", 30, start_y + upgrade_spacing * 2, 1100, 8, 0, pygame.time.get_ticks(),
                    pygame.image.load("images/cookie_plant.png"),
                    pygame.image.load("images/cookie_plant_dark.png"))

up_bakery = Upgrades("bakery", 30, start_y + upgrade_spacing * 3, 12000, 47, 0, pygame.time.get_ticks(),
                     pygame.image.load("images/Bakery.png"),
                     pygame.image.load("images/Bakery_dark.png"))

up_farm = Upgrades("farm", 30, start_y + upgrade_spacing * 4, 130000, 260, 0, pygame.time.get_ticks(),
                   pygame.image.load("images/cookie_farm_icon.png"),
                   pygame.image.load("images/cookie_farm_icon_dark.png"))

up_mine = Upgrades("mine", 30, start_y + upgrade_spacing * 5, 1400000, 1400, 0, pygame.time.get_ticks(),
                   pygame.image.load("images/Cookie_mine.png"),
                   pygame.image.load("images/Cookie_mine_dark.png"))

up_factory = Upgrades("factory", 30, start_y + upgrade_spacing * 6, 20000000, 7800, 0, pygame.time.get_ticks(),
                      pygame.image.load("images/Factory.png"),
                      pygame.image.load("images/Factory_dark.png"))

up_laboratory = Upgrades("laboratory", 30, start_y + upgrade_spacing * 7, 330000000, 44000, 0, pygame.time.get_ticks(),
                         pygame.image.load("images/cookie_labor1.png"),
                         pygame.image.load("images/cookie_labor1_dark.png"))

upgrades = [up_clicker, up_grandma, up_plant, up_bakery, up_farm, up_mine, up_factory, up_laboratory]
for upgrade in upgrades:
    upgrade_data = loaded_data["upgrades"].get(upgrade.name, {})
    upgrade.amount = upgrade_data.get("amount", 0)
    saved_price = upgrade_data.get("price", upgrade.base_price)
    upgrade.price = saved_price

max_scroll = max(0, (len(upgrades) * upgrade_spacing) - 450)

settings_image = None
settings_open = False
music_slider_rect = None
sound_slider_rect = None
save_button_rect = None
reset_button_rect = None
close_button_rect = None
dragging_music = False
dragging_sound = False


def draw_settings_button(window):
    global settings_image
    settings_image = pygame.image.load("images/Settings_image.png")
    window.blit(settings_image, (830, 0))


def draw_settings_menu(window):
    overlay = pygame.Surface((900, 560))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(180)
    window.blit(overlay, (0, 0))

    panel_width = 400
    panel_height = 300
    panel_x = (900 - panel_width) // 2
    panel_y = (560 - panel_height) // 2

    pygame.draw.rect(window, (44, 62, 80), (panel_x, panel_y, panel_width, panel_height))
    pygame.draw.rect(window, (255, 255, 255), (panel_x, panel_y, panel_width, panel_height), 3)

    title_font = pygame.font.Font("freesansbold.ttf", 32)
    title_text = title_font.render("Game Settings", True, (255, 255, 255))
    title_rect = title_text.get_rect(center=(450, panel_y + 40))
    window.blit(title_text, title_rect)

    label_font = pygame.font.Font("freesansbold.ttf", 20)
    music_label = label_font.render("Music Volume:", True, (255, 255, 255))
    window.blit(music_label, (panel_x + 30, panel_y + 80))

    global music_slider_rect
    slider_x = panel_x + 30
    slider_y = panel_y + 110
    slider_width = 340
    slider_height = 10

    pygame.draw.rect(window, (100, 100, 100), (slider_x, slider_y, slider_width, slider_height))

    fill_width = int(slider_width * music_volume)
    pygame.draw.rect(window, (100, 200, 100), (slider_x, slider_y, fill_width, slider_height))

    handle_x = slider_x + fill_width
    pygame.draw.circle(window, (255, 255, 255), (handle_x, slider_y + slider_height // 2), 12)
    music_slider_rect = pygame.Rect(slider_x - 10, slider_y - 10, slider_width + 20, slider_height + 20)

    sound_label = label_font.render("Sound Effects Volume:", True, (255, 255, 255))
    window.blit(sound_label, (panel_x + 30, panel_y + 140))

    global sound_slider_rect
    slider_y = panel_y + 170

    pygame.draw.rect(window, (100, 100, 100), (slider_x, slider_y, slider_width, slider_height))

    # Slider fill
    fill_width = int(slider_width * sound_volume)
    pygame.draw.rect(window, (100, 200, 100), (slider_x, slider_y, fill_width, slider_height))

    handle_x = slider_x + fill_width
    pygame.draw.circle(window, (255, 255, 255), (handle_x, slider_y + slider_height // 2), 12)
    sound_slider_rect = pygame.Rect(slider_x - 10, slider_y - 10, slider_width + 20, slider_height + 20)

    button_font = pygame.font.Font("freesansbold.ttf", 18)
    button_y = panel_y + 230

    global save_button_rect
    save_button_rect = pygame.Rect(panel_x + 30, button_y, 100, 40)
    pygame.draw.rect(window, (70, 130, 180), save_button_rect)
    pygame.draw.rect(window, (255, 255, 255), save_button_rect, 2)
    save_text = button_font.render("Save", True, (255, 255, 255))
    save_text_rect = save_text.get_rect(center=save_button_rect.center)
    window.blit(save_text, save_text_rect)

    global reset_button_rect
    reset_button_rect = pygame.Rect(panel_x + 150, button_y, 100, 40)
    pygame.draw.rect(window, (180, 70, 70), reset_button_rect)
    pygame.draw.rect(window, (255, 255, 255), reset_button_rect, 2)
    reset_text = button_font.render("Reset", True, (255, 255, 255))
    reset_text_rect = reset_text.get_rect(center=reset_button_rect.center)
    window.blit(reset_text, reset_text_rect)

    global close_button_rect
    close_button_rect = pygame.Rect(panel_x + 270, button_y, 100, 40)
    pygame.draw.rect(window, (100, 100, 100), close_button_rect)
    pygame.draw.rect(window, (255, 255, 255), close_button_rect, 2)
    close_text = button_font.render("Close", True, (255, 255, 255))
    close_text_rect = close_text.get_rect(center=close_button_rect.center)
    window.blit(close_text, close_text_rect)


def handle_settings_click(mouse_pos):
    global settings_open, music_volume, sound_volume, dragging_music, dragging_sound
    global points, total_cookies_earned, scroll_offset

    if save_button_rect and save_button_rect.collidepoint(mouse_pos):
        save()
        settings_open = False
        return True

    elif reset_button_rect and reset_button_rect.collidepoint(mouse_pos):
        import os
        if os.path.exists("save_data.json"):
            os.remove("save_data.json")
            points = 0
            total_cookies_earned = 0
            scroll_offset = 0
            for upgrade in upgrades:
                upgrade.amount = 0
                upgrade.price = upgrade.base_price
            save()
        settings_open = False
        return True

    elif close_button_rect and close_button_rect.collidepoint(mouse_pos):
        settings_open = False
        return True

    elif music_slider_rect and music_slider_rect.collidepoint(mouse_pos):
        dragging_music = True
        return True

    elif sound_slider_rect and sound_slider_rect.collidepoint(mouse_pos):
        dragging_sound = True
        return True

    return False


def update_sliders(mouse_pos):
    global music_volume, sound_volume, dragging_music, dragging_sound

    if dragging_music and music_slider_rect:
        slider_x = music_slider_rect.x + 10
        slider_width = music_slider_rect.width - 20
        relative_x = mouse_pos[0] - slider_x
        music_volume = max(0.0, min(1.0, relative_x / slider_width))
        pygame.mixer.music.set_volume(music_volume)

    if dragging_sound and sound_slider_rect:
        slider_x = sound_slider_rect.x + 10
        slider_width = sound_slider_rect.width - 20
        relative_x = mouse_pos[0] - slider_x
        sound_volume = max(0.0, min(1.0, relative_x / slider_width))


def handle_scroll(event):
    global scroll_offset, max_scroll
    if event.type == pygame.MOUSEWHEEL and not settings_open:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if mouse_x < 300:
            scroll_offset += event.y * 30
            scroll_offset = max(-max_scroll, min(0, scroll_offset))


def open_settings():
    global settings_image, settings_open
    if Mouse_pressed:
        mouse_pos = pygame.mouse.get_pos()
        rect = pygame.Rect(830, 0, settings_image.get_width(), settings_image.get_height())
        if rect.collidepoint(mouse_pos):
            settings_open = True


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Cookie Clicker - Enhanced Edition with 8 Upgrades")
        self.window = pygame.display.set_mode((900, 560))
        self.background = pygame.image.load("images/background.png")
        self.clock = pygame.time.Clock()
        self.running = True
        self.fps = 60

        pygame.mixer.init()
        try:
            pygame.mixer.music.load("sounds/Jorge Hernandez - Chopsticks ♫ NO COPYRIGHT 8-bit Music.mp3")
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(music_volume)
        except:
            print("Background music not found")

    def run(self):
        while self.running:
            global shown_cookie, points, Mouse_pressed, dragging_music, dragging_sound, settings_open

            self.window.fill("lightblue")
            self.window.blit(self.background, (0, 0))

            if shown_cookie.target_scale > 1.0:
                shown_cookie.target_scale = 1.0

            cookie_points(self.window)
            show_cps_text(self.window)
            shown_cookie.draw(self.window)
            draw_settings_button(self.window)
            update_floating_texts(self.window)

            if not settings_open:
                for upgrade in upgrades:
                    upgrade.print_upgrade(self.window)
                    upgrade.gain_upgrades()

            show_stats(self.window)

            if settings_open:
                draw_settings_menu(self.window)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    save()
                    self.running = False

                handle_scroll(event)

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    Mouse_pressed = True

                    if settings_open:
                        handle_settings_click(pygame.mouse.get_pos())
                    else:
                        open_settings()

                        for upgrade in upgrades:
                            upgrade.buy_upgrade()

                        if shown_cookie.clicked():
                            shown_cookie = clicked_cookie

                if event.type == pygame.MOUSEBUTTONUP:
                    Mouse_pressed = False
                    shown_cookie = normal_cookie
                    dragging_music = False
                    dragging_sound = False

                if event.type == pygame.MOUSEMOTION:
                    if dragging_music or dragging_sound:
                        update_sliders(pygame.mouse.get_pos())

            cps_update()

            auto_save()
            self.clock.tick(self.fps)
            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    try:
        print("Starting Cookie Clicker...")
        game = Game()
        game.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        input("Press Enter to exit...")