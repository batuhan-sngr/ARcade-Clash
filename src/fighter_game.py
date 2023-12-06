import cv2
import mediapipe as mp
import pygame
import sys
import random

# Initialize video capture
cap = cv2.VideoCapture(0)  # 0 represents the default camera, you may need to change it based on your setup

# Initialize Mediapipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

# Initialize Pygame
pygame.init()

# Set up display
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("Fighter Game")

# Load images
background = pygame.image.load("images/BG_1.png")
player1_sheet = pygame.image.load("images/spriteSheet1.png")
player2_sheet = pygame.image.load("images/spriteSheet2.png")

# Player positions
player1_x, player1_y = 100, 300
player2_x, player2_y = 600, 300

# Player size
player_size = (64, 64)

# Player speed
player_speed = 2

# Hand landmarks indices
THUMB_TIP = 4
INDEX_FINGER_TIP = 8
PINKY_TIP = 20

# Animation frames and counters
idle_frames = [0, 1, 2, 3, 4, 5]
punch_frames = [6, 7, 8]
shield_frame = 9
damage_frame = 10
super_attack_frames = [11, 12, 13]


player1_action = "idle"
player1_frame = 0
player1_super_attack_count = 0
super_attack_threshold = 3  # Number of successful hits required for superpower

# Health system
player1_health = 100
player1_super_attack_count = 0
super_attack_threshold = 3
damage_per_punch = 18
damage_per_super_attack = 35

# Projectile system
projectile_speed = 5
projectiles = []

# Resize factors for the camera window
camera_width = 200
camera_height = 150

# Animation duration and cooldown
animation_duration = 10  # Adjust as needed
animation_cooldown = 0

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

    # Get hand landmarks
    _, frame = cap.read()
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    # Get hand positions
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            thumb_tip_x = int(hand_landmarks.landmark[THUMB_TIP].x * screen_width)
            thumb_tip_y = int(hand_landmarks.landmark[THUMB_TIP].y * screen_height)
            index_finger_tip_x = int(hand_landmarks.landmark[INDEX_FINGER_TIP].x * screen_width)
            index_finger_tip_y = int(hand_landmarks.landmark[INDEX_FINGER_TIP].y * screen_height)
            pinky_tip_x = int(hand_landmarks.landmark[PINKY_TIP].x * screen_width)
            pinky_tip_y = int(hand_landmarks.landmark[PINKY_TIP].y * screen_height)

             # Check hand gestures and trigger animations
            if thumb_tip_y > index_finger_tip_y and thumb_tip_y > pinky_tip_y and player1_action != "punch":
                player1_action = "shield"
            elif index_finger_tip_y > thumb_tip_y and index_finger_tip_y > pinky_tip_y and player1_action != "shield":
                player1_action = "punch"
            elif pinky_tip_y > thumb_tip_y and pinky_tip_y > index_finger_tip_y and player1_super_attack_count >= super_attack_threshold and player1_action != "shield" and player1_action != "punch":
                player1_action = "superpower"
            elif player1_action not in ["punch", "superpower"]:
                player1_action = "idle"

            # Determine hand shape
            if thumb_tip_y < index_finger_tip_y and thumb_tip_y < pinky_tip_y:
                hand_shape = "fist"
            elif thumb_tip_y > index_finger_tip_y and thumb_tip_y > pinky_tip_y:
                hand_shape = "all fingers up"
            elif thumb_tip_x < index_finger_tip_x and thumb_tip_x < pinky_tip_x:
                hand_shape = "pinky finger"
            elif thumb_tip_x > index_finger_tip_x and thumb_tip_x > pinky_tip_x:
                hand_shape = "index finger"
            else:
                hand_shape = "unknown"

            # Draw hand landmarks on the screen
            for lm in hand_landmarks.landmark:
                lm_x = int(lm.x * screen_width)
                lm_y = int(lm.y * screen_height)
                pygame.draw.circle(screen, (255, 0, 0), (lm_x, lm_y), 5)

            # Display hand shape
            font = pygame.font.Font(None, 36)
            text = font.render(f"Hand Shape: {hand_shape}", True, (0, 0, 0))
            screen.blit(text, (10, 10))

    # Resize the camera window
    small_frame = cv2.resize(frame, (camera_width, camera_height))
    small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    small_frame = pygame.surfarray.make_surface(small_frame)

    # Update player animation frames
    if animation_cooldown == 0:
        if player1_action == "idle":
            player1_frame = (player1_frame + 1) % len(idle_frames)
        elif player1_action == "punch":
            player1_frame = (player1_frame + 1) % len(punch_frames)
            # Deal damage to the opponent
            player1_health = max(0, player1_health - damage_per_punch)
            animation_cooldown = animation_duration
        elif player1_action == "shield":
            player1_frame = shield_frame
            animation_cooldown = animation_duration
        elif player1_action == "superpower" and player1_super_attack_count >= super_attack_threshold:
            player1_frame = (player1_frame + 1) % len(super_attack_frames)
            # Deal damage to the opponent
            player1_health = max(0, player1_health - damage_per_super_attack)
            animation_cooldown = animation_duration

        if player1_action in ["punch", "superpower"]:
            # Set cooldown for the next action
            animation_cooldown = animation_duration

    # Draw background and players with actions
    screen.fill((255, 255, 255))  # Fill with white to clear previous frames
    screen.blit(background, (0, 0))

    # Draw player1 with action
    if player1_action == "idle":
        player1_rect = pygame.Rect(idle_frames[player1_frame] * 64, 0, 64, 64)
        player1_rect.inflate_ip(20, 20)  # Increase player size slightly
        player1_rect.clamp_ip(player1_sheet.get_rect())
        screen.blit(player1_sheet.subsurface(player1_rect), (player1_x - 10, player1_y - 10))
    elif player1_action == "punch":
        player1_rect = pygame.Rect(punch_frames[player1_frame] * 64, 0, 64, 64)
        player1_rect.inflate_ip(20, 20)
        player1_rect.clamp_ip(player1_sheet.get_rect())
        screen.blit(player1_sheet.subsurface(player1_rect), (player1_x - 10, player1_y - 10))
    elif player1_action == "shield":
        player1_rect = pygame.Rect(shield_frame * 64, 0, 64, 64)
        player1_rect.inflate_ip(20, 20)
        player1_rect.clamp_ip(player1_sheet.get_rect())
        screen.blit(player1_sheet.subsurface(player1_rect), (player1_x - 10, player1_y - 10))
    elif player1_action == "superpower":
        player1_rect = pygame.Rect(super_attack_frames[player1_frame] * 64, 0, 64, 64)
        player1_rect.inflate_ip(20, 20)
        player1_rect.clamp_ip(player1_sheet.get_rect())
        screen.blit(player1_sheet.subsurface(player1_rect), (player1_x - 10, player1_y - 10))

    # Draw camera feed in the left bottom corner
    screen.blit(small_frame, (0, screen_height - camera_height))

    # Draw health bar for player1
    pygame.draw.rect(screen, (255, 0, 0), (screen_width - 120, 10, 100, 20))  # Red background
    pygame.draw.rect(
        screen,
        (0, 255, 0),
        (screen_width - 120, 10, max(0, (player1_health / 100) * 100), 20),
    )  # Green health bar
    # Display health text
    font = pygame.font.Font(None, 36)
    text = font.render(f"Health: {player1_health}", True, (0, 0, 0))
    screen.blit(text, (screen_width - 200, 10))

    # Generate projectiles
    if random.randint(0, 100) < 5:  # Adjust the probability based on your preference
        projectile = pygame.Rect(screen_width - 20, random.randint(0, screen_height - 20), 10, 10)
        projectiles.append(projectile)

    # Move projectiles
    for projectile in projectiles:
        projectile.x -= projectile_speed

        # Check if the projectile hits the player1
        if player1_rect.colliderect(projectile):
            if player1_action != "shield":
                player1_health = max(0, player1_health - 20)
            projectiles.remove(projectile)

    # Draw projectiles
    for projectile in projectiles:
        pygame.draw.rect(screen, (0, 0, 255), projectile)

    # Remove projectiles that go off the screen
    projectiles = [p for p in projectiles if p.x > 0]

    # Optional: Add a delay to control the speed of the game
    pygame.time.delay(20)

    # Update display
    pygame.display.flip()

    # Generate projectiles
    if random.randint(0, 100) < 5:  # Adjust the probability based on your preference
        projectile = pygame.Rect(player2_x + player_size[0], player2_y, 10, 10)
        projectiles.append(projectile)

    # Move projectiles
    for projectile in projectiles:
        projectile.x -= projectile_speed

        # Check if the projectile hits the player1
        if player1_rect.colliderect(projectile):
            if player1_action != "shield":
                player1_health = max(0, player1_health - 20)
            projectiles.remove(projectile)

    # Draw projectiles
    for projectile in projectiles:
        pygame.draw.rect(screen, (0, 0, 255), projectile)

    # Remove projectiles that go off the screen
    projectiles = [p for p in projectiles if p.x > 0]

    # Optional: Add a delay to control the speed of the game
    pygame.time.delay(20)
