from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random

camera_offset_z = 0.0          
camera_rotation_offset = 0.0   # Manual rotation around player
CAMERA_MOVE_SPEED = 3.0        # How fast camera moves up/down
CAMERA_ROTATE_SPEED = 2.0      # How fast camera rotates
CAMERA_ZOOM_SPEED = 5.0        # How fast camera zooms



#  BOMB SYSTEM 
player_bombs = 0
MAX_BOMBS = 3
thrown_bombs = []
BOMB_SPEED = 8.0
BOMB_EXPLOSION_RADIUS = 120
BOMB_THROW_COOLDOWN = 30
bomb_cooldown = 0

# FLOATING TEXT FLAGS =====
show_hp_text_timer = 0
show_fuel_text_timer = 0

FLOAT_TEXT_DURATION = 40



PLAYER_COLLISION_RADIUS = 30
ENEMY_COLLISION_RADIUS = 28
COLLISION_PUSH = 0.55


# ===== HP HEAL VISUAL EFFECT =====
hp_heal_effect_timer = 0
HP_HEAL_EFFECT_DURATION = 20

# ===== FUEL REPAIR VISUAL EFFECT =====
fuel_repair_effect_timer = 0
FUEL_REPAIR_EFFECT_DURATION = 8   # short, refreshes while refueling

# Bomb pickups on map
bomb_pickups = []
# ===== KEY STATE TRACKING =====
keys_pressed = {
    b'w': False, b'W': False,
    b'a': False, b'A': False,
    b's': False, b'S': False,   # brake
    b'd': False, b'D': False,
    b'b': False, b'B': False    # NEW: backward
}

# ===== CHECKPOINT KILL REQUIREMENT =====
ENEMIES_REQUIRED_PER_CHECKPOINT = 3
enemies_killed_since_checkpoint = 0

# ===== CAMERA MODES =====
first_person_mode = False
# ===== CAMERA SHAKE =====
camera_shake_timer = 0
CAMERA_SHAKE_DURATION = 12     # frames
CAMERA_SHAKE_INTENSITY = 6.0   # units

# ===== SLOW MOTION =====
slow_motion = False
SLOW_MOTION_FACTOR = 0.60   


shift_pressed = False

# ===== GAME STATE =====
player_x, player_y, player_z = 0.0, 0.0, 0.0
player_angle = 0.0
player_speed = 0.0
player_max_speed = 8.0
player_nitro_speed = 15.0
player_acceleration = 1.0
player_deceleration = 0.2
player_rotation_speed = 3.5

player_hp = 3  
player_max_hp = 3
player_hit_flash = 0  
FLASH_DURATION = 12    

player_defeated = False
defeat_timer = 0      
DEFAT_DURATION = 60    
player_defeat_angle = 0 

ghost_cars = []
MAX_GHOSTS = 2
GHOST_LIFETIME = 300

HP_HEAL_AMOUNT = 1
HP_HEALER_COOLDOWN = 360

time_left = 60.0
TIME_PER_CHECKPOINT = 12
TIME_DRAIN_RATE = 0.02

# ===== LIVES / RESPAWN SYSTEM =====
MAX_LIVES = 3
player_lives = MAX_LIVES

last_checkpoint_state = None


missiles = []
missile_speed = 12.0
missile_cooldown = 0
MISSILE_COOLDOWN_MAX = 15

BOUNDARY_SIZE = 1600
CORNER_OFFSET = 200
CORNER_POS = BOUNDARY_SIZE - CORNER_OFFSET

fuel = 100.0
max_fuel = 100.0
fuel_consumption_normal = 0.015
fuel_consumption_nitro = 0.08
is_boosting = False

camera_distance = 250.0
camera_height = 150.0

dune_time = 0.0
dune_speed = 0.03

enemy_cars = []
for i in range(5):
    angle = (i * 72) * math.pi / 180
    distance = 400 + random.randint(0, 150)
    enemy_cars.append({
        'x': math.cos(angle) * distance,
        'y': math.sin(angle) * distance,
        'z': 0.0,
        'angle': random.uniform(0, 360),
        'speed': 1.2 + random.uniform(0, 0.4),
        'color': (random.uniform(0.4, 0.9), random.uniform(0.4, 0.9), random.uniform(0.4, 0.9)),
        'chase_cooldown': 0,
        'missile_cooldown': 0
    })

enemy_missiles = []
enemy_missile_speed = 10.0
ENEMY_MISSILE_COOLDOWN = 180

repair_drones = [
    {'x': CORNER_POS, 'y': CORNER_POS, 'z': 50.0, 'rotation': 0.0, 'active': True, 'bob_phase': random.uniform(0, math.pi)},
    {'x': -CORNER_POS, 'y': -CORNER_POS, 'z': 50.0, 'rotation': 0.0, 'active': True, 'bob_phase': random.uniform(0, math.pi)}
]

hp_healers = [
    {'x': -CORNER_POS, 'y': CORNER_POS, 'z': 0.0, 'active': True, 'cooldown': 0, 'pulse': random.uniform(0, 2 * math.pi)},
    {'x': CORNER_POS, 'y': -CORNER_POS, 'z': 0.0, 'active': True, 'cooldown': 0, 'pulse': random.uniform(0, 2 * math.pi)}
]

cheat_mode = False
game_over = False
game_time = 0
checkpoints = []
# ===== SAND PITS =====
sand_pits = []
SAND_PIT_RADIUS = 150
SAND_PIT_SINK_RATE = 0.008
player_scale = 1.0  # Track player shrinking
MIN_PLAYER_SCALE = 0.3
SCALE_RECOVERY_RATE = 0.008

# ===== DRAWING FUNCTIONS =====

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    """
    Draw text with proper line spacing
    Supports multi-line text with \n
    """
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Fixed line height for consistent spacing
    line_height = 22  # Standard spacing for HELVETICA_18
    
    # Split text into lines if it contains \n
    lines = text.split('\n')
    
    # Draw each line with consistent spacing
    for i, line in enumerate(lines):
        # Calculate Y position (going downward for each line)
        line_y = y - (i * line_height)
        
        glRasterPos2f(x, line_y)
        for ch in line:
            glutBitmapCharacter(font, ord(ch))
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
def draw_missile(x, y, z, angle):
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(angle, 0, 0, 1)
    glColor3f(0.9, 0.8, 0.2)
    glPushMatrix()
    glScalef(0.4, 0.2, 0.2)
    glutSolidCube(8)
    glPopMatrix()
    glColor3f(1, 0.9, 0.1)
    glPushMatrix()
    glTranslatef(5, 0, 0)
    glRotatef(-90, 0, 1, 0)
    glutSolidCone(4, 8, 8, 1)
    glPopMatrix()
    glColor3f(0.7, 0.6, 0.1)
    for i in range(4):
        glPushMatrix()
        glRotatef(i * 90, 1, 0, 0)
        glTranslatef(-4, 3, 0)
        glScalef(0.1, 0.8, 0.3)
        glutSolidCube(6)
        glPopMatrix()
    glPopMatrix()

#Dynamic Terrain Heights.generates a height value that changes over time
def calculate_dune_height(x, y, time):
    wave1 = math.sin(x * 0.006 + time * 0.8) * 28
    wave2 = math.cos(y * 0.005 - time * 0.6) * 24
    wave3 = math.sin((x + y) * 0.003 + time * 0.4) * 18
    wave4 = math.cos((x - y) * 0.004 - time * 0.3) * 14
    return max(wave1 + wave2 + wave3 + wave4, -8)

#get_dune_normal.calculates the differences in height between surrounding points
def get_dune_normal(x, y, time, sample=8.0):
    hL = calculate_dune_height(x - sample, y, time)
    hR = calculate_dune_height(x + sample, y, time)
    hD = calculate_dune_height(x, y - sample, time)
    hU = calculate_dune_height(x, y + sample, time)

    nx = hL - hR
    ny = hD - hU
    nz = 2.0 * sample

    length = math.sqrt(nx*nx + ny*ny + nz*nz)
    return nx/length, ny/length, nz/length

def normal_to_angles(nx, ny, nz):
    pitch = math.degrees(math.atan2(nx, nz))   # forward/back tilt
    roll  = math.degrees(math.atan2(ny, nz))   # side tilt
    return pitch, roll

#Ghost cars appear to shrink and expand in size due to the continuous change in their scale_phase, which affects the size of the cars
def draw_ghost_car(x, y, z, angle, scale, pulse):
    glPushMatrix()

    # ===== Hover + pulse =====
    hover = math.sin(pulse * 1.8) * 5
    glTranslatef(x, y, z + 8 + hover)
    glRotatef(angle, 0, 0, 1)

    pulse_scale = 1.0 + math.sin(pulse * 2.0) * 0.05
    glScalef(scale * pulse_scale, scale * pulse_scale, scale)

    

    # =====================================================
    #  MAIN BODY (same as player, slightly slimmer)
    # =====================================================
    glColor3f(0.2, 0.9, 1.0)
    glPushMatrix()
    glScalef(2.8, 1.15, 0.4)
    glutSolidCube(12)
    glPopMatrix()

    # =====================================================
    #  CABIN (player-like but ghost variant)
    # =====================================================
    glColor3f(0.35, 1.0, 1.0)
    glPushMatrix()
    glTranslatef(3.5, 0, 4)
    glScalef(1.3, 0.9, 0.6)
    glutSolidCube(10)
    glPopMatrix()

    # =====================================================
    #  WHEEL BLOCKS (same positions as player)
    # =====================================================
    glColor3f(0.15, 0.6, 0.7)
    for wx in (-12, 12):
        for wy in (-7, 7):
            glPushMatrix()
            glTranslatef(wx, wy, -2)
            glScalef(0.6, 0.6, 0.3)
            glutSolidCube(8)
            glPopMatrix()

    # =====================================================
    #  GHOST OUTLINE SHELL
    # =====================================================
    glColor3f(0.5, 1.0, 1.0)
    glPushMatrix()
    glTranslatef(0, 0, 2)
    glScalef(3.0, 1.3, 0.5)
    glutWireCube(12)
    glPopMatrix()

    # =====================================================
    #  SIDE ENERGY STRIPES (difference from player)
    # =====================================================
    glLineWidth(3)
    glColor3f(0.4, 1.0, 1.0)
    glBegin(GL_LINES)
    for y in (-6, 6):
        glVertex3f(-18, y, 2)
        glVertex3f( 18, y, 2)
    glEnd()

    # =====================================================
    #  REAR GHOST TRAILS
    # =====================================================
    glColor3f(0.6, 1.0, 1.0)
    glBegin(GL_LINES)
    for i in (-3, 0, 3):
        glVertex3f(-20, i, 1)
        glVertex3f(-30, i, 5)
    glEnd()

    glPopMatrix()





def draw_buggy(x, y, z, angle, color=(1, 0, 0), is_player=False, scale=1.0):
    glPushMatrix()
    glTranslatef(x, y, z)
    glScalef(scale, scale, scale)  # <-- NEW: Apply scale
    glRotatef(angle, 0, 0, 1)
    glColor3f(color[0] * 0.8, color[1] * 0.8, color[2] * 0.8)
    glPushMatrix()
    glScalef(1.5, 1.0, 0.5)
    glutSolidCube(15)
    glPopMatrix()
    glColor3f(*color)
    glPushMatrix()
    glTranslatef(-3, 0, 10)
    glScalef(1.0, 0.8, 0.6)
    glutSolidCube(15)
    glPopMatrix()
    glColor3f(color[0] * 0.6, color[1] * 0.6, color[2] * 0.6)
    glPushMatrix()
    glTranslatef(12, 0, -3)
    glScalef(0.3, 0.8, 0.4)
    glutSolidCube(15)
    glPopMatrix()
    glColor3f(0.15, 0.15, 0.15)
    for wx, wy, wz in [(-8, -9, -5), (8, -9, -5), (-8, 9, -5), (8, 9, -5)]:
        glPushMatrix()
        glTranslatef(wx, wy, wz)
        gluSphere(gluNewQuadric(), 3.5, 8, 8)
        glPopMatrix()
    if is_player:
        glColor3f(1, 1, 0)
        glPushMatrix()
        glTranslatef(0, 0, 25)
        gluSphere(gluNewQuadric(), 3, 6, 6)
        glPopMatrix()
    glPopMatrix()

def draw_repair_drone(x, y, z, rotation, active, bob_phase):
    glPushMatrix()
    glTranslatef(x, y, z + math.sin(bob_phase) * 10)
    glColor3f(0.2, 1, 0.2) if active else glColor3f(0.6, 0.6, 0.6)
    gluSphere(gluNewQuadric(), 12, 12, 12)
    glColor3f(0.5, 1, 0.5)
    gluSphere(gluNewQuadric(), 7, 10, 10)
    glLineWidth(3)
    for ring_idx, ring_offset in enumerate([0, 120, 240]):
        glColor3f(1, 1, 0) if ring_idx == 0 else glColor3f(0, 1, 1) if ring_idx == 1 else glColor3f(1, 0.5, 0)
        glPushMatrix()
        glRotatef(rotation + ring_offset, 0, 0, 1)
        glRotatef(60, 1, 0, 0)
        glBegin(GL_LINES)
        for i in range(24):
            a1, a2 = (i / 24) * 2 * math.pi, ((i + 1) / 24) * 2 * math.pi
            glVertex3f(math.cos(a1) * 22, math.sin(a1) * 22, 0)
            glVertex3f(math.cos(a2) * 22, math.sin(a2) * 22, 0)
        glEnd()
        glPopMatrix()
    glPopMatrix()

def draw_hp_healer(x, y, z, active, pulse):
    """
    🟥 BOX HP HEALER (PLUS SIGN)
    - Layered cube
    - Glowing seams
    - Floating motion
    - Strong readable plus
    """

    glPushMatrix()

    # Floating + slow rotation
    bob = math.sin(pulse * 1.2) * 6
    glTranslatef(x, y, z + bob)
    glRotatef(math.sin(pulse) * 6, 0, 0, 1)

    # Pulse scale
    scale = 1.0 + math.sin(pulse * 2.0) * 0.08
    glScalef(scale, scale, scale)

    # ================= COLORS =================
    if active:
        shell = (0.9, 0.15, 0.18)
        core  = (1.0, 0.45, 0.45)
        glow  = (1.0, 0.7, 0.7)
    else:
        shell = (0.45, 0.45, 0.45)
        core  = (0.6, 0.6, 0.6)
        glow  = (0.5, 0.5, 0.5)

    # ================= OUTER CUBE =================
    glColor3f(*shell)
    glPushMatrix()
    glScalef(1.1, 1.1, 1.1)
    glutSolidCube(26)
    glPopMatrix()

    # ================= INNER CORE =================
    glColor3f(*core)
    glutSolidCube(20)

    # ================= GLOW SEAMS =================
    glLineWidth(3)
    glColor3f(*glow)
    glBegin(GL_LINES)

    s = 14
    for sx in (-s, s):
        for sy in (-s, s):
            glVertex3f(sx, sy, -s)
            glVertex3f(sx, sy,  s)

    for sz in (-s, s):
        for sx in (-s, s):
            glVertex3f(sx, -s, sz)
            glVertex3f(sx,  s, sz)

    for sz in (-s, s):
        for sy in (-s, s):
            glVertex3f(-s, sy, sz)
            glVertex3f( s, sy, sz)

    glEnd()

    # ================= PLUS SIGN =================
    glColor3f(1, 1, 1)
    glBegin(GL_QUADS)

    PLUS_Z = 16  # <-- IMPORTANT: in front of cube

# Vertical bar
    glVertex3f(-3, -10, PLUS_Z)
    glVertex3f( 3, -10, PLUS_Z)
    glVertex3f( 3,  10, PLUS_Z)
    glVertex3f(-3,  10, PLUS_Z)

# Horizontal bar
    glVertex3f(-10, -3, PLUS_Z)
    glVertex3f( 10, -3, PLUS_Z)
    glVertex3f( 10,  3, PLUS_Z)
    glVertex3f(-10,  3, PLUS_Z)

    glEnd()


    # ================= ENERGY CORNER STRUTS =================
    glLineWidth(2)
    glColor3f(0.8, 1.0, 0.8)

    glBegin(GL_LINES)
    for sx in (-12, 12):
        for sy in (-12, 12):
            glVertex3f(sx, sy, -12)
            glVertex3f(sx * 1.2, sy * 1.2, 18)
    glEnd()

    glPopMatrix()
#The color of the sand pit changes based on the pulse effect, making it appear slightly bigger/smaller over time.
def draw_sand_pit(x, y, radius, pulse):
    """Sinking sand pit hazard (GL_LINES / GL_QUADS only)"""
    z = calculate_dune_height(x, y, dune_time)

    # Stronger pulsing effect
    pulse_scale = 1.0 + math.sin(pulse) * 0.15

    glPushMatrix()
    glTranslatef(x, y, z + 1)

    # Darker sand color
    darkness = 0.2 + math.sin(pulse) * 0.08
    glColor3f(darkness, darkness * 0.7, darkness * 0.4)

    # ---------------------------
    # Draw main filled circle using TRIANGLE STRIP approximation
    # ---------------------------
    segments = 36
    glBegin(GL_QUADS)   ## Drawing a circle with a "swirling" effect
    for i in range(segments):
        a1 = (i / segments) * 2 * math.pi
        a2 = ((i + 1) / segments) * 2 * math.pi

        # Quad from center outward
        glVertex3f(0, 0, 0)  # center
        glVertex3f(math.cos(a1) * radius * pulse_scale, math.sin(a1) * radius * pulse_scale, -2)
        glVertex3f(math.cos(a2) * radius * pulse_scale, math.sin(a2) * radius * pulse_scale, -2)
        glVertex3f(0, 0, 0)  # center again
    glEnd()

    # ---------------------------
    # Draw swirling rings with GL_LINES
    # ---------------------------
    glLineWidth(4)
    for ring in range(5):
        alpha = 1.0 - (ring * 0.15)
        glColor3f(0.5 * alpha, 0.4 * alpha, 0.2 * alpha)

        ring_segments = 32
        glBegin(GL_LINES)
        for i in range(ring_segments):
            a1 = (i / ring_segments) * 2 * math.pi + pulse * 0.5
            a2 = ((i + 1) / ring_segments) * 2 * math.pi + pulse * 0.5
            r = radius * (0.2 + ring * 0.18) * pulse_scale

            glVertex3f(math.cos(a1) * r, math.sin(a1) * r, 0)
            glVertex3f(math.cos(a2) * r, math.sin(a2) * r, 0)
        glEnd()

    # ---------------------------
    # Orange warning markers
    # ---------------------------
    glColor3f(1.0, 0.3, 0.0)
    for i in range(8):
        angle = (i / 8.0) * 2 * math.pi + pulse
        px = math.cos(angle) * radius * pulse_scale
        py = math.sin(angle) * radius * pulse_scale
        glPushMatrix()
        glTranslatef(px, py, 5)
        glutSolidSphere(4, 6, 6)
        glPopMatrix()

    glPopMatrix()

    

def draw_ground_with_dunes():
    colors = [(0.93, 0.84, 0.62), (0.88, 0.79, 0.57), (0.90, 0.82, 0.60), (0.86, 0.77, 0.55)]
    grid_size, grid_range = 80, 20
    for i in range(-grid_range, grid_range):
        for j in range(-grid_range, grid_range):
            x1, y1 = i * grid_size, j * grid_size
            x2, y2 = (i + 1) * grid_size, (j + 1) * grid_size
            z1 = calculate_dune_height(x1, y1, dune_time)
            z2 = calculate_dune_height(x2, y1, dune_time)
            z3 = calculate_dune_height(x2, y2, dune_time)
            z4 = calculate_dune_height(x1, y2, dune_time)
            height_factor = ((z1 + z2 + z3 + z4) / 4 + 20) / 60
            base_color = colors[(i + j) % 4]
            r, g, b = [c * (0.7 + height_factor * 0.3) for c in base_color]
            glBegin(GL_QUADS)
            glColor3f(r, g, b)
            glVertex3f(x1, y1, z1); glVertex3f(x2, y1, z2); glVertex3f(x2, y2, z3); glVertex3f(x1, y2, z4)
            glEnd()
    glLineWidth(4)
    glColor3f(1, 0.3, 0.3)
    b = BOUNDARY_SIZE
    glBegin(GL_LINES)
    glVertex3f(-b, -b, 5); glVertex3f(b, -b, 5); glVertex3f(b, -b, 5); glVertex3f(b, b, 5)
    glVertex3f(b, b, 5); glVertex3f(-b, b, 5); glVertex3f(-b, b, 5); glVertex3f(-b, -b, 5)
    glEnd()

def generate_random_checkpoints(num=6):
    cps = []
    for _ in range(num):
        while True:
            x = random.uniform(-BOUNDARY_SIZE + 150, BOUNDARY_SIZE - 150)
            y = random.uniform(-BOUNDARY_SIZE + 150, BOUNDARY_SIZE - 150)
            if math.sqrt(x*x + y*y) > 150:
                break

        cps.append({
            'x': x,
            'y': y,
            'z': calculate_dune_height(x, y, dune_time) + 10,
            'reached': False,
            'rotation': random.uniform(0, 360),
            'pulse': random.uniform(0, 2 * math.pi)
        })
    return cps

def draw_checkpoint(cp):
    """
    Standing racing-style checkpoint ring
    RED   = locked (not enough kills)
    GREEN = unlocked
    """
    x, y = cp['x'], cp['y']
    cp['rotation'] += 0.5

    z = calculate_dune_height(x, y, dune_time) + 25

    # ===== LOCK STATE =====
    unlocked = enemies_killed_since_checkpoint >= ENEMIES_REQUIRED_PER_CHECKPOINT

    if unlocked:
        outer_color = (0.2, 1.0, 0.2)   # GREEN
        inner_color = (0.0, 0.4, 0.0)
    else:
        outer_color = (1.0, 0.2, 0.2)   # RED
        inner_color = (0.4, 0.0, 0.0)

    glPushMatrix()
    glTranslatef(x, y, z)

    # Stand the ring upright
    glRotatef(90, 1, 0, 0)
    glRotatef(cp['rotation'], 0, 0, 1)

    segments = 64

    # ===== OUTER RING =====
    glLineWidth(6)
    glColor3f(*outer_color)
    glBegin(GL_LINES)
    for i in range(segments):
        a1 = (i / segments) * 2 * math.pi
        a2 = ((i + 1) / segments) * 2 * math.pi

        glVertex3f(math.cos(a1) * 60, math.sin(a1) * 60, 0)
        glVertex3f(math.cos(a2) * 60, math.sin(a2) * 60, 0)
    glEnd()

    # ===== INNER RING =====
    glLineWidth(4)
    glColor3f(*inner_color)
    glBegin(GL_LINES)
    for i in range(segments):
        a1 = (i / segments) * 2 * math.pi
        a2 = ((i + 1) / segments) * 2 * math.pi

        glVertex3f(math.cos(a1) * 45, math.sin(a1) * 45, 0)
        glVertex3f(math.cos(a2) * 45, math.sin(a2) * 45, 0)
    glEnd()

    glPopMatrix()


def draw_bomb_pickup(x, y, z, pulse):
    """Draw a bomb pickup item"""
    glPushMatrix()
    glTranslatef(x, y, z + math.sin(pulse) * 5)
    
    # Pulsing scale
    scale = 1.0 + math.sin(pulse * 2) * 0.15
    glScalef(scale, scale, scale)
    
    # Black sphere (bomb body)
    glColor3f(0.1, 0.1, 0.1)
    gluSphere(gluNewQuadric(), 8, 12, 12)
    
    # Red fuse
    glColor3f(1, 0, 0)
    glPushMatrix()
    glTranslatef(0, 0, 8)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 1, 1, 5, 6, 1)
    glPopMatrix()
    
    # Yellow spark at tip
    glColor3f(1, 1, 0)
    glPushMatrix()
    glTranslatef(0, 0, 13)
    gluSphere(gluNewQuadric(), 2, 6, 6)
    glPopMatrix()
    
    glPopMatrix()



def draw_explosion(x, y, z, progress):
    """Draw explosion effect (progress from 0 to 1)"""
    glPushMatrix()
    glTranslatef(x, y, z)
    
    # Expanding sphere
    radius = BOMB_EXPLOSION_RADIUS * progress
    alpha = 1.0 - progress
    
    # Orange/red explosion
    glColor3f(1.0, 0.5 * alpha, 0)
    gluSphere(gluNewQuadric(), radius * 0.6, 12, 12)
    
    # Yellow core
    glColor3f(1, 1, 0)
    gluSphere(gluNewQuadric(), radius * 0.3, 10, 10)
    
    glPopMatrix()


def generate_bomb_pickups(num=3):
    """Generate random bomb pickups on the map"""
    pickups = []
    for _ in range(num):
        while True:
            x = random.uniform(-BOUNDARY_SIZE + 250, BOUNDARY_SIZE - 250)
            y = random.uniform(-BOUNDARY_SIZE + 250, BOUNDARY_SIZE - 250)
            # Don't spawn too close to origin
            if math.sqrt(x*x + y*y) > 200:
                # Don't spawn too close to other pickups
                too_close = False
                for pickup in pickups:
                    dx, dy = x - pickup['x'], y - pickup['y']
                    if math.sqrt(dx*dx + dy*dy) < 300:
                        too_close = True
                        break
                if not too_close:
                    break
        
        pickups.append({
            'x': x,
            'y': y,
            'z': 0,
            'active': True,
            'pulse': random.uniform(0, 2 * math.pi)
        })
    return pickups

# Add this function with other update functions (around line 600-800)

def check_bomb_pickups():
    """Check if player collected a bomb pickup"""
    global player_bombs
    
    for pickup in bomb_pickups:
        if not pickup['active']:
            continue
            
        dx = player_x - pickup['x']
        dy = player_y - pickup['y']
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < 40:
            if player_bombs < MAX_BOMBS:
                player_bombs += 1
                pickup['active'] = False
                print(f"💣 Bomb collected! ({player_bombs}/{MAX_BOMBS})")



#create sand pits
def generate_sand_pits(num=4):
    """✅ ENHANCED: Generate 4 strategically placed sand pits (one per quadrant)"""
    pits = []
    
    # ✅ STRATEGIC PLACEMENT: One pit per quadrant for guaranteed coverage
    quadrants = [
        (1, 1),   # Top-right
        (-1, 1),  # Top-left
        (-1, -1), # Bottom-left
        (1, -1)   # Bottom-right
    ]
    
    for qx, qy in quadrants:
        # Place pit in each quadrant between 400-1300 units from center
        x = qx * random.uniform(400, BOUNDARY_SIZE - 300)
        y = qy * random.uniform(400, BOUNDARY_SIZE - 300)
        
        pits.append({
            'x': x,
            'y': y,
            'radius': SAND_PIT_RADIUS,
            'pulse': random.uniform(0, 2 * math.pi)
        })
        print(f"🕳️ Sand pit placed at ({int(x)}, {int(y)})")
    
    return pits

def draw_bar(x, y, w, h, fill_ratio, color, border=True):

    # ===== BORDER (GL_LINES instead of GL_LINE_LOOP) =====
    if border:
        glLineWidth(2)
        glColor3f(1, 1, 1)
        glBegin(GL_LINES)

        # Bottom
        glVertex2f(x, y)
        glVertex2f(x + w, y)

        # Right
        glVertex2f(x + w, y)
        glVertex2f(x + w, y + h)

        # Top
        glVertex2f(x + w, y + h)
        glVertex2f(x, y + h)

        # Left
        glVertex2f(x, y + h)
        glVertex2f(x, y)

        glEnd()

    # ===== BACKGROUND =====
    glColor3f(0.2, 0.2, 0.2)
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + w, y)
    glVertex2f(x + w, y + h)
    glVertex2f(x, y + h)
    glEnd()

    # ===== FILL =====
    glColor3f(*color)
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + w * fill_ratio, y)
    glVertex2f(x + w * fill_ratio, y + h)
    glVertex2f(x, y + h)
    glEnd()


def draw_checkpoints_bar():
    total = len(checkpoints)
    reached = sum(1 for cp in checkpoints if cp['reached'])
    draw_bar(10, 700, 250, 20, reached / total if total > 0 else 0, (0.3, 0.7, 1.0))
    draw_text(270, 703, f"Checkpoints: {reached}/{total}")

def draw_time_bar():
    fill = time_left / 120.0
    color = (0.2, 0.8, 0.2) if time_left > 20 else (1, 0.8, 0) if time_left > 8 else (1, 0, 0)
    draw_bar(10, 665, 250, 18, fill, color, border=False)
    draw_text(270, 667, f"TIME: {int(time_left)}s")

def draw_fuel_bar():
    fill = fuel / max_fuel
    color = (0, 0.8, 0) if fuel > 50 else (1, 0.8, 0) if fuel > 25 else (1, 0, 0)
    draw_bar(10, 745, 250, 25, fill, color)
    draw_text(270, 750, f"{int(fuel)}%")

def draw_hp_heal_effect():
    """Green healing aura around player (GL_LINES compliant)"""
    if hp_heal_effect_timer <= 0:
        return

    progress = 1.0 - (hp_heal_effect_timer / HP_HEAL_EFFECT_DURATION)
    radius = 30 + progress * 60
    alpha = 1.0 - progress

    glPushMatrix()
    glTranslatef(player_x, player_y, player_z + 5)

    glColor4f(0.2, 1.0, 0.2, alpha)
    glLineWidth(4)

    segments = 48
    glBegin(GL_LINES)
    for i in range(segments):
        a1 = (i / segments) * 2 * math.pi
        a2 = ((i + 1) / segments) * 2 * math.pi

        glVertex3f(
            math.cos(a1) * radius,
            math.sin(a1) * radius,
            0
        )
        glVertex3f(
            math.cos(a2) * radius,
            math.sin(a2) * radius,
            0
        )
    glEnd()

    glPopMatrix()

def draw_floating_text_3d(x, y, z, text, color=(1,1,1)):
    glColor3f(*color)
    glRasterPos3f(x, y, z)
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))


def draw_fuel_repair_effect():
    """Blue fuel repair energy effect (GL_LINES compliant)"""
    if fuel_repair_effect_timer <= 0:
        return

    progress = 1.0 - (fuel_repair_effect_timer / FUEL_REPAIR_EFFECT_DURATION)

    base_radius = 35
    rise = progress * 25
    alpha = 1.0 - progress

    glPushMatrix()
    glTranslatef(player_x, player_y, player_z + 5 + rise)

    glColor4f(0.2, 0.6, 1.0, alpha)
    glLineWidth(3)

    segments = 40
    glBegin(GL_LINES)
    for i in range(segments):
        a1 = (i / segments) * 2 * math.pi
        a2 = ((i + 1) / segments) * 2 * math.pi

        glVertex3f(
            math.cos(a1) * base_radius,
            math.sin(a1) * base_radius,
            0
        )
        glVertex3f(
            math.cos(a2) * base_radius,
            math.sin(a2) * base_radius,
            0
        )
    glEnd()

    glPopMatrix()

def resolve_player_enemy_collisions():
    global player_x, player_y, player_speed

    for enemy in enemy_cars:
        dx = player_x - enemy['x']
        dy = player_y - enemy['y']
        dist = math.sqrt(dx*dx + dy*dy)

        min_dist = PLAYER_COLLISION_RADIUS + ENEMY_COLLISION_RADIUS

        if dist < min_dist and dist > 0:
            overlap = min_dist - dist
            nx = dx / dist
            ny = dy / dist

            # Push player back
            player_x += nx * overlap * COLLISION_PUSH
            player_y += ny * overlap * COLLISION_PUSH

            # Push enemy away
            enemy['x'] -= nx * overlap * (1 - COLLISION_PUSH)
            enemy['y'] -= ny * overlap * (1 - COLLISION_PUSH)

            # Only slow down if moving INTO the enemy
            player_rad = player_angle * math.pi / 180
            player_dir_x = math.cos(player_rad)
            player_dir_y = math.sin(player_rad)
            
            # Dot product: negative means moving toward enemy
            dot = player_dir_x * (-nx) + player_dir_y * (-ny)
            
            if dot > 0 and player_speed > 0:  # Moving toward enemy
                player_speed *= 0.7  # Less aggressive slowdown

#When the player is defeated the car flips down by modifying the player's angle. The angle changes over time to simulate the flip
def update_player():
    global player_x, player_y, player_z, player_speed, player_angle
    global fuel, is_boosting, player_defeat_angle, defeat_timer

    if game_over or player_defeated:
        if player_defeated and defeat_timer > 0:
            rad = player_angle * math.pi / 180
            player_x -= math.cos(rad) * 1.5
            player_y -= math.sin(rad) * 1.5
            player_defeat_angle = 360 * (DEFAT_DURATION - defeat_timer) / DEFAT_DURATION
            defeat_timer -= 1
        return

    # ================= FORWARD (W) =================
    if keys_pressed.get(b'w') or keys_pressed.get(b'W'):
        if cheat_mode:
            player_speed = player_nitro_speed
        elif fuel > 0:
            player_speed = min(player_speed + player_acceleration, player_max_speed)
            is_boosting = False
        else:
            player_speed = 0

    # ================= BRAKE (S) =================
    if keys_pressed.get(b's') or keys_pressed.get(b'S'):
        player_speed = max(0, player_speed - player_acceleration * 2.5)

    # ================= BACKWARD (B) =================
    if keys_pressed.get(b'b') or keys_pressed.get(b'B'):
        if cheat_mode:
            player_speed = -player_max_speed * 0.7
        else:
            player_speed = max(
                player_speed - player_acceleration * 2.0,
                -player_max_speed * 0.5
            )

    # ================= ROTATION =================
    if keys_pressed.get(b'a') or keys_pressed.get(b'A'):
        player_angle += player_rotation_speed

    if keys_pressed.get(b'd') or keys_pressed.get(b'D'):
        player_angle -= player_rotation_speed

    # ================= NITRO (SHIFT / UP) =================
    if shift_pressed:
        if cheat_mode:
            is_boosting = True
            player_speed = player_nitro_speed
        elif fuel > 5:
            is_boosting = True
            player_speed = min(player_speed + 3, player_nitro_speed)
        else:
            is_boosting = False

    # ================= MOVEMENT (FORWARD + BACKWARD) =================
    if abs(player_speed) > 0.01:
        rad = player_angle * math.pi / 180
        new_x = player_x + math.cos(rad) * player_speed
        new_y = player_y + math.sin(rad) * player_speed

        if abs(new_x) < BOUNDARY_SIZE - 30:
            player_x = new_x
        else:
            player_speed *= 0.3

        if abs(new_y) < BOUNDARY_SIZE - 30:
            player_y = new_y
        else:
            player_speed *= 0.3

        # ✅ FIX: Car always stays ABOVE sand (minimum 15 units clearance)
        ground_height = calculate_dune_height(player_x, player_y, dune_time)
        player_z = ground_height + 15  # Changed from +10 to +15

        # Fuel consumption (only forward / nitro)
        if not cheat_mode and player_speed > 0:
            if is_boosting and fuel > 0:
                fuel -= fuel_consumption_nitro
            else:
                fuel -= fuel_consumption_normal

            fuel = max(0, fuel)
            if fuel <= 0:
                player_speed = 0
                is_boosting = False

    # ================= NATURAL DECELERATION =================
    if abs(player_speed) > 0.05:
        if player_speed > 0:
            player_speed -= player_deceleration
        else:
            player_speed += player_deceleration
    else:
        player_speed = 0

      

     
            
#ghost car shrink and expand in size continuously, and disappear after a set amount of time
def update_ghosts():
    global ghost_cars
    i = 0
    while i < len(ghost_cars):
        ghost = ghost_cars[i]
        rad = ghost['angle'] * math.pi / 180
        ghost['x'] += math.cos(rad) * ghost['speed']
        ghost['y'] += math.sin(rad) * ghost['speed']
        ghost['angle'] += random.uniform(-3, 3)
        
        # ✅ FIX: Ghost stays above sand
        ground_height = calculate_dune_height(ghost['x'], ghost['y'], dune_time)
        ghost['z'] = ground_height + 15  # Changed from +10 to +15
        
        ghost['scale_phase'] += ghost['scale_speed']
        ghost['life'] -= 1
        if ghost['life'] <= 0:
            ghost_cars.pop(i)
            print("👻 Ghost vanished")
            continue
        i += 1
#When Cheat Mode is enabled, the player's missiles will curve toward the nearest enemy
def update_missiles():
    global missiles, missile_cooldown
    if missile_cooldown > 0:
        missile_cooldown -= 1
    
    i = 0
    while i < len(missiles):
        missile = missiles[i]
        
        # ================= FIND CLOSEST TARGET =================
        target_enemy = None
        min_distance = float('inf')
        
        for enemy in enemy_cars:
            dx = enemy['x'] - missile['x']
            dy = enemy['y'] - missile['y']
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist < min_distance:
                min_distance = dist
                target_enemy = enemy
        
        # ================= IMPROVED HOMING (stronger, more accurate) =================
        if target_enemy and min_distance < 400:  # # Find the nearest enemy to curve the missile towards
            # Calculate target angle
            target_angle = math.atan2(
                target_enemy['y'] - missile['y'],
                target_enemy['x'] - missile['x']
            ) * 180 / math.pi
            
            # ✅ STRONGER TURNING: 0.25 instead of 0.12
            angle_diff = target_angle - missile['angle']
            
            # Normalize angle difference to -180 to 180
            while angle_diff > 180:
                angle_diff -= 360
            while angle_diff < -180:
                angle_diff += 360
            
            # Apply turning with stronger force when close
            turn_strength = 0.25 if min_distance > 100 else 0.35
            missile['angle'] += angle_diff * turn_strength
        
        # # Regular missile movement and updates go here (for both cheat mode and normal mode)
        rad = missile['angle'] * math.pi / 180
        missile['x'] += math.cos(rad) * missile_speed
        missile['y'] += math.sin(rad) * missile_speed
        missile['z'] = calculate_dune_height(missile['x'], missile['y'], dune_time) + 15
        
        # ================= BOUNDARY CHECK =================
        if abs(missile['x']) > BOUNDARY_SIZE or abs(missile['y']) > BOUNDARY_SIZE:
            missiles.pop(i)
            continue
        
        # ================= COLLISION DETECTION (IMPROVED) =================
        hit = False
        for enemy in enemy_cars:
            dx = missile['x'] - enemy['x']
            dy = missile['y'] - enemy['y']
            dz = missile['z'] - enemy['z']
            
            # ✅ LARGER HIT RADIUS: 80 instead of 60
            distance_3d = math.sqrt(dx*dx + dy*dy + dz*dz)
            
            if distance_3d < 80:  # More forgiving hit detection
                print("💀 Enemy destroyed!")
                
                enemy_cars.remove(enemy)
                missiles.pop(i)
                
                global enemies_killed_since_checkpoint
                enemies_killed_since_checkpoint += 1
                print(f"Enemies killed for checkpoint: {enemies_killed_since_checkpoint}/"
                     f"{ENEMIES_REQUIRED_PER_CHECKPOINT}")
                
                hit = True
                break
        
        if hit:
            continue
        
        # ================= TIMEOUT =================
        missile['timeout'] = missile.get('timeout', 0) + 1
        if missile['timeout'] > 300:  # Increased from 250
            missiles.pop(i)
        else:
            i += 1
          
#player is hit by an enemy missile, their health (player_hp) is reduced, and the game over condition is checked.
def update_enemy_missiles():
    global enemy_missiles, player_hp, player_hit_flash
    global player_defeated, defeat_timer, game_over, player_lives

    # ===== SLOW MOTION FACTOR =====
    speed_factor = SLOW_MOTION_FACTOR if slow_motion else 1.0

    i = 0
    while i < len(enemy_missiles):
        missile = enemy_missiles[i]

        rad = missile['angle'] * math.pi / 180

        # ===== SMOOTH SLOW MOTION MOVEMENT =====
        missile['x'] += math.cos(rad) * enemy_missile_speed * speed_factor
        missile['y'] += math.sin(rad) * enemy_missile_speed * speed_factor
        missile['z'] = calculate_dune_height(
            missile['x'], missile['y'], dune_time
        ) + 15

        # Remove missile if out of boundary
        if abs(missile['x']) > BOUNDARY_SIZE or abs(missile['y']) > BOUNDARY_SIZE:
            enemy_missiles.pop(i)
            continue

        dx = missile['x'] - player_x
        dy = missile['y'] - player_y
        dz = missile['z'] - player_z

        # ================= COLLISION =================
        if math.sqrt(dx*dx + dy*dy + dz*dz) < 40:

            # ===== CHEAT MODE =====
            if cheat_mode:## When cheat mode is enabled, enemy missiles don't hit the player
                enemy_missiles.pop(i)
                continue

            # ===== NORMAL DAMAGE =====
            print("💥 Player hit!")
            # ===== CAMERA SHAKE TRIGGER =====
            global camera_shake_timer
            camera_shake_timer = CAMERA_SHAKE_DURATION
            enemy_missiles.pop(i)
            player_hp = max(0, player_hp - 1)
            player_hit_flash = FLASH_DURATION

            if player_hp <= 0:
                player_lives -= 1  #player hp reduced
                print(f"💔 Life lost! Lives remaining: {player_lives}")

                if player_lives > 0:
                    respawn_from_checkpoint()
                else:
                    player_defeated = True
                    defeat_timer = DEFAT_DURATION
                    game_over = True
                    print("☠️ GAME OVER - NO LIVES LEFT")

            continue

        i += 1


#Enemies ignore the player,Enemies chase the nearest ghost

def update_enemies():
    global enemy_cars, enemy_missiles
    if game_over:
        return

    speed_factor = SLOW_MOTION_FACTOR if slow_motion else 1.0

    ENEMY_RADIUS = 40     # collision size of enemy car
    PLAYER_RADIUS = 45
    SEPARATION_FORCE = 1.05

    for enemy in enemy_cars:

        # ================= TARGET SELECTION =================
        target_x, target_y = player_x, player_y
        # # If ghosts are present, target the nearest ghost
        if ghost_cars:
            min_dist = float('inf')
            for ghost in ghost_cars:
                dxg = ghost['x'] - enemy['x']
                dyg = ghost['y'] - enemy['y']
                distg = math.sqrt(dxg * dxg + dyg * dyg)
                if distg < min_dist:
                    min_dist = distg
                    target_x, target_y = ghost['x'], ghost['y']

        dx = target_x - enemy['x']
        dy = target_y - enemy['y']
        distance = math.sqrt(dx * dx + dy * dy)

        # ================= BASE MOVEMENT =================
        move_x = 0.0
        move_y = 0.0

        if distance > 400:
            if random.random() < 0.03 * speed_factor:
                enemy['angle'] += random.uniform(-25, 25)

            rad = enemy['angle'] * math.pi / 180
            move_x += math.cos(rad) * enemy['speed'] * 0.6 * speed_factor
            move_y += math.sin(rad) * enemy['speed'] * 0.6 * speed_factor

        else:
            if distance > 0:
                move_x += (dx / distance) * enemy['speed'] * speed_factor
                move_y += (dy / distance) * enemy['speed'] * speed_factor
                enemy['angle'] = math.atan2(dy, dx) * 180 / math.pi

            if (
                distance < 180 and
                enemy.get('missile_cooldown', 0) <= 0 and
                enemy.get('chase_cooldown', 0) <= 0
            ):
                enemy_missiles.append({
                    'x': enemy['x'],
                    'y': enemy['y'],
                    'z': enemy['z'] + 15,
                    'angle': math.atan2(dy, dx) * 180 / math.pi
                })
                enemy['missile_cooldown'] = ENEMY_MISSILE_COOLDOWN

        # ================= ENEMY ↔ ENEMY SEPARATION =================
        for other in enemy_cars:
            if other is enemy:
                continue

            ox = enemy['x'] - other['x']
            oy = enemy['y'] - other['y']
            dist = math.sqrt(ox * ox + oy * oy)

            if 0 < dist < ENEMY_RADIUS * 2:
                push = (ENEMY_RADIUS * 2 - dist) / (ENEMY_RADIUS * 2)
                move_x += (ox / dist) * push * SEPARATION_FORCE
                move_y += (oy / dist) * push * SEPARATION_FORCE

        # ================= ENEMY ↔ PLAYER SEPARATION =================
        px = enemy['x'] - player_x
        py = enemy['y'] - player_y
        pdist = math.sqrt(px * px + py * py)

        if 0 < pdist < (ENEMY_RADIUS + PLAYER_RADIUS):
           push = (ENEMY_RADIUS + PLAYER_RADIUS - pdist) / (ENEMY_RADIUS + PLAYER_RADIUS)
           move_x += (px / pdist) * push * 0.4
           move_y += (py / pdist) * push * 0.4


        # ================= APPLY MOVEMENT =================
        enemy['x'] += move_x
        enemy['y'] += move_y

        # ================= COOLDOWNS =================
        if enemy.get('missile_cooldown', 0) > 0:
            enemy['missile_cooldown'] -= speed_factor

        if enemy.get('chase_cooldown', 0) > 0:
            enemy['chase_cooldown'] -= speed_factor

        # ================= BOUNDARY =================
        if abs(enemy['x']) > BOUNDARY_SIZE - 20:
            enemy['x'] *= 0.92
        if abs(enemy['y']) > BOUNDARY_SIZE - 20:
            enemy['y'] *= 0.92

        # ================= TERRAIN HEIGHT =================
        # ================= TERRAIN HEIGHT =================
        # ✅ FIX: Enemies stay above sand with minimum clearance
        ground_height = calculate_dune_height(enemy['x'], enemy['y'], dune_time)
        enemy['z'] = ground_height + 15  # Changed from +10 to +15


       
def spawn_enemies(num=5):
    """Spawn a fresh wave of enemies"""
    enemy_cars.clear()

    for i in range(num):
        angle = (i * (360 / num)) * math.pi / 180
        distance = 400 + random.randint(0, 150)

        enemy_cars.append({
            'x': math.cos(angle) * distance,
            'y': math.sin(angle) * distance,
            'z': 0.0,
            'angle': random.uniform(0, 360),
            'speed': 1.2 + random.uniform(0, 0.4),
            'color': (
                random.uniform(0.4, 0.9),
                random.uniform(0.4, 0.9),
                random.uniform(0.4, 0.9)
            ),
            'chase_cooldown': 0,
            'missile_cooldown': 0
        })

  

def check_repair_drones():
    global fuel, fuel_repair_effect_timer, show_fuel_text_timer

    for drone in repair_drones:
        if drone['active']:
            dx, dy = player_x - drone['x'], player_y - drone['y']
            if math.sqrt(dx * dx + dy * dy) < 40:

                if fuel < max_fuel:
                    fuel = min(max_fuel, fuel + 1.2)

                    # 🔵 VISUAL EFFECT
                    fuel_repair_effect_timer = FUEL_REPAIR_EFFECT_DURATION

                    # 🔤 FLOATING TEXT
                    show_fuel_text_timer = FLOAT_TEXT_DURATION
#function checks if the player is close to any active HP healer. If the player is within range and the healer is active, it heals the player and applies the cooldown
def check_hp_healers():
    global player_hp, hp_heal_effect_timer, show_hp_text_timer

    for healer in hp_healers:
        if healer['cooldown'] > 0:
            healer['cooldown'] -= 1
            if healer['cooldown'] == 0:
                healer['active'] = True
            continue

        if healer['active']:
            dx, dy = player_x - healer['x'], player_y - healer['y']
            if math.sqrt(dx * dx + dy * dy) < 40 and player_hp < player_max_hp:
                player_hp = min(player_max_hp, player_hp + HP_HEAL_AMOUNT)

                hp_heal_effect_timer = HP_HEAL_EFFECT_DURATION
                show_hp_text_timer = FLOAT_TEXT_DURATION   # 🔤 TEXT

                healer['active'], healer['cooldown'] = False, HP_HEALER_COOLDOWN

#sinking" effect when the player moves into the sand pits
def check_sand_pits():
    """Check if player is in sand pit and apply shrinking"""
    global player_scale, player_speed
    
    in_sand = False
    for pit in sand_pits:
        dx = player_x - pit['x']
        dy = player_y - pit['y']
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < pit['radius']:
            in_sand = True
            
            
            if player_scale > 0.5:  # Only print when first entering
                print(f"🕳️ IN SAND PIT! Scale: {player_scale:.2f}, Distance: {distance:.1f}")
            
            # Shrink player
            if player_scale > MIN_PLAYER_SCALE:
                player_scale -= SAND_PIT_SINK_RATE
                if player_scale < MIN_PLAYER_SCALE:
                    player_scale = MIN_PLAYER_SCALE
            
            # Slow down player in sand
            player_speed *= 0.92  ## Reduce speed when in sand
            break
    
    # Recover scale when not in sand
    if not in_sand and player_scale < 1.0:
        player_scale += SCALE_RECOVERY_RATE
        if player_scale > 1.0:
            player_scale = 1.0


    
def update_checkpoints():
    global time_left, enemies_killed_since_checkpoint

    for cp in checkpoints:
        if cp['reached']:
            continue

        dx = player_x - cp['x']
        dy = player_y - cp['y']
        dz = player_z - cp['z']

        if math.sqrt(dx*dx + dy*dy + dz*dz) < 50:

            # ❌ BLOCK if kill requirement not met
            if enemies_killed_since_checkpoint < ENEMIES_REQUIRED_PER_CHECKPOINT:
                print("🚫 Checkpoint locked! Kill more enemies!")
                return

            # ✅ ALLOW checkpoint
            cp['reached'] = True

            # ===== SAVE CHECKPOINT STATE =====
            global last_checkpoint_state
            last_checkpoint_state = {
              'player_x': player_x,
               'player_y': player_y,
                'player_z': player_z,
                'player_angle': player_angle,
               'fuel': fuel,
              'player_hp': player_hp,
             'time_left': time_left,
                'checkpoints': [c['reached'] for c in checkpoints]
             }


            # RESET kill counter
            enemies_killed_since_checkpoint = 0
           # 💣 RESET PLAYER BOMBS
            global player_bombs
            player_bombs = 0
            print("💣 Bombs reset! Collect new ones.")
            
            # 💣 RESPAWN BOMB PICKUPS
            global bomb_pickups
            bomb_pickups = generate_bomb_pickups(num=3)
            print("🗺️ Bomb pickups respawned!")

             # ADD time bonus
            time_left = min(120, time_left + TIME_PER_CHECKPOINT)

              # 🔥 RESPAWN ENEMIES
            spawn_enemies(num=5)

            print(f"✅ Checkpoint cleared! Enemies respawned. +{TIME_PER_CHECKPOINT}s")
            

            return




def respawn_from_checkpoint():
    global player_x, player_y, player_z, player_angle
    global fuel, player_hp, time_left
    global player_speed, player_defeated, defeat_timer, game_over

    if last_checkpoint_state is None:
        return  # No checkpoint reached yet

    player_x = last_checkpoint_state['player_x']
    player_y = last_checkpoint_state['player_y']
    player_z = last_checkpoint_state['player_z']
    player_angle = last_checkpoint_state['player_angle']
    fuel = last_checkpoint_state['fuel']
    player_hp = last_checkpoint_state['player_hp']
    time_left = last_checkpoint_state['time_left']
    player_speed = 0

    # Restore checkpoint progress
    for i, cp in enumerate(checkpoints):
        cp['reached'] = last_checkpoint_state['checkpoints'][i]

    # Reset combat state
    missiles.clear()
    enemy_missiles.clear()
    spawn_enemies(5)

    player_defeated = False
    defeat_timer = 0
    game_over = False

    print("🔁 Respawned from last checkpoint")


def reset_game():
    """Reset game"""
    global player_x, player_y, player_z, player_angle, player_speed
    global fuel, enemy_cars, game_over, is_boosting
    global dune_time, missiles, missile_cooldown
    global player_hp, player_max_hp, player_defeated, defeat_timer, player_defeat_angle, player_hit_flash
    global checkpoints, hp_healers, repair_drones
    global time_left
    global sand_pits, player_scale
    global enemies_killed_since_checkpoint

    global player_lives, last_checkpoint_state
    global player_bombs, bomb_pickups, thrown_bombs, bomb_cooldown
    player_bombs = 0
    bomb_pickups = generate_bomb_pickups(num=3)
    thrown_bombs.clear()
    bomb_cooldown = 0
    player_lives = MAX_LIVES
    last_checkpoint_state = None

    enemies_killed_since_checkpoint = 0

    time_left = 60.0

    checkpoints = generate_random_checkpoints(num=6)
    sand_pits = generate_sand_pits(num=4)
    player_scale = 1.0 

    player_hp = player_max_hp
    player_hit_flash = 0
    player_x, player_y, player_z = 0.0, 0.0, 0.0
    player_angle = 0.0
    player_speed = 0.0
    fuel = 100.0
    game_over = False
    is_boosting = False
    dune_time = 0.0

    missiles.clear()
    missile_cooldown = 0

    player_defeated = False
    defeat_timer = 0
    player_defeat_angle = 0

    # ===== RESET ENEMIES =====
    enemy_cars.clear()
    for i in range(5):
        angle = (i * 72) * math.pi / 180
        distance = 400 + random.randint(0, 150)
        enemy_cars.append({
            'x': math.cos(angle) * distance,
            'y': math.sin(angle) * distance,
            'z': 0.0,
            'angle': random.uniform(0, 360),
            'speed': 1.2 + random.uniform(0, 0.4),
            'color': (
                random.uniform(0.4, 0.9),
                random.uniform(0.4, 0.9),
                random.uniform(0.4, 0.9)
            ),
            'chase_cooldown': 0
        })

    # ===== RESET HP HEALERS (NO REASSIGN) =====
    hp_healers.clear()
    hp_healers.extend([
        {
            'x': -CORNER_POS,
            'y':  CORNER_POS,
            'z': 0.0,
            'active': True,
            'cooldown': 0,
            'pulse': random.uniform(0, 2 * math.pi)
        },
        {
            'x':  CORNER_POS,
            'y': -CORNER_POS,
            'z': 0.0,
            'active': True,
            'cooldown': 0,
            'pulse': random.uniform(0, 2 * math.pi)
        }
    ])

    # ===== RESET REPAIR DRONES (NO REASSIGN) =====
    repair_drones.clear()
    repair_drones.extend([
        {
            'x':  CORNER_POS,
            'y':  CORNER_POS,
            'z': 50.0,
            'rotation': 0.0,
            'active': True,
            'bob_phase': random.uniform(0, math.pi)
        },
        {
            'x': -CORNER_POS,
            'y': -CORNER_POS,
            'z': 50.0,
            'rotation': 0.0,
            'active': True,
            'bob_phase': random.uniform(0, math.pi)
        }
    ])

    


# ===== INPUT HANDLERS =====
def keyboardListener(key, x, y):
    """Handle keyboard input"""
    global player_speed, player_angle, is_boosting
    global cheat_mode, fuel, missiles, missile_cooldown, slow_motion
    global shift_pressed  # Track shift key
    global camera_offset_z, camera_rotation_offset  # For reset

    # ================= SHIFT KEY (enable camera controls) =================
    if key == b'\x00':  # This won't trigger, but we'll use a different approach
        pass
    
    # ================= RESET CAMERA (V) =================
    if key == b'v' or key == b'V':
        camera_offset_z = 0.0
        camera_rotation_offset = 0.0
        print("📷 Camera reset to default")

    # ================= FORWARD (W) =================
    if key == b'w' or key == b'W':
        if cheat_mode:
            player_speed = player_nitro_speed
        else:
            if fuel <= 0:
                player_speed = 0
            else:
                player_speed = min(player_speed + player_acceleration, player_max_speed)
                is_boosting = False

    # ================= BRAKE (S) =================
    if key == b's' or key == b'S':
        player_speed = max(0, player_speed - player_acceleration * 2.5)

    # ================= BACKWARD (B) =================
    # NEW: Reverse movement key
    if key == b'b' or key == b'B':
        if cheat_mode:
            player_speed = -player_max_speed * 0.7
        else:
            player_speed = max(
                player_speed - player_acceleration * 2.0,
                -player_max_speed * 0.5
            )

    # ================= ROTATION =================
    if key == b'a' or key == b'A':
        player_angle += player_rotation_speed

    if key == b'd' or key == b'D':
        player_angle -= player_rotation_speed

    # ================= FIRE MISSILE (SPACE) =================
    if key == b' ' and missile_cooldown <= 0:
        missiles.append({
            'x': player_x,
            'y': player_y,
            'z': player_z + 15,
            'angle': player_angle
        })
        missile_cooldown = MISSILE_COOLDOWN_MAX

    # ================= CHEAT MODE TOGGLE (C) =================
    if key == b'c' or key == b'C':
        cheat_mode = not cheat_mode
        if cheat_mode:
            fuel = max_fuel
        print(f"Cheat Mode: {'ON' if cheat_mode else 'OFF'}")

    # ================= RESET GAME (R) =================
    if key == b'r' or key == b'R':
        reset_game()
        print("Game Reset!")


    # ================= FIRST PERSON TOGGLE (F) =================
    if key == b'f' or key == b'F':
       global first_person_mode
       first_person_mode = not first_person_mode
       slow_motion = False   # auto-disable slow motion when switching
       print(f"First Person Mode: {'ON' if first_person_mode else 'OFF'}")


    # ================= SLOW MOTION (M) =================
    if key == b'm' or key == b'M':
       if first_person_mode:
        slow_motion = not slow_motion
        print(f"Slow Motion: {'ON' if slow_motion else 'OFF'}")

    

    # ================= SPAWN GHOST CAR (G) =================
    if (key == b'g' or key == b'G') and len(ghost_cars) < MAX_GHOSTS:
        angle = random.uniform(0, 360)
        dist = random.uniform(120, 300)

        gx = player_x + math.cos(angle * math.pi / 180) * dist
        gy = player_y + math.sin(angle * math.pi / 180) * dist
        gz = calculate_dune_height(gx, gy, dune_time) + 10

        ghost_cars.append({
            'x': gx,
            'y': gy,
            'z': gz,
            'angle': random.uniform(0, 360),
            'speed': random.uniform(2.5, 4.5),
            'life': GHOST_LIFETIME,
            'scale_phase': random.uniform(0, 2 * math.pi),
            'scale_speed': random.uniform(0.08, 0.14)
        })
        print("👻 Ghost car deployed at random location!")

    glutPostRedisplay()


      
    

def specialKeyListener(key, x, y):
    """Handle special keys"""
    global is_boosting, player_speed, fuel
    global camera_offset_z, camera_rotation_offset, camera_distance
    
    # Check if SHIFT is currently pressed
    modifiers = glutGetModifiers()
    shift_is_pressed = (modifiers & GLUT_ACTIVE_SHIFT) != 0
    
    # ================= CAMERA CONTROLS (with SHIFT modifier) =================
    if shift_is_pressed:
        # Up Arrow - Move camera UP
        if key == GLUT_KEY_UP:
            camera_offset_z += CAMERA_MOVE_SPEED
            print(f"📷 Camera Height: {camera_offset_z:.0f}")
        
        # Down Arrow - Move camera DOWN
        elif key == GLUT_KEY_DOWN:
            camera_offset_z -= CAMERA_MOVE_SPEED
            print(f"📷 Camera Height: {camera_offset_z:.0f}")
        
        # Left Arrow - Rotate camera LEFT around player
        elif key == GLUT_KEY_LEFT:
            camera_rotation_offset += CAMERA_ROTATE_SPEED
            print(f"📷 Camera Rotation: {camera_rotation_offset:.0f}°")
        
        # Right Arrow - Rotate camera RIGHT around player
        elif key == GLUT_KEY_RIGHT:
            camera_rotation_offset -= CAMERA_ROTATE_SPEED
            print(f"📷 Camera Rotation: {camera_rotation_offset:.0f}°")
        
        # Page Up - Zoom IN
        elif key == GLUT_KEY_PAGE_UP:
            camera_distance = max(50, camera_distance - CAMERA_ZOOM_SPEED)
            print(f"📷 Camera Distance: {camera_distance:.0f}")
        
        # Page Down - Zoom OUT
        elif key == GLUT_KEY_PAGE_DOWN:
            camera_distance = min(500, camera_distance + CAMERA_ZOOM_SPEED)
            print(f"📷 Camera Distance: {camera_distance:.0f}")
    
    # ================= NITRO (UP ARROW without SHIFT) =================
    else:
        if key == GLUT_KEY_UP:
            if cheat_mode:
                is_boosting = True
                player_speed = player_nitro_speed
            elif fuel > 5:
                is_boosting = True
                player_speed = min(player_speed + 3, player_nitro_speed)
            else:
                is_boosting = False
    
    glutPostRedisplay()

def mouseListener(button, state, x, y):
    """Handle mouse input"""
    global missiles, missile_cooldown
    global bomb_cooldown, player_bombs
    global enemies_killed_since_checkpoint, camera_shake_timer

    # ================= LEFT CLICK — FIRE MISSILE =================
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if missile_cooldown <= 0:
            missiles.append({
                'x': player_x,
                'y': player_y,
                'z': player_z + 15,
                'angle': player_angle
            })
            missile_cooldown = MISSILE_COOLDOWN_MAX
            glutPostRedisplay()

    # ================= RIGHT CLICK — SMART INSTANT BOMB =================
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:

        if player_bombs <= 0 or bomb_cooldown > 0:
            print("❌ No bombs or cooldown active")
            return

        # ===== FIND NEAREST ENEMY =====
        nearest_enemy = None
        min_dist = float('inf')

        for enemy in enemy_cars:
            dx = enemy['x'] - player_x
            dy = enemy['y'] - player_y
            dist = math.sqrt(dx * dx + dy * dy)

            if dist < min_dist:
                min_dist = dist
                nearest_enemy = enemy

        # ===== EXPLOSION POSITION =====
        if nearest_enemy:
            bx = nearest_enemy['x']
            by = nearest_enemy['y']
        else:
            # Fallback: explode forward
            rad = player_angle * math.pi / 180
            bx = player_x + math.cos(rad) * 120
            by = player_y + math.sin(rad) * 120

        bz = calculate_dune_height(bx, by, dune_time) + 15

        print("💥 INSTANT BOMB BLAST!")

        # ===== DAMAGE: KILL 2 NEAREST ENEMIES =====
        enemy_distances = []

        for enemy in enemy_cars:
            dx = enemy['x'] - bx
            dy = enemy['y'] - by
            dist = math.sqrt(dx * dx + dy * dy)
            enemy_distances.append((dist, enemy))

# Sort by distance to explosion
        enemy_distances.sort(key=lambda x: x[0])

# Kill up to 2 closest enemies
        kills = min(2, len(enemy_distances))

        for i in range(kills):
             enemy = enemy_distances[i][1]
             enemy_cars.remove(enemy)
             enemies_killed_since_checkpoint += 1
             print("💀 Enemy destroyed by SMART bomb!")


        # ===== EFFECTS =====
        camera_shake_timer = CAMERA_SHAKE_DURATION

        # ===== CONSUME BOMB =====
        player_bombs -= 1
        bomb_cooldown = BOMB_THROW_COOLDOWN
        print(f"💣 Bomb used! Remaining: {player_bombs}")

        glutPostRedisplay()


# ===== CAMERA & RENDERING =====

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(55, 1.25, 0.1, 3000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # ===== APPLY CAMERA ROTATION OFFSET =====
    cam_rad = (player_angle + camera_rotation_offset) * math.pi / 180

    tilt = 0.0

    if first_person_mode:
        cam_x = player_x + math.cos(cam_rad) * 10
        cam_y = player_y + math.sin(cam_rad) * 10
        ground_z = calculate_dune_height(player_x, player_y, dune_time)

        cam_z = max(player_z + 18, ground_z + 12) + camera_offset_z  # ✅ ADD OFFSET

        look_x = cam_x + math.cos(cam_rad) * 100
        look_y = cam_y + math.sin(cam_rad) * 100
        look_z = cam_z

        if player_defeated:
            tilt = player_defeat_angle

    else:
        cam_x = player_x - math.cos(cam_rad) * camera_distance
        cam_y = player_y - math.sin(cam_rad) * camera_distance
        cam_z = camera_height + player_z + camera_offset_z  # ✅ ADD OFFSET

        look_x = player_x + math.cos(cam_rad) * 30
        look_y = player_y + math.sin(cam_rad) * 30
        look_z = player_z + 15

    # ===== CAMERA SHAKE =====
    if camera_shake_timer > 0:
        strength = CAMERA_SHAKE_INTENSITY * (camera_shake_timer / CAMERA_SHAKE_DURATION)
        cam_x += random.uniform(-strength, strength)
        cam_y += random.uniform(-strength, strength)
        cam_z += random.uniform(-strength * 0.4, strength * 0.4)

    # ===== APPLY CAMERA =====
    gluLookAt(
        cam_x, cam_y, cam_z,
        look_x, look_y, look_z,
        0, 0, 1
    )

    if first_person_mode and player_defeated:
        glRotatef(tilt, 0, 0, 1)



def idle():
    """Update game state"""
    global game_time, dune_time, player_hit_flash
    
    global time_left, game_over, player_defeated, defeat_timer
    global camera_shake_timer, bomb_cooldown

    global hp_heal_effect_timer
    global fuel_repair_effect_timer
    global show_hp_text_timer, show_fuel_text_timer

    if show_hp_text_timer > 0:
      show_hp_text_timer -= 1

    if show_fuel_text_timer > 0:
      show_fuel_text_timer -= 1

    if fuel_repair_effect_timer > 0:
       fuel_repair_effect_timer -= 1

    if hp_heal_effect_timer > 0:
      hp_heal_effect_timer -= 1

    # ===== BOMB COOLDOWN =====
    if bomb_cooldown > 0:
       bomb_cooldown -= 1

    
    if camera_shake_timer > 0:
      camera_shake_timer -= 1

    if not game_over and not cheat_mode:
      time_left -= TIME_DRAIN_RATE

      if time_left <= 0:
        time_left = 0
        print("⏰ TIME UP! GAME OVER")
        player_defeated = True
        defeat_timer = DEFAT_DURATION
        game_over = True



    game_time += 0.02
    global player_hit_flash
    if player_hit_flash > 0:
          player_hit_flash -= 1

    dune_time += dune_speed
    
    for drone in repair_drones:
        drone['rotation'] += 2.5
        if drone['rotation'] >= 360:
            drone['rotation'] = 0
        drone['bob_phase'] += 0.06
    
    for healer in hp_healers:
        healer['pulse'] += 0.08
    for pit in sand_pits:
        pit['pulse'] += 0.05


    update_player()
    resolve_player_enemy_collisions()
    update_ghosts()
    update_missiles()
    update_enemies()
    update_enemy_missiles()


    
    check_repair_drones()
    update_checkpoints()
    check_hp_healers()
    check_sand_pits()

    check_bomb_pickups()
    
    
    # Update bomb pickup pulses
    for pickup in bomb_pickups:
        pickup['pulse'] += 0.08
    
    
    

    glutPostRedisplay()


def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)

    glEnable(GL_DEPTH_TEST)
    setupCamera()

    # visually drawing the dynamic terrain
    draw_ground_with_dunes()

    for healer in hp_healers:
        healer['z'] = calculate_dune_height(healer['x'], healer['y'], dune_time) + 8
        draw_hp_healer(healer['x'], healer['y'], healer['z'],
                       healer['active'], healer['pulse'])

    for drone in repair_drones:
        draw_repair_drone(drone['x'], drone['y'], drone['z'],
                          drone['rotation'], drone['active'], drone['bob_phase'])

    for pit in sand_pits:
        draw_sand_pit(pit['x'], pit['y'], pit['radius'], pit['pulse'])

    for missile in missiles:
        draw_missile(missile['x'], missile['y'], missile['z'], missile['angle'])

    for missile in enemy_missiles:
        draw_missile(missile['x'], missile['y'], missile['z'], missile['angle'])

    for pickup in bomb_pickups:
        if pickup['active']:
            pickup['z'] = calculate_dune_height(pickup['x'], pickup['y'], dune_time) + 20
            draw_bomb_pickup(pickup['x'], pickup['y'], pickup['z'], pickup['pulse'])

    # ===== PLAYER COLOR FLASH =====
    if player_hit_flash > 0:
        t = player_hit_flash / FLASH_DURATION
        flash_color = (1.0, 0.5 + 0.5 * t, 0.0)
    else:
        flash_color = (1, 0.1, 0.1)

    
    #  DRAW PLAYER BUGGY ONLY IN THIRD PERSON
   
    if not first_person_mode:
        nx, ny, nz = get_dune_normal(player_x, player_y, dune_time)
        pitch, roll = normal_to_angles(nx, ny, nz)
        
        glPushMatrix()
        glTranslatef(player_x, player_y, player_z)
        if player_defeated:
            glRotatef(player_defeat_angle, 1, 0, 0)
        
        glRotatef(player_angle, 0, 0, 1)   # yaw
        glRotatef(pitch, 0, 1, 0)          # pitch
        glRotatef(-roll, 1, 0, 0)          # roll

        draw_buggy(0, 0, 0, 0, flash_color,
                   is_player=True, scale=player_scale)
        glPopMatrix()

    draw_hp_heal_effect()
    draw_fuel_repair_effect()
    
    # ===== FLOATING TEXT ABOVE PLAYER =====
    text_height = player_z + 55

    if show_hp_text_timer > 0:
        draw_floating_text_3d(
            player_x,
            player_y,
            text_height,
            "+HP",
            (0.2, 1.0, 0.2)
        )

    if show_fuel_text_timer > 0:
        draw_floating_text_3d(
            player_x,
            player_y,
            text_height + 12,
            "+FUEL",
            (0.2, 0.6, 1.0)
        )

    for enemy in enemy_cars:
        nx, ny, nz = get_dune_normal(enemy['x'], enemy['y'], dune_time)
        pitch, roll = normal_to_angles(nx, ny, nz)

        glPushMatrix()
        glTranslatef(enemy['x'], enemy['y'], enemy['z'])

        glRotatef(enemy['angle'], 0, 0, 1)
        glRotatef(pitch, 0, 1, 0)
        glRotatef(-roll, 1, 0, 0)

        draw_buggy(0, 0, 0, 0, enemy['color'])
        glPopMatrix()

    for ghost in ghost_cars:
        scale = 0.85 + math.sin(ghost['scale_phase']) * 0.25
        draw_ghost_car(
            ghost['x'], ghost['y'], ghost['z'],
            ghost['angle'], scale,
            ghost['scale_phase']   # ✅ pulse
        )

    for cp in checkpoints:
        if not cp['reached']:
            draw_checkpoint(cp)

    glDisable(GL_DEPTH_TEST)

    # ===== UI WITH UNIFORM SPACING =====
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # ===== TOP BARS (Fixed positions) =====
    draw_fuel_bar()
    draw_text(270, 750, f"{int(fuel)}%")
    
    draw_checkpoints_bar()
    draw_text(270, 703, f"Checkpoints: {sum(1 for cp in checkpoints if cp['reached'])}/{len(checkpoints)}")
    
    draw_time_bar()
    draw_text(270, 667, f"TIME: {int(time_left)}s")
    
    # ===== LEFT SIDE INFO (Uniform spacing) =====
    ui_x = 10
    ui_y_start = 645
    ui_line_height = 30
    
    draw_text(ui_x, ui_y_start, 
              f"Missiles Ready: {'YES' if missile_cooldown <= 0 else 'NO'}")
    
    draw_text(ui_x, ui_y_start - ui_line_height, 
              f"Kills for checkpoint: {enemies_killed_since_checkpoint}/{ENEMIES_REQUIRED_PER_CHECKPOINT}")
    
    draw_text(ui_x, ui_y_start - (ui_line_height * 2), 
              f"Lives: {player_lives}/{MAX_LIVES}")
    
    draw_text(ui_x, ui_y_start - (ui_line_height * 3), 
              f"Bombs: {player_bombs}/{MAX_BOMBS} | RightClick to throw")
    
    # ===== MODE INDICATORS (Right side) =====
    mode_x = 750
    mode_y = 770
    
    if first_person_mode:
        draw_text(mode_x, mode_y, "FIRST PERSON")
        mode_y -= 30
    
    if slow_motion:
        draw_text(mode_x, mode_y, "SLOW MOTION")
    
    # ===== CENTER MESSAGES =====
    if cheat_mode:
        draw_text(310, 750, "*** CHEAT MODE ACTIVE ***")
    
    if is_boosting:
        draw_text(380, 680, 
                  ">>> SUPER NITRO! <<<" if cheat_mode else ">>> NITRO BOOST! <<<")
    
    if fuel <= 0 and not cheat_mode:
        draw_text(280, 400, "OUT OF FUEL! Find Drone or Press R")
   
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    glutSwapBuffers()



# ===== MAIN =====

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Dune Blaster Rally - CURVING MISSILES FIXED!")
    
    glClearColor(0.53, 0.81, 0.92, 1.0)
    # ===== INITIAL GAME RESET =====
    reset_game()   # <-- THIS WILL GENERATE RANDOM CHECKPOINTS
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    
    glutMainLoop()

if __name__ == "__main__":
    main()

