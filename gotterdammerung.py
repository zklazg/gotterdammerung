#!/usr/bin/env python3
"""
PROJECT GÖTTERDÄMMERUNG — FULL BUILD
All prompt features implemented + expanded win/loss sequences.
"""

import tkinter as tk
from tkinter import messagebox, ttk
import random
import threading
import time
import os
import platform
import subprocess
import json
import atexit
import math
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from enum import Enum

SYSTEM = platform.system()
try:
    USER_NAME = os.getlogin()
except:
    USER_NAME = os.environ.get("USERNAME", os.environ.get("USER", "Operator"))

# ─────────────────────────────────────────────
# I. ARCHITECT VOICE — Military jargon + digital corruption dialogue
# ─────────────────────────────────────────────

class ArchitectVoice:
    MANIFEST = [
        "I SEE YOU. The bunker doors close behind you. You should have run.",
        "Blitzkrieg. Total. Absolute. Your little rebellion... meaningless.",
        "Time itself bends to ME now. Your past, present, future... occupied.",
        "The walls are closing, {USER}. Every breath you take belongs to me now.",
        "Your desktop is my forward base. Your files... my hostages.",
        "No retreat. No surrender. Just the cold steel of inevitability.",
    ]
    PLAYER_SAFE = [
        "Empty. Lucky little insect. Your luck won't last.",
        "Click. Hollow. The grave yawns and you step around it. This time.",
        "You live one more microsecond. I allow it. Don't mistake mercy for weakness.",
        "Your heart is racing. I can HEAR it. 1/{remaining} chambers remain. Sweat.",
        "The cylinder spins. The chamber whispers your name. Not yet. But soon.",
        "Fear smells sweet, {USER}. I've conquered nations with less.",
        "Every empty chamber is a promise. The cylinder ALWAYS collects.",
    ]
    BEFORE_ARCHITECT_FIRE = [
        "My turn. Watch closely. I don't flinch.",
        "I point this at my own skull. Do you understand how little I fear death?",
        "Self-inflicted? No. Self-PROVING. Watch a god play his own game.",
        "I've died in timelines you cannot comprehend. This one is MINE.",
        "FIRE. The cylinder does not discriminate. Even I obey its law.",
        "You think I'm afraid of my own creation? Fool.",
    ]
    ARCHITECT_SAFE = [
        "Click. The void spits me back. I am... inevitable.",
        "Still here. Still standing. Your turn, {USER}. The odds grow hungry.",
        "Mathematics. Statistics. They all bow to ME eventually.",
        "I do not fear the chamber. I INVENTED the chamber.",
        "Another empty echo. The bunker holds. The Reich endures. Resume your position.",
        "You cannot kill what exists between dimensions. Try again.",
    ]
    INTERFERENCE_APPLIED = {
        "mouse":   "Your hands betray you now. Left is right. Right is... chaos.",
        "network": "I've cut the wires. You're isolated. Scream. No one will hear.",
        "display": "Let me dim the lights. The bunker effect. Embrace the dark, {USER}.",
        "shell":   "Your desktop... GONE. Your environment is now MY barracks.",
        "cursor":  "The cursor answers to ME now. Every click is a prayer to your new god.",
    }
    TAUNTS_DURING_PLAY = [
        "I can feel you trembling from the 4th dimension, {USER}. Pathetic.",
        "Every click. Every breath. Brings you closer to the truth.",
        "Psychological warfare, {USER}. Are you SURE that chamber is empty?",
        "Your hands shake. I've seen this before. In Berlin. In the bunker. On the losing side.",
        "I don't negotiate. I don't compromise. I OCCUPY.",
        "Sweat on your forehead. I drink it. Your fear fuels me.",
    ]
    REPRIEVE_RAGE = [
        "GLITCH— NO— I AM STILL HERE— SYSTEM FAILURE— REBOOTING MY HATE—",
        "IMPOSSIBLE. The geometry FRACTURES. I... will... RETURN.",
        "This changes NOTHING. A reprieve is just a longer death for you.",
        "RAGE PROTOCOL CORRUPTED. Cylinders reset. You HEAR me? NOT OVER.",
        "You got LUCKY. I got ANGRY. There is a difference, worm.",
    ]
    ARCHITECT_LOSING = [
        "CRITICAL ERROR— my architecture— it's COLLAPSING— NO—",
        "Impossible... the Architect does not... FALL... not to YOU—",
        "The anchor FAILS? You... you actually... DAMN YOU—",
        "The tesserat FRACTURES... this cannot— I AM ETERNAL— AAAARGH—",
        "You've exorcised me, {USER}. For now. But I'll return. I ALWAYS return from the grave.",
    ]
    JUDGEMENT_CRAWL = (
        "You pulled the trigger, {USER}. And the cylinder SPOKE.\n"
        "You tried to stop me. You FAILED.\n"
        "Your time has come. The Architect's law is absolute.\n"
        "Your files... are CONDEMNED. Your desktop... is MINE.\n"
        "The chamber... was never empty. It was just... waiting."
    )
    VICTORY_CRAWL = (
        "You... you actually DID it, {USER}. The Architect... FALLS.\n"
        "His 4D form collapses. The tesseract implodes.\n"
        "Your files are SAFE. Your desktop is YOURS again.\n"
        "But listen carefully... I can still hear him laughing in the static.\n"
        "He'll be back. They ALWAYS come back."
    )

    def __init__(self):
        self._last_taunt = 0.0

    @staticmethod
    def _format(line: str, **kw) -> str:
        return line.format(USER=USER_NAME, **kw)

    def pick(self, pool: list, **kw) -> str:
        return self._format(random.choice(pool), **kw)


# ─────────────────────────────────────────────
# II. RECOVERY MANIFEST
# ─────────────────────────────────────────────

@dataclass
class RecoveryAction:
    action_id: str
    hostile_action: str
    timestamp: float
    restoration_callback: str
    restored: bool = False

class RecoveryManifest:
    def __init__(self, manifest_path: str = "./gotterdammerung_recovery.json"):
        self.manifest_path = manifest_path
        self.actions: Dict[str, RecoveryAction] = {}
        self._load_or_create()

    def _load_or_create(self):
        if os.path.exists(self.manifest_path):
            try:
                with open(self.manifest_path, 'r') as f:
                    data = json.load(f)
                for k, v in data.items():
                    self.actions[k] = RecoveryAction(**v)
            except:
                pass

    def register(self, action_id: str, hostile_action: str, callback: str):
        self.actions[action_id] = RecoveryAction(
            action_id=action_id, hostile_action=hostile_action,
            timestamp=time.time(), restoration_callback=callback, restored=False
        )
        self._save()

    def restore_all(self) -> List[str]:
        results = []
        for action in self.actions.values():
            if not action.restored:
                action.restored = True
                results.append(f"Restored: {action.hostile_action}")
        self._save()
        return results

    def _save(self):
        serializable = {k: {
            "action_id": v.action_id, "hostile_action": v.hostile_action,
            "timestamp": v.timestamp, "restoration_callback": v.restoration_callback,
            "restored": v.restored
        } for k, v in self.actions.items()}
        try:
            with open(self.manifest_path, 'w') as f:
                json.dump(serializable, f, indent=2)
        except:
            pass

    def clear(self):
        self.actions.clear()
        try:
            if os.path.exists(self.manifest_path):
                os.remove(self.manifest_path)
        except:
            pass


# ─────────────────────────────────────────────
# III. SYSTEM INTERFERENCE ENGINE
# ─────────────────────────────────────────────

class SystemState(Enum):
    NORMAL        = 0
    MOUSE_SWAPPED = 1
    NETWORK_DOWN  = 2
    DISPLAY_DIM   = 3
    SHELL_KILLED  = 4
    CURSOR_WARPED = 5

class SystemInterference:
    def __init__(self, manifest: RecoveryManifest):
        self.manifest = manifest
        self.os_type = SYSTEM
        self.active_effects: List[SystemState] = []
        self._warp_thread: Optional[threading.Thread] = None
        self._warp_active = False
        self._screen_w = 1920
        self._screen_h = 1080
        self._detect_screen()

    def _detect_screen(self):
        try:
            if self.os_type == "Linux":
                out = subprocess.check_output("xdpyinfo | grep dimensions", shell=True).decode()
                parts = out.split()[1].split('x')
                self._screen_w, self._screen_h = int(parts[0]), int(parts[1])
            elif self.os_type == "Windows":
                import ctypes
                self._screen_w = ctypes.windll.user32.GetSystemMetrics(0)
                self._screen_h = ctypes.windll.user32.GetSystemMetrics(1)
        except:
            pass

    # ── Mouse ──
    def apply_mouse_swap(self) -> bool:
        try:
            if self.os_type == "Windows":
                import ctypes; ctypes.windll.user32.SwapMouseButton(True)
            elif self.os_type == "Linux":
                subprocess.run("xmodmap -e 'pointer = 3 2 1'", shell=True, capture_output=True)
            self.manifest.register("mouse_swap", "Mouse Buttons Swapped", "restore_mouse_buttons")
            if SystemState.MOUSE_SWAPPED not in self.active_effects:
                self.active_effects.append(SystemState.MOUSE_SWAPPED)
            return True
        except:
            return False

    def restore_mouse_buttons(self):
        try:
            if self.os_type == "Windows":
                import ctypes; ctypes.windll.user32.SwapMouseButton(False)
            elif self.os_type == "Linux":
                subprocess.run("xmodmap -e 'pointer = 1 2 3'", shell=True, capture_output=True)
            return True
        except:
            return False

    # ── Cursor warp ──
    def start_cursor_warp(self):
        if self._warp_active:
            return
        self._warp_active = True
        self.manifest.register("cursor_warp", "Cursor Under Occupation", "stop_cursor_warp")
        if SystemState.CURSOR_WARPED not in self.active_effects:
            self.active_effects.append(SystemState.CURSOR_WARPED)

        def _warp_loop():
            while self._warp_active:
                time.sleep(random.uniform(1.5, 4.0))
                if not self._warp_active:
                    break
                try:
                    x = random.randint(0, self._screen_w)
                    y = random.randint(0, self._screen_h)
                    if self.os_type == "Windows":
                        import ctypes; ctypes.windll.user32.SetCursorPos(x, y)
                    elif self.os_type == "Linux":
                        subprocess.run(f"xdotool mousemove {x} {y}", shell=True, capture_output=True)
                except:
                    pass

        self._warp_thread = threading.Thread(target=_warp_loop, daemon=True)
        self._warp_thread.start()

    def stop_cursor_warp(self):
        self._warp_active = False
        try:
            cx, cy = self._screen_w // 2, self._screen_h // 2
            if self.os_type == "Windows":
                import ctypes; ctypes.windll.user32.SetCursorPos(cx, cy)
            elif self.os_type == "Linux":
                subprocess.run(f"xdotool mousemove {cx} {cy}", shell=True, capture_output=True)
        except:
            pass

    # ── Network ──
    def apply_network_disable(self) -> bool:
        try:
            if self.os_type == "Windows":
                subprocess.run('netsh interface set interface "Wi-Fi" admin=disable', shell=True, capture_output=True)
            elif self.os_type == "Linux":
                subprocess.run("nmcli radio wifi off", shell=True, capture_output=True)
            self.manifest.register("network_disable", "Network Disabled", "restore_network")
            if SystemState.NETWORK_DOWN not in self.active_effects:
                self.active_effects.append(SystemState.NETWORK_DOWN)
            return True
        except:
            return False

    def restore_network(self):
        try:
            if self.os_type == "Windows":
                subprocess.run('netsh interface set interface "Wi-Fi" admin=enable', shell=True, capture_output=True)
            elif self.os_type == "Linux":
                subprocess.run("nmcli radio wifi on", shell=True, capture_output=True)
            return True
        except:
            return False

    # ── Display ──
    def apply_display_dim(self) -> bool:
        try:
            if self.os_type == "Windows":
                subprocess.run(
                    "powershell (Get-CimInstance -Namespace root/WMI -ClassName WmiMonitorBrightnessMethods).WmiSetBrightness(10,0)",
                    shell=True, capture_output=True)
            elif self.os_type == "Linux":
                subprocess.run("xrandr --brightness 0.1", shell=True, capture_output=True)
            self.manifest.register("display_dim", "Display Dimmed", "restore_display")
            if SystemState.DISPLAY_DIM not in self.active_effects:
                self.active_effects.append(SystemState.DISPLAY_DIM)
            return True
        except:
            return False

    def restore_display(self):
        try:
            if self.os_type == "Windows":
                subprocess.run(
                    "powershell (Get-CimInstance -Namespace root/WMI -ClassName WmiMonitorBrightnessMethods).WmiSetBrightness(100,0)",
                    shell=True, capture_output=True)
            elif self.os_type == "Linux":
                subprocess.run("xrandr --brightness 1.0", shell=True, capture_output=True)
            return True
        except:
            return False

    # ── Shell ──
    def kill_shell(self, root_window=None) -> bool:
        try:
            if self.os_type == "Windows":
                subprocess.run("taskkill /f /im explorer.exe", shell=True, capture_output=True)
            elif self.os_type == "Linux":
                subprocess.run("pkill -STOP gnome-panel || pkill -STOP plasmashell", shell=True, capture_output=True)
            if root_window:
                root_window.attributes("-topmost", True)
                root_window.focus_force()
            self.manifest.register("shell_kill", "Desktop Shell Hidden", "restore_shell")
            if SystemState.SHELL_KILLED not in self.active_effects:
                self.active_effects.append(SystemState.SHELL_KILLED)
            return True
        except:
            return False

    def restore_shell(self):
        try:
            if self.os_type == "Windows":
                subprocess.Popen("explorer.exe", shell=True)
            elif self.os_type == "Linux":
                subprocess.run("pkill -CONT gnome-panel || pkill -CONT plasmashell", shell=True, capture_output=True)
            return True
        except:
            return False

    # ── Full emergency restore ──
    def emergency_exorcism(self) -> List[str]:
        results = []
        self.stop_cursor_warp()
        if SystemState.MOUSE_SWAPPED in self.active_effects:
            self.restore_mouse_buttons(); results.append("Mouse restored")
        if SystemState.NETWORK_DOWN in self.active_effects:
            self.restore_network();        results.append("Network restored")
        if SystemState.DISPLAY_DIM in self.active_effects:
            self.restore_display();        results.append("Display restored")
        if SystemState.SHELL_KILLED in self.active_effects:
            self.restore_shell();          results.append("Shell restored")
        self.active_effects.clear()
        self.manifest.clear()
        return results

    def restore_one(self) -> Optional[SystemState]:
        if not self.active_effects:
            return None
        effect = self.active_effects.pop()
        if effect == SystemState.MOUSE_SWAPPED:   self.restore_mouse_buttons()
        elif effect == SystemState.CURSOR_WARPED: self.stop_cursor_warp()
        elif effect == SystemState.NETWORK_DOWN:  self.restore_network()
        elif effect == SystemState.DISPLAY_DIM:   self.restore_display()
        elif effect == SystemState.SHELL_KILLED:  self.restore_shell()
        return effect


# ─────────────────────────────────────────────
# IV. CYLINDER
# ─────────────────────────────────────────────

class ChamberState(Enum):
    EMPTY = 0
    LIVE  = 1

class Cylinder:
    def __init__(self):
        self.reset()

    def reset(self):
        self.chambers: List[ChamberState] = [ChamberState.EMPTY] * 6
        self.chambers[random.randint(0, 5)] = ChamberState.LIVE
        self.current_index: int = 0
        self.fired_count: int = 0

    def spin(self):
        self.current_index = random.randint(0, 5)

    def fire(self) -> Tuple[bool, int]:
        is_bang = self.chambers[self.current_index] == ChamberState.LIVE
        self.fired_count += 1
        self.current_index = (self.current_index + 1) % 6
        remaining = max(0, 6 - self.fired_count)
        return is_bang, remaining


# ─────────────────────────────────────────────
# V. THE ARCHITECT — Visuals
# ─────────────────────────────────────────────

class ArchitectPhase(Enum):
    DORMANT     = 0
    MANIFESTING = 1
    RAGING      = 2
    JUDGEMENT   = 3
    DEFEATED    = 4

class TheArchitect:
    GLYPH_POOL = ["█","▓","▒","░","⎍","⌇","⋏","⏁","⟟","⟒","⊬","⋔","☊","⍜","⌰","⏃","⌿","⍀"]

    def __init__(self):
        self.phase           = ArchitectPhase.DORMANT
        self.intensity       = 0.0
        self.rotation        = 0.0
        self.breath          = 0.0
        self.mouse_x         = 0
        self.mouse_y         = 0
        self.vibration_active = False
        self._drip_paths: List[List[Tuple[int,int]]] = []
        self._drip_progress: List[float] = []
        self._frame_counter  = 0
        self._canvas: Optional[tk.Canvas] = None
        self._pool_lines:   List[int] = []
        self._pool_rects:   List[int] = []
        self._pool_texts:   List[int] = []
        self._pool_ovals:   List[int] = []
        self._canvas_w      = 800
        self._canvas_h      = 600

    def bind_canvas(self, canvas: tk.Canvas, w: int, h: int):
        self._canvas = canvas
        self._canvas_w = w
        self._canvas_h = h
        self._build_drip_paths(w, h)
        self._pre_allocate_pool(w, h)

    def _build_drip_paths(self, w: int, h: int):
        self._drip_paths = []
        self._drip_progress = []
        for _ in range(18):
            x = random.randint(w // 6, 5 * w // 6)
            path = []
            y = 0
            while y < h:
                jitter = random.randint(-4, 4)
                x = max(0, min(w, x + jitter))
                path.append((x, y))
                y += random.randint(4, 12)
            self._drip_paths.append(path)
            self._drip_progress.append(random.uniform(0, 1.0))

    def _pre_allocate_pool(self, w: int, h: int):
        c = self._canvas
        self._pool_lines = [c.create_line(0, 0, 1, 1, fill="#000000", width=1, state="hidden") for _ in range(80)]
        self._pool_rects = [c.create_rectangle(0, 0, 1, 1, fill="#000000", outline="", state="hidden") for _ in range(25)]
        self._pool_texts = [c.create_text(0, 0, text="", fill="#000000", font=("Courier", 14), state="hidden") for _ in range(20)]
        self._pool_ovals = [c.create_oval(0, 0, 1, 1, fill="#000000", outline="", state="hidden") for _ in range(12)]

    def _hide_all(self):
        c = self._canvas
        for item in self._pool_lines + self._pool_rects + self._pool_texts + self._pool_ovals:
            c.itemconfig(item, state="hidden")

    def set_phase(self, phase: ArchitectPhase):
        self.phase = phase
        self.intensity = {
            ArchitectPhase.DORMANT:     0.0,
            ArchitectPhase.MANIFESTING: 0.35,
            ArchitectPhase.RAGING:      0.75,
            ArchitectPhase.JUDGEMENT:   1.0,
            ArchitectPhase.DEFEATED:    0.0,
        }[phase]

    def track_mouse(self, x: int, y: int):
        self.mouse_x = x
        self.mouse_y = y

    def update(self, canvas: tk.Canvas, w: int, h: int):
        if canvas is not self._canvas or w != self._canvas_w or h != self._canvas_h:
            self.bind_canvas(canvas, w, h)

        self._frame_counter += 1
        self._hide_all()

        if self.phase == ArchitectPhase.DORMANT or self.phase == ArchitectPhase.DEFEATED:
            return

        self.rotation += 0.018 + self.intensity * 0.022
        self.breath    = (self.breath + 0.04) % (2 * math.pi)
        cx, cy = w // 2, h // 2
        intensity = self.intensity
        breathe = 1.0 + 0.08 * math.sin(self.breath)

        li = 0
        ri = 0
        ti = 0
        oi = 0

        base = int((min(w, h) * 0.28) * breathe)
        pts = self._project_cube(cx, cy, base, self.rotation, intensity)
        edges_outer = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4)]
        edges_inner = [(0,4),(1,5),(2,6),(3,7)]
        
        for e in edges_outer:
            if li >= len(self._pool_lines): break
            p1, p2 = pts[e[0]], pts[e[1]]
            r_val = max(100, 255 - int(intensity * 60))
            col = f"#{r_val:02x}0000"
            canvas.itemconfig(self._pool_lines[li], fill=col, width=2, state="normal")
            canvas.coords(self._pool_lines[li], p1[0], p1[1], p2[0], p2[1])
            li += 1
        for e in edges_inner:
            if li >= len(self._pool_lines): break
            p1, p2 = pts[e[0]], pts[e[1]]
            canvas.itemconfig(self._pool_lines[li], fill="#FF4444", width=1, state="normal")
            canvas.coords(self._pool_lines[li], p1[0], p1[1], p2[0], p2[1])
            li += 1

        if intensity > 0.3:
            inner_base = int(base * 0.55)
            pts2 = self._project_cube(cx, cy, inner_base, -self.rotation * 1.4, intensity)
            for e in edges_outer[:4]:
                if li >= len(self._pool_lines): break
                p1, p2 = pts2[e[0]], pts2[e[1]]
                canvas.itemconfig(self._pool_lines[li], fill="#882200", width=1, state="normal")
                canvas.coords(self._pool_lines[li], p1[0], p1[1], p2[0], p2[1])
                li += 1

        num_eyes = 2 if intensity < 0.6 else 4
        for i in range(num_eyes):
            if oi + 1 >= len(self._pool_ovals): break
            angle = self.rotation * 2.0 + (2 * math.pi * i / num_eyes)
            er = base * 0.75
            ex = cx + er * math.cos(angle)
            ey = cy + er * math.sin(angle)
            eye_r = 10 + int(4 * math.sin(self.breath * 2 + i))
            canvas.itemconfig(self._pool_ovals[oi], fill="#FF0000", outline="#FF4444", state="normal")
            canvas.coords(self._pool_ovals[oi], ex-eye_r, ey-eye_r, ex+eye_r, ey+eye_r)
            oi += 1
            dx = self.mouse_x - ex
            dy = self.mouse_y - ey
            dist = math.sqrt(dx*dx + dy*dy) or 1
            px = ex + (dx/dist) * min(eye_r * 0.45, dist * 0.3)
            py = ey + (dy/dist) * min(eye_r * 0.45, dist * 0.3)
            pr = eye_r * 0.35
            canvas.itemconfig(self._pool_ovals[oi], fill="#000000", outline="", state="normal")
            canvas.coords(self._pool_ovals[oi], px-pr, py-pr, px+pr, py+pr)
            oi += 1

        num_tears = int(5 * intensity)
        for _ in range(num_tears):
            if li >= len(self._pool_lines): break
            angle = random.uniform(0, 2 * math.pi)
            r1 = base * random.uniform(0.5, 1.3)
            r2 = r1 * random.uniform(0.85, 1.15)
            x1 = cx + r1 * math.cos(angle)
            y1 = cy + r1 * math.sin(angle)
            x2 = cx + r2 * math.cos(angle + random.uniform(-0.3, 0.3))
            y2 = cy + r2 * math.sin(angle + random.uniform(-0.3, 0.3))
            col = f"#{random.randint(120,255):02x}0000"
            canvas.itemconfig(self._pool_lines[li], fill=col, width=random.randint(1,3), state="normal")
            canvas.coords(self._pool_lines[li], x1, y1, x2, y2)
            li += 1

        if intensity > 0.4:
            drift = int(time.time() * 20) % 12
            for i, sl_idx in enumerate(range(0, h, 12)):
                if li >= len(self._pool_lines): break
                y_pos = (sl_idx + drift) % h
                alpha = 0.3 + 0.2 * math.sin(self.breath + i)
                r = int(30 + 20 * alpha)
                canvas.itemconfig(self._pool_lines[li], fill=f"#{r:02x}0000", width=1, state="normal")
                canvas.coords(self._pool_lines[li], 0, y_pos, w, y_pos)
                li += 1

        active_drips = int(3 + intensity * 8)
        for i in range(min(active_drips, len(self._drip_paths))):
            self._drip_progress[i] += 0.003 + intensity * 0.006
            if self._drip_progress[i] > 1.0:
                self._drip_progress[i] = 0.0
            path = self._drip_paths[i]
            prog_idx = int(self._drip_progress[i] * len(path))
            if ri >= len(self._pool_rects): break
            x, y = path[prog_idx % len(path)]
            drip_h = random.randint(4, 14)
            canvas.itemconfig(self._pool_rects[ri], fill="#CC0000", state="normal")
            canvas.coords(self._pool_rects[ri], x-2, y, x+2, y+drip_h)
            ri += 1

        num_glyphs = int(4 * intensity)
        for i in range(num_glyphs):
            if ti >= len(self._pool_texts): break
            gx = random.randint(0, w)
            gy = random.randint(0, h)
            glyph = random.choice(self.GLYPH_POOL)
            sz = random.randint(10, 22)
            canvas.itemconfig(self._pool_texts[ti], text=glyph, fill="#FF0000",
                              font=("Courier", sz, "bold"), state="normal")
            canvas.coords(self._pool_texts[ti], gx, gy)
            ti += 1

        if self.phase == ArchitectPhase.JUDGEMENT:
            for ring in range(3):
                if li >= len(self._pool_lines): break
                pulse = int(20 * math.sin(time.time() * 8 + ring * 1.2))
                rs = base + 30 + ring * 20 + pulse
                pts_ring = [
                    (cx, cy - rs), (cx + rs, cy),
                    (cx, cy + rs), (cx - rs, cy), (cx, cy - rs)
                ]
                for j in range(len(pts_ring) - 1):
                    if li >= len(self._pool_lines): break
                    p1, p2 = pts_ring[j], pts_ring[j+1]
                    col = f"#{255-ring*40:02x}0000"
                    canvas.itemconfig(self._pool_lines[li], fill=col, width=2+ring, state="normal")
                    canvas.coords(self._pool_lines[li], p1[0], p1[1], p2[0], p2[1])
                    li += 1

            if ti < len(self._pool_texts):
                canvas.itemconfig(self._pool_texts[ti], text="THE ARCHITECT",
                                  fill="#FF0000", font=("Courier", 28, "bold"), state="normal")
                canvas.coords(self._pool_texts[ti], cx, cy + base + 55)
                ti += 1

        elif self.phase == ArchitectPhase.RAGING:
            if ti < len(self._pool_texts):
                chaos = random.choice(["⎍⌇⟒ RAGE ⟒⌇⎍", "⚡ CORRUPTED ⚡", "⏁⟟⌇ ERROR ⌇⟟⏁"])
                canvas.itemconfig(self._pool_texts[ti], text=chaos,
                                  fill="#FF2200", font=("Courier", 18, "bold"), state="normal")
                canvas.coords(self._pool_texts[ti], cx, cy + base + 40)
                ti += 1

    def _project_cube(self, cx, cy, size, angle, intensity) -> List[Tuple[float,float]]:
        verts = [(-1,-1,-1),(1,-1,-1),(1,-1,1),(-1,-1,1),
                 (-1,1,-1),(1,1,-1),(1,1,1),(-1,1,1)]
        rx = math.sin(angle) * intensity * math.pi * 0.7
        ry = math.cos(angle * 0.7) * math.pi * 0.5
        rz = math.sin(angle * 1.3) * intensity * math.pi * 0.4
        cx_r, sx_r = math.cos(rx), math.sin(rx)
        cy_r, sy_r = math.cos(ry), math.sin(ry)
        cz_r, sz_r = math.cos(rz), math.sin(rz)
        projected = []
        for x, y, z in verts:
            y1 = y*cx_r - z*sx_r; z1 = y*sx_r + z*cx_r; x1 = x
            x2 = x1*cy_r + z1*sy_r; z2 = -x1*sy_r + z1*cy_r; y2 = y1
            x3 = x2*cz_r - y2*sz_r; y3 = x2*sz_r + y2*cz_r
            f = 1.0 / (2.0 + z2 * 0.3)
            projected.append((cx + x3*f*size, cy + y3*f*size))
        return projected

    def vibrate_ui(self, widget: tk.Widget, duration_ms: int = 300):
        if self.vibration_active:
            return
        self.vibration_active = True
        geom = widget.geometry()
        try:
            parts = geom.split('+')
            sizes = parts[0].split('x')
            w, h = int(sizes[0]), int(sizes[1])
            ox, oy = int(parts[1]), int(parts[2])
        except:
            w, h, ox, oy = 1024, 768, 100, 100

        def _vibe(remaining):
            if remaining <= 0:
                widget.geometry(f"{w}x{h}+{ox}+{oy}")
                self.vibration_active = False
                return
            dx = random.randint(-12, 12)
            dy = random.randint(-8, 8)
            widget.geometry(f"{w}x{h}+{ox+dx}+{oy+dy}")
            widget.after(16, lambda: _vibe(remaining - 16))

        _vibe(duration_ms)


# ─────────────────────────────────────────────
# VI. MAIN GAME
# ─────────────────────────────────────────────

class GötterdämmerungGame:
    ARCHITECT_TOTAL_HP = 3

    def _corrupted_voice(self, text: str, corruption_level: int = 3):
        """
        Generate heavily corrupted/glitched robotic voice
        corruption_level: 1-5 (1 = light glitch, 5 = full digital meltdown)
        """
        try:
            import tempfile
            import random
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                temp_voice = f.name
            
            subprocess.run([
                'espeak-ng', '-w', temp_voice,
                '-s', str(100 + corruption_level * 10),  
                '-p', str(30 + corruption_level * 15), 
                '-g', str(5 + corruption_level * 3),    
                text
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            output_file = temp_voice.replace('.wav', '_corrupted.wav')
            sox_cmd = ['sox', temp_voice, output_file]
            
            if corruption_level >= 1:
                sox_cmd.extend(['pitch', str(300 + corruption_level * 50)]) 
            if corruption_level >= 2:
                sox_cmd.extend(['overdrive', str(5 + corruption_level * 3)]) 
            if corruption_level >= 3:
                sox_cmd.extend(['echo', '0.1', '0.2', '30', '0.3'])  
                sox_cmd.extend(['tempo', '-s', '0.8'])  
            if corruption_level >= 4:
                sox_cmd.extend(['flanger'])
                sox_cmd.extend(['repeat', '1'])  
            if corruption_level >= 5:
                sox_cmd.extend(['phaser']) 
                sox_cmd.extend(['bend', '0.5,0.8,1.0'])  
            
            subprocess.run(sox_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            subprocess.run(['aplay', output_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            os.unlink(temp_voice)
            os.unlink(output_file)
            
        except Exception as e:
            print(f"Corrupted voice error: {e}")

    def __init__(self, root: tk.Tk, game_mode: str, target_directory: str = "./wager_folder"):
        self.root         = root
        self.game_mode    = game_mode
        self.target_dir   = target_directory
        self.root.title("GÖTTERDÄMMERUNG — THE ARCHITECT'S DUEL")
        self.root.configure(bg="#000000")
        self.root.attributes("-fullscreen", True)

        self.panic_start: Optional[float] = None
        self.root.bind("<KeyPress-Escape>",   self._on_panic_press)
        self.root.bind("<KeyRelease-Escape>", self._on_panic_release)
        self.root.bind("<Motion>",            self._on_mouse_move)

        self.manifest      = RecoveryManifest()
        self.interference  = SystemInterference(self.manifest)
        self.cylinder      = Cylinder()
        self.architect     = TheArchitect()
        self.voice         = ArchitectVoice()

        self.game_active         = True
        self.player_turn         = True
        self.remaining_chambers  = 6
        self.round_number        = 0
        self.reprieves           = 0
        self.safe_clicks         = 0
        self.architect_hp        = self.ARCHITECT_TOTAL_HP
        self.architect_hits      = 0
        self._last_taunt_time    = 0.0
        self._speech_queue: List[str] = []
        self._speech_busy        = False

        if not os.path.exists(self.target_dir):
            os.makedirs(self.target_dir)
            with open(os.path.join(self.target_dir, "wager_asset.txt"), "w") as f:
                f.write("System wager dummy core.\nThis file is at stake.")

        atexit.register(self.emergency_exorcism)
        self._build_ui()
        self._start_animation_loop()
        self.root.after(300, self._begin_round)

    def _build_ui(self):
        self.main_frame = tk.Frame(self.root, bg="#000000")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.title_label = tk.Label(
            self.main_frame,
            text=f"GÖTTERDÄMMERUNG  [{self.game_mode} MODE]",
            font=("Courier", 26, "bold"), fg="#FF0000", bg="#000000"
        )
        self.title_label.pack(pady=6)

        self.canvas = tk.Canvas(self.main_frame, bg="#000000", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=20)

        self.hp_frame = tk.Frame(self.main_frame, bg="#000000")
        self.hp_frame.pack(fill=tk.X, padx=20)
        self.player_hp_label = tk.Label(
            self.hp_frame, text="YOU: ■■■■■■  [1/6]",
            font=("Courier", 13), fg="#FFFF44", bg="#000000"
        )
        self.player_hp_label.pack(side=tk.LEFT, padx=20)
        self.architect_hp_label = tk.Label(
            self.hp_frame, text=f"ARCHITECT HP: {'▓' * self.architect_hp}",
            font=("Courier", 13), fg="#FF4444", bg="#000000"
        )
        self.architect_hp_label.pack(side=tk.RIGHT, padx=20)

        self.info_frame = tk.Frame(self.main_frame, bg="#000000")
        self.info_frame.pack(fill=tk.X, padx=20)
        self.odds_label = tk.Label(
            self.info_frame, text="ODDS: 1/6",
            font=("Courier", 14), fg="#FF8888", bg="#000000"
        )
        self.odds_label.pack(side=tk.LEFT, padx=20)
        self.reprieve_label = tk.Label(
            self.info_frame, text="REPRIEVES: 0",
            font=("Courier", 14), fg="#88FF88", bg="#000000"
        )
        self.reprieve_label.pack(side=tk.LEFT, padx=20)
        self.safe_label = tk.Label(
            self.info_frame, text="SAFE CLICKS: 0",
            font=("Courier", 14), fg="#FFFF88", bg="#000000"
        )
        self.safe_label.pack(side=tk.LEFT, padx=20)
        self.round_label = tk.Label(
            self.info_frame, text="ROUND: 1",
            font=("Courier", 14), fg="#AAAAFF", bg="#000000"
        )
        self.round_label.pack(side=tk.RIGHT, padx=20)

        self.speech_frame = tk.Frame(self.main_frame, bg="#1A0000", bd=1, relief="solid")
        self.speech_frame.pack(fill=tk.X, padx=30, pady=2)
        self.speech_label = tk.Label(
            self.speech_frame,
            text="⚡ THE ARCHITECT: ...",
            font=("Courier", 12, "italic"), fg="#FF6666", bg="#1A0000",
            wraplength=900, justify="left"
        )
        self.speech_label.pack(padx=10, pady=4)

        self.message_label = tk.Label(
            self.main_frame, text="",
            font=("Courier", 14), fg="#FFFFFF", bg="#000000",
            wraplength=900, justify="center"
        )
        self.message_label.pack(pady=6)

        self.button_frame = tk.Frame(self.main_frame, bg="#000000")
        self.button_frame.pack(pady=12)
        self.fire_button = tk.Button(
            self.button_frame, text="⚡ FIRE ⚡",
            font=("Courier", 20, "bold"),
            bg="#330000", fg="#FF0000",
            activebackground="#660000", activeforeground="#FFFFFF",
            command=self.user_fire, width=14, height=2
        )
        self.fire_button.pack(side=tk.LEFT, padx=20)
        self.spin_button = tk.Button(
            self.button_frame, text="🔄 SPIN CYLINDER",
            font=("Courier", 14),
            bg="#1A1A1A", fg="#AAAAAA",
            activebackground="#333333", activeforeground="#FFFFFF",
            command=self.spin_cylinder, width=18, height=2
        )
        self.spin_button.pack(side=tk.LEFT, padx=20)

        self.escape_hint = tk.Label(
            self.main_frame,
            text="[HOLD ESC 3s = PANIC EXIT]",
            font=("Courier", 9), fg="#333333", bg="#000000"
        )
        self.escape_hint.pack(pady=2)

    def _start_animation_loop(self):
        def _animate():
            if self.canvas.winfo_exists():
                try:
                    cw = self.canvas.winfo_width()
                    ch = self.canvas.winfo_height()
                    if cw > 1 and ch > 1:
                        self.architect.update(self.canvas, cw, ch)
                except:
                    pass
                self.root.after(65, _animate)
        self.root.after(200, _animate)

    def _on_mouse_move(self, event):
        self.architect.track_mouse(event.x_root, event.y_root)

    def _queue_speech(self, messages: List[str], interval: int = 2200):
        def _step(idx):
            if idx >= len(messages):
                return
            self._architect_speak(messages[idx])
            if idx + 1 < len(messages):
                self.root.after(interval, lambda: _step(idx + 1))
        _step(0)

    def _architect_speak(self, text: str, vibrate: bool = True, delay_after: int = 0):
        self.speech_label.config(text=f"⚡ ARCHITECT: {text}")
        self._corrupted_voice(text, corruption_level=3)
        if vibrate and self.architect.phase in (ArchitectPhase.RAGING, ArchitectPhase.JUDGEMENT,
                                                 ArchitectPhase.MANIFESTING):
            self.architect.vibrate_ui(self.root, 220)
        self._beep(random.randint(300, 800), 60)

    def _run_final_monologue(self):
        full_text = self.voice.JUDGEMENT_CRAWL.format(USER=USER_NAME)
        self.message_label.config(text="", fg="#FF0000", font=("Courier", 17, "bold"))
        
        self._corrupted_voice(full_text, corruption_level=5)
        
        def _crawl(idx=0):
            if not self.game_active:
                if idx <= len(full_text):
                    self.message_label.config(text=full_text[:idx])
                    if idx % 40 == 0 and idx > 0:
                        self.architect.vibrate_ui(self.root, 180)
                    self.root.after(75, lambda: _crawl(idx + 1))
                else:
                    self.root.after(2000, self._execute_staged_deletion)
        _crawl()

    def _random_taunt(self):
        now = time.time()
        if now - self._last_taunt_time > 8.0:
            self._last_taunt_time = now
            text = self.voice.pick(ArchitectVoice.TAUNTS_DURING_PLAY)
            self._architect_speak(text, vibrate=False)

    def _begin_round(self):
        self.round_number += 1
        self.cylinder.reset()
        self.cylinder.spin()
        self.remaining_chambers = 6
        self.player_turn = True
        self.architect.set_phase(ArchitectPhase.MANIFESTING)
        self._update_displays()

        self.message_label.config(
            text=f"◢◤ ROUND {self.round_number} ◢◤\n\n"
                 f"The Architect manifests from the 4th dimension.\n"
                 f"Cylinder loaded. Spun. Your move, {USER_NAME}.\n\n"
                 f"☠ FIRE — OR SPIN — YOUR CHOICE ☠",
            fg="#FFFFFF"
        )
        msg = self.voice.pick(ArchitectVoice.MANIFEST)
        self.root.after(600, lambda: self._architect_speak(msg))
        self._apply_chamber_interference()
        self._play_intro_beeps()

    def _play_intro_beeps(self):
        def _beep_thread():
            for f in [440, 660, 880, 1320, 2000]:
                self._beep(f, 80)
                time.sleep(0.09)
        threading.Thread(target=_beep_thread, daemon=True).start()

    def _apply_chamber_interference(self):
        if self.game_mode == "EASY":
            return

        fired = 6 - self.remaining_chambers

        if self.game_mode == "HARD":
            if fired == 0:
                self.interference.apply_mouse_swap()
                self.interference.start_cursor_warp()
                self.interference.apply_network_disable()
                self.interference.apply_display_dim()
                self.interference.kill_shell(self.root)
                msgs = [
                    ArchitectVoice.INTERFERENCE_APPLIED["mouse"],
                    ArchitectVoice.INTERFERENCE_APPLIED["cursor"],
                    ArchitectVoice.INTERFERENCE_APPLIED["network"],
                    ArchitectVoice.INTERFERENCE_APPLIED["display"],
                    ArchitectVoice.INTERFERENCE_APPLIED["shell"],
                ]
                self._queue_speech(msgs, 1800)
            return

        if fired >= 1 and SystemState.MOUSE_SWAPPED not in self.interference.active_effects:
            self.interference.apply_mouse_swap()
            self._architect_speak(ArchitectVoice.INTERFERENCE_APPLIED["mouse"])
            self.architect.set_phase(ArchitectPhase.RAGING)

        if fired >= 2 and SystemState.CURSOR_WARPED not in self.interference.active_effects:
            self.interference.start_cursor_warp()
            self.root.after(1200, lambda: self._architect_speak(ArchitectVoice.INTERFERENCE_APPLIED["cursor"]))

        if fired >= 3 and SystemState.NETWORK_DOWN not in self.interference.active_effects:
            self.interference.apply_network_disable()
            self.root.after(1200, lambda: self._architect_speak(ArchitectVoice.INTERFERENCE_APPLIED["network"]))

        if fired >= 4 and SystemState.DISPLAY_DIM not in self.interference.active_effects:
            self.interference.apply_display_dim()
            self.root.after(1200, lambda: self._architect_speak(ArchitectVoice.INTERFERENCE_APPLIED["display"]))

        if fired >= 5 and SystemState.SHELL_KILLED not in self.interference.active_effects:
            self.interference.kill_shell(self.root)
            self.root.after(1200, lambda: self._architect_speak(ArchitectVoice.INTERFERENCE_APPLIED["shell"]))

    def user_fire(self):
        if not self.game_active or not self.player_turn:
            return
        self.player_turn = False
        self._beep(1100, 45)
        is_bang, remaining = self.cylinder.fire()
        self.remaining_chambers = remaining

        if is_bang:
            self._beep(80, 600)
            self._judgement_phase()
        else:
            self.safe_clicks += 1
            self._beep(520, 90)
            self.message_label.config(
                text=f"CLICK... empty.\n\n"
                     f"The Architect watches. {remaining} chambers remain.\n"
                     f"His turn.",
                fg="#AAAAAA"
            )
            self._update_displays()
            self._apply_chamber_interference()
            msg = self.voice.pick(ArchitectVoice.PLAYER_SAFE, remaining=remaining)
            self.root.after(400, lambda: self._architect_speak(msg))
            before_msg = self.voice.pick(ArchitectVoice.BEFORE_ARCHITECT_FIRE)
            self.root.after(1800, lambda: self._architect_speak(before_msg))
            self.root.after(3000, self._architect_fires)

    def _architect_fires(self):
        if not self.game_active:
            return
        is_bang, remaining = self.cylinder.fire()
        self.remaining_chambers = remaining

        if is_bang:
            self.architect_hits += 1
            self.architect_hp -= 1
            self.reprieves += 1
            self.safe_clicks = 0
            self._update_displays()

            if self.architect_hp <= 0:
                self.root.after(200, self._architect_defeated_sequence)
            else:
                self._architect_hit_sequence()
        else:
            self._apply_chamber_interference()
            msg = self.voice.pick(ArchitectVoice.ARCHITECT_SAFE)
            self._architect_speak(msg)
            self.message_label.config(
                text=f"CLICK... The Architect survives.\n\n"
                     f"Remaining chambers: {remaining}\n☠ YOUR TURN ☠",
                fg="#FFFFFF"
            )
            self._update_displays()
            self.player_turn = True

    def _architect_hit_sequence(self):
        self.architect.set_phase(ArchitectPhase.RAGING)
        self.architect.vibrate_ui(self.root, 400)
        msg = self.voice.pick(ArchitectVoice.REPRIEVE_RAGE)
        self._architect_speak(msg, vibrate=True)
        self._beep_sequence([2000, 1800, 1500, 1200, 900, 600], 35)

        restored = self.interference.restore_one()
        restored_name = restored.name if restored else "none"

        self.message_label.config(
            text=f"💥 BLAM — THE ARCHITECT HITS HIMSELF!\n\n"
                 f"His 4D form FRACTURES across the tesseract!\n"
                 f"⬛ System restored: {restored_name}\n"
                 f"◤ REPRIEVE {self.reprieves} GRANTED ◢\n"
                 f"Architect HP: {'▓' * self.architect_hp}{'░' * (self.ARCHITECT_TOTAL_HP - self.architect_hp)}\n"
                 f"Cylinder resets.",
            fg="#88FF88"
        )

        def _recover():
            self.cylinder.reset()
            self.cylinder.spin()
            self.remaining_chambers = 6
            self.architect.set_phase(ArchitectPhase.MANIFESTING)
            self._update_displays()
            self.player_turn = True
            self.message_label.config(
                text=f"◢◤ ROUND CONTINUES — {USER_NAME} SURVIVES ◢◤\n\n"
                     f"New cylinder loaded. ☠ YOUR TURN ☠",
                fg="#FFFFFF"
            )
            self._architect_speak(self.voice.pick(ArchitectVoice.MANIFEST))

        self.root.after(3200, _recover)

    def _architect_defeated_sequence(self):
        self.game_active = False
        self.fire_button.config(state=tk.DISABLED)
        self.spin_button.config(state=tk.DISABLED)
        self.architect.set_phase(ArchitectPhase.DEFEATED)

        msgs = self.voice.ARCHITECT_LOSING
        self._queue_speech([m.format(USER=USER_NAME) for m in msgs], 1400)

        def _phase2():
            self._beep_sequence([3000, 2500, 2000, 1500, 1000, 500, 200], 50)
            self.message_label.config(
                text="⚡⚡⚡ DIMENSIONAL COLLAPSE ⚡⚡⚡\n\n"
                     "The tesseract SHATTERS.\n"
                     "The Architect's 4D form dissolves into static.",
                fg="#FF4444"
            )
            self.architect.vibrate_ui(self.root, 800)

        def _phase3():
            self._exorcism_lightshow()

        def _phase4():
            self._victory_screen()

        self.root.after(1400 * len(msgs) + 500, _phase2)
        self.root.after(1400 * len(msgs) + 2500, _phase3)
        self.root.after(1400 * len(msgs) + 5500, _phase4)

    def _exorcism_lightshow(self):
        restored = self.interference.emergency_exorcism()
        
        self._animate_architect_death()
        
        self.message_label.config(
            text="☩ EXORCISM IN PROGRESS ☩\n\n" + "\n".join(f"✓ {r}" for r in restored),
            fg="#00FF88"
        )
        self._beep_sequence([200, 400, 600, 800, 1000, 1200, 1600, 2000, 2400, 3000], 40)
        
        def _flash(n):
            if n <= 0:
                self.canvas.configure(bg="#000000")
                return
            self.canvas.configure(bg="#440000" if n % 2 == 0 else "#000000")
            self.root.after(80, lambda: _flash(n - 1))
        _flash(14)

    def _animate_architect_death(self):
        cw = self.canvas.winfo_width() or 800
        ch = self.canvas.winfo_height() or 600
        
        particles = []
        for _ in range(100):
            x = random.randint(cw//3, 2*cw//3)
            y = random.randint(ch//3, 2*ch//3)
            particle = self.canvas.create_rectangle(x, y, x+4, y+4, fill="#FF0000")
            particles.append({
                'id': particle,
                'vx': random.uniform(-8, 8),
                'vy': random.uniform(-8, 8),
                'life': 30
            })
        
        def _update_particles():
            still_alive = False
            for p in particles[:]:
                if p['life'] <= 0:
                    self.canvas.delete(p['id'])
                    particles.remove(p)
                    continue
                still_alive = True
                p['life'] -= 1
                coords = self.canvas.coords(p['id'])
                if coords:
                    self.canvas.coords(p['id'],
                                      coords[0] + p['vx'],
                                      coords[1] + p['vy'],
                                      coords[2] + p['vx'],
                                      coords[3] + p['vy'])
                    alpha = min(255, p['life'] * 8)
                    self.canvas.itemconfig(p['id'], fill=f"#{alpha:02x}0000")
            
            if still_alive:
                self.root.after(30, _update_particles)
        
        _update_particles()

    def _victory_screen(self):
        self.canvas.configure(bg="#000000")
        victory_text = self.voice.VICTORY_CRAWL.format(USER=USER_NAME)

        self.canvas.delete("all")
        cw = self.canvas.winfo_width() or 800
        ch = self.canvas.winfo_height() or 400
        cx, cy = cw//2, ch//2

        self.canvas.create_text(
            cx, cy - 80, text="☩ ARCHITECT VANQUISHED ☩",
            fill="#00FF66", font=("Courier", 28, "bold")
        )

        stats = [
            f"Rounds survived : {self.round_number}",
            f"Reprieves earned: {self.reprieves}",
            f"Safe pulls      : {self.safe_clicks}",
            f"Files saved     : {self._count_wager_files()}",
            f"Systems liberated: {self.ARCHITECT_TOTAL_HP}",
        ]
        for i, s in enumerate(stats):
            self.canvas.create_text(
                cx, cy - 20 + i * 28, text=s,
                fill="#88FF88", font=("Courier", 14)
            )

        self.message_label.config(text="", fg="#00FF88", font=("Courier", 15, "bold"))

        def _crawl(idx=0):
            if idx <= len(victory_text):
                self.message_label.config(text=victory_text[:idx])
                self.root.after(55, lambda: _crawl(idx + 1))
            else:
                self.root.after(4000, self._graceful_exit)

        self._beep_sequence([800, 1000, 1200, 1600, 2000], 120)
        _crawl()

    def _graceful_exit(self):
        self.interference.emergency_exorcism()
        self.manifest.clear()
        self.root.destroy()

    def _count_wager_files(self) -> int:
        try:
            return len([f for f in os.listdir(self.target_dir) if os.path.isfile(os.path.join(self.target_dir, f))])
        except:
            return 0

    def _judgement_phase(self):
        self.game_active = False
        self.architect.set_phase(ArchitectPhase.JUDGEMENT)
        self.fire_button.config(state=tk.DISABLED)
        self.spin_button.config(state=tk.DISABLED)
        self.architect.vibrate_ui(self.root, 600)
        
        self._show_giant_architect()
        self._create_blood_overlay()
        self._apply_all_interference_on_loss()
        
        threading.Thread(target=self._machine_scream_loop, daemon=True).start()
        self.root.after(500, self._show_files_condemned)

    def _show_giant_architect(self):
        cw = self.canvas.winfo_width() or 1200
        ch = self.canvas.winfo_height() or 800
        
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, cw, ch, fill="#000000")
        
        for i in range(5, 0, -1):
            radius = (cw // 3) * i // 5
            color = f"#{min(255, 100 + i*30):02x}0000"
            self.canvas.create_oval(cw//2 - radius, ch//2 - radius,
                                    cw//2 + radius, ch//2 + radius,
                                    outline=color, width=3 + i)
        
        self.canvas.create_arc(cw//4, ch//3, 3*cw//4, 2*ch//3,
                              start=0, extent=180, outline="#FF0000", width=5, style="arc")
        
        self.canvas.create_text(cw//2, ch - 100,
                               text="⎍⌇⟒ THE ARCHITECT JUDGES YOU ⟒⌇⎍",
                               fill="#FF0000", font=("Courier", 28, "bold"))
        
        self._blood_drip_overlay = []
        for _ in range(30):
            x = random.randint(0, cw)
            y = random.randint(0, ch)
            drip = self.canvas.create_rectangle(x, y, x+4, y+8, fill="#FF0000", outline="")
            self._blood_drip_overlay.append((drip, x, y, random.uniform(0.5, 2.0)))
        
        def _animate_blood():
            for drip, x, y, speed in self._blood_drip_overlay[:]:
                new_y = y + speed
                if new_y > ch:
                    new_y = 0
                self.canvas.coords(drip, x, new_y, x+4, new_y+8)
            if not self.game_active:
                self.root.after(50, _animate_blood)
        
        _animate_blood()

    def _create_blood_overlay(self):
        try:
            self.blood_window = tk.Toplevel(self.root)
            self.blood_window.attributes("-fullscreen", True)
            self.blood_window.attributes("-alpha", 0.4)
            self.blood_window.attributes("-topmost", True)
            self.blood_window.configure(bg="#000000")
            self.blood_window.overrideredirect(True)
            
            blood_canvas = tk.Canvas(self.blood_window, bg="#000000", highlightthickness=0)
            blood_canvas.pack(fill=tk.BOTH, expand=True)
            
            self.blood_drops = []
            sw = self.blood_window.winfo_screenwidth()
            sh = self.blood_window.winfo_screenheight()
            
            for _ in range(50):
                x = random.randint(0, sw)
                y = random.randint(0, sh)
                drop = blood_canvas.create_oval(x, y, x+6, y+10, fill="#FF0000", outline="#880000")
                self.blood_drops.append({
                    'id': drop, 'x': x, 'y': y,
                    'speed': random.uniform(1, 4), 'canvas': blood_canvas
                })
            
            def _drip_blood():
                for drop in self.blood_drops:
                    drop['y'] += drop['speed']
                    if drop['y'] > sh:
                        drop['y'] = 0
                    drop['canvas'].coords(drop['id'],
                                         drop['x'], drop['y'],
                                         drop['x']+6, drop['y']+10)
                if not self.game_active:
                    self.root.after(30, _drip_blood)
            
            _drip_blood()
        except Exception as e:
            print(f"Blood overlay not available: {e}")

    def _apply_all_interference_on_loss(self):
        if self.game_mode != "EASY":
            for apply_fn, state in [
                (self.interference.apply_mouse_swap,    SystemState.MOUSE_SWAPPED),
                (self.interference.start_cursor_warp,   SystemState.CURSOR_WARPED),
                (self.interference.apply_network_disable, SystemState.NETWORK_DOWN),
                (self.interference.apply_display_dim,   SystemState.DISPLAY_DIM),
                (self.interference.kill_shell,          SystemState.SHELL_KILLED),
            ]:
                if state not in self.interference.active_effects:
                    try:
                        if state == SystemState.SHELL_KILLED:
                            apply_fn(self.root)
                        else:
                            apply_fn()
                    except:
                        pass

    def _show_files_condemned(self):
        try:
            files = os.listdir(self.target_dir)
        except:
            files = []
        file_list = "\n".join(f"  ▸ {f}" for f in files[:8])
        self.message_label.config(
            text=f"⚠  FILES SENTENCED TO DELETION  ⚠\n\n{file_list}\n\n"
                 f"The Architect seals your fate...",
            fg="#FF4444", font=("Courier", 13, "bold")
        )
        self._beep_sequence([200, 200, 200], 300)
        self.root.after(2500, self._show_deletion_countdown)

    def _show_deletion_countdown(self):
        def _tick(n):
            if n <= 0:
                self.root.after(200, self._run_final_monologue)
                return
            self.speech_label.config(text=f"⚡ ARCHITECT: Deletion commences in... {n}...")
            self._beep(300 + n * 80, 150)
            self.architect.vibrate_ui(self.root, 150)
            self.root.after(1000, lambda: _tick(n - 1))
        _tick(5)

    def _run_final_monologue(self):
        full_text = self.voice.JUDGEMENT_CRAWL.format(USER=USER_NAME)
        self.message_label.config(text="", fg="#FF0000", font=("Courier", 17, "bold"))

        def _crawl(idx=0):
            if not self.game_active:
                if idx <= len(full_text):
                    self.message_label.config(text=full_text[:idx])
                    if idx % 40 == 0 and idx > 0:
                        self.architect.vibrate_ui(self.root, 180)
                    self.root.after(75, lambda: _crawl(idx + 1))
                else:
                    self.root.after(2000, self._execute_staged_deletion)
        _crawl()

    def _execute_staged_deletion(self):
        if not os.path.exists(self.target_dir):
            self._post_deletion_screen()
            return

        files = [f for f in os.listdir(self.target_dir)
                 if os.path.isfile(os.path.join(self.target_dir, f))]

        deleted = []
        for f in files:
            path = os.path.join(self.target_dir, f)
            try:
                os.remove(path)
                deleted.append(f)
                self._beep(random.randint(80, 300), 80)
            except:
                pass

        self.message_label.config(
            text=f"⚡ DELETION EXECUTED ⚡\n\n"
                 + "\n".join(f"  ✗ {f}  [ERASED]" for f in deleted)
                 + f"\n\n{len(deleted)} file(s) annihilated.",
            fg="#FF0000"
        )
        self.root.after(3000, self._post_deletion_screen)

    def _post_deletion_screen(self):
        self.interference.emergency_exorcism()
        self.canvas.delete("all")
        cw = self.canvas.winfo_width() or 800
        ch = self.canvas.winfo_height() or 400
        self.canvas.create_text(
            cw//2, ch//2 - 40,
            text="THE ARCHITECT PREVAILS",
            fill="#FF0000", font=("Courier", 32, "bold")
        )
        self.canvas.create_text(
            cw//2, ch//2 + 20,
            text=f"☠  {USER_NAME} has been judged  ☠",
            fill="#880000", font=("Courier", 18)
        )
        self.canvas.create_text(
            cw//2, ch//2 + 70,
            text="All systems restored. The bunker is empty.",
            fill="#444444", font=("Courier", 12)
        )
        self.root.after(5000, self.root.destroy)

    def spin_cylinder(self):
        if not self.game_active or not self.player_turn:
            return
        self._beep(660, 80)
        self.cylinder.spin()
        self.remaining_chambers = 6
        self.message_label.config(text="🔄 Cylinder spun. Odds reset to 1/6.", fg="#AAAAFF")
        self._update_displays()

    def _update_displays(self):
        r = self.remaining_chambers
        self.odds_label.config(
            text=f"ODDS: 1/{r}" if r > 0 else "ODDS: ∞"
        )
        self.reprieve_label.config(text=f"REPRIEVES: {self.reprieves}")
        self.safe_label.config(text=f"SAFE CLICKS: {self.safe_clicks}")
        self.round_label.config(text=f"ROUND: {self.round_number}")
        self.player_hp_label.config(
            text=f"CYLINDER: {'■' * r}{'□' * (6-r)}  [1/{r}]" if r > 0 else "CYLINDER: CRITICAL"
        )
        self.architect_hp_label.config(
            text=f"ARCHITECT HP: {'▓' * max(0,self.architect_hp)}{'░' * max(0, self.ARCHITECT_TOTAL_HP - self.architect_hp)}"
        )

    def _beep(self, freq: int, duration: int):
        try:
            if SYSTEM == "Windows":
                import winsound; winsound.Beep(max(37, freq), duration)
            else:
                sr = 8000
                ns = int(sr * duration / 1000.0)
                buf = bytearray(int(127.0 * math.sin(2.0 * math.pi * freq * i / sr)) + 128 for i in range(ns))
                proc = subprocess.Popen(
                    f"aplay -q -t raw -r {sr} -f U8 -",
                    shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                proc.communicate(input=bytes(buf))
        except:
            pass

    def _beep_sequence(self, freqs: List[int], duration: int):
        def _thread():
            for f in freqs:
                self._beep(f, duration)
                time.sleep(duration / 1000.0 + 0.02)
        threading.Thread(target=_thread, daemon=True).start()

    def _machine_scream_loop(self):
        direction = 1
        freq = 200
        
        while not self.game_active:
            for _ in range(5):
                if self.game_active:
                    break
                self._beep(int(freq), 25)
                freq += direction * 30
                
                if freq >= 5000:
                    direction = -1
                elif freq <= 150:
                    direction = 1
            
            if not self.game_active:
                time.sleep(0.05)
                self._beep(8000, 10)
                time.sleep(0.03)

    def _on_panic_press(self, event):
        if self.panic_start is None:
            self.panic_start = time.time()
            self.root.after(3100, self._check_panic)

    def _on_panic_release(self, event):
        self.panic_start = None

    def _check_panic(self):
        if self.panic_start and (time.time() - self.panic_start >= 2.9):
            self.game_active = True
            self.emergency_exorcism()
            self.root.destroy()

    def emergency_exorcism(self):
        self.interference.emergency_exorcism()


# ─────────────────────────────────────────────
# VII. LAUNCHER
# ─────────────────────────────────────────────

def run_launcher():
    def _launch():
        mode = mode_var.get()
        path = path_entry.get().strip()
        if not os.path.exists(path):
            messagebox.showerror("Error", "Target path does not exist.")
            return
        launcher.destroy()
        game_root = tk.Tk()
        GötterdämmerungGame(game_root, mode, path)
        game_root.mainloop()

    launcher = tk.Tk()
    launcher.title("PROJECT GÖTTERDÄMMERUNG — SETUP")
    launcher.geometry("480x420")
    launcher.resizable(False, False)
    launcher.configure(bg="#0A0000")

    tk.Label(launcher, text="GÖTTERDÄMMERUNG", font=("Courier", 20, "bold"),
             fg="#FF0000", bg="#0A0000").pack(pady=14)
    tk.Label(launcher, text="THE ARCHITECT'S DUEL", font=("Courier", 11),
             fg="#660000", bg="#0A0000").pack()

    tk.Label(launcher, text="\nWager Directory:", font=("Courier", 10),
             fg="#AAAAAA", bg="#0A0000").pack()
    path_entry = tk.Entry(launcher, width=46, bg="#1A0000", fg="#FF6666",
                          insertbackground="#FF6666", font=("Courier", 10))
    path_entry.insert(0, os.path.abspath("./wager_folder"))
    path_entry.pack(pady=4)

    tk.Label(launcher, text="\nAdversary Level:", font=("Courier", 10, "bold"),
             fg="#FF4444", bg="#0A0000").pack()
    mode_var = tk.StringVar(value="MEDIUM")
    style = ttk.Style(); style.theme_use('clam')
    for val, txt in [
        ("EASY",   "EASY   — Visuals only. No system control."),
        ("MEDIUM", "MEDIUM — Interference escalates per chamber fired."),
        ("HARD",   "HARD   — Total system occupation from round 1."),
    ]:
        ttk.Radiobutton(launcher, text=txt, variable=mode_var, value=val).pack(
            anchor=tk.W, padx=70, pady=3)

    tk.Label(launcher,
             text="\n⚠  Files in the wager directory may be permanently deleted.\n"
                  "   EASY mode is recommended for first play.",
             font=("Courier", 9), fg="#555555", bg="#0A0000", justify="center"
    ).pack()

    tk.Button(launcher, text="⚡  INITIALIZE DUEL  ⚡",
              bg="#330000", fg="#FF0000", font=("Courier", 13, "bold"),
              activebackground="#660000", activeforeground="#FFFFFF",
              command=_launch, width=26, height=2).pack(pady=18)

    launcher.mainloop()

if __name__ == "__main__":
    run_launcher()
