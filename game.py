import os
# os.environ["MEDIAPIPE_GPU"] = "0"  
if "MEDIAPIPE_GPU" in os.environ:
    del os.environ["MEDIAPIPE_GPU"]

import cv2
import time
import pickle
import random
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from geometry import extract_feature

latest_result = None
#async callback fn
def on_hand_landmarks_ready(result: vision.HandLandmarkerResult, output_image: mp.Image, timestamp_mp: int):
    global latest_result
    latest_result = result


# Particle class for organic chaos energy sparks
class EnergyParticle:
    def __init__(self, x, y, color):
        self.x = float(x)
        self.y = float(y)
        angle = random.uniform(0, 2 * np.pi)
        speed = random.uniform(40, 200)
        self.vx = np.cos(angle) * speed
        self.vy = np.sin(angle) * speed
        self.life = random.uniform(0.3, 0.7)
        self.max_life = self.life
        self.color = color
        self.size = random.randint(3, 8)

    def update_and_draw(self, canvas, dt, target_pos=None, implode=False):
        if implode and target_pos is not None:
            tx, ty = target_pos
            dx, dy = tx - self.x, ty - self.y
            dist = max(1.0, np.sqrt(dx**2 + dy**2))
            self.vx += (dx / dist) * 600.0 * dt
            self.vy += (dy / dist) * 600.0 * dt
            self.vx *= 0.88
            self.vy *= 0.88
        else:
            self.vx += random.uniform(-100, 100) * dt
            self.vy += random.uniform(-100, 100) * dt
            self.vx *= 0.94
            self.vy *= 0.94

        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt

        if self.life > 0:
            alpha = self.life / self.max_life
            r = max(1, int(self.size * alpha))
            col = (int(self.color[0] * alpha), int(self.color[1] * alpha), int(self.color[2] * alpha))
            cv2.circle(canvas, (int(self.x), int(self.y)), r, col, -1, cv2.LINE_AA)
            return True
        return False


def draw_chaos_lightning(canvas, p1, p2, color, thickness=2, num_displacements=4, max_displacement=15):
    """Generates chaotic jagged energy arcs between two points."""
    pts = [p1]
    
    # Recursive/Segmented displacement logic for lightning
    segments = [(p1, p2)]
    for _ in range(num_displacements):
        next_segments = []
        for s_start, s_end in segments:
            mid_x = (s_start[0] + s_end[0]) / 2.0
            mid_y = (s_start[1] + s_end[1]) / 2.0
            
            # Offset perpendicular to segment
            dx = s_end[0] - s_start[0]
            dy = s_end[1] - s_start[1]
            dist = max(1.0, np.sqrt(dx**2 + dy**2))
            
            nx = -dy / dist
            ny = dx / dist
            
            disp = random.uniform(-max_displacement, max_displacement)
            mid_x += nx * disp
            mid_y += ny * disp
            
            mid_pt = (int(mid_x), int(mid_pt_y := mid_y))
            next_segments.append((s_start, mid_pt))
            next_segments.append((mid_pt, s_end))
        segments = next_segments

    # Extract ordered points
    lightning_pts = [segments[0][0]] + [s[1] for s in segments]
    pts_arr = np.array(lightning_pts, np.int32)
    cv2.polylines(canvas, [pts_arr], isClosed=False, color=color, thickness=thickness, lineType=cv2.LINE_AA)


def draw_wanda_magic(canvas, palm_center, hand_landmarks, prediction, rotation_angle, W, H, particles):
    cx, cy = palm_center
    
    # BGR Colors: Crimson Core, Bright Magenta Flame, Wanda Red
    MAGENTA = (220, 20, 255)
    CRIMSON = (30, 0, 255)
    SCARLET = (80, 50, 255)
    CYAN_ELECTRIC = (255, 255, 0)

    # Pixel coords for key landmarks
    wrist = (int(hand_landmarks[0].x * W), int(hand_landmarks[0].y * H))
    thumb = (int(hand_landmarks[4].x * W), int(hand_landmarks[4].y * H))
    index = (int(hand_landmarks[8].x * W), int(hand_landmarks[8].y * H))
    middle = (int(hand_landmarks[12].x * W), int(hand_landmarks[12].y * H))
    ring = (int(hand_landmarks[16].x * W), int(hand_landmarks[16].y * H))
    pinky = (int(hand_landmarks[20].x * W), int(hand_landmarks[20].y * H))

    tips = [thumb, index, middle, ring, pinky]

    # --- GESTURE 1: OPEN PALM (Full Chaos Energy Blast) ---
    if prediction == 1:
        # 1. Pulsing Core Aura
        core_r = int(35 + 10 * np.sin(np.radians(rotation_angle * 4)))
        cv2.circle(canvas, (cx, cy), core_r, CRIMSON, -1, cv2.LINE_AA)
        cv2.circle(canvas, (cx, cy), int(core_r * 0.6), MAGENTA, -1, cv2.LINE_AA)

        # 2. Organic Energy Tendrils connecting Palm to Fingertips
        for tip in tips:
            draw_chaos_lightning(canvas, (cx, cy), tip, color=SCARLET, thickness=2, num_displacements=3, max_displacement=12)
            cv2.circle(canvas, tip, random.randint(6, 12), MAGENTA, -1, cv2.LINE_AA)

        # 3. Dynamic Radial Flame Ribbons
        num_ribbons = 8
        for i in range(num_ribbons):
            base_angle = rotation_angle * 1.5 + (i * 360.0 / num_ribbons)
            ribbon_pts = []
            for r_step in range(10, 90, 10):
                # Swirling logarithmic spiral formula
                a = np.radians(base_angle + r_step * 0.8)
                rx = int(cx + r_step * np.cos(a))
                ry = int(cy + r_step * np.sin(a))
                ribbon_pts.append([rx, ry])
            cv2.polylines(canvas, [np.array(ribbon_pts, np.int32)], isClosed=False, color=SCARLET, thickness=3, lineType=cv2.LINE_AA)

        # Emit burst particles
        for _ in range(8):
            particles.append(EnergyParticle(cx, cy, SCARLET))

    # --- GESTURE 0: FIST (Gravity Implosion / Dark Scarlet Sphere) ---
    elif prediction == 0:
        cv2.circle(canvas, (cx, cy), 25, CRIMSON, -1, cv2.LINE_AA)
        cv2.circle(canvas, (cx, cy), 15, (0, 0, 180), -1, cv2.LINE_AA)
        
        # Dense orbital energy rings
        for r_offset in [30, 45, 60]:
            cv2.ellipse(canvas, (cx, cy), (r_offset, int(r_offset * 0.4)), int(rotation_angle * 2), 0, 360, MAGENTA, 2, cv2.LINE_AA)

        # Spawn surrounding particles pulling INWARD
        for _ in range(6):
            spawn_a = random.uniform(0, 2 * np.pi)
            spawn_r = random.uniform(70, 130)
            sx = cx + np.cos(spawn_a) * spawn_r
            sy = cy + np.sin(spawn_a) * spawn_r
            particles.append(EnergyParticle(sx, sy, CRIMSON))

    # --- GESTURE 2: PINCH (Concentrated Energy Beam / Hex Sigil) ---
    elif prediction == 2:
        px, py = int((index[0] + thumb[0]) / 2), int((index[1] + thumb[1]) / 2)
        cv2.circle(canvas, (px, py), 12, MAGENTA, -1, cv2.LINE_AA)
        cv2.circle(canvas, (px, py), 6, (255, 255, 255), -1, cv2.LINE_AA)

        # Arcs linking thumb & index tip
        draw_chaos_lightning(canvas, thumb, index, color=CYAN_ELECTRIC, thickness=2, num_displacements=3, max_displacement=8)

        for _ in range(4):
            particles.append(EnergyParticle(px, py, CYAN_ELECTRIC))

    # --- GESTURE 3: PEACE (Dual Energy Streams / Wanda Tiara Motif) ---
    elif prediction == 3:
        for tip in [index, middle]:
            cv2.circle(canvas, tip, 10, MAGENTA, -1, cv2.LINE_AA)
            draw_chaos_lightning(canvas, wrist, tip, color=SCARLET, thickness=2, num_displacements=3, max_displacement=15)
            for _ in range(3):
                particles.append(EnergyParticle(tip[0], tip[1], SCARLET))


def run_game():
    model_path = 'gesture_model.pkl'
    task_path = 'hand_landmarker.task'

    if not os.path.exists(model_path) or not os.path.exists(task_path):
        print("[ERROR] Missing required model files!")
        return

    with open(model_path, 'rb') as f:
        model = pickle.load(f)

    options = vision.HandLandmarkerOptions(
        base_options=python.BaseOptions(
            model_asset_path=task_path,
            delegate=python.BaseOptions.Delegate.GPU
        ),
        running_mode=vision.RunningMode.LIVE_STREAM,
        num_hands=2,
        min_hand_detection_confidence=0.7,
        min_tracking_confidence=0.7,
        result_callback=on_hand_landmarks_ready
    )

    W, H = 640, 480
    cap = cv2.VideoCapture(0)

    try:
        if not cap.isOpened():
            raise RuntimeError("No functional camera detected on index 0")

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, W)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, H)

        with vision.HandLandmarker.create_from_options(options) as landmarker:
            print("\n=== WANDA MAXIMOFF CHAOS MAGIC ENGINE RUNNING ===")
            print("Press 'q' to quit Game Mode\n")

            particles = []
            rotation = 0.0
            last_timestamp_ms = 0
            prev_time = time.time()

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                curr_time = time.time()
                dt = curr_time - prev_time
                prev_time = curr_time
                rotation = (rotation + dt * 120.0) % 360.0

                frame = cv2.flip(frame, 1)

                rgba_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGBA, data=rgba_frame)

                timestamp_ms = int(time.time() * 1000)
                if timestamp_ms <= last_timestamp_ms:
                    timestamp_ms = last_timestamp_ms + 1
                last_timestamp_ms = timestamp_ms

                landmarker.detect_async(mp_image, timestamp_ms)

                # Isolated layer for drawing pure energy
                magic_layer = np.zeros_like(frame, dtype=np.uint8)

                prediction = None
                palm_center = (0, 0)

                if latest_result and latest_result.hand_landmarks and len(latest_result.hand_landmarks) > 0:
                    active_landmarks = latest_result.hand_landmarks[0]
                    features = extract_feature(active_landmarks)

                    if features is not None:
                        features_arr = np.array(features).reshape(1, -1)
                        prediction = model.predict(features_arr)[0]

                        wrist = np.array([active_landmarks[0].x * W, active_landmarks[0].y * H])
                        index_tip = np.array([active_landmarks[8].x * W, active_landmarks[8].y * H])
                        middle_tip = np.array([active_landmarks[12].x * W, active_landmarks[12].y * H])

                        palm_center = (int((wrist[0] + index_tip[0] + middle_tip[0]) / 3),
                                       int((wrist[1] + index_tip[1] + middle_tip[1]) / 3))

                        # Draw Wanda Chaos Graphics
                        draw_wanda_magic(magic_layer, palm_center, active_landmarks, prediction, rotation, W, H, particles)

                # --- Update & Render Particles ---
                alive_particles = []
                is_fist = (prediction == 0)
                for p in particles:
                    if p.update_and_draw(magic_layer, dt, target_pos=palm_center, implode=is_fist):
                        alive_particles.append(p)
                particles = alive_particles

                # --- Triple-Pass Bloom Glow Effect ---
                # Pass 1: Soft broad crimson halo
                halo_glow = cv2.GaussianBlur(magic_layer, (35, 35), 0)
                # Pass 2: Intense vibrant core glow
                core_glow = cv2.GaussianBlur(magic_layer, (15, 15), 0)

                # Blending: Original frame + sharp magic + broad halo + core bloom
                combined = cv2.add(frame, magic_layer)
                combined = cv2.addWeighted(combined, 1.0, halo_glow, 0.8, 0)
                output = cv2.addWeighted(combined, 1.0, core_glow, 0.6, 0)

                cv2.imshow("Wanda Chaos Magic Engine", output)

                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break

    except Exception as e:
        print(f"An error occurred during game mode: {e}")

    finally:
        if cap is not None and cap.isOpened():
            cap.release()
        cv2.destroyAllWindows()
        print("Wanda Engine Exited Cleanly.")


if __name__ == "__main__":
    run_game()