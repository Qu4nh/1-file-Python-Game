import pygame
import sys

# Khai báo các biến toàn cục
WIDTH, HEIGHT = 640, 480
BALL_RADIUS = 10
PADDLE_WIDTH, PADDLE_HEIGHT = 15, 60
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Khởi tạo Pygame
pygame.init()

# Tạo cửa sổ game
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ping Pong Game")

# Khởi tạo các đối tượng trong game
ball = pygame.Rect(WIDTH // 2 - BALL_RADIUS, HEIGHT // 2 - BALL_RADIUS, BALL_RADIUS * 2, BALL_RADIUS * 2)
player_paddle = pygame.Rect(50, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
opponent_paddle = pygame.Rect(WIDTH - 50 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)

# Thiết lập tốc độ di chuyển của quả bóng
ball_speed = [5, 5]

# Thiết lập tốc độ di chuyển của gậy đánh
paddle_speed = 7

# Vòng lặp chính của game
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Xử lý sự kiện nhấn phím
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] and player_paddle.top > 0:
        player_paddle.y -= paddle_speed
    if keys[pygame.K_DOWN] and player_paddle.bottom < HEIGHT:
        player_paddle.y += paddle_speed

    # Di chuyển quả bóng
    ball.x += ball_speed[0]
    ball.y += ball_speed[1]

    # Xử lý va chạm của quả bóng với các biên
    if ball.top <= 0 or ball.bottom >= HEIGHT:
        ball_speed[1] = -ball_speed[1]

    # Xử lý va chạm của quả bóng với gậy đánh người chơi
    if ball.colliderect(player_paddle):
        ball_speed[0] = -ball_speed[0]

    # Xử lý va chạm của quả bóng với gậy đánh đối thủ
    if ball.colliderect(opponent_paddle):
        ball_speed[0] = -ball_speed[0]

    # Di chuyển gậy đánh của đối thủ theo quả bóng
    if opponent_paddle.centery < ball.centery:
        opponent_paddle.y += paddle_speed
    elif opponent_paddle.centery > ball.centery:
        opponent_paddle.y -= paddle_speed

    # Vẽ các đối tượng lên màn hình
    screen.fill(BLACK)
    pygame.draw.ellipse(screen, WHITE, ball)
    pygame.draw.rect(screen, WHITE, player_paddle)
    pygame.draw.rect(screen, WHITE, opponent_paddle)

    # Cập nhật màn hình
    pygame.display.flip()

    # Đặt tốc độ của game
    clock.tick(FPS)
