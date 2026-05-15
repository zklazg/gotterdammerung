#!/usr/bin/env python3
import tkinter as tk
import random
import threading
import time
import os
import sys
import platform
import subprocess
import json
import atexit
import math
from dataclasses import dataclass
from typing import Dict, Any, List, Tuple
from enum import Enum
from datetime import datetime

try:
    import numpy as np
    NP_AVAILABLE = True
except ImportError:
    NP_AVAILABLE = False

try:
    import pygame.mixer as mixer
    from pygame import sndarray
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

SYSTEM = platform.system()

class SystemState(Enum):
    NORMAL = 0
    MOUSE_SWAPPED = 1
    NETWORK_DOWN = 2
    DISPLAY_DIM = 3
    SHELL_KILLED = 4

@dataclass
class RecoveryAction:
    action_id: str
    hostile_action: str
    timestamp: float
    restoration_callback: str
    restored: bool = False

class RecoveryManifest:
    def __init__(self, manifest_path: str = "./götterdämmerung_recovery.json"):
        self.manifest_path = manifest_path
        self.actions: Dict[str, RecoveryAction] = {}
        self._load_or_create()
        
    def _load_or_create(self):
        if os.path.exists(self.manifest_path):
            try:
                with open(self.manifest_path, 'r') as f:
                    data = json.load(f)
                for k, v in data.items():
                    self.actions[k] = RecoveryAction(
                        action_id=v['action_id'],
                        hostile_action=v['hostile_action'],
                        timestamp=v['timestamp'],
                        restoration_callback=v['restoration_callback'],
                        restored=v['restored']
                    )
            except:
                pass
                
    def register(self, action_id: str, hostile_action: str, callback: str) -> None:
        self.actions[action_id] = RecoveryAction(
            action_id=action_id,
            hostile_action=hostile_action,
            timestamp=time.time(),
            restoration_callback=callback,
            restored=False
        )
        self._save()
        
    def restore_all(self) -> List[str]:
        results = []
        for action_id, action in self.actions.items():
            if not action.restored:
                action.restored = True
                results.append(f"Restored: {action.hostile_action}")
        self._save()
        return results
    
    def _save(self):
        serializable = {}
        for k, v in self.actions.items():
            serializable[k] = {
                "action_id": v.action_id,
                "hostile_action": v.hostile_action,
                "timestamp": v.timestamp,
                "restoration_callback": v.restoration_callback,
                "restored": v.restored
            }
        with open(self.manifest_path, 'w') as f:
            json.dump(serializable, f, indent=2)
            
    def clear(self):
        self.actions.clear()
        if os.path.exists(self.manifest_path):
            os.remove(self.manifest_path)


class SystemInterference:
    def __init__(self, manifest: RecoveryManifest):
        self.manifest = manifest
        self.os_type = SYSTEM
        self.active_effects: List[SystemState] = []
        
    def apply_mouse_swap(self) -> bool:
        try:
            if self.os_type == "Windows":
                import ctypes
                ctypes.windll.user32.SwapMouseButton(True)
            elif self.os_type == "Linux":
                subprocess.run(["xmodmap", "-e", "pointer = 3 2 1 4 5 6 7 8 9"], capture_output=True)
            self.manifest.register("mouse_swap", "Mouse Buttons Swapped", "restore_mouse_buttons")
            self.active_effects.append(SystemState.MOUSE_SWAPPED)
            return True
        except:
            return False
            
    def restore_mouse_buttons(self):
        try:
            if self.os_type == "Windows":
                import ctypes
                ctypes.windll.user32.SwapMouseButton(False)
            elif self.os_type == "Linux":
                subprocess.run(["xmodmap", "-e", "pointer = 1 2 3 4 5 6 7 8 9"], capture_output=True)
            return True
        except:
            return False
            
    def apply_network_disable(self) -> bool:
        try:
            if self.os_type == "Windows":
                subprocess.run(["netsh", "interface", "set", "interface", "Wi-Fi", "admin=disable"], capture_output=True)
            elif self.os_type == "Linux":
                subprocess.run(["nmcli", "radio", "wifi", "off"], capture_output=True)
                subprocess.run(["rfkill", "block", "wifi"], capture_output=True)
            self.manifest.register("network_disable", "Network Disabled", "restore_network")
            self.active_effects.append(SystemState.NETWORK_DOWN)
            return True
        except:
            return False
            
    def restore_network(self):
        try:
            if self.os_type == "Windows":
                subprocess.run(["netsh", "interface", "set", "interface", "Wi-Fi", "admin=enable"], capture_output=True)
            elif self.os_type == "Linux":
                subprocess.run(["nmcli", "radio", "wifi", "on"], capture_output=True)
                subprocess.run(["rfkill", "unblock", "wifi"], capture_output=True)
            return True
        except:
            return False
            
    def apply_display_dim(self) -> bool:
        try:
            if self.os_type == "Linux":
                subprocess.run(["xrandr", "--output", "eDP-1", "--brightness", "0.1"], capture_output=True)
            self.manifest.register("display_dim", "Display Dimmed", "restore_display")
            self.active_effects.append(SystemState.DISPLAY_DIM)
            return True
        except:
            return False
            
    def restore_display(self):
        try:
            if self.os_type == "Linux":
                subprocess.run(["xrandr", "--output", "eDP-1", "--brightness", "1.0"], capture_output=True)
            return True
        except:
            return False
            
    def kill_shell(self) -> bool:
        try:
            if self.os_type == "Windows":
                subprocess.run(["taskkill", "/f", "/im", "explorer.exe"], capture_output=True)
            elif self.os_type == "Linux":
                subprocess.run(["pkill", "gnome-shell"], capture_output=True)
            self.manifest.register("shell_kill", "Desktop Shell Killed", "restore_shell")
            self.active_effects.append(SystemState.SHELL_KILLED)
            return True
        except:
            return False
            
    def restore_shell(self):
        try:
            if self.os_type == "Windows":
                subprocess.Popen(["explorer.exe"])
            elif self.os_type == "Linux":
                subprocess.Popen(["gnome-shell", "--replace"])
            return True
        except:
            return False
            
    def emergency_exorcism(self) -> List[str]:
        results = []
        if SystemState.MOUSE_SWAPPED in self.active_effects:
            self.restore_mouse_buttons()
            results.append("Mouse buttons restored")
        if SystemState.NETWORK_DOWN in self.active_effects:
            self.restore_network()
            results.append("Network restored")
        if SystemState.DISPLAY_DIM in self.active_effects:
            self.restore_display()
            results.append("Display restored")
        if SystemState.SHELL_KILLED in self.active_effects:
            self.restore_shell()
            results.append("Shell restored")
        self.active_effects.clear()
        self.manifest.clear()
        return results


class ChamberState(Enum):
    EMPTY = 0
    LIVE = 1

class Cylinder:
    def __init__(self):
        self.reset()
        
    def _load_random_chamber(self):
        position = random.randint(0, 5)
        self.chambers[position] = ChamberState.LIVE
        
    def reset(self):
        self.chambers: List[ChamberState] = [ChamberState.EMPTY] * 6
        self._load_random_chamber()
        self.current_index: int = 0
        self.fired_indices: List[int] = []
        
    def spin(self):
        self.current_index = random.randint(0, 5)
        
    def fire(self) -> Tuple[bool, float, int]:
        is_bang = self.chambers[self.current_index] == ChamberState.LIVE
        self.fired_indices.append(self.current_index)
        self.current_index = (self.current_index + 1) % 6
        remaining = sum(1 for i, c in enumerate(self.chambers) if c == ChamberState.LIVE and i not in self.fired_indices)
        next_odds = 1.0 / remaining if remaining > 0 else 0
        return is_bang, next_odds, remaining


class ArchitectPhase(Enum):
    DORMANT = 0
    MANIFESTING = 1
    RAGING = 2
    JUDGEMENT = 3

class TheArchitect:
    def __init__(self, master_widget=None):
        self.phase = ArchitectPhase.DORMANT
        self.glitch_intensity = 0.0
        self.master_widget = master_widget
        self.vibration_active = False
        self.rotation_angle = 0
        self.pulse_scale = 0
        self.dimension_offset = 0
        self.glitch_frames = []
        self._precompute_glitch_frames()
        
    def _precompute_glitch_frames(self):
        for _ in range(60):
            frame = []
            for __ in range(50):
                frame.append([random.choice(["█", "▓", "▒", "░", "⎍", "⌇", "⋏", "⏁", "⟟", "⌇", "⟒", "⌇", "⊬", "⌇", "⏁", "⟒", "⋔"]) for ___ in range(50)])
            self.glitch_frames.append(frame)
            
    def manifest(self):
        self.phase = ArchitectPhase.MANIFESTING
        self.glitch_intensity = 0.3
        
    def rage(self):
        self.phase = ArchitectPhase.RAGING
        self.glitch_intensity = 0.8
        
    def judgement(self):
        self.phase = ArchitectPhase.JUDGEMENT
        self.glitch_intensity = 1.0
        
    def _draw_tesseract(self, canvas, cx, cy, size, intensity, angle):
        points_3d = [
            (-1, -1, -1), ( 1, -1, -1), ( 1, -1,  1), (-1, -1,  1),
            (-1,  1, -1), ( 1,  1, -1), ( 1,  1,  1), (-1,  1,  1)
        ]
        edges = [
            (0,1), (1,2), (2,3), (3,0),
            (4,5), (5,6), (6,7), (7,4),
            (0,4), (1,5), (2,6), (3,7)
        ]
        outer_edges = [(0,1), (1,2), (2,3), (3,0), (4,5), (5,6), (6,7), (7,4)]
        inner_edges = [(0,4), (1,5), (2,6), (3,7)]
        
        def project(x, y, z):
            factor = 1.0 / (2.0 + z * 0.3)
            x_proj = x * factor * size
            y_proj = y * factor * size
            return cx + x_proj, cy + y_proj
            
        rot_x = math.sin(angle) * intensity * math.pi
        rot_y = math.cos(angle * 0.7) * intensity * math.pi
        rot_z = math.sin(angle * 1.3) * intensity * math.pi
        
        cos_x, sin_x = math.cos(rot_x), math.sin(rot_x)
        cos_y, sin_y = math.cos(rot_y), math.sin(rot_y)
        cos_z, sin_z = math.cos(rot_z), math.sin(rot_z)
        
        projected = []
        for x, y, z in points_3d:
            y1 = y * cos_x - z * sin_x
            z1 = y * sin_x + z * cos_x
            x1 = x
            y1 = y1
            
            x2 = x1 * cos_y + z1 * sin_y
            z2 = -x1 * sin_y + z1 * cos_y
            y2 = y1
            
            x3 = x2 * cos_z - y2 * sin_z
            y3 = x2 * sin_z + y2 * cos_z
            z3 = z2
            
            px, py = project(x3, y3, z3)
            projected.append((px, py))
            
        for edge in edges:
            p1, p2 = projected[edge[0]], projected[edge[1]]
            if edge in outer_edges:
                width = 3
                color = f"#{255 - int(intensity*50):02x}0000"
            elif edge in inner_edges:
                width = 1
                color = "#FF4444"
            else:
                width = 2
                color = "#AA2222"
            if random.random() < intensity * 0.3:
                offset = random.randint(-3, 3)
                p1 = (p1[0] + offset, p1[1] + offset)
                p2 = (p2[0] + offset, p2[1] + offset)
            canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill=color, width=width, tags="architect")
            
    def _draw_hypercube_ring(self, canvas, cx, cy, size, intensity, angle):
        num_cubes = 8
        for i in range(num_cubes):
            cube_angle = angle * 2 + (2 * math.pi * i / num_cubes)
            radius = size * 0.8
            x = cx + radius * math.cos(cube_angle)
            y = cy + radius * math.sin(cube_angle)
            sub_size = size * 0.25 * (0.5 + 0.5 * math.sin(angle * 3 + i))
            self._draw_tesseract(canvas, x, y, sub_size, intensity * 0.6, angle + i)
            
    def _draw_4d_spiral(self, canvas, cx, cy, size, intensity, angle):
        points = []
        for t in range(0, 360, 15):
            rad = math.radians(t + angle * 180 / math.pi)
            r = size * (0.3 + 0.2 * math.sin(rad * 5))
            x = cx + r * math.cos(rad)
            y = cy + r * math.sin(rad)
            z_offset = math.sin(rad * 3) * size * 0.1
            points.append((x + z_offset, y + z_offset))
        for i in range(len(points) - 1):
            if random.random() < intensity * 0.5:
                canvas.create_line(points[i][0], points[i][1], points[i+1][0], points[i+1][1], fill="#FF0000", width=2, tags="architect")
                
    def _draw_dimensional_tear(self, canvas, cx, cy, size, intensity):
        for i in range(int(15 * intensity)):
            start_angle = random.uniform(0, 2 * math.pi)
            end_angle = start_angle + random.uniform(0.1, 0.5)
            rad1 = size * random.uniform(0.3, 1.2)
            rad2 = rad1 * random.uniform(0.8, 1.2)
            x1 = cx + rad1 * math.cos(start_angle)
            y1 = cy + rad1 * math.sin(start_angle)
            x2 = cx + rad2 * math.cos(end_angle)
            y2 = cy + rad2 * math.sin(end_angle)
            canvas.create_line(x1, y1, x2, y2, fill=f"#{random.randint(100,255):02x}0000", width=random.randint(1, 4), tags="architect")
            
    def _draw_digital_blood(self, canvas, width, height, intensity):
        for _ in range(int(120 * intensity)):
            x = random.randint(0, width)
            y = random.randint(0, height)
            for i in range(random.randint(5, 30)):
                canvas.create_rectangle(x + i, y + i//2, x + i + 2, y + i//2 + 4, fill="#FF0000", outline="", tags="blood")
                
    def _draw_scanlines(self, canvas, width, height, intensity):
        for y in range(0, height, 2):
            if random.random() < intensity * 0.7:
                canvas.create_line(0, y, width, y, fill="#FF0000" if random.random() > 0.8 else "#220000", width=1, tags="scanline")
                
    def _draw_glitch_texture(self, canvas, width, height, intensity):
        frame = self.glitch_frames[int(time.time() * 30) % len(self.glitch_frames)]
        cell_w = width // 50
        cell_h = height // 50
        for y in range(min(50, len(frame))):
            for x in range(min(50, len(frame[y]))):
                if random.random() < intensity * 0.3:
                    canvas.create_text(x * cell_w, y * cell_h, text=frame[y][x], fill="#FF0000", font=("Courier", cell_w), tags="glitch_texture")
                    
    def _draw_4d_eye(self, canvas, cx, cy, size, intensity, angle):
        for layer in range(3):
            layer_size = size * (0.3 + layer * 0.2)
            for i in range(12):
                sub_angle = angle * 4 + (2 * math.pi * i / 12)
                x = cx + layer_size * math.cos(sub_angle) * (1 + intensity * math.sin(angle * 5))
                y = cy + layer_size * math.sin(sub_angle) * (1 + intensity * math.cos(angle * 3))
                canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="#FF0000", outline="#FFFFFF", width=1, tags="architect")
                
    def update_visuals(self, canvas: tk.Canvas, width: int, height: int):
        canvas.delete("architect")
        canvas.delete("blood")
        canvas.delete("scanline")
        canvas.delete("glitch_texture")
        
        if self.phase == ArchitectPhase.DORMANT:
            return
            
        intensity = self.glitch_intensity
        self.rotation_angle += 0.02 * (1 + intensity * 2)
        self.pulse_scale = 0.5 + 0.5 * math.sin(time.time() * 10)
        self.dimension_offset += 0.01 * intensity
        
        cx = width // 2
        cy = height // 2
        
        if self.phase == ArchitectPhase.JUDGEMENT:
            base_size = min(width, height) // 2
            for i in range(3):
                pulse = int(20 * math.sin(time.time() * 15) * intensity)
                canvas.create_oval(cx - base_size - pulse - i*10, cy - base_size - pulse - i*10, cx + base_size + pulse + i*10, cy + base_size + pulse + i*10, outline=f"#{255 - i*50:02x}0000", width=2 + i, tags="architect")
                
        glitch_shift_x = random.randint(-int(15 * intensity), int(15 * intensity))
        glitch_shift_y = random.randint(-int(10 * intensity), int(10 * intensity))
        canvas.move("architect", glitch_shift_x, glitch_shift_y)
        
        base_size = 180 + int(70 * intensity)
        
        if self.phase == ArchitectPhase.JUDGEMENT:
            for i in range(5):
                size = base_size + i * 20
                self._draw_tesseract(canvas, cx, cy, size, intensity, self.rotation_angle + i)
        else:
            self._draw_tesseract(canvas, cx, cy, base_size, intensity, self.rotation_angle)
            
        if intensity > 0.4:
            self._draw_hypercube_ring(canvas, cx, cy, base_size, intensity, self.rotation_angle)
            
        if intensity > 0.6:
            self._draw_4d_spiral(canvas, cx, cy, base_size, intensity, self.rotation_angle)
            
        self._draw_dimensional_tear(canvas, cx, cy, base_size, intensity)
        self._draw_4d_eye(canvas, cx, cy, base_size, intensity, self.rotation_angle)
        
        if self.phase == ArchitectPhase.JUDGEMENT:
            self._draw_digital_blood(canvas, width, height, 1.0)
            self._draw_glitch_texture(canvas, width, height, 1.0)
            for y in range(0, height, 3):
                r = random.randint(150, 255)
                canvas.create_line(0, y + random.randint(-1, 1), width, y + random.randint(-1, 1), fill=f"#{r:02x}0000", width=random.randint(1, 3), tags="architect")
            glitch_title = "⌇ ⊬ ⌇ ⏁ ⟒ ⋔   ☊ ⍜ ⌰ ⌰ ⏃ ⌿ ⌇ ⟒"
            for i, char in enumerate(glitch_title):
                offset = random.randint(-5, 5)
                canvas.create_text(cx - 200 + i * 25 + offset, cy - base_size - 40, text=char, fill="#FF0000", font=("Courier", 20, "bold"), tags="architect")
            canvas.create_text(cx, cy + base_size + 60, text="THE ARCHITECT", fill="#FF0000", font=("Courier", 36, "bold"), tags="architect")
            canvas.create_text(cx, cy + base_size + 110, text="⊬⍜⎍⍀   ⌿⍀⟒⌇⟒⋏☊⟒   ⟟⌇   ⍀⟒⍊⍜☊⏃⏁⟒⎅", fill="#FF0000", font=("Courier", 18), tags="architect")
        elif self.phase == ArchitectPhase.RAGING:
            self._draw_glitch_texture(canvas, width, height, 0.7)
            for _ in range(50):
                x = random.randint(0, width)
                y = random.randint(0, height)
                canvas.create_text(x, y, text=random.choice(["█", "▓", "▒", "░", "⎍", "⌇", "⋏", "⏁", "⟟", "⌇", "⟒", "☊", "⏃", "⌿", "⏁", "⎍", "⍀", "⟒", "⌇", "⊬", "⌇", "⏁", "⟒", "⋔"]), fill="#FF0000", font=("Courier", random.randint(12, 36)), tags="architect")
            canvas.create_text(cx, cy + base_size + 40, text="⌇⊬⌇⏁⟒⋔   ⌿⟒⋏⟒⏁⍀⏃⏁⟟⍜⋏   ⌿⊑⏃⌇⟒   ⎅⟒⏁⟒☊⏁⟒⎅", fill="#FF0000", font=("Courier", 14, "bold"), tags="architect")
            
        if self.phase == ArchitectPhase.JUDGEMENT:
            for _ in range(200):
                x = random.randint(0, width)
                y = random.randint(0, height)
                canvas.create_text(x, y, text=random.choice(["0", "1", "⌇", "⋏", "⏁", "⟟", "⌰", "⟒", "⏁", "⊑", "⏃", "⌰"]), fill="#FF0000" if random.random() > 0.5 else "#330000", font=("Courier", random.randint(8, 18)), tags="architect")
                
        if intensity > 0.5:
            self._draw_scanlines(canvas, width, height, intensity)
            
        canvas.move("architect", -glitch_shift_x, -glitch_shift_y)
        
    def vibrate_ui(self, widget: tk.Widget, duration_ms: int = 200):
        if self.vibration_active:
            return
        self.vibration_active = True
        original_x = widget.winfo_x()
        original_y = widget.winfo_y()
        def vibrate(remaining):
            if remaining <= 0:
                widget.geometry(f"+{original_x}+{original_y}")
                self.vibration_active = False
                return
            offset_x = random.randint(-10, 10)
            offset_y = random.randint(-7, 7)
            widget.geometry(f"+{original_x + offset_x}+{original_y + offset_y}")
            widget.after(15, lambda: vibrate(remaining - 15))
        vibrate(duration_ms)


class GötterdämmerungGame:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("GÖTTERDÄMMERUNG - THE ARCHITECT'S DUEL")
        self.root.configure(bg="#000000")
        self.root.geometry("1024x768")
        self.root.bind("<Escape>", self.panic_exit)
        self.panic_press_start = None
        self.root.bind("<KeyPress-Escape>", self.on_panic_press)
        self.root.bind("<KeyRelease-Escape>", self.on_panic_release)
        self.manifest = RecoveryManifest()
        self.interference = SystemInterference(self.manifest)
        self.cylinder = Cylinder()
        self.architect = TheArchitect()
        self.game_active = True
        self.current_odds = 1.0 / 6.0
        self.remaining_chambers = 6
        self.round_number = 0
        self.reprieves = 0
        self.safe_clicks = 0
        self.tts_engine = None
        if TTS_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', 100)
                self.tts_engine.setProperty('volume', 0.9)
            except:
                self.tts_engine = None
        atexit.register(self.emergency_exorcism)
        self._build_ui()
        self._show_duel_screen()
        self._start_animation_loop()
        
    def _build_ui(self):
        self.main_frame = tk.Frame(self.root, bg="#000000")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.title_label = tk.Label(self.main_frame, text="GÖTTERDÄMMERUNG", font=("Courier", 32, "bold"), fg="#FF0000", bg="#000000")
        self.title_label.pack(pady=10)
        self.canvas = tk.Canvas(self.main_frame, bg="#000000", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.info_frame = tk.Frame(self.main_frame, bg="#000000")
        self.info_frame.pack(fill=tk.X, padx=20, pady=10)
        self.odds_label = tk.Label(self.info_frame, text="ODDS: 1/6", font=("Courier", 16), fg="#FF8888", bg="#000000")
        self.odds_label.pack(side=tk.LEFT, padx=30)
        self.reprieve_label = tk.Label(self.info_frame, text="REPRIEVES: 0", font=("Courier", 16), fg="#88FF88", bg="#000000")
        self.reprieve_label.pack(side=tk.LEFT, padx=30)
        self.safe_label = tk.Label(self.info_frame, text="SAFE CLICKS: 0", font=("Courier", 16), fg="#FFFF88", bg="#000000")
        self.safe_label.pack(side=tk.LEFT, padx=30)
        self.message_label = tk.Label(self.main_frame, text="", font=("Courier", 14), fg="#FFFFFF", bg="#000000", wraplength=900, justify="center")
        self.message_label.pack(pady=10)
        self.button_frame = tk.Frame(self.main_frame, bg="#000000")
        self.button_frame.pack(pady=20)
        self.fire_button = tk.Button(self.button_frame, text="⚡ FIRE ⚡", font=("Courier", 20, "bold"), bg="#330000", fg="#FF0000", activebackground="#660000", activeforeground="#FFFFFF", command=self.user_fire, width=14, height=2)
        self.fire_button.pack(side=tk.LEFT, padx=20)
        self.spin_button = tk.Button(self.button_frame, text="🔄 SPIN CYLINDER 🔄", font=("Courier", 14), bg="#222222", fg="#CCCCCC", activebackground="#444444", activeforeground="#FFFFFF", command=self.spin_cylinder, width=18, height=2)
        self.spin_button.pack(side=tk.LEFT, padx=20)
        
    def _start_animation_loop(self):
        def animate():
            if self.game_active:
                self.architect.update_visuals(self.canvas, self.canvas.winfo_width(), self.canvas.winfo_height())
            self.root.after(50, animate)
        self.root.after(50, animate)
        
    def _show_duel_screen(self):
        self.architect.manifest()
        self.cylinder.spin()
        self.current_odds = 1.0 / 6.0
        self.remaining_chambers = 6
        self.round_number += 1
        self.message_label.config(text=f"◢◤ ROUND {self.round_number} ◢◤\n\nThe Architect manifests from the 4th dimension.\nA tesseract of crimson and void.\nThe cylinder spins with deadly purpose.\n\n☠ YOUR TURN TO FIRE ☠")
        self._update_displays()
        self._apply_round_interference()
        self._play_dramatic_beep()
        
    def _play_dramatic_beep(self):
        def beep_thread():
            for freq in [440, 880, 1760, 3520]:
                self._beep(freq, 100)
                time.sleep(0.1)
            self._beep(2000, 300)
        threading.Thread(target=beep_thread, daemon=True).start()
        
    def _apply_round_interference(self):
        if self.round_number >= 2 and self.reprieves == 0:
            if random.random() < 0.2 + (self.round_number * 0.05):
                self.interference.apply_mouse_swap()
                self._beep(800, 200)
                self.message_label.config(text=self.message_label.cget("text") + "\n\n⌇⊬⌇⏁⟒⋔ ⍜☊☊⎍⌿⏃⏁⟟⍜⋏⌇\n[MOUSE CONTROL COMPROMISED]")
        if self.round_number >= 3:
            if random.random() < 0.15:
                self.interference.apply_network_disable()
                self._beep(600, 300)
                self.message_label.config(text=self.message_label.cget("text") + "\n\n⌇⟒☊⎍⍀⟟⏁⊬ ⎐⟟⍜⌰⏃⏁⟟⍜⋏\n[NETWORK OFFLINE]")
        if self.round_number >= 4:
            if random.random() < 0.1:
                self.interference.apply_display_dim()
                self._beep(400, 400)
                self.message_label.config(text=self.message_label.cget("text") + "\n\n⏚⎍⋏☠⟒⍀ ⌿⊑⏃⌇⟒\n[DISPLAY COMPROMISED]")
        if self.round_number >= 5 and self.reprieves == 0:
            if random.random() < 0.08:
                self.interference.kill_shell()
                self._beep(300, 500)
                self.message_label.config(text=self.message_label.cget("text") + "\n\n⎅⟒⌇☠⏁⍜⌿ ⌇⊑⟒⌰⌰ ☊⍜⌰⌰⏃⌿⌇⟒\n[DESKTOP ENVIRONMENT DESTABILIZED]")
                
    def _update_displays(self):
        odds_text = f"ODDS: 1/{int(1/self.current_odds)}" if self.current_odds > 0 else "ODDS: 0"
        self.odds_label.config(text=odds_text)
        self.reprieve_label.config(text=f"REPRIEVES: {self.reprieves}")
        self.safe_label.config(text=f"SAFE CLICKS: {self.safe_clicks}")
        
    def user_fire(self):
        if not self.game_active:
            return
        self._beep(1000, 50)
        is_bang, next_odds, remaining = self.cylinder.fire()
        if is_bang:
            self._beep(100, 500)
            self._judgement_phase()
        else:
            self._beep(500, 100)
            self.safe_clicks += 1
            self.current_odds = next_odds
            self.remaining_chambers = remaining
            self.message_label.config(text=f"CLICK... EMPTY.\n\nThe Architect watches from beyond.\nHis turn to fire.")
            self._update_displays()
            self.root.update()
            self.root.after(1500, self.architect_fire)
            
    def architect_fire(self):
        if not self.game_active:
            return
        is_bang, next_odds, remaining = self.cylinder.fire()
        if is_bang:
            self.reprieves += 1
            self.safe_clicks = 0
            self.cylinder.reset()
            self.cylinder.spin()
            self.current_odds = 1.0 / 6.0
            self.remaining_chambers = 6
            self._architect_glitch()
            self._beep(2000, 200)
            self.message_label.config(text=f"💥 BLAM! 💥\n\nThe Architect hits himself!\nHis 4D form glitches across reality!\n\n◤ REPRIEVE GRANTED ◢\nSystem corruption partially reversed.\nThe cylinder resets.")
            self._update_displays()
            self._apply_reprieve()
            self.root.after(2500, self._next_round)
        else:
            self.current_odds = next_odds
            self.remaining_chambers = remaining
            self._beep(400, 80)
            self.message_label.config(text=f"CLICK... EMPTY.\n\nThe Architect smirks through the tesseract.\n\n☠ YOUR TURN AGAIN ☠\nOdds: 1/{int(1/self.current_odds)}")
            self._update_displays()
            
    def _architect_glitch(self):
        self.architect.glitch_intensity = 1.0
        self.architect.rage()
        for _ in range(15):
            self.architect.update_visuals(self.canvas, self.canvas.winfo_width(), self.canvas.winfo_height())
            self.root.update()
            self._beep(random.randint(400, 2000), 30)
            time.sleep(0.03)
            self.canvas.delete("all")
            self.root.update()
            self._beep(random.randint(200, 1000), 30)
            time.sleep(0.03)
        self.architect.glitch_intensity = 0.3
        self.architect.manifest()
        
    def _apply_reprieve(self):
        if self.interference.active_effects:
            effect = self.interference.active_effects.pop()
            if effect == SystemState.MOUSE_SWAPPED:
                self.interference.restore_mouse_buttons()
                self.message_label.config(text=self.message_label.cget("text") + "\n\n[EXORCISM: Mouse control restored]")
            elif effect == SystemState.NETWORK_DOWN:
                self.interference.restore_network()
                self.message_label.config(text=self.message_label.cget("text") + "\n\n[EXORCISM: Network restored]")
            elif effect == SystemState.DISPLAY_DIM:
                self.interference.restore_display()
                self.message_label.config(text=self.message_label.cget("text") + "\n\n[EXORCISM: Display restored]")
            elif effect == SystemState.SHELL_KILLED:
                self.interference.restore_shell()
                self.message_label.config(text=self.message_label.cget("text") + "\n\n[EXORCISM: Desktop restored]")
                
    def _next_round(self):
        self.round_number += 1
        self.cylinder.spin()
        self.current_odds = 1.0 / 6.0
        self.remaining_chambers = 6
        self.message_label.config(text=f"◢◤ ROUND {self.round_number} ◢◤\n\nThe tesseract rotates...\nBlood drips from higher dimensions...\n\n☠ YOUR TURN ☠")
        self._update_displays()
        self._apply_round_interference()
        
    def spin_cylinder(self):
        if not self.game_active:
            return
        self._beep(600, 100)
        self.cylinder.spin()
        self.current_odds = 1.0 / 6.0
        self.remaining_chambers = 6
        self.message_label.config(text="🔄 You spin the cylinder...\nOdds reset to 1/6 🔄")
        self._update_displays()
        
    def _judgement_phase(self):
        self.game_active = False
        self.architect.judgement()
        self.fire_button.config(state=tk.DISABLED)
        self.spin_button.config(state=tk.DISABLED)
        self.message_label.config(text="⌇⊬⌇⏁⟒⋔ ⌰⍜☊☍⎅⍜⬍⋏\n[INPUT LOCKDOWN ACTIVE]\n\nThe Architect fills your dimension.\nHold ESC for 3 seconds to escape judgement.")
        self.canvas.delete("all")
        self.root.update()
        for intensity in range(0, 100, 3):
            self.architect.glitch_intensity = intensity / 100
            self.architect.update_visuals(self.canvas, self.canvas.winfo_width(), self.canvas.winfo_height())
            self._beep(200 + intensity * 20, 15)
            self.root.update()
            time.sleep(0.015)
        for _ in range(300):
            x = random.randint(0, self.canvas.winfo_width())
            y = random.randint(0, self.canvas.winfo_height())
            self.canvas.create_rectangle(x, y, x + random.randint(2, 10), y + random.randint(4, 15), fill="#FF0000", outline="", tags="blood")
            self.root.update()
            time.sleep(0.008)
        user = os.getenv("USER", os.getenv("USERNAME", "CHALLENGER"))
        monologue = f"You've lost... {user}. You've tried to stop me. It's too late... your time has come."
        self.monologue_text = ""
        self._type_monologue(monologue)
        self._machine_scream()
        self.root.after(10000, self._execution)
        
    def _type_monologue(self, text: str, index: int = 0):
        if index < len(text):
            self.architect.vibrate_ui(self.root, 30)
            self.monologue_text += text[index]
            self.message_label.config(text=self.monologue_text)
            if self.tts_engine and index % 2 == 0 and text[index] != ' ':
                def speak():
                    try:
                        self.tts_engine.say(text[index])
                        self.tts_engine.runAndWait()
                    except:
                        pass
                threading.Thread(target=speak, daemon=True).start()
            self._beep(random.randint(300, 600), 25)
            self.root.after(60, lambda: self._type_monologue(text, index + 1))
            
    def _machine_scream(self):
        def beep_sequence():
            for freq in range(200, 3000, 25):
                self._beep(freq, 12)
                time.sleep(0.006)
            for freq in range(3000, 200, -25):
                self._beep(freq, 12)
                time.sleep(0.006)
            for _ in range(15):
                self._beep(random.randint(100, 3500), 40)
                time.sleep(0.04)
        threading.Thread(target=beep_sequence, daemon=True).start()
        if NP_AVAILABLE and PYGAME_AVAILABLE:
            self._generate_synth_scream()
            
    def _generate_synth_scream(self):
        try:
            if mixer.get_init() is None:
                mixer.init(frequency=44100, size=-16, channels=2)
            duration = 3.0
            sample_rate = 44100
            t = np.linspace(0, duration, int(sample_rate * duration))
            frequencies = [220, 440, 880, 1760, 3520, 1760, 880, 440, 220]
            audio_data = np.zeros(len(t))
            for i, freq in enumerate(frequencies):
                envelope = np.exp(-t * 10) if i < len(frequencies)//2 else 1 - np.exp(-t * 10)
                audio_data += np.sin(2 * np.pi * freq * t) * envelope * (0.25 / len(frequencies))
            noise = np.random.normal(0, 0.2, len(t))
            audio_data = audio_data + noise
            audio_data = audio_data / np.max(np.abs(audio_data))
            audio_int16 = (audio_data * 32767).astype(np.int16)
            stereo = np.array([audio_int16, audio_int16]).T
            sound = sndarray.make_sound(stereo)
            sound.play()
            time.sleep(duration)
            mixer.stop()
        except:
            pass
            
    def _beep(self, frequency: int, duration_ms: int):
        try:
            if SYSTEM == "Windows":
                import winsound
                winsound.Beep(frequency, duration_ms)
            else:
                subprocess.Popen(["beep", "-f", str(frequency), "-l", str(duration_ms)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass
            
    def _execution(self):
        quarantine_dir = "./quarantine"
        os.makedirs(quarantine_dir, exist_ok=True)
        judgement_file = os.path.join(quarantine_dir, f"JUDGEMENT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(judgement_file, 'w') as f:
            f.write("═══════════════════════════════════════════════════════════\n")
            f.write("                    JUDGEMENT EXECUTED\n")
            f.write("═══════════════════════════════════════════════════════════\n\n")
            f.write(f"Target: {os.getenv('USER', os.getenv('USERNAME', 'UNKNOWN'))}\n")
            f.write(f"Rounds Survived: {self.round_number}\n")
            f.write(f"Reprieves Earned: {self.reprieves}\n")
            f.write(f"Safe Clicks: {self.safe_clicks}\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("THE ARCHITECT HAS CLAIMED ANOTHER SOUL.\n")
            f.write("YOUR FILES HAVE BEEN CLAIMED.\n")
            f.write("THE TESSERACT CLOSES.\n")
            f.write("═══════════════════════════════════════════════════════════\n")
        self._beep(100, 1000)
        self._beep(50, 800)
        self.message_label.config(text=self.message_label.cget("text") + "\n\n\n⌇⟒⋏⏁⟒⋏☊⟒ ⌿⟒⍀⎎⍜⍀⋔⟒⎅\n[JUDGEMENT EXECUTED]\n\nThe Architect claims another dimension.\n\nGAME OVER")
        self.root.after(4000, self.game_over)
        
    def game_over(self):
        self.emergency_exorcism()
        self.message_label.config(text="⌇⊬⌇⏁⟒⋔ ⍀⟒⌇⏁⍜⍀⟒⎅\n[SYSTEM RESTORED]\n\nThe Architect retreats... for now.\n\nClose window to exit.")
        
    def emergency_exorcism(self):
        results = self.interference.emergency_exorcism()
        for result in results:
            print(f"[EXORCISM] {result}")
            
    def on_panic_press(self, event):
        self.panic_press_start = time.time()
        self._beep(800, 50)
        
    def on_panic_release(self, event):
        if self.panic_press_start and (time.time() - self.panic_press_start) >= 3:
            self._beep(2000, 300)
            self.panic_exit(event)
        self.panic_press_start = None
        
    def panic_exit(self, event=None):
        self.emergency_exorcism()
        self.game_active = False
        self.message_label.config(text="⌿⏃⋏⟟☊ ⟒⌖⟟⏁\n[PANIC EXIT]\n\nSystem restored.\nYou escaped the Architect's judgement.\nThe tesseract collapses.\n\nClosing...")
        self.root.after(2000, self.root.destroy)
        
    def on_closing(self):
        self.emergency_exorcism()
        self.root.destroy()


def main():
    root = tk.Tk()
    game = GötterdämmerungGame(root)
    root.protocol("WM_DELETE_WINDOW", game.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()