#!/usr/bin/env python3
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
from dataclasses import dataclass
from typing import Dict, List, Tuple
from enum import Enum

SYSTEM = platform.system()
USER_NAME = os.getlogin() if SYSTEM != "Windows" else os.environ.get("USERNAME", "User")

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
            try: os.remove(self.manifest_path)
            except: pass


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
                import ctypes
                ctypes.windll.user32.SwapMouseButton(False)
            elif self.os_type == "Linux":
                subprocess.run("xmodmap -e 'pointer = 1 2 3'", shell=True, capture_output=True)
            return True
        except:
            return False
            
    def apply_network_disable(self) -> bool:
        try:
            if self.os_type == "Windows":
                subprocess.run("netsh interface set interface \"Wi-Fi\" admin=disable", shell=True, capture_output=True)
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
                subprocess.run("netsh interface set interface \"Wi-Fi\" admin=enable", shell=True, capture_output=True)
            elif self.os_type == "Linux":
                subprocess.run("nmcli radio wifi on", shell=True, capture_output=True)
            return True
        except:
            return False
            
    def apply_display_dim(self) -> bool:
        try:
            if self.os_type == "Windows":
                subprocess.run("powershell (Get-CimInstance -Namespace root/WMI -ClassName WmiMonitorBrightnessMethods).WmiSetBrightness(10, 0)", shell=True, capture_output=True)
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
                subprocess.run("powershell (Get-CimInstance -Namespace root/WMI -ClassName WmiMonitorBrightnessMethods).WmiSetBrightness(100, 0)", shell=True, capture_output=True)
            elif self.os_type == "Linux":
                subprocess.run("xrandr --brightness 1.0", shell=True, capture_output=True)
            return True
        except:
            return False
            
    def kill_shell(self, root_window=None) -> bool:
        try:
            if self.os_type == "Windows":
                subprocess.run("taskkill /f /im explorer.exe", shell=True, capture_output=True)
            elif self.os_type == "Linux":
                # Defensively targeting UI shell panels to avoid thread locking the core window display server
                subprocess.run("pkill -STOP gnome-panel || pkill -STOP plasmashell", shell=True, capture_output=True)
            
            # Application isolation protocol fallback across platforms
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
        remaining = 6 - len(self.fired_indices)
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
            
            x2 = x1 * cos_y + z1 * sin_y
            z2 = -x1 * sin_y + z1 * cos_y
            y2 = y1
            
            x3 = x2 * cos_z - y2 * sin_z
            y3 = x2 * sin_z + y2 * cos_z
            
            px, py = project(x3, y3, z2)
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
        cell_w = max(width // 50, 1)
        cell_h = max(height // 50, 1)
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
            glitch_title = "☊ ⍜ ⌰ ⌰ ⏃ ⌿ ⌇ ⟒"
            for i, char in enumerate(glitch_title):
                offset = random.randint(-5, 5)
                canvas.create_text(cx - 100 + i * 25 + offset, cy - base_size - 40, text=char, fill="#FF0000", font=("Courier", 20, "bold"), tags="architect")
            canvas.create_text(cx, cy + base_size + 60, text="THE ARCHITECT", fill="#FF0000", font=("Courier", 36, "bold"), tags="architect")
        elif self.phase == ArchitectPhase.RAGING:
            self._draw_glitch_texture(canvas, width, height, 0.7)
            for _ in range(50):
                x = random.randint(0, width)
                y = random.randint(0, height)
                canvas.create_text(x, y, text=random.choice(["█", "▓", "▒", "░", "⎍", "⌇", "⋏", "⏁", "⟟", "⌇", "⟒", "☊", "⏃", "⌿", "⏁", "⎍", "⍀", "⟒", "⏁⟒⋔"]), fill="#FF0000", font=("Courier", random.randint(12, 36)), tags="architect")
            
        if intensity > 0.5:
            self._draw_scanlines(canvas, width, height, intensity)
            
        canvas.move("architect", -glitch_shift_x, -glitch_shift_y)
        
    def vibrate_ui(self, widget: tk.Widget, duration_ms: int = 200):
        if self.vibration_active:
            return
        self.vibration_active = True
        original_geometry = widget.geometry()
        
        def parse_geometry(geom_str):
            try:
                parts = geom_str.split('+')
                sizes = parts[0].split('x')
                return int(sizes[0]), int(sizes[1]), int(parts[1]), int(parts[2])
            except:
                return 1024, 768, 100, 100

        w, h, original_x, original_y = parse_geometry(original_geometry)

        def vibrate(remaining):
            if remaining <= 0:
                widget.geometry(f"{w}x{h}+{original_x}+{original_y}")
                self.vibration_active = False
                return
            offset_x = random.randint(-10, 10)
            offset_y = random.randint(-7, 7)
            widget.geometry(f"{w}x{h}+{original_x + offset_x}+{original_y + offset_y}")
            widget.after(15, lambda: vibrate(remaining - 15))
        vibrate(duration_ms)


class GötterdämmerungGame:
    def __init__(self, root: tk.Tk, game_mode: str, target_directory: str = "./wager_folder"):
        self.root = root
        self.game_mode = game_mode
        self.target_dir = target_directory
        self.root.title("GÖTTERDÄMMERUNG - THE ARCHITECT'S DUEL")
        self.root.configure(bg="#000000")
        self.root.attributes("-fullscreen", True)
        
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
        
        if not os.path.exists(self.target_dir):
            os.makedirs(self.target_dir)
            with open(os.path.join(self.target_dir, "wager_asset.txt"), "w") as f:
                f.write("System wager dummy core.")

        atexit.register(self.emergency_exorcism)
        self._build_ui()
        self._show_duel_screen()
        self._start_animation_loop()
        
    def _build_ui(self):
        self.main_frame = tk.Frame(self.root, bg="#000000")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.title_label = tk.Label(self.main_frame, text=f"GÖTTERDÄMMERUNG [{self.game_mode} MODE]", font=("Courier", 32, "bold"), fg="#FF0000", bg="#000000")
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
            if self.canvas.winfo_exists():
                self.architect.update_visuals(self.canvas, self.canvas.winfo_width(), self.canvas.winfo_height())
                if not self.game_active:
                    self.architect.vibrate_ui(self.root, 40)
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
        if self.game_mode == "EASY":
            return

        if self.game_mode == "HARD":
            self.interference.apply_mouse_swap()
            self.interference.apply_network_disable()
            self.interference.apply_display_dim()
            if self.round_number >= 2:
                self.interference.kill_shell(self.root)
            self.message_label.config(text=self.message_label.cget("text") + "\n\n[TOTAL SYSTEM OCCUPATION ACTIVE]")
            return

        if self.round_number >= 2 and self.reprieves == 0:
            self.interference.apply_mouse_swap()
            self._beep(800, 200)
            self.message_label.config(text=self.message_label.cget("text") + "\n\n[MOUSE CONTROL COMPROMISED]")
        if self.round_number >= 3:
            self.interference.apply_network_disable()
            self._beep(600, 300)
            self.message_label.config(text=self.message_label.cget("text") + "\n\n[NETWORK OFFLINE]")
        if self.round_number >= 4:
            self.interference.apply_display_dim()
            self._beep(400, 400)
            self.message_label.config(text=self.message_label.cget("text") + "\n\n[DISPLAY COMPROMISED]")
        if self.round_number >= 5 and self.reprieves == 0:
            self.interference.kill_shell(self.root)
            self._beep(300, 500)
            self.message_label.config(text=self.message_label.cget("text") + "\n\n[DESKTOP ENVIRONMENT DESTABILIZED]")
                
    def _update_displays(self):
        odds_text = f"ODDS: 1/{self.remaining_chambers}" if self.remaining_chambers > 0 else "ODDS: CRITICAL"
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
            self.message_label.config(text=f"CLICK... EMPTY.\n\nThe Architect smirks through the tesseract.\n\n☠ YOUR TURN AGAIN ☠")
            self._update_displays()
            
    def _architect_glitch(self):
        self.architect.glitch_intensity = 1.0
        self.architect.rage()
        for _ in range(15):
            self.root.update()
            self._beep(random.randint(400, 2000), 30)
            time.sleep(0.03)
        self.architect.glitch_intensity = 0.3
        self.architect.manifest()
        
    def _apply_reprieve(self):
        if self.interference.active_effects:
            effect = self.interference.active_effects.pop()
            if effect == SystemState.MOUSE_SWAPPED:
                self.interference.restore_mouse_buttons()
            elif effect == SystemState.NETWORK_DOWN:
                self.interference.restore_network()
            elif effect == SystemState.DISPLAY_DIM:
                self.interference.restore_display()
            elif effect == SystemState.SHELL_KILLED:
                self.interference.restore_shell()
                
    def _next_round(self):
        self.round_number += 1
        self.cylinder.spin()
        self.current_odds = 1.0 / 6.0
        self.remaining_chambers = 6
        self.message_label.config(text=f"◢◤ ROUND {self.round_number} ◢◤\n\nThe tesseract rotates...\n\n☠ YOUR TURN ☠")
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

    def _beep(self, freq, duration):
        try:
            if SYSTEM == "Windows":
                import winsound
                winsound.Beep(freq, duration)
            else:
                # Upgraded robust audio pipeline fallback for standard audio devices on Linux environments
                sample_rate = 8000
                num_samples = int(sample_rate * (duration / 1000.0))
                raw_buffer = bytearray()
                for i in range(num_samples):
                    t = float(i) / sample_rate
                    val = int(127.0 * math.sin(2.0 * math.pi * freq * t)) + 128
                    raw_buffer.append(val)
                # Spawns structural sound processing via an optimized PCM stream passing directly to system audio hardware
                cmd = f"aplay -q -t raw -r {sample_rate} -f U8 -"
                proc = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                proc.communicate(input=bytes(raw_buffer))
        except:
            pass

    def _machine_scream_loop(self):
        while not self.game_active:
            for freq in range(100, 5000, 80):
                if self.game_active: break
                self._beep(freq, 20)
            for freq in range(5000, 300, -120):
                if self.game_active: break
                self._beep(freq, 15)

    def _execute_deletion(self):
        if not self.game_active and os.path.exists(self.target_dir):
            for filename in os.listdir(self.target_dir):
                file_path = os.path.join(self.target_dir, filename)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                except:
                    pass
        self.emergency_exorcism()
        self.root.destroy()

    def _judgement_phase(self):
        self.game_active = False
        self.architect.judgement()
        self.fire_button.config(state=tk.DISABLED)
        self.spin_button.config(state=tk.DISABLED)
        
        monologue = f"You've lost... {USER_NAME}. You've tried to stop me. It's too late... your time has come."
        
        def crawl_text(index=0):
            if not self.game_active: 
                if index <= len(monologue):
                    self.message_label.config(text=monologue[:index], fg="#FF0000", font=("Courier", 18, "bold"))
                    self.root.after(80, lambda: crawl_text(index + 1))
                else:
                    self.root.after(3000, self._execute_deletion)

        threading.Thread(target=self._machine_scream_loop, daemon=True).start()
        crawl_text()

    def on_panic_press(self, event):
        if self.panic_press_start is None:
            self.panic_press_start = time.time()
            self.root.after(3000, self._check_panic_hold)
            
    def on_panic_release(self, event):
        self.panic_press_start = None
        
    def _check_panic_hold(self):
        if self.panic_press_start and (time.time() - self.panic_press_start >= 2.9):
            self.game_active = True 
            self.emergency_exorcism()
            self.root.destroy()
            
    def emergency_exorcism(self):
        self.interference.emergency_exorcism()


# --- VI. MODE SELECTOR CONFIGURATION LAUNCHER ---
def run_launcher():
    def confirm_selection():
        mode = mode_var.get()
        path = path_entry.get().strip()
        if not os.path.exists(path):
            messagebox.showerror("Error", "Specified path target does not exist.")
            return
        launcher_root.destroy()
        
        game_root = tk.Tk()
        GötterdämmerungGame(game_root, mode, path)
        game_root.mainloop()

    launcher_root = tk.Tk()
    launcher_root.title("PROJECT GÖTTERDÄMMERUNG SETUP")
    launcher_root.geometry("450x380")
    launcher_root.resizable(False, False)
    
    style = ttk.Style()
    style.theme_use('clam')
    
    lbl_title = tk.Label(launcher_root, text="GÖTTERDÄMMERUNG CORE", font=("Courier", 16, "bold"), fg="red")
    lbl_title.pack(pady=15)
    
    lbl_path = tk.Label(launcher_root, text="Target Directory Path to Wager:")
    lbl_path.pack(pady=2)
    path_entry = tk.Entry(launcher_root, width=45)
    path_entry.insert(0, os.path.abspath("./wager_folder"))
    path_entry.pack(pady=5)
    
    lbl_mode = tk.Label(launcher_root, text="Select Game Adversary Level:", font=("Helvetica", 10, "bold"))
    lbl_mode.pack(pady=10)
    
    mode_var = tk.StringVar(value="MEDIUM")
    
    r1 = ttk.Radiobutton(launcher_root, text="EASY (Visuals only, no active system control)", variable=mode_var, value="EASY")
    r1.pack(anchor=tk.W, padx=60, pady=2)
    r2 = ttk.Radiobutton(launcher_root, text="MEDIUM (System variables occupied incrementally)", variable=mode_var, value="MEDIUM")
    r2.pack(anchor=tk.W, padx=60, pady=2)
    r3 = ttk.Radiobutton(launcher_root, text="HARD (Total instant system occupation)", variable=mode_var, value="HARD")
    r3.pack(anchor=tk.W, padx=60, pady=2)
    
    btn_launch = tk.Button(launcher_root, text="INITIALIZE GAME DUEL", bg="#330000", fg="white", font=("Courier", 11, "bold"), command=confirm_selection, width=25, height=2)
    btn_launch.pack(pady=25)
    
    launcher_root.mainloop()

if __name__ == "__main__":
    run_launcher()
