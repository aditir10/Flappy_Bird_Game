import random
import sys
import pygame
from pygame.locals import *

# Global variables
FPS = 32
SCREENWIDTH = 500
SCREENHEIGHT = 500
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))

GAME_SPRITES = {}
GAME_SOUNDS = {}
PLAYER = 'gallery/new_sprites/bird.png'
BACKGROUND = 'gallery/sprites/background.png'
PIPE = 'gallery/new_sprites/pipe.png'

# Ghost Mode variables
GHOST_DURATION = 3000  # milliseconds
GHOST_COOLDOWN = 5000  # milliseconds

def welcomeScreen():
    playerx = int(SCREENWIDTH / 5)
    playery = int((SCREENHEIGHT - GAME_SPRITES['player'].get_height()) / 2)
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
                SCREEN.blit(GAME_SPRITES['player'], (playerx, playery - 20))
                player_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
                player_surface.blit(GAME_SPRITES['player'], (0, 0))
                SCREEN.blit(player_surface, (playerx, playery))
                SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))
                pygame.display.update()
                FPSCLOCK.tick(FPS)

def mainGame():
    score = 0
    playerx = int(SCREENWIDTH / 5)
    playery = int(SCREENWIDTH / 2)
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

    ghost_mode = False
    ghost_start_time = 0
    last_ghost_used = -GHOST_COOLDOWN

    while True:
        current_time = pygame.time.get_ticks()

        if ghost_mode and current_time - ghost_start_time > GHOST_DURATION:
            ghost_mode = False

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                if event.key == K_SPACE or event.key == K_UP:
                    if playery > 0:
                        playerVelY = playerFlapAccv
                        playerFlapped = True
                        GAME_SOUNDS['wing'].play()
                       
                elif event.key == K_g and current_time - last_ghost_used >= GHOST_COOLDOWN:
                    ghost_mode = True
                    ghost_start_time = current_time
                    last_ghost_used = current_time
                    print("Ghost Mode Activated!")

        if not ghost_mode:
            crashTest = isCollide(playerx, playery, upperPipes, lowerPipes)
            if crashTest:
                return

        playerMidPos = playerx + GAME_SPRITES['player'].get_width() / 2
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + GAME_SPRITES['pipe'][0].get_width() / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                score += 1
                print(f"Your score is {score}")
                GAME_SOUNDS['point'].play()

        if playerVelY < playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY

        if playerFlapped:
            playerFlapped = False

        playerHeight = GAME_SPRITES['player'].get_height()
        playery = playery + min(playerVelY, GROUNDY - playery - playerHeight)

        for upperPipe, lowerpipe in zip(upperPipes, lowerPipes):
            upperPipe['x'] += pipeVelX
            lowerpipe['x'] += pipeVelX

        if 0 < upperPipes[0]['x'] < 5:
            newpipe = getRandomPipe()
            upperPipes.append(newpipe[0])
            lowerPipes.append(newpipe[1])

        if upperPipes[0]['x'] < -GAME_SPRITES['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)

        SCREEN.blit(GAME_SPRITES['background'], (0, 0))

        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(GAME_SPRITES['pipe'][0], (upperPipe['x'], upperPipe['y']))
            SCREEN.blit(GAME_SPRITES['pipe'][1], (lowerPipe['x'], lowerPipe['y']))

        SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))

        if ghost_mode:
            ghost_surface = GAME_SPRITES['player'].copy()
            ghost_surface.set_alpha(100)
            SCREEN.blit(ghost_surface, (playerx, playery))
        else:
            SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))

        myDigits = [int(x) for x in list(str(score))]
        width = sum(GAME_SPRITES['numbers'][digit].get_width() for digit in myDigits)
        Xoffset = (SCREENWIDTH - width) / 2

        for digit in myDigits:
            SCREEN.blit(GAME_SPRITES['numbers'][digit], (Xoffset, SCREENHEIGHT * 0.12))
            Xoffset += GAME_SPRITES['numbers'][digit].get_width()

        pygame.display.update()
        FPSCLOCK.tick(FPS)

def isCollide(playerx, playery, upperPipes, lowerPipes):
    if playery > GROUNDY - 25 or playery < 0:
        GAME_SOUNDS['hit'].play()
        return True

    for pipe in upperPipes:
        pipeHeight = GAME_SPRITES['pipe'][0].get_height()
        if playery < pipeHeight + pipe['y'] and abs(playerx - pipe['x']) < GAME_SPRITES['pipe'][0].get_width():
            GAME_SOUNDS['hit'].play()
            return True

    for pipe in lowerPipes:
        if playery + GAME_SPRITES['player'].get_height() > pipe['y'] and abs(playerx - pipe['x']) < GAME_SPRITES['pipe'][0].get_width():
            GAME_SOUNDS['hit'].play()
            return True

    return False

def getRandomPipe():
    pipeHeight = GAME_SPRITES['pipe'][0].get_height()
    offset = SCREENHEIGHT / 3
    y2 = offset + random.randrange(0, int(SCREENHEIGHT - GAME_SPRITES['base'].get_height() - 1.2 * offset))
    pipeX = SCREENWIDTH + 10
    y1 = pipeHeight - y2 + offset
    pipe = [
        {'x': pipeX, 'y': -y1},
        {'x': pipeX, 'y': y2}
    ]
    return pipe

if __name__ == "__main__":
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_caption('Flappy Bird from NAA')

    GAME_SPRITES['numbers'] = tuple(
        pygame.image.load(f'gallery/new_sprites/{i}.png').convert_alpha() for i in range(10)
    )

    GAME_SPRITES['base'] = pygame.image.load("gallery/sprites/base.png").convert_alpha()
    GAME_SPRITES['pipe'] = (
        pygame.transform.rotate(pygame.image.load(PIPE).convert_alpha(), 180),
        pygame.image.load(PIPE).convert_alpha()
    )

    GAME_SOUNDS['die'] = pygame.mixer.Sound('gallery/audio/die.mp3')
    GAME_SOUNDS['hit'] = pygame.mixer.Sound('gallery/audio/hit.mp3')
    GAME_SOUNDS['point'] = pygame.mixer.Sound('gallery/audio/point.mp3')
    GAME_SOUNDS['swoosh'] = pygame.mixer.Sound('gallery/audio/swoosh.mp3')
    GAME_SOUNDS['wing'] = pygame.mixer.Sound('gallery/audio/wing.mp3')
    GAME_SOUNDS['bgm'] = pygame.mixer.Sound('gallery/audio/bgm.mp3')

    GAME_SPRITES['player'] = pygame.image.load(PLAYER).convert_alpha()
    GAME_SPRITES['player'] = pygame.transform.scale(GAME_SPRITES['player'], (50, 50))
    GAME_SPRITES['background'] = pygame.image.load(BACKGROUND).convert()
    GAME_SPRITES['background'] = pygame.transform.scale(GAME_SPRITES['background'], (SCREENWIDTH, SCREENHEIGHT))

    GROUNDY = SCREENHEIGHT - GAME_SPRITES['base'].get_height()

    while True:
        welcomeScreen()
        mainGame()
