import pygame, sys, random
import numpy as np
import pyaudio
import struct
import signal

# Cấu hình PyAudio
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)


# Hàm lọc thông thấp
def low_pass_filter(data, cutoff=1000.0, fs=44100.0, order=5):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
    y = signal.lfilter(b, a, data)
    return y


# Tạo hàm để lấy mức độ âm thanh từ microphone
def get_audio_level():
    data = stream.read(CHUNK, exception_on_overflow=False)
    data = struct.unpack(str(CHUNK) + 'h', data)  # 'h' is for int16
    data = np.array(data, dtype='int16')
    peak = np.abs(data).mean()
    return peak


# TẠO HÀM CHO GAME

# hàm sàn
def ve_san():
    screen.blit(floor, (floor_x_pos, 650))
    screen.blit(floor, (floor_x_pos + 432, 650))


# hàm ống
def create_pipe():
    random_pipe_pos = random.choice(pipe_height)
    duoi_pipe_hitbox = pipe_surface.get_rect(midtop=(500, random_pipe_pos))
    tren_pipe_hitbox = pipe_surface.get_rect(midtop=(500, random_pipe_pos - 650))

    return duoi_pipe_hitbox, tren_pipe_hitbox


def move_pipe(pipes):
    for pipe in pipes:
        pipe.centerx -= 6
    return pipes


def draw_pipe(pipes):
    for pipe in pipes:
        if pipe.bottom >= 500:
            screen.blit(pipe_surface, pipe)
        else:
            flip_pipe = pygame.transform.flip(pipe_surface, False, True)
            screen.blit(flip_pipe, pipe)


# hàm check va chạm
def check_va_cham(pipes):
    for pipe in pipes:
        if bird_hitbox.colliderect(pipe):
            return False
    if bird_hitbox.top <= -75 or bird_hitbox.bottom >= 650:
        return False
    return True


# hàm tạo animation cho chim
def rotate_bird(bird1):
    new_bird = pygame.transform.rotozoom(bird1, -bird_movement * 3, 1)
    return new_bird


# hàm tạo điểm
def score_display(game_state):
    if game_state == 'main game':
        score_surface = game_font.render(str(int(score)), True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(216, 100))
        screen.blit(score_surface, score_rect)
    if game_state == 'game over':
        score_surface = game_font.render(f'Score: {int(score)}', True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(216, 100))
        screen.blit(score_surface, score_rect)

        high_score_surface = game_font.render(f'High Score: {int(high_score)}', True, (255, 255, 255))
        high_score_rect = high_score_surface.get_rect(center=(216, 630))
        screen.blit(high_score_surface, high_score_rect)


def update_score(score, high_score):
    if score > high_score:
        high_score = score
    return high_score


pygame.init()
screen = pygame.display.set_mode((432, 768))
clock = pygame.time.Clock()
game_font = pygame.font.Font('04B_19.TTF', 40)

#  TẠO BIẾN GAME
trong_luc = 0.45
bird_movement = 0
game_active = True
score = 0
high_score = 0
# chèn background
bg = pygame.image.load('framework/background-night.jpg').convert()
bg = pygame.transform.scale2x(bg)
# chèn sàn
floor = pygame.image.load('framework/floor.png').convert()
floor = pygame.transform.scale2x(floor)
floor_x_pos = 0
# tạo chim
bird = pygame.image.load('framework/yellowbird-midflap.png').convert_alpha()
bird = pygame.transform.scale2x(bird)
bird_hitbox = bird.get_rect(center=(100, 384))
# tạo ống
pipe_surface = pygame.image.load('framework/1.png').convert_alpha()
pipe_surface = pygame.transform.scale2x(pipe_surface)
pipe_list = []
# Tạo timer
spawnpipe = pygame.USEREVENT
pygame.time.set_timer(spawnpipe, 1200)
pipe_height = [200, 300, 400]
# tạo màn hình kết thúc
game_over_surface = pygame.image.load('framework/gameover.png').convert_alpha()
game_over_surface = pygame.transform.scale2x(game_over_surface)
game_over_rect = game_over_surface.get_rect(center=(216, 384))
# WHILE LOOP CỦA TRÒ CHƠI
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_active:
                continue
            if event.key == pygame.K_SPACE and game_active == False:
                game_active = True
                pipe_list.clear()
                bird_hitbox.center = (125, 384)
                bird_movement = 0
                score = 0
        if event.type == spawnpipe:
            pipe_list.extend(create_pipe())

    screen.blit(bg, (0, 0))

    if game_active:
        # Lấy mức độ âm thanh từ microphone
        audio_level = get_audio_level()

        # Điều chỉnh vận tốc di chuyển của chim dựa trên mức độ âm thanh
        if audio_level > 600:  # Điều chỉnh ngưỡng tùy theo mức độ nhạy của microphone
            bird_movement = -7.25  # Điều chỉnh vận tốc nhảy của chim

        # chim
        bird_movement += trong_luc
        xoay_bird = rotate_bird(bird)
        bird_hitbox.centery += bird_movement
        screen.blit(xoay_bird, bird_hitbox)
        game_active = check_va_cham(pipe_list)
        # ống
        pipe_list = move_pipe(pipe_list)
        draw_pipe(pipe_list)
        score += 0.0125
        score_display('main game')
    else:
        screen.blit(game_over_surface, game_over_rect)
        high_score = update_score(score, high_score)
        score_display('game over')
    # sàn
    floor_x_pos -= 1
    ve_san()
    # chuyển 2 sàn để lặp lại nhau
    if floor_x_pos <= -432:
        floor_x_pos = 0
    pygame.display.update()
    clock.tick(100)

# Kết thúc PyAudio khi thoát khỏi vòng lặp chính
stream.stop_stream()
stream.close()
p.terminate()
