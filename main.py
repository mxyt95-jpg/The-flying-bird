import random
import sys
import os
import pygame
from pygame.locals import *

pygame.init()

# === PATH SETTINGS ===
ASSET_PATH = r"C:\Users\Abhishek\OneDrive\Desktop\first py\gamegg.py\sprites"
AUDIO_PATH = r"C:\Users\Abhishek\OneDrive\Desktop\first py\gamegg.py\audio"
HIGHSCORE_FILE = "highscore.txt"

# === GAME CONSTANTS ===
FPS = 32
SCREENWIDTH = 289
SCREENHEIGHT = 511
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
GROUNDY = SCREENHEIGHT * 0.8

GAME_SPRITES = {}
GAME_SOUNDS = {}
PLAYER = 'yellowbird-midflap.png'
BACKGROUND = 'background-day.png'
PIPE = 'pipe-green.png'

def load_highscore():
    if not os.path.exists(HIGHSCORE_FILE):
        with open(HIGHSCORE_FILE, 'w') as f:
            f.write("0")
        return 0
    with open(HIGHSCORE_FILE, 'r') as f:
        try:
            return int(f.read().strip())
        except:
            return 0

def save_highscore(score):
    with open(HIGHSCORE_FILE, 'w') as f:
        f.write(str(score))

def show_text(text, x, y, size=24):
    font = pygame.font.SysFont("Arial", size, bold=True)
    label = font.render(str(text), True, (255, 255, 255))
    SCREEN.blit(label, (x, y))

def welcomeScreen(highscore):
    playerx = int(SCREENWIDTH / 5)
    playery = int((SCREENHEIGHT - GAME_SPRITES['player'].get_height()) / 2)
    messagex = int((SCREENWIDTH - GAME_SPRITES['message'].get_width()) / 2)
    messagey = int(SCREENHEIGHT * 0.13)
    basex = 0
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                return
            else:
                SCREEN.blit(GAME_SPRITES['background'], (0, 0))
                SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))
                SCREEN.blit(GAME_SPRITES['message'], (messagex, messagey))
                SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))
                show_text(f"High Score: {highscore}", 10, 10, 22)
                pygame.display.update()
                FPSCLOCK.tick(FPS)

def mainGame(highscore):
    score = 0
    playerx = int(SCREENWIDTH / 5)
    playery = int(SCREENHEIGHT / 2)
    basex = 0

    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    upperPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[0]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[0]['y']},
    ]
    lowerPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[1]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[1]['y']},
    ]

    pipeVelX = -4
    playerVelY = -9
    playerMaxVelY = 10
    playerMinVelY = -8
    playerAccY = 1
    playerFlapAccv = -8
    playerFlapped = False

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery > 0:
                    playerVelY = playerFlapAccv
                    playerFlapped = True
                    GAME_SOUNDS['wing'].play()

        crashTest = isCollide(playerx, playery, upperPipes, lowerPipes)
        if crashTest:
            GAME_SOUNDS['die'].play()
            return score

        playerMidPos = playerx + GAME_SPRITES['player'].get_width() / 2
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + GAME_SPRITES['pipe'][0].get_width() / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                score += 1
                GAME_SOUNDS['point'].play()

        if playerVelY < playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY
        if playerFlapped:
            playerFlapped = False
        playerHeight = GAME_SPRITES['player'].get_height()
        playery = playery + min(playerVelY, GROUNDY - playery - playerHeight)

        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            upperPipe['x'] += pipeVelX
            lowerPipe['x'] += pipeVelX

        if 0 < upperPipes[0]['x'] < 5:
            newPipe = getRandomPipe()
            upperPipes.append(newPipe[0])
            lowerPipes.append(newPipe[1])

        if upperPipes[0]['x'] < -GAME_SPRITES['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)

        SCREEN.blit(GAME_SPRITES['background'], (0, 0))
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(GAME_SPRITES['pipe'][0], (upperPipe['x'], upperPipe['y']))
            SCREEN.blit(GAME_SPRITES['pipe'][1], (lowerPipe['x'], lowerPipe['y']))
        SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))
        SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))

        # Draw scores
        show_text(f"Score: {score}", 10, 10, 22)
        show_text(f"High: {highscore}", 200, 10, 22)

        pygame.display.update()
        FPSCLOCK.tick(FPS)

def isCollide(playerx, playery, upperPipes, lowerPipes):
    if playery > GROUNDY - 25 or playery < 0:
        GAME_SOUNDS['hit'].play()
        return True
    for pipe in upperPipes:
        pipeHeight = GAME_SPRITES['pipe'][0].get_height()
        if (playery < pipeHeight + pipe['y']) and (abs(playerx - pipe['x']) < GAME_SPRITES['pipe'][0].get_width()):
            GAME_SOUNDS['hit'].play()
            return True
    for pipe in lowerPipes:
        if (playery + GAME_SPRITES['player'].get_height() > pipe['y']) and (abs(playerx - pipe['x']) < GAME_SPRITES['pipe'][0].get_width()):
            GAME_SOUNDS['hit'].play()
            return True
    return False

def getRandomPipe():
    pipeHeight = GAME_SPRITES['pipe'][0].get_height()
    # Increase gap between pipes (was SCREENHEIGHT/3 before)
    offset = SCREENHEIGHT / 2.8  
    y2 = offset + random.randrange(0, int(SCREENHEIGHT - GAME_SPRITES['base'].get_height() - 1.5 * offset))
    pipeX = SCREENWIDTH + 10
    y1 = pipeHeight - y2 + offset
    return [{'x': pipeX, 'y': -y1}, {'x': pipeX, 'y': y2}]

if __name__ == "__main__":
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_caption('Flappy Bird')

    GAME_SPRITES['numbers'] = tuple(
        pygame.image.load(f"{ASSET_PATH}/{i}.png").convert_alpha() for i in range(10)
    )
    GAME_SPRITES['message'] = pygame.image.load(f"{ASSET_PATH}/message.png").convert_alpha()
    GAME_SPRITES['base'] = pygame.image.load(f"{ASSET_PATH}/base.png").convert_alpha()
    GAME_SPRITES['pipe'] = (
        pygame.transform.rotate(pygame.image.load(f"{ASSET_PATH}/{PIPE}").convert_alpha(), 180),
        pygame.image.load(f"{ASSET_PATH}/{PIPE}").convert_alpha(),
    )

    GAME_SPRITES['background'] = pygame.image.load(f"{ASSET_PATH}/{BACKGROUND}").convert_alpha()
    GAME_SPRITES['player'] = pygame.image.load(f"{ASSET_PATH}/{PLAYER}").convert_alpha()

    GAME_SOUNDS['die'] = pygame.mixer.Sound(f"{AUDIO_PATH}/die.wav")
    GAME_SOUNDS['hit'] = pygame.mixer.Sound(f"{AUDIO_PATH}/hit.wav")
    GAME_SOUNDS['point'] = pygame.mixer.Sound(f"{AUDIO_PATH}/point.wav")
    GAME_SOUNDS['swoosh'] = pygame.mixer.Sound(f"{AUDIO_PATH}/swoosh.wav")
    GAME_SOUNDS['wing'] = pygame.mixer.Sound(f"{AUDIO_PATH}/wing.wav")

    highscore = load_highscore()

    while True:
        welcomeScreen(highscore)
        score = mainGame(highscore)
        if score > highscore:
            highscore = score
            save_highscore(highscore)