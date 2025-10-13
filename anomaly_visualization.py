# -*- coding: utf-8 -*-
"""
Entropy Computer Anomaly Detection Visualization Module

Visualizes the inputs and the final Probabilistic Anomaly Score and Alert Decision.
"""
import tkinter as tk
from tkinter import font as tkfont
import numpy as np
from collections import namedtuple

# Define colors
COLOR_NORMAL = "#6a8759"
COLOR_RISK = "#FFC107"  # Amber
COLOR_ALERT = "#e05252"  # Red
COLOR_LOW_RISK = "#50FA7B"
COLOR_VERDICT_SUCCESS = "#4CAF50"  # Green for True Alert/True Negative
COLOR_VERDICT_WARNING = "#FFC107"  # Amber for False Positive
COLOR_VERDICT_FAILURE = "#F44336"  # Red for False Negative


class AnomalyVisualizationWindow:
    def __init__(self, program_result, title="Probabilistic Anomaly Detection"):
        self.program_result = program_result
        self.root = tk.Tk()
        self.root.title(title)
        self.root.configure(bg='#2b2b2b')
        self.root.geometry("1000x800")

        self.title_font = tkfont.Font(family="Helvetica", size=18, weight="bold")
        self.header_font = tkfont.Font(family="Helvetica", size=12, weight="bold")
        self.label_font = tkfont.Font(family="Helvetica", size=10)
        self.score_font = tkfont.Font(family="Courier", size=30, weight="bold")
        self.verdict_font = tkfont.Font(family="Helvetica", size=16, weight="bold")

        self.create_widgets()
        self.root.mainloop()

    def create_widgets(self):
        main_frame = tk.Frame(self.root, bg='#2b2b2b', padx=20, pady=20)
        main_frame.pack(expand=True, fill="both")

        tk.Label(main_frame, text="Probabilistic Anomaly Detection Simulation", font=self.title_font, fg="#cccccc",
                 bg="#2b2b2b").pack(pady=(0, 20))

        # --- Input/Output Frame ---
        io_frame_bg = '#3c3f41'
        io_frame = tk.Frame(main_frame, bg=io_frame_bg, padx=15, pady=15, relief="flat", bd=1)
        io_frame.pack(fill="x", pady=10)
        io_frame.grid_columnconfigure(0, weight=1)
        io_frame.grid_columnconfigure(1, weight=1)

        self.draw_input_state(io_frame, io_frame_bg, self.program_result.initial_state)
        self.draw_output_score(io_frame, io_frame_bg, self.program_result.final_state)

        # --- Final Verdict Frame ---
        verdict_frame = tk.Frame(main_frame, bg=io_frame_bg, padx=15, pady=15, relief="flat", bd=1)
        verdict_frame.pack(fill="x", pady=(10, 20))
        self.draw_final_verdict(verdict_frame, io_frame_bg, self.program_result.final_state)

        # --- Processing Steps Trace ---
        steps_frame = tk.Frame(main_frame, bg='#3c3f41', bd=1, relief="sunken")
        steps_frame.pack(fill="both", expand=True, pady=(0, 0))

        tk.Label(steps_frame, text="Anomaly Detection Trace:", font=self.header_font, fg="#a9b7c6", bg="#3c3f41").pack(
            anchor="w", padx=10, pady=5)

        scrolled_text = tk.Text(steps_frame, bg="#2b2b2b", fg="#cccccc", font=self.label_font, relief="flat",
                                wrap="word")
        scrolled_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        trace = ""
        for step_name, state in self.program_result.intermediate_steps:
            # Display only relevant keys
            relevant_state = {k: v for k, v in state.items() if
                              k in ['PacketSizeDev', 'TimeDeltaDev', 'SourceIPEntropy', 'AnomalyScore',
                                    'AlertDecision']}
            state_str = ", ".join(
                [f"{k}:{v:.4f}" if isinstance(v, float) else f"{k}:{v}" for k, v in relevant_state.items()])
            trace += f"{step_name.ljust(30)} -> [{state_str}]\n"

        scrolled_text.insert(tk.END, trace)
        scrolled_text.config(state=tk.DISABLED)

    def draw_input_state(self, parent_frame, bg_color, state):
        input_frame = tk.Frame(parent_frame, bg=bg_color)
        input_frame.grid(row=0, column=0, sticky="nsew", padx=10)
        tk.Label(input_frame, text="Simulated Traffic Deviations", font=self.header_font, fg="#a9b7c6",
                 bg=bg_color).pack(pady=(0, 10))

        inputs = {
            'PacketSizeDev': ("Packet Size Deviation", "Normal/Deviation"),
            'TimeDeltaDev': ("Time Delta Deviation", "Consistent/Erratic"),
            'SourceIPEntropy': ("Source IP Entropy", "High/Low (Suspicious)")
        }

        for key, (label, status_text) in inputs.items():
            val = state.get(key, 0)
            text = f"{label}: {'1 (Suspicious)' if val == 1 else '0 (Normal)'}"
            color = COLOR_ALERT if val == 1 else COLOR_NORMAL
            tk.Label(input_frame, text=text, font=self.label_font, fg=color, bg=bg_color).pack(anchor="w")

        # Calculate Initial Risk Level (sum of inputs)
        initial_risk = state.get('PacketSizeDev', 0) + state.get('TimeDeltaDev', 0) + state.get('SourceIPEntropy', 0)
        risk_color = COLOR_ALERT if initial_risk >= 2 else (COLOR_RISK if initial_risk == 1 else COLOR_NORMAL)
        tk.Label(input_frame, text=f"\nInitial Risk Score: {initial_risk}/3", font=self.label_font, fg=risk_color,
                 bg=bg_color).pack(anchor="w")

    def draw_output_score(self, parent_frame, bg_color, state):
        output_frame = tk.Frame(parent_frame, bg=bg_color)
        output_frame.grid(row=0, column=1, sticky="nsew", padx=10)
        tk.Label(output_frame, text="Probabilistic Anomaly Result", font=self.header_font, fg="#a9b7c6",
                 bg=bg_color).pack(pady=(0, 10))

        anomaly_score = state.get('AnomalyScore', 0.0)
        alert_decision = state.get('AlertDecision', 0)

        # Color based on score magnitude
        if anomaly_score > 0.8:
            score_color = COLOR_ALERT
            score_text = "HIGH RISK"
        elif anomaly_score > 0.6:
            score_color = COLOR_RISK
            score_text = "MODERATE RISK"
        else:
            score_color = COLOR_LOW_RISK
            score_text = "LOW RISK"

        tk.Label(output_frame, text="Anomaly Score:", font=self.label_font, fg="#a9b7c6", bg=bg_color).pack(anchor="w")
        tk.Label(output_frame, text=f"{anomaly_score:.4f}", font=self.score_font, fg=score_color, bg=bg_color).pack(
            anchor="w")
        tk.Label(output_frame, text=score_text, font=self.label_font, fg=score_color, bg=bg_color).pack(anchor="w")

        # Alert Decision
        if alert_decision == 1:
            decision_text = "ALERT TRIGGERED (1)"
            decision_color = COLOR_ALERT
        else:
            decision_text = "ALERT SUPPRESSED (0)"
            decision_color = COLOR_NORMAL

        tk.Label(output_frame, text="\nSystem Decision:", font=self.label_font, fg="#a9b7c6", bg=bg_color).pack(
            anchor="w")
        tk.Label(output_frame, text=decision_text, font=self.header_font, fg=decision_color, bg=bg_color).pack(
            anchor="w")

    def draw_final_verdict(self, parent_frame, bg_color, final_state):
        tk.Label(parent_frame, text="--- Final Anomaly Verdict ---", font=self.header_font, fg="#a9b7c6",
                 bg=bg_color).pack(pady=(0, 10))

        anomaly_score = final_state.get('AnomalyScore', 0.0)
        alert_decision = final_state.get('AlertDecision', 0)

        # Calculate the deterministic state based on the score threshold (0.6)
        deterministic_alert = 1 if anomaly_score > 0.6 else 0

        verdict_text = ""
        verdict_color = COLOR_NORMAL
        report_details = []

        report_details.append(f"The Entropy analysis yielded an **Anomaly Score of {anomaly_score:.4f}**.")
        report_details.append(f"The probabilistic **ALERT threshold is nominally 0.6**.")

        if alert_decision == 1 and deterministic_alert == 1:
            verdict_text = "TRUE ALERT"
            verdict_color = COLOR_VERDICT_SUCCESS
            report_details.append(
                "\nVERDICT: The system correctly generated an ALERT. The traffic is highly suspicious.")
        elif alert_decision == 0 and deterministic_alert == 0:
            verdict_text = "TRUE NEGATIVE"
            verdict_color = COLOR_VERDICT_SUCCESS
            report_details.append("\nVERDICT: The system correctly suppressed the alert. Traffic appears to be clean.")
        elif alert_decision == 1 and deterministic_alert == 0:
            verdict_text = "FALSE POSITIVE"
            verdict_color = COLOR_VERDICT_WARNING
            report_details.append(
                "\nVERDICT: A **FALSE POSITIVE** occurred. The core's entropy caused the system to raise an unnecessary alert, despite the low score.")
        else:  # alert_decision == 0 and deterministic_alert == 1
            verdict_text = "FALSE NEGATIVE"
            verdict_color = COLOR_VERDICT_FAILURE
            report_details.append(
                "\nVERDICT: A **FALSE NEGATIVE** occurred. The core's entropy caused the system to suppress a necessary alert, despite the high score.")

        tk.Label(parent_frame, text=verdict_text, font=self.verdict_font, fg=verdict_color, bg=bg_color, pady=10).pack()

        # Use simple label for multiline details
        for detail in report_details:
            tk.Label(parent_frame, text=detail, font=self.label_font, fg="#cccccc", bg=bg_color, wraplength=700,
                     justify="left").pack(anchor="w", padx=10)


if __name__ == '__main__':
    # Dummy data for visualization test
    ProgramResult = namedtuple('ProgramResult', ['initial_state', 'final_state', 'intermediate_steps'])

    # Example: Inputs 1, 0, 0 (Initial Risk 1). Final Score 0.45, Alert 0 (True Negative)
    dummy_initial = {'PacketSizeDev': 1, 'TimeDeltaDev': 0, 'SourceIPEntropy': 0, 'AnomalyScore': 0.0,
                     'AlertDecision': 0}
    dummy_final = {'PacketSizeDev': 1, 'TimeDeltaDev': 0, 'SourceIPEntropy': 0, 'AnomalyScore': 0.4512,
                   'AlertDecision': 0}
    dummy_steps = [
        ("Initial State", dummy_initial),
        ("Step 1: ProbabilisticAnomalyGate", dummy_final)
    ]

    result = ProgramResult(dummy_initial, dummy_final, dummy_steps)
    AnomalyVisualizationWindow(result, title="Anomaly Detection Test").root.mainloop()