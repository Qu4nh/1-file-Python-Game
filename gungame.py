import pygame
import sys
import math
import random

pygame.init()

# Cấu hình màn hình trò chơi
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Trò chơi bắn súng")

# Màu sắc
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Người chơi
player_width, player_height = 50, 50
player_x, player_y = (screen_width - player_width) // 2, (screen_height - player_height) // 2
player_speed = 5
player_slide_speed = player_speed*2  # Tốc độ lướt chậm hơn (có thể tùy chỉnh)
player_direction = 0, 0  # Hướng di chuyển ban đầu của người chơi
player_is_sliding = False
slide_duration = 100  # Thời gian lướt (500 milliseconds = 0.5 giây)
slide_cooldown = 2000  # Thời gian hồi phục sau khi lướt (2000 milliseconds = 2 giây)
last_slide_time = pygame.time.get_ticks()
energy = 100  # Năng lượng ban đầu
energy_regen_rate = 10  # Tốc độ hồi phục năng lượng (mỗi giây)

# Máu người chơi
player_health = 100

enemy_speeds = [2, 3, 4, 5]

# Đạn
bullet_radius = 5
bullet_speed = 10

class Bullet:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction

    def update(self):
        self.x += self.direction[0] * bullet_speed
        self.y += self.direction[1] * bullet_speed

    def draw(self):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), bullet_radius)

# Màu sắc của các kiểu kẻ địch
enemy_colors = {'small': RED, 'medium': (255, 165, 0), 'large': (255, 0, 255), 'boss': (255, 0, 0)}

# Địch
enemy_widths = {'small': 30, 'medium': 40, 'large': 50, 'boss': 100}  # Đổi kích thước của từng loại kẻ địch
enemy_heights = {'small': 30, 'medium': 40, 'large': 50, 'boss': 100}

enemy_types = ['small', 'medium', 'large', 'boss']
enemy_spawn_rates = [0.6, 0.3, 0.1, 0]
enemy_spawn_rate_multiplier = 1.2
enemy_max_healths = {'small': 50, 'medium': 100, 'large': 150, 'boss': 500}

# Boss
boss_width, boss_height = 100, 100
boss_spawn_rate = 0  # Tỷ lệ xuất hiện của boss (1/10 wave)
boss_max_health = 500  # Máu tối đa của boss

enemies_for_money = []

# Hằng số điều chỉnh hành vi di chuyển của kẻ địch
SEPARATION_RADIUS = 50  # Bán kính tách biệt
COHESION_RADIUS = 100   # Bán kính hội tụ
ALIGNMENT_RADIUS = 80   # Bán kính căn chỉnh
SEPARATION_FORCE = 1.5  # Lực tách biệt
COHESION_FORCE = 0.8    # Lực hội tụ
ALIGNMENT_FORCE = 1.0   # Lực căn chỉnh

# Enemy
class Enemy:
    def __init__(self, enemy_type):
        self.enemy_type = enemy_type
        self.width = enemy_widths[enemy_type]  # Thay 'enemy_width' thành 'enemy_widths'
        self.height = enemy_heights[enemy_type]  # Thay 'enemy_height' thành 'enemy_heights'

        # Ngẫu nhiên chọn một trong bốn vị trí xung quanh người chơi
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            self.x = random.randint(0, screen_width - self.width)
            self.y = -self.height
        elif side == 'bottom':
            self.x = random.randint(0, screen_width - self.width)
            self.y = screen_height
        elif side == 'left':
            self.x = -self.width
            self.y = random.randint(0, screen_height - self.height)
        else:
            self.x = screen_width
            self.y = random.randint(0, screen_height - self.height)

        self.health = enemy_max_healths[self.enemy_type]
        self.speed = enemy_speeds[enemy_types.index(self.enemy_type)]  # Tốc độ di chuyển của bot

        self.money = self.health // 4        

        self.spawn_time = pygame.time.get_ticks()  # Thời gian khi kẻ địch được sinh ra
        self.can_drop_money = random.random() < 0.7  # Có khả năng rơi tiền, 70% tỷ lệ

    def update(self):
        # Di chuyển đến vị trí của người chơi
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance > 0:
            # Nếu cách xa người chơi, di chuyển theo hướng của người chơi
            self.x += dx / distance * self.speed
            self.y += dy / distance * self.speed
        else:
            # Nếu đã đạt gần người chơi, thì di chuyển ngẫu nhiên
            self.x += random.uniform(-self.speed, self.speed)
            self.y += random.uniform(-self.speed, self.speed)

        # Kiểm tra va chạm với các kẻ địch khác
        for enemy in enemies:
            if enemy != self:
                dx = enemy.x - self.x
                dy = enemy.y - self.y
                distance = math.sqrt(dx ** 2 + dy ** 2)
                if distance < self.width:
                    # Tránh va chạm bằng cách di chuyển ra xa kẻ địch
                    self.x -= dx / distance * (self.width - distance) / 2
                    self.y -= dy / distance * (self.width - distance) / 2

        self.existence_time = pygame.time.get_ticks()
    def draw(self):
        # Vẽ kẻ địch với màu dựa vào loại kẻ địch
        color = enemy_colors[self.enemy_type]
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))

        if self.can_drop_money:
            pygame.draw.rect(screen, (255, 255, 0), (self.x - 2, self.y - 2, enemy_widths[self.enemy_type] + 4, enemy_heights[self.enemy_type] + 4), 3)  # Viền màu vàng cho kẻ địch có khả năng rơi tiền

    def draw_health_bar(self):
        health_bar_width = enemy_widths[self.enemy_type]
        health_bar_height = 5
        health_bar_x = self.x
        health_bar_y = self.y - 10
        pygame.draw.rect(screen, RED, (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
        pygame.draw.rect(screen, GREEN, (health_bar_x, health_bar_y, self.health / enemy_max_healths[self.enemy_type] * health_bar_width, health_bar_height))
    def drop_money(self):
        if self in enemies_for_money:
            global player_money
            time_decay = 0.002  # Tỷ lệ giảm số tiền theo thời gian tồn tại (có thể điều chỉnh).
            money_dropped = max(1, self.money - int(self.existence_time * time_decay))
            player_money += money_dropped
            enemies_for_money.remove(self)

# Boss
class Boss(Enemy):
    def __init__(self):
        super().__init__('boss')
        self.health = boss_max_health
        self.speed = 2  # Tốc độ di chuyển của boss (có thể điều chỉnh)

    def update(self):
        # Di chuyển đến vị trí của người chơi
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        if distance != 0:
            self.x += dx / distance * self.speed
            self.y += dy / distance * self.speed

    # Thêm kỹ năng của boss ở đây (ví dụ: bắn đạn, tấn công mạnh, ...)
    def use_skill(self):
        pass
    def drop_money(self):
        if self in enemies_for_money:
            global player_money
            money_dropped = 100  # Số tiền từ boss luôn là 100
            player_money += money_dropped
            enemies_for_money.remove(self)

# Tạo biến boss_spawned để theo dõi xem boss đã xuất hiện trong wave chia hết cho 5 chưa
boss_spawned = False

is_wave_shop = False  # Trạng thái xác định liệu wave shop đang diễn ra hay không
items_to_sell = []    # Danh sách các món hàng để người chơi lựa chọn
selected_items = []   # Danh sách các món hàng đã được người chơi chọn

# Thêm biến player_money để theo dõi số tiền của người chơi
player_money = 0

def generate_shop_items():
    global items_to_sell
    available_items = list(shop_items.keys())
    items_to_sell = random.sample(available_items, 3)

def draw_shop_info():
    font = pygame.font.SysFont(None, 30)
    text_y = 100
    for i, item in enumerate(items_to_sell):
        item_text = font.render(f"{i + 1}. {item}: {shop_items[item]} Money", True, WHITE)
        screen.blit(item_text, (screen_width - item_text.get_width() - 10, text_y))
        text_y += 30

def select_item(item_index):
    global selected_items
    item = items_to_sell[item_index - 1]
    selected_items.append(item)
    items_to_sell.remove(item)

def buy_selected_items():
    global player_money
    for item in selected_items:
        if player_money >= shop_items[item]:
            player_money -= shop_items[item]
            apply_item_effect(item)  # Áp dụng hiệu ứng của món hàng đã mua

def apply_item_effect(item):
    global player_health, energy_regen_rate, bullet_speed, bullet_radius

    if item == "Health Upgrade":
        player_health = min(100, player_health + 25)
    elif item == "Energy Upgrade":
        energy_regen_rate += 5
    elif item == "Bullet Speed Upgrade":
        bullet_speed += 2
    elif item == "Bullet Size Upgrade":
        bullet_radius += 2

def leave_shop():
    global is_wave_shop, selected_items, items_to_sell
    is_wave_shop = False
    selected_items = []
    items_to_sell = []

def draw_player(x, y):
    pygame.draw.rect(screen, BLUE, (x, y, player_width, player_height))

def draw_energy_bar():
    energy_bar_width = 100
    energy_bar_height = 10
    energy_bar_x = 10
    energy_bar_y = 10
    pygame.draw.rect(screen, WHITE, (energy_bar_x, energy_bar_y, energy_bar_width, energy_bar_height))
    pygame.draw.rect(screen, GREEN, (energy_bar_x, energy_bar_y, energy, energy_bar_height))

def draw_health_bar():
    health_bar_width = 100
    health_bar_height = 10
    health_bar_x = 10
    health_bar_y = 30
    pygame.draw.rect(screen, WHITE, (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
    pygame.draw.rect(screen, RED, (health_bar_x, health_bar_y, player_health, health_bar_height))

def game_over(score):
    font = pygame.font.SysFont(None, 100)
    text = font.render("Game Over", True, RED)
    screen.blit(text, (screen_width//2 - text.get_width()//2, screen_height//2 - text.get_height()//2))
    font = pygame.font.SysFont(None, 50)
    score_text = font.render(f"Score: {score}", True, RED)
    screen.blit(score_text, (screen_width//2 - score_text.get_width()//2, screen_height//2 + score_text.get_height()))
    pygame.display.update()
    pygame.time.wait(2000)
    pygame.quit()
    sys.exit()

def aim_closest_enemy(x, y):
    closest_distance = float('inf')
    closest_enemy = None
    for enemy in enemies:
        dx = enemy.x - x
        dy = enemy.y - y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        if distance < closest_distance:
            closest_distance = distance
            closest_enemy = enemy
    if closest_enemy is not None:
        dx = closest_enemy.x - x
        dy = closest_enemy.y - y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        direction = dx / distance, dy / distance
        return direction
    return 0, 0
    
shop_items = {
    "Health Upgrade": 50,
    "Energy Upgrade": 30,
    "Bullet Speed Upgrade": 20,
    "Bullet Size Upgrade": 15
}

# Vòng (wave) và điểm
wave = 0
score = 0
player_money = 0

# Vòng lặp trò chơi
clock = pygame.time.Clock()
bullets = []
enemies = []
can_shoot = True
last_shot_time = pygame.time.get_ticks()

is_resting = False
rest_start_time = 0
rest_duration = 5000  # 5000 milliseconds (5 seconds) thời gian nghỉ giữa các wave

# Hàm tạo cục máu ngẫu nhiên
def spawn_health_pickup():
    x = random.randint(0, screen_width - 20)
    y = random.randint(0, screen_height - 20)
    return x, y

health_pickup_x, health_pickup_y = spawn_health_pickup()

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
while True:
    screen.fill((0, 0, 0))  # Xóa màn hình trước khi vẽ lại

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if not is_wave_shop:  # Nếu không phải wave shop, xử lý các sự kiện liên quan đến người chơi và địch như trước

            # Xử lý sự kiện khi người chơi ấn phím trong wave shop
            if is_wave_shop:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:  # Nếu ấn phím 1
                        select_item(1)
                    elif event.key == pygame.K_2:  # Nếu ấn phím 2
                        select_item(2)
                    elif event.key == pygame.K_3:  # Nếu ấn phím 3
                        select_item(3)
                    elif event.key == pygame.K_RETURN:  # Nếu ấn phím Enter
                        buy_selected_items()
                        leave_shop()

    # Xử lý sự kiện phím di chuyển người chơi
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a] and player_x > 0:
        player_x -= player_speed
        if keys[pygame.K_w] and player_y > 0:
            player_y -= player_speed
            player_direction = -1, -1  # Đi chéo trái lên
        elif keys[pygame.K_s] and player_y < screen_height - player_height:
            player_y += player_speed
            player_direction = -1, 1  # Đi chéo trái xuống
        else:
            player_direction = -1, 0  # Đi sang trái
    elif keys[pygame.K_d] and player_x < screen_width - player_width:
        player_x += player_speed
        if keys[pygame.K_w] and player_y > 0:
            player_y -= player_speed
            player_direction = 1, -1  # Đi chéo phải lên
        elif keys[pygame.K_s] and player_y < screen_height - player_height:
            player_y += player_speed
            player_direction = 1, 1  # Đi chéo phải xuống
        else:
            player_direction = 1, 0  # Đi sang phải
    elif keys[pygame.K_w] and player_y > 0:
        player_y -= player_speed
        player_direction = 0, -1  # Đi lên
    elif keys[pygame.K_s] and player_y < screen_height - player_height:
        player_y += player_speed
        player_direction = 0, 1  # Đi xuống
    else:
        player_direction = 0, 0  # Đứng yên

    # Kiểm tra năng lượng để có thể lướt
    if keys[pygame.K_LSHIFT] and not player_is_sliding and energy >= 10:
        player_speed = player_slide_speed  # Thay đổi tốc độ di chuyển khi lướt
        player_is_sliding = True
        last_slide_time = pygame.time.get_ticks()
        energy -= 10

    # Kiểm tra thời gian lướt
    current_time = pygame.time.get_ticks()
    if current_time - last_slide_time >= slide_duration and player_is_sliding:
        player_speed = 5  # Hồi phục lại tốc độ di chuyển ban đầu
        player_is_sliding = False
    
    # Hồi phục năng lượng
    if energy < 100:
        current_time = pygame.time.get_ticks()
        if current_time - last_slide_time >= slide_cooldown:
            energy += energy_regen_rate

    # Kiểm tra thời gian delay giữa các viên đạn
    current_time = pygame.time.get_ticks()
    if current_time - last_shot_time >= 500:  # 500 milliseconds (0.5 seconds) delay giữa các viên đạn
        can_shoot = True

    # Xử lý sự kiện bắn đạn
    if keys[pygame.K_SPACE] and can_shoot:
        bullet_direction = aim_closest_enemy(player_x + player_width // 2, player_y + player_height // 2)
        bullets.append(Bullet(player_x + player_width // 2, player_y + player_height // 2, bullet_direction))
        can_shoot = False
        last_shot_time = pygame.time.get_ticks()

    # Cập nhật vị trí đạn và vẽ đạn lên màn hình
    for bullet in bullets:
        bullet.update()
        bullet.draw()

    if len(enemies) == 0 and not is_resting:
        is_resting = True
        rest_start_time = pygame.time.get_ticks()
        player_health = min(100, player_health + 20)  # Người chơi hồi phục 20 máu khi vào thời gian nghỉ

    # Kiểm tra thời gian nghỉ
    current_time = pygame.time.get_ticks()
    if is_resting and current_time - rest_start_time >= rest_duration:
        is_resting = False
        # Tạo cục máu mới khi kết thúc thời gian nghỉ
        health_pickup_x, health_pickup_y = spawn_health_pickup()

    # Vẽ cục máu
    if is_resting:
        pygame.draw.rect(screen, GREEN, (health_pickup_x, health_pickup_y, 20, 20))

    # Kiểm tra va chạm giữa người chơi và cục máu
    if is_resting and player_x <= health_pickup_x + 20 and player_x + player_width >= health_pickup_x and \
            player_y <= health_pickup_y + 20 and player_y + player_height >= health_pickup_y:
        # Nếu người chơi va chạm với cục máu thì hồi phục 20 máu
        player_health = min(100, player_health + 20)
        # Tạo cục máu mới sau khi người chơi hồi phục
        health_pickup_x, health_pickup_y = spawn_health_pickup()

    if len(enemies) == 0:
        wave += 1

        if wave % 5 == 0 and not boss_spawned:  # Chỉ spawn boss khi wave chia hết cho 5 và boss chưa xuất hiện trong wave này
            enemies.append(Boss())
            boss_spawned = True  # Đánh dấu boss đã xuất hiện
        elif wave % 5 == 1:  # Nếu wave chia hết cho 5 + 1 (wave shop)
            is_wave_shop = True
            generate_shop_items()
            # Xóa hết các viên đạn và kẻ địch còn tồn tại khi chuyển sang wave shop
            bullets.clear()
            enemies.clear()
        else:
            for _ in range(wave * 2):
                enemy_type = random.choices(enemy_types, enemy_spawn_rates)[0]
                enemies.append(Enemy(enemy_type))

    # Kiểm tra xem còn kẻ địch nào là boss không, nếu không thì đánh dấu boss_spawned thành False để sẵn sàng spawn boss tiếp theo
    if not any(isinstance(enemy, Boss) for enemy in enemies):
        boss_spawned = False

    # Cập nhật vị trí địch và vẽ địch lên màn hình
    for enemy in enemies:
        enemy.update()
        enemy.draw()
        enemy.draw_health_bar()  # Vẽ thanh máu của kẻ địch

    # Kiểm tra va chạm giữa đạn và địch
    for enemy in enemies[:]:
        for bullet in bullets[:]:
            if (enemy.x <= bullet.x <= enemy.x + enemy.width and
                enemy.y <= bullet.y <= enemy.y + enemy.height):
                damage = min(enemy.health, 20)  # Lượng máu cần trừ của kẻ địch khi bị bắn trúng
                enemy.health -= damage

                # Kiểm tra nếu máu của kẻ địch <= 0, tăng điểm cho người chơi và xóa kẻ địch
                if enemy.health <= 0:
                    score_multiplier = 1  # Hệ số nhân điểm tùy thuộc vào loại kẻ địch
                    if enemy.enemy_type == 'small':
                        score_multiplier = 1
                    elif enemy.enemy_type == 'medium':
                        score_multiplier = 2
                    elif enemy.enemy_type == 'large':
                        score_multiplier = 3
                    elif enemy.enemy_type == 'boss':
                        score_multiplier = 5
                    if enemy.can_drop_money:
                        enemies_for_money.append(enemy)
                    score += 10 * score_multiplier  # Người chơi được cộng điểm khi bắn trúng kẻ địch
                    enemies.remove(enemy)
                    
                bullets.remove(bullet)

    # Kiểm tra va chạm giữa người chơi và kẻ địch
        for enemy in enemies[:]:
            for enemy in enemies[:]:
                if (player_x <= enemy.x + enemy_widths[enemy.enemy_type] and player_x + player_width >= enemy.x and
                    player_y <= enemy.y + enemy_heights[enemy.enemy_type] and player_y + player_height >= enemy.y):
                    damage = enemy.health // 4  # Lượng máu bị trừ là 1/4 máu còn lại của địch
                    player_health -= damage
                    enemies.remove(enemy)
                    if player_health <= 0:
                        game_over(score)
            draw_energy_bar()
            draw_health_bar()

     # Vẽ người chơi lên màn hình sau đó vẽ đạn để người chơi nằm trên đạn
    draw_player(player_x, player_y)
    # Xử lý việc rơi tiền khi kẻ địch bị tiêu diệt
    for enemy in enemies_for_money[:]:
        enemy.drop_money()
    # Hiển thị số vòng và điểm lên màn hình
    font = pygame.font.SysFont(None, 30)
    wave_text = font.render(f"Wave: {wave}", True, WHITE)
    screen.blit(wave_text, (10, screen_height - 40))
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, screen_height - 70))
    
    # Hiển thị số tiền của người chơi
    money_text = font.render(f"Money: {player_money}", True, WHITE)
    screen.blit(money_text, (10, screen_height - 100))


    pygame.display.update()
    clock.tick(60)  # Giới hạn tốc độ khung hình
