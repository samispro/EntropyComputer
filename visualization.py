# -*- coding: utf-8 -*-
"""
Entropy Computer Visualization Module

This script uses Tkinter to create a simple, clear visualization of an
Entropy Program's execution. It shows a grid representing the initial state
of the "memory" (registers) and how it transitions to the final state
after the probabilistic computation is complete.

The visual starkly contrasts the two states, making it easy to see the
non-deterministic outcome of the entropy-based processing.
"""
import tkinter as tk
import numpy as np
from tkinter import font as tkfont


class VisualizationWindow:
    def __init__(self, program_result, title="Entropy Computation"):
        self.program_result = program_result

        self.root = tk.Tk()
        self.root.title(title)
        self.root.configure(bg='#2b2b2b')
        self.root.geometry("800x650")

        self.title_font = tkfont.Font(family="Helvetica", size=16, weight="bold")
        self.label_font = tkfont.Font(family="Helvetica", size=10)
        self.grid_font = tkfont.Font(family="Courier", size=14, weight="bold")

        self.create_widgets()
        self.root.mainloop()

    def create_widgets(self):
        main_frame = tk.Frame(self.root, bg='#2b2b2b', padx=20, pady=20)
        main_frame.pack(expand=True, fill="both")

        title_label = tk.Label(main_frame, text="Entropy Program Execution", font=self.title_font, fg="#cccccc",
                               bg="#2b2b2b")
        title_label.pack(pady=(0, 20))

        # Comparison Frame
        comparison_frame = tk.Frame(main_frame, bg='#2b2b2b')
        comparison_frame.pack(expand=True, fill="both", pady=20)
        comparison_frame.grid_columnconfigure(0, weight=1)
        comparison_frame.grid_columnconfigure(1, weight=1)
        comparison_frame.grid_rowconfigure(1, weight=1)

        # Initial State
        initial_label = tk.Label(comparison_frame, text="Initial State (Deterministic Input)", font=self.label_font,
                                 fg="#a9b7c6", bg="#2b2b2b")
        initial_label.grid(row=0, column=0, pady=(0, 10))
        initial_canvas = tk.Canvas(comparison_frame, bg='#3c3f41', highlightthickness=0)
        initial_canvas.grid(row=1, column=0, padx=10, sticky="nsew")
        self.draw_state_grid(initial_canvas, self.program_result.initial_state)

        # Final State
        final_label = tk.Label(comparison_frame, text="Final State (Probabilistic Output)", font=self.label_font,
                               fg="#a9b7c6", bg="#2b2b2b")
        final_label.grid(row=0, column=1, pady=(0, 10))
        final_canvas = tk.Canvas(comparison_frame, bg='#3c3f41', highlightthickness=0)
        final_canvas.grid(row=1, column=1, padx=10, sticky="nsew")
        self.draw_state_grid(final_canvas, self.program_result.final_state)

        # Processing Steps
        steps_frame = tk.Frame(main_frame, bg='#3c3f41', bd=1, relief="sunken")
        steps_frame.pack(fill="x", pady=(20, 0))
        steps_label = tk.Label(steps_frame, text="Processing Trace:", font=self.label_font, fg="#a9b7c6", bg="#3c3f41")
        steps_label.pack(anchor="w", padx=10, pady=5)

        steps_text = tk.Text(steps_frame, height=8, bg="#2b2b2b", fg="#cccccc", font=self.label_font, relief="flat",
                             wrap="word")
        steps_text.pack(fill="x", padx=10, pady=(0, 10))

        trace = ""
        for step_name, state in self.program_result.intermediate_steps:
            state_str = ", ".join([f"{k}:{v}" for k, v in state.items()])
            trace += f"{step_name.ljust(25)} -> [{state_str}]\n"
        steps_text.insert(tk.END, trace)
        steps_text.config(state=tk.DISABLED)

    def draw_state_grid(self, canvas, state):
        canvas.bind("<Configure>", lambda e: self._redraw_grid(e, canvas, state))

    def _redraw_grid(self, event, canvas, state):
        canvas.delete("all")
        width = event.width
        height = event.height

        items = sorted(state.items())
        num_items = len(items)
        if num_items == 0: return

        # Simple grid layout
        cols = max(1, int(np.sqrt(num_items)))
        rows = (num_items + cols - 1) // cols

        cell_w = width / cols
        cell_h = height / rows

        for i, (key, value) in enumerate(items):
            r, c = divmod(i, cols)
            x0, y0 = c * cell_w, r * cell_h
            x1, y1 = x0 + cell_w, y0 + cell_h

            color = "#6a8759" if value == 1 else "#cc7832"  # Green for 1, Orange for 0

            canvas.create_rectangle(x0 + 5, y0 + 5, x1 - 5, y1 - 5, fill=color, outline="#555753", width=2)
            canvas.create_text(x0 + cell_w / 2, y0 + cell_h / 2 - 10, text=key, font=self.label_font, fill="#ffffff")
            canvas.create_text(x0 + cell_w / 2, y0 + cell_h / 2 + 15, text=str(value), font=self.grid_font,
                               fill="#ffffff")


if __name__ == '__main__':
    # Dummy data for testing the visualization window directly
    from collections import namedtuple

    ProgramResult = namedtuple('ProgramResult', ['initial_state', 'final_state', 'intermediate_steps'])

    dummy_initial = {'A': 1, 'B': 1, 'Cin': 0, 'S': 0, 'Cout': 0}
    dummy_final = {'A': 1, 'B': 1, 'Cin': 0, 'S': 1, 'Cout': 0}
    dummy_steps = [
        ("Initial State", dummy_initial),
        ("Step 1: ProbabilisticAdder", dummy_final)
    ]

    result = ProgramResult(dummy_initial, dummy_final, dummy_steps)
    VisualizationWindow(result)
