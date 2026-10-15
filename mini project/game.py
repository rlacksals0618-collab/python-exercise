"""바닷속 탈출 - 발판을 밟고 수면 위 출구까지 올라가는 게임.

조작: ←/→ 이동, ↑ 또는 Space 점프, ↓ 빠르게 내려오기, Esc 난이도 선택으로
화면 오른쪽 아래의 방향 버튼을 마우스로 눌러도 조작할 수 있습니다.
"""
import math
import random
import tkinter as tk

# ── 화면과 물리 설정 ──
WIDTH, HEIGHT = 900, 600
FRAME_MS = 16           # 한 프레임 간격(ms). 약 60fps
GRAVITY = 0.6
JUMP_POWER = 13         # 최대 점프 높이는 약 140px
MOVE_SPEED = 5
FAST_FALL = 0.8         # ↓를 누르고 있을 때 더해지는 중력
MAX_FALL_SPEED = 15
JUMP_BUFFER = 6         # 착지 직전에 누른 점프도 이 프레임 수만큼 기억
PLAYER_W, PLAYER_H = 44, 44
GROUND_Y = HEIGHT - 40
PLATFORM_H = 14

# ── 특수 발판 ──
ICE_GRIP = 0.05         # 미끄러운 발판: 매 프레임 원하는 속도에 5%씩만 가까워진다
ICE_MIN_WIDTH = 120     # 미끄러운 발판은 너무 좁으면 바로 떨어지므로 최소 폭을 둔다
SLOW_FACTOR = 0.4       # 느려지는 발판: 걷는 속도가 40%로 줄어든다

# ── 게임 규칙 ──
MAX_LIVES = 3
INVERT_GAP = (8, 10)    # 반전까지 올라야 하는 층수 (이 범위에서 무작위)
REVERT_AFTER = 3        # 반전 후 원래대로 돌아오기까지 올라야 하는 층수
FLASH_FRAMES = 12       # 번쩍임 지속 시간 (약 0.2초, 1회)

# ── 난이도별 발판 규칙 ──
# widths: 발판 폭 후보, gap_y: 위아래 간격, gap_x: 발판 끝과 끝 사이 가로 간격 (최소, 최대)
# moving_*: 움직이는 발판, special_*: 미끄러운/느려지는 발판 (from층부터 chance 확률로 등장)
RULES = {
    "easy": {"widths": [120, 150, 180, 210], "gap_y": (80, 95), "gap_x": (30, 110),
             "moving_from": 8, "moving_chance": 0.15, "moving_speed": 1.2,
             "special_from": 5, "special_chance": 0.15},
    "normal": {"widths": [90, 120, 150, 180], "gap_y": (80, 105), "gap_x": (60, 135),
               "moving_from": 6, "moving_chance": 0.25, "moving_speed": 1.5,
               "special_from": 4, "special_chance": 0.25},
    "hard": {"widths": [60, 80, 100, 130], "gap_y": (90, 110), "gap_x": (90, 145),
             "moving_from": 3, "moving_chance": 0.35, "moving_speed": 2.0,
             "special_from": 3, "special_chance": 0.35},
}

# 모드: (이름, 발판 규칙, 도착 층). 무한 모드는 도착점이 없고 50층부터 하드 규칙을 쓴다.
MODES = [
    ("이지", "easy", 30),
    ("노말", "normal", 50),
    ("하드", "hard", 70),
    ("무한", "endless", None),
]
ENDLESS_HARD_FROM = 50

FONT = "Malgun Gothic"

COLORS = {
    "bg": "#eaf7fc",
    "wave": "#a6daf2",
    "bubble": "#7fc6ea",
    "platform": "#111111",
    "moving": "#2f5fd0",
    "ice": "#9be7ff",
    "slow": "#7a4b22",
    "goal": "#2a9d4a",
    "body": "#c4c4c4",
    "shade": "#8a8a8a",
    "eye": "#ffffff",
    "line": "#000000",
    "text": "#111111",
    "faint": "#8aa0aa",
    "heart": "#e02020",
    "heart_empty": "#c8c8c8",
    "button": "#ffffff",
    "pressed": "#ffd84d",
    "panel": "#ffffff",
}


def invert(hex_color):
    """'#rrggbb' 색을 반전한다. 예: #ffffff → #000000"""
    value = int(hex_color[1:], 16)
    return f"#{0xFFFFFF - value:06x}"


INVERTED_COLORS = {name: invert(value) for name, value in COLORS.items()}

# 화면 오른쪽 아래 방향 버튼: 키 이름 → (왼쪽 x, 위쪽 y, 기호)
BUTTON_SIZE = 50
BUTTONS = {
    "Up": (WIDTH - 150, HEIGHT - 135, "▲"),
    "Left": (WIDTH - 210, HEIGHT - 75, "◀"),
    "Down": (WIDTH - 150, HEIGHT - 75, "▼"),
    "Right": (WIDTH - 90, HEIGHT - 75, "▶"),
}

WAVE_BAND = 220         # 배경 물결선을 이 높이마다 한 묶음씩 그린다
BUBBLE_COUNT = 14


def clamp(value, low, high):
    return max(low, min(value, high))


class Platform:
    def __init__(self, floor, center_x, y, width, kind="normal", speed=0):
        self.floor = floor
        self.kind = kind                # normal, moving, ice, slow, goal
        self.w = width
        self.center0 = center_x         # 처음 놓인 가운데 위치 (다음 발판 배치 기준)
        self.x = center_x - width / 2   # 왼쪽 끝
        self.y = y                      # 윗면
        self.speed = random.choice([-speed, speed]) if kind == "moving" else 0
        self.min_x = max(10, self.x - 80)
        self.max_x = min(WIDTH - 10 - width, self.x + 80)

    def update(self):
        if self.speed == 0:
            return
        self.x += self.speed
        if self.x <= self.min_x or self.x >= self.max_x:
            self.speed = -self.speed


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.standing = None   # 지금 밟고 있는 발판 (공중이면 None)
        self.facing = 1        # 1: 오른쪽, -1: 왼쪽


class Game:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, highlightthickness=0)
        self.canvas.pack()
        self.keys = set()        # 키보드로 누르고 있는 키
        self.mouse_key = None    # 마우스로 누르고 있는 화면 버튼
        root.bind("<KeyPress>", self.on_key_down)
        root.bind("<KeyRelease>", self.on_key_up)
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.mode_index = 1                    # 처음 선택된 난이도: 노말
        self.records = [0] * len(MODES)        # 모드별 최고 기록 (프로그램을 끄면 사라짐)
        self.bubbles = [[random.uniform(0, WIDTH), random.uniform(0, HEIGHT),
                         random.uniform(3, 8), random.uniform(0.4, 1.2)] for _ in range(BUBBLE_COUNT)]
        self.reset()
        self.state = "title"     # title → play → over 또는 clear
        self.loop()

    def reset(self):
        _, self.rule_key, self.goal = MODES[self.mode_index]
        self.platforms = [Platform(0, WIDTH / 2, GROUND_Y, WIDTH)]   # platforms[n]은 n층
        self.player = Player(WIDTH / 2 - PLAYER_W / 2, GROUND_Y - PLAYER_H)
        self.lives = MAX_LIVES
        self.highest = 0
        self.best_platform = self.platforms[0]   # 부활할 발판
        self.inverted = False
        self.next_invert = random.randint(*INVERT_GAP)
        self.revert_at = 0
        self.flash = 0
        self.blink = 0
        self.jump_buffer = 0
        self.cam_y = 0           # 화면 맨 위가 가리키는 세계 좌표 y
        self.bg_seed = random.randint(0, 10000)
        self.ensure_platforms()

    def start(self):
        self.reset()
        self.state = "play"

    def go_to_title(self):
        self.reset()
        self.state = "title"

    def end_game(self, state):
        self.state = state
        self.records[self.mode_index] = max(self.records[self.mode_index], self.highest)

    # ── 발판 만들기 ──
    def rules_for(self, floor):
        if self.rule_key == "endless":
            return RULES["hard"] if floor >= ENDLESS_HARD_FROM else RULES["normal"]
        return RULES[self.rule_key]

    def add_platform(self):
        """맨 위 발판보다 한 층 위에 새 발판을 놓는다. 항상 점프로 닿는 거리에 놓인다."""
        prev = self.platforms[-1]
        floor = prev.floor + 1
        rules = self.rules_for(floor)
        y = prev.y - random.randint(*rules["gap_y"])
        if floor == self.goal:
            kind, w = "goal", 220
        else:
            w = random.choice(rules["widths"])
            roll = random.random()
            if floor >= rules["moving_from"] and roll < rules["moving_chance"]:
                kind = "moving"
            elif floor >= rules["special_from"] and roll < rules["moving_chance"] + rules["special_chance"]:
                kind = random.choice(["ice", "slow"])
            else:
                kind = "normal"
            if kind == "ice":
                w = max(w, ICE_MIN_WIDTH)
        # 이전 발판의 왼쪽이나 오른쪽으로 gap_x만큼 떨어뜨린다. 벽에 막히면 반대쪽에 놓는다.
        # 점프 한 번에 가로로 155~165px까지 갈 수 있으므로 최대 간격은 그보다 작게 둔다.
        prev_w = min(prev.w, 200)            # 0층 바닥(화면 전체 폭)은 200으로 취급
        distance = prev_w / 2 + random.uniform(*rules["gap_x"]) + w / 2
        low, high = w / 2 + 20, WIDTH - w / 2 - 20
        side = random.choice([-1, 1])
        center_x = prev.center0 + side * distance
        if not low <= center_x <= high:
            center_x = prev.center0 - side * distance
        center_x = clamp(center_x, low, high)
        self.platforms.append(Platform(floor, center_x, y, w, kind, rules["moving_speed"]))

    def ensure_platforms(self):
        """지금 층보다 15층 위까지 발판을 미리 만들어 둔다 (무한 모드는 계속 이어진다)."""
        while self.platforms[-1].floor < self.highest + 15:
            if self.goal and self.platforms[-1].floor >= self.goal:
                break
            self.add_platform()

    def nearby_platforms(self):
        """화면에 보일 만한 발판만 골라 계산량을 줄인다."""
        return self.platforms[max(0, self.highest - 12): self.highest + 16]

    # ── 입력 ──
    def on_key_down(self, event):
        key = event.keysym
        if self.state == "title":
            if key == "Up":
                self.mode_index = (self.mode_index - 1) % len(MODES)
                self.reset()
            elif key == "Down":
                self.mode_index = (self.mode_index + 1) % len(MODES)
                self.reset()
            elif key in ("1", "2", "3", "4"):
                self.mode_index = int(key) - 1
                self.start()
            elif key in ("Return", "space"):
                self.start()
            return
        if self.state in ("over", "clear"):
            if key in ("Return", "space"):
                self.start()
            elif key == "Escape":
                self.go_to_title()
            return
        if key == "Escape":
            self.go_to_title()
            return
        if key in ("Up", "space") and key not in self.keys:
            self.jump_buffer = JUMP_BUFFER
        self.keys.add(key)

    def on_key_up(self, event):
        self.keys.discard(event.keysym)

    def on_mouse_down(self, event):
        if self.state == "title":
            for i, (x1, y1, x2, y2) in enumerate(self.title_layout()[3]):
                if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                    self.mode_index = i
                    self.start()
            return
        if self.state != "play":
            self.start()
            return
        for key, (x, y, _) in BUTTONS.items():
            if x <= event.x <= x + BUTTON_SIZE and y <= event.y <= y + BUTTON_SIZE:
                self.mouse_key = key
                if key == "Up":
                    self.jump_buffer = JUMP_BUFFER

    def on_mouse_up(self, event):
        self.mouse_key = None

    def pressed(self, key):
        return key in self.keys or self.mouse_key == key

    # ── 게임 진행 ──
    def update(self):
        p = self.player
        nearby = self.nearby_platforms()
        for plat in nearby:
            plat.update()

        # 좌우 이동. 밟고 있는 발판 종류에 따라 움직임이 달라진다.
        target = 0
        if self.pressed("Left"):
            target -= MOVE_SPEED
            p.facing = -1
        if self.pressed("Right"):
            target += MOVE_SPEED
            p.facing = 1
        surface = p.standing.kind if p.standing else None
        if surface == "slow":
            target *= SLOW_FACTOR
        if surface == "ice":
            p.vx += (target - p.vx) * ICE_GRIP   # 천천히 빨라지고 천천히 멈춘다
        else:
            p.vx = target
        if p.standing:
            p.x += p.standing.speed               # 움직이는 발판 위에서는 같이 이동
        p.x = clamp(p.x + p.vx, 0, WIDTH - PLAYER_W)

        # 점프는 발판 위에 서 있을 때만 가능
        if self.jump_buffer > 0 and p.standing:
            p.vy = -JUMP_POWER
            self.jump_buffer = 0
        self.jump_buffer = max(0, self.jump_buffer - 1)

        # 중력
        p.vy += GRAVITY
        if self.pressed("Down"):
            p.vy += FAST_FALL
        p.vy = min(p.vy, MAX_FALL_SPEED)
        old_bottom = p.y + PLAYER_H
        p.y += p.vy

        # 착지 판정: 내려오는 중에 발판 윗면을 지나쳤으면 그 위에 세운다.
        # 올라갈 때는 발판을 통과하므로 아래에서 점프해 올라탈 수 있다.
        p.standing = None
        if p.vy > 0:
            for plat in nearby:
                overlap_x = plat.x < p.x + PLAYER_W and p.x < plat.x + plat.w
                if overlap_x and old_bottom <= plat.y <= p.y + PLAYER_H:
                    p.y = plat.y - PLAYER_H
                    p.vy = 0
                    p.standing = plat
                    self.on_land(plat)
                    break

        # 카메라: 주인공이 화면 위쪽 35% 선을 넘으면 따라 올라간다 (내려가지는 않음)
        top_line = self.cam_y + HEIGHT * 0.35
        if p.y < top_line:
            self.cam_y += (p.y - top_line) * 0.15

        # 화면 아래로 떨어지면 추락
        if p.y > self.cam_y + HEIGHT + 20:
            self.lose_life()

        self.flash = max(0, self.flash - 1)
        self.blink = max(0, self.blink - 1)

    def on_land(self, plat):
        if plat.floor <= self.highest:
            return
        self.highest = plat.floor
        self.best_platform = plat
        if plat.floor == self.goal:
            self.end_game("clear")
            return
        self.ensure_platforms()
        self.check_invert()

    def check_invert(self):
        """돌발 상황: 8~10층을 오를 때마다 화면이 반전되고, 3층을 더 오르면 원래대로 돌아온다."""
        if not self.inverted and self.highest >= self.next_invert:
            self.inverted = True
            self.revert_at = self.highest + REVERT_AFTER
            self.flash = FLASH_FRAMES
        elif self.inverted and self.highest >= self.revert_at:
            self.inverted = False
            self.next_invert = self.highest + random.randint(*INVERT_GAP)
            self.flash = FLASH_FRAMES

    def lose_life(self):
        self.lives -= 1
        if self.lives == 0:
            self.end_game("over")
            return
        # 가장 높이 올라갔던 발판 위에서 부활
        plat = self.best_platform
        p = self.player
        p.x = plat.x + plat.w / 2 - PLAYER_W / 2
        p.y = plat.y - PLAYER_H
        p.vx = 0
        p.vy = 0
        p.standing = plat
        self.cam_y = min(0, plat.y - HEIGHT * 0.6)
        self.blink = 60

    def update_bubbles(self):
        for bubble in self.bubbles:
            bubble[1] -= bubble[3]
            bubble[0] += math.sin(bubble[1] / 25) * 0.3
            if bubble[1] < -10:
                bubble[0] = random.uniform(0, WIDTH)
                bubble[1] = HEIGHT + 10

    def loop(self):
        if self.state == "play":
            self.update()
        self.update_bubbles()
        self.draw()
        self.root.after(FRAME_MS, self.loop)

    # ── 그리기 ──
    def color(self, name):
        return INVERTED_COLORS[name] if self.inverted else COLORS[name]

    def draw(self):
        c = self.canvas
        c.delete("all")
        self.draw_background()
        self.draw_platforms()
        self.draw_player()
        self.draw_hud()
        self.draw_buttons()
        if self.state == "title":
            self.draw_title()
        elif self.state != "play":
            self.draw_result()
        # 번쩍임: 반전되는 순간 흰 화면을 한 번 보여준다
        if self.flash > 0:
            c.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#ffffff", outline="")

    def draw_background(self):
        """바닷속 배경: 물결선은 화면보다 느리게 움직여 깊이감을 주고, 물방울은 위로 떠오른다."""
        c = self.canvas
        c.create_rectangle(0, 0, WIDTH, HEIGHT, fill=self.color("bg"), outline="")
        scroll = self.cam_y * 0.5
        first = math.floor(scroll / WAVE_BAND)
        for band in range(first - 1, first + HEIGHT // WAVE_BAND + 2):
            rng = random.Random(band * 7919 + self.bg_seed)   # 같은 묶음은 항상 같은 모양
            for _ in range(2):
                x = rng.uniform(-100, WIDTH - 100)
                base_y = band * WAVE_BAND + rng.uniform(0, WAVE_BAND) - scroll
                points = []
                for i in range(rng.randint(5, 11)):
                    points += [x + i * 40, base_y + rng.uniform(-14, 14)]
                c.create_line(*points, fill=self.color("wave"), width=6, smooth=True, capstyle="round")
        for x, y, r, _ in self.bubbles:
            c.create_oval(x - r, y - r, x + r, y + r, outline=self.color("bubble"), width=2)

    def draw_platforms(self):
        c = self.canvas
        for plat in self.nearby_platforms():
            y = plat.y - self.cam_y
            if y < -100 or y > HEIGHT + 20:
                continue
            x1, x2, y2 = plat.x, plat.x + plat.w, y + PLATFORM_H
            if plat.kind in ("ice", "slow"):
                c.create_rectangle(x1, y, x2, y2, fill=self.color(plat.kind), outline=self.color("line"), width=2)
            else:
                fill = self.color("platform") if plat.kind == "normal" else self.color(plat.kind)
                c.create_rectangle(x1, y, x2, y2, fill=fill, outline="")
            if plat.kind == "ice":       # 반짝이는 줄
                c.create_line(x1 + 8, y + 4, x2 - 8, y + 4, fill=self.color("eye"), width=2)
            if plat.kind == "slow":      # 아래로 흘러내리는 진흙
                for i in range(1, 4):
                    dx = x1 + plat.w * i / 4
                    c.create_oval(dx - 4, y2 - 2, dx + 4, y2 + 8, fill=self.color("slow"), outline="")
            if plat.kind == "goal":
                door_x = plat.x + plat.w / 2
                c.create_rectangle(door_x - 25, y - 70, door_x + 25, y, fill=self.color("goal"),
                                   outline=self.color("line"), width=2)
                c.create_text(door_x, y - 35, text="EXIT", fill=self.color("eye"), font=(FONT, 10, "bold"))

    def draw_player(self):
        # 부활 직후에는 깜빡인다
        if self.blink > 0 and (self.blink // 5) % 2 == 0:
            return
        c = self.canvas
        p = self.player
        x, y = p.x, p.y - self.cam_y
        w, h = PLAYER_W, PLAYER_H
        c.create_oval(x - 3, y + 2, x + w + 3, y + h + 2, fill=self.color("shade"), outline="")
        c.create_oval(x, y, x + w, y + h, fill=self.color("body"), outline="")
        # 눈동자와 입은 바라보는 방향으로 살짝 치우친다
        look = p.facing * 2
        for eye_x in (x + 14, x + 30):
            c.create_oval(eye_x - 7, y + 10, eye_x + 7, y + 22, fill=self.color("eye"),
                          outline=self.color("line"), width=2)
            c.create_oval(eye_x - 3 + look, y + 13, eye_x + 3 + look, y + 19, fill=self.color("line"), outline="")
        mx, my = x + w / 2 + look, y + 32
        c.create_polygon(mx, my - 5, mx + 5, my, mx, my + 5, mx - 5, my,
                         fill=self.color("body"), outline=self.color("line"), width=2)

    def draw_hud(self):
        c = self.canvas
        name = MODES[self.mode_index][0]
        goal_text = f"목표 {self.goal} F" if self.goal else "끝없이"
        # 발판이 글자 위로 지나가도 읽을 수 있도록 배경색 받침을 깐다
        c.create_rectangle(0, 0, 200, 78, fill=self.color("bg"), outline="")
        c.create_text(20, 16, text=f"{self.highest} F", anchor="nw",
                      fill=self.color("text"), font=(FONT, 22, "bold"))
        c.create_text(22, 54, text=f"{name} · {goal_text}", anchor="nw",
                      fill=self.color("text"), font=(FONT, 11, "bold"))
        # 남은 목숨은 빨간 하트, 사용한 목숨은 회색 하트
        c.create_rectangle(WIDTH - 170, 0, WIDTH, 68, fill=self.color("bg"), outline="")
        for i in range(MAX_LIVES):
            heart = "heart" if i < self.lives else "heart_empty"
            x = WIDTH - 40 - (MAX_LIVES - 1 - i) * 45
            c.create_text(x, 34, text="♥", fill=self.color(heart), font=(FONT, 30))
        if self.inverted and self.state == "play":
            left = self.revert_at - self.highest
            c.create_text(WIDTH / 2, 30, text=f"모래알이 덮쳐왔다! {left}층 더 오르면 돌아온다!",
                          fill=self.color("text"), font=(FONT, 13, "bold"))

    def draw_buttons(self):
        c = self.canvas
        for key, (x, y, symbol) in BUTTONS.items():
            fill = self.color("pressed") if self.pressed(key) else self.color("button")
            c.create_rectangle(x, y, x + BUTTON_SIZE, y + BUTTON_SIZE, fill=fill,
                               outline=self.color("line"), width=3)
            c.create_text(x + BUTTON_SIZE / 2, y + BUTTON_SIZE / 2, text=symbol,
                          fill=self.color("line"), font=(FONT, 16))

    def title_layout(self):
        """시작 화면 패널의 위치와 난이도 버튼 4개의 위치 (그리기와 클릭 판정에 같이 쓴다)"""
        left, right, top = WIDTH / 2 - 300, WIDTH / 2 + 300, 30
        options = []
        for i in range(len(MODES)):
            y = top + 140 + i * 44
            options.append((left + 70, y, right - 70, y + 36))
        return left, right, top, options

    def draw_title(self):
        c = self.canvas
        left, right, top, options = self.title_layout()
        c.create_rectangle(left, top, right, top + 470, fill=self.color("panel"),
                           outline=self.color("line"), width=3)
        texts = [
            (top + 40, "바닷속 탈출", 28, "bold"),
            (top + 85, "깊은 바닷속에서 눈을 떴다.", 13, "normal"),
            (top + 112, "발판을 밟고 올라가 수면 위 출구로 탈출하자!", 13, "normal"),
        ]
        for y, text, size, weight in texts:
            c.create_text(WIDTH / 2, y, text=text, fill=self.color("text"), font=(FONT, size, weight))
        for i, (x1, y1, x2, y2) in enumerate(options):
            name, _, goal = MODES[i]
            selected = i == self.mode_index
            c.create_rectangle(x1, y1, x2, y2, fill=self.color("pressed" if selected else "panel"),
                               outline=self.color("line"), width=3 if selected else 1)
            goal_text = f"목표 {goal} F" if goal else "끝없이"
            c.create_text(x1 + 20, (y1 + y2) / 2, text=f"{i + 1}. {name}", anchor="w",
                          fill=self.color("text"), font=(FONT, 14, "bold"))
            c.create_text(x1 + 140, (y1 + y2) / 2, text=goal_text, anchor="w",
                          fill=self.color("text"), font=(FONT, 12))
            if self.records[i]:
                c.create_text(x2 - 20, (y1 + y2) / 2, text=f"최고 {self.records[i]} F", anchor="e",
                              fill=self.color("faint"), font=(FONT, 11))
        legend_y = top + 340
        c.create_text(WIDTH / 2, legend_y, text="←/→ 이동    ↑·Space 점프    ↓ 빠르게 내려오기",
                      fill=self.color("text"), font=(FONT, 12))
        # 발판 종류 안내
        samples = [("platform", "보통"), ("moving", "움직임"), ("ice", "미끄러움"), ("slow", "느려짐")]
        for i, (kind, label) in enumerate(samples):
            x = left + 95 + i * 115
            outline = self.color("line") if kind in ("ice", "slow") else ""
            c.create_rectangle(x, legend_y + 30, x + 34, legend_y + 40, fill=self.color(kind), outline=outline)
            c.create_text(x + 40, legend_y + 35, text=label, anchor="w",
                          fill=self.color("text"), font=(FONT, 11))
        c.create_text(WIDTH / 2, legend_y + 85, text="↑/↓로 고르고 Enter로 시작 (숫자키·클릭도 가능)",
                      fill=self.color("text"), font=(FONT, 13, "bold"))

    def draw_result(self):
        name = MODES[self.mode_index][0]
        if self.state == "clear":
            title = "수면 위로 탈출 성공!"
            detail = f"{name} 모드 · 남은 목숨 {self.lives}개"
        elif self.goal is None:
            title = "게임 오버"
            detail = f"무한 모드 기록: {self.highest} F (최고 {self.records[self.mode_index]} F)"
        else:
            title = "탈출 실패"
            detail = f"{name} 모드 · {self.highest} F / {self.goal} F"
        lines = [(title, 28, "bold"), (detail, 15, "normal"),
                 ("Enter·클릭: 다시 하기    Esc: 난이도 선택", 13, "normal")]
        c = self.canvas
        top = HEIGHT / 2 - 100
        c.create_rectangle(WIDTH / 2 - 290, top, WIDTH / 2 + 290, top + 180,
                           fill=self.color("panel"), outline=self.color("line"), width=3)
        for i, (text, size, weight) in enumerate(lines):
            c.create_text(WIDTH / 2, top + 45 + i * 45, text=text,
                          fill=self.color("text"), font=(FONT, size, weight))


if __name__ == "__main__":
    root = tk.Tk()
    root.title("바닷속 탈출")
    root.resizable(False, False)
    Game(root)
    root.mainloop()
