import cv2
import mediapipe as mp
import pygame
import sys
import os
import math

class FighterGame:
    def __init__(self):
        
        self.cap = cv2.VideoCapture(1)  # 0 represents the default camera, you may need to change it based on your setup
        self.ret, self.frame = self.cap.read()

        # Initialize Mediapipe
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands()

        # Initialize Pygame
        pygame.init()

        # Set up display
        self.screen_width, self.screen_height = 1410, 940  # Adjusted to match the new background image
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
        pygame.display.set_caption("ARcade Clash")

        self.background = pygame.image.load("images/background.png")
        self.background = pygame.transform.scale(self.background, (self.screen_width, self.screen_height))

        # Load frames for each action
        self.idle_frames_player = self.load_frames("Brawler Girl", "idle", 4)
        self.hurt_frames_player = self.load_frames("Brawler Girl", "hurt", 2)
        self.punch_frames_player = self.load_frames("Brawler Girl", "punch", 3)
        self.kick_frames_player = self.load_frames("Brawler Girl", "kick", 5)
        self.walk_frames_player = self.load_frames("Brawler Girl", "walk", 10)
        
        # Load frames for each action for Enemy (Enemy Punk)
        self.idle_frames_enemy = self.load_frames("Enemy Punk", "idle", 4)
        self.hurt_frames_enemy = self.load_frames("Enemy Punk", "hurt", 4)
        self.punch_frames_enemy = self.load_frames("Enemy Punk", "punch", 3)
        self.walk_frames_enemy = self.load_frames("Enemy Punk", "walk", 4)



        # Player attributes
        self.player1_action = "idle"
        self.player1_frame = 0
        self.player1_health = 100
        self.player1_rect = pygame.Rect(0, 0, 64, 47)  # Initialize player1_rect
        self.player1_x, self.player1_y = 300, 750
        self.animation_cooldown_player = 0

        # Enemy attributes
        self.enemy_action = "idle"
        self.enemy_frame = 0
        self.enemy_health = 100
        self.enemy_rect = pygame.Rect(0, 0, 64, 47)  # Initialize enemy_rect
        self.enemy_x, self.enemy_y = 600, 750
        self.animation_cooldown_enemy = 0
        self.enemy_speed = 2

        # Player speed
        self.player_speed = 2

        # Hand landmarks indices
        self.THUMB_TIP = 4
        self.THUMB_MCP = 2
        self.THUMB_CMC = 1
        self.INDEX_FINGER_TIP = 8
        self.INDEX_FINGER_PIP = 6
        self.INDEX_FINGER_MCP = 5
        self.PINKY_TIP = 20
        self.PINKY_DIP = 19
        self.WRIST = 0
        self.MIDDLE_FINGER_TIP = 12

        # Damage values
        self.damage_per_punch = 18
        self.damage_per_kick = 35

        # Resize factors for the camera window
        self.camera_width = 200
        self.camera_height = 150

        # Animation duration and cooldown
        self.animation_duration = 2  # Adjust as needed
        self.animation_cooldown = 0

        # Initialize animation variables for player and enemy
        self.current_action_player = "idle"
        self.current_frame_player = 0
        self.action_counter_player = 0

        self.current_action_enemy = "idle"
        self.current_frame_enemy = 0
        self.action_counter_enemy = 0

        # Update actions_info_player and actions_info_enemy with the loaded frames
        self.actions_info_player = {
            "idle": {"frames": self.idle_frames_player, "cooldown": self.animation_duration},
            "punch": {"frames": self.punch_frames_player, "cooldown": self.animation_duration},
            "kick": {"frames": self.kick_frames_player, "cooldown": self.animation_duration},
            "hurt": {"frames": self.hurt_frames_player, "cooldown": self.animation_duration},
            "walk": {"frames": self.walk_frames_player, "cooldown": self.animation_duration},
        }

        self.actions_info_enemy = {
            "idle": {"frames": self.idle_frames_enemy, "cooldown": self.animation_duration},
            "punch": {"frames": self.punch_frames_enemy, "cooldown": self.animation_duration},
            "hurt": {"frames": self.hurt_frames_enemy, "cooldown": self.animation_duration},
            "walk": {"frames": self.walk_frames_enemy, "cooldown": self.animation_duration},
        }


    def load_frames(self, character, action, frame_count):
        frames = []
        for i in range(1, frame_count + 1):
            frame_path = os.path.join("images", character, action, f"{action}{i}.png")
            frame = pygame.image.load(frame_path).convert_alpha()
            frames.append(frame)
        return frames

    def extract_frame(self, action, frame_index, is_player=True):
        if is_player:
            info = self.actions_info_player.get(action)
        else:
            info = self.actions_info_enemy.get(action)

        if info:
            frames = info.get("frames")
            if frames:
                return frames[frame_index % len(frames)]  # Ensure the index is within the frame count
            else:
                print(f"Error: No frames found for action - {action}")
        else:
            print(f"Error: Unknown action - {action}")
        return None

    def calculate_distance(self, point1, point2):
        return math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)

    def run_game(self):
        punch_cooldown = 5000  # Set the punch cooldown in milliseconds (adjust as needed)
        hurt_cooldown = 500  # Set the hurt animation cooldown in milliseconds (adjust as needed)
        enemy_walk_cooldown = 500  # milliseconds (adjust as needed)
        last_punch_time = pygame.time.get_ticks()
        last_hurt_time = 0
        last_enemy_walk_time = 0

        # Cooldown for player actions
        player_action_cooldown = 500  # milliseconds (adjust as needed)
        last_player_action_time = 0

        # Adjust the punch collision detection
        punch_collision_rect = pygame.Rect(
            self.player1_x + self.player1_rect.width,  # Adjusted to the right edge of the player
            self.player1_y + self.player1_rect.height * 0.2,  # Adjusted for the punch height
            10,  # Width of the punch
            self.player1_rect.height * 0.6,  # Adjusted for the punch height
        )        

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

            _, self.frame = self.cap.read()
            frame_rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(frame_rgb)

            self.frame.flags.writeable = True

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    thumb_tip = (hand_landmarks.landmark[self.THUMB_TIP].x, hand_landmarks.landmark[self.THUMB_TIP].y)
                    thumb_mcp = (hand_landmarks.landmark[self.THUMB_MCP].x, hand_landmarks.landmark[self.THUMB_MCP].y)
                    thumb_cmc = (hand_landmarks.landmark[self.THUMB_CMC].x, hand_landmarks.landmark[self.THUMB_CMC].y)
                    index_finger_tip = (hand_landmarks.landmark[self.INDEX_FINGER_TIP].x, hand_landmarks.landmark[self.INDEX_FINGER_TIP].y)
                    index_finger_mcp = (hand_landmarks.landmark[self.INDEX_FINGER_MCP].x, hand_landmarks.landmark[self.INDEX_FINGER_MCP].y)
                    index_finger_pip = (hand_landmarks.landmark[self.INDEX_FINGER_PIP].x, hand_landmarks.landmark[self.INDEX_FINGER_PIP].y)
                    pinky_tip = (hand_landmarks.landmark[self.PINKY_TIP].x, hand_landmarks.landmark[self.PINKY_TIP].y)
                    pinky_dip = (hand_landmarks.landmark[self.PINKY_DIP].x, hand_landmarks.landmark[self.PINKY_DIP].y)
                    wrist = (hand_landmarks.landmark[self.WRIST].x, hand_landmarks.landmark[self.WRIST].y)
                    middle_tip = (hand_landmarks.landmark[self.MIDDLE_FINGER_TIP].x, hand_landmarks.landmark[self.MIDDLE_FINGER_TIP].y)

                    thumb_tip_to_index_mcp_distance = self.calculate_distance(thumb_tip, index_finger_mcp)
                    index_tip_to_wrist_distance = self.calculate_distance(index_finger_tip, wrist)
                    index_finger_tip_to_pinky_tip_distance = self.calculate_distance(index_finger_tip, pinky_tip)
                    pinky_tip_to_dip_distance = self.calculate_distance(pinky_tip, pinky_dip)
                    pinky_tip_to_wrist_distance = self.calculate_distance(pinky_dip, wrist)
                    thumb_tip_to_wrist_distance = self.calculate_distance(thumb_tip, wrist)
                    middle_tip_to_wrist_distance = self.calculate_distance(middle_tip, wrist)
                    # Check for cooldown on player actions
                    current_time = pygame.time.get_ticks()
                    if current_time - last_player_action_time < player_action_cooldown:
                        continue  # Skip the rest of the loop if the player is on cooldown



                    if current_time - last_punch_time > punch_cooldown:
                        if index_tip_to_wrist_distance > 0.3 and middle_tip_to_wrist_distance > 0.3:
                            self.player1_action = "walk"
                            self.player1_x += self.player_speed
                        elif thumb_tip_to_index_mcp_distance < 0.15:
                            self.player1_action = "punch"
                            # Check for collision with the enemy when punching
                            if self.player1_action == "punch" and punch_collision_rect.colliderect(self.enemy_rect):
                                self.enemy_health -= self.damage_per_punch
                                self.enemy_action = "hurt"
                                last_hurt_time = current_time
                                print("Enemy Health:", self.enemy_health)

                                # Set cooldown for player actions
                                last_player_action_time = current_time
                        elif thumb_tip_to_wrist_distance > 0.35 and pinky_tip_to_wrist_distance > 0.5:
                            self.player1_action = "kick"
                        elif all(lm.y < thumb_tip[1] for lm in hand_landmarks.landmark[1:]):
                            self.player1_action = "idle"
                    
                    # Check for cooldown on hurt animation
                    if current_time - last_hurt_time > hurt_cooldown:
                        # If enemy health is zero, keep hurt animation at the last frame
                        if self.enemy_health > 0:
                            self.enemy_action = "idle"
                            # Reset cooldown for player actions when hurt animation is complete
                            last_player_action_time = 0

                    self.mp_drawing.draw_landmarks(
                        self.frame,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_drawing_styles.get_default_hand_landmarks_style(),
                        self.mp_drawing_styles.get_default_hand_connections_style())
            else:
                self.player1_action = "idle"
                print("No hands detected.")

            print("Player Action:", self.player1_action)
            print("Player Frame:", self.player1_frame)

            small_frame = cv2.resize(self.frame, (self.camera_width, self.camera_height))
            small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            small_frame = pygame.surfarray.make_surface(small_frame)
            self.frame = cv2.rotate(self.frame, cv2.ROTATE_90_CLOCKWISE)

            if self.player1_action != self.current_action_player:
                # Reset the animation variables when a new action is detected
                self.current_action_player = self.player1_action
                self.current_frame_player = 0
                self.action_counter_player = 0

            # Update player animation frames
            if self.animation_cooldown_player == 0 and self.player1_action != "idle":
                self.current_frame_player = (self.current_frame_player + 1) % len(self.actions_info_player[self.player1_action]["frames"])

            # Handle player animation cooldown
            if self.animation_cooldown_player > 0:
                self.animation_cooldown_player -= 1

            # Update enemy animation frames
            if self.animation_cooldown_enemy == 0:
                if self.enemy_action == "idle":
                    self.enemy_frame = (self.enemy_frame + 1) % len(self.idle_frames_enemy)
                elif self.enemy_action == "hurt" and self.enemy_health > 0:
                    # Keep the hurt animation at the last frame if enemy health is zero
                    self.enemy_frame = min(self.enemy_frame, len(self.hurt_frames_enemy) - 1)
                else:
                    self.enemy_frame = (self.enemy_frame + 1) % len(
                        self.actions_info_enemy[self.enemy_action]["frames"])

            # Handle enemy animation cooldown
            if self.animation_cooldown_enemy > 0:
                self.animation_cooldown_enemy -= 1

            # Check for cooldown on enemy walking
            current_time = pygame.time.get_ticks()
            if current_time - last_enemy_walk_time > enemy_walk_cooldown:
                # Walk towards the player
                if self.enemy_x < self.player1_x:
                    self.enemy_x += self.enemy_speed
                elif self.enemy_x > self.player1_x:
                    self.enemy_x -= self.enemy_speed

                # Reset cooldown for enemy walking
                last_enemy_walk_time = current_time

            # Check for cooldown on player actions
            if current_time - last_player_action_time < player_action_cooldown:
                continue  # Skip the rest of the loop if the player is on cooldown

            # Adjust the punch collision detection for the enemy
            punch_collision_rect_enemy = pygame.Rect(
                self.enemy_x - 10,  # Adjusted to the left edge of the enemy
                self.enemy_y + self.enemy_rect.height * 0.2,  # Adjusted for the punch height
                10,  # Width of the punch
                self.enemy_rect.height * 0.6,  # Adjusted for the punch height
            )

            # Check for punch action
            if current_time - last_punch_time > punch_cooldown:
                self.enemy_action = "punch"
                # Check for collision with the player when punching
                if self.enemy_action == "punch" and punch_collision_rect_enemy.colliderect(player_rect):
                    self.player1_health -= self.damage_per_punch
                    self.player1_action = "hurt"
                    last_hurt_time = current_time
                    print("Player Health:", self.player1_health)

                    # Set cooldown for player actions
                    last_player_action_time = current_time

                # Reset cooldown for punch action
                last_punch_time = current_time

            # Check for cooldown on hurt animation
            if current_time - last_hurt_time > hurt_cooldown:
                # If player health is zero, keep hurt animation at the last frame
                if self.player1_health > 0:
                    self.player1_action = "idle"
                    # Reset cooldown for player actions when hurt animation is complete
                    last_player_action_time = 0

            # Collision detection between player and enemy
            player_rect = pygame.Rect(self.player1_x, self.player1_y, 35, 47)
            enemy_rect = pygame.Rect(self.enemy_x, self.enemy_y, 35, 47)

            if player_rect.colliderect(enemy_rect):
                # Adjust player position to prevent overlap
                if self.player1_x < self.enemy_x:
                    self.player1_x = self.enemy_x - 38
                else:
                    self.player1_x = self.enemy_x + 38

            self.screen.fill((36, 36, 36))
            self.screen.blit(self.background, (0, 0))

            # Draw player1 with action
            if self.player1_rect:
                current_frame_player = self.extract_frame(self.player1_action, self.current_frame_player, is_player=True)
                self.screen.blit(current_frame_player, (self.player1_x - 10, self.player1_y - 10))

            self.screen.blit(small_frame, (0, self.screen_height - self.camera_height))

            pygame.draw.rect(self.screen, (255, 0, 0), (self.screen_width - 120, 10, 100, 20))
            pygame.draw.rect(
                self.screen,
                (0, 255, 0),
                (self.screen_width - 120, 10, max(0, (self.player1_health / 100) * 100), 20),
            )
            font = pygame.font.Font(None, 36)
            text = font.render(f"{self.player1_health}", True, (0, 0, 0))
            self.screen.blit(text, (self.screen_width - 200, 10))

           # Draw enemy with action
            if self.enemy_rect:
                current_frame = self.extract_frame(self.enemy_action, self.enemy_frame, is_player=False)
                self.screen.blit(current_frame, (self.enemy_x - 10, self.enemy_y - 10))


            pygame.time.delay(20)
            pygame.display.flip()

if __name__ == "__main__":
    game = FighterGame()
    game.run_game()