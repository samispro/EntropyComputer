# -*- coding: utf-8 -*-
"""
Entropy Computer Firewall Visualization Module

Shows the simulated network attack inputs, the firewall's probabilistic
decision, and the resulting defense status.
"""
import tkinter as tk
from tkinter import font as tkfont
from collections import namedtuple

# Define colors for clarity in the firewall context
COLOR_ALLOW = "#6a8759"
COLOR_BLOCK = "#cc7832"
COLOR_ATTACK = "#e05252"
COLOR_NEUTRAL = "#888888"
COLOR_VERDICT_SUCCESS = "#4CAF50"  # Green for successful defense/clean pass
COLOR_VERDICT_WARNING = "#FFC107"  # Amber for overblock
COLOR_VERDICT_FAILURE = "#F44336"  # Red for defense failure


class FirewallVisualizationWindow:
    def __init__(self, program_result, title="Entropy Firewall Simulation"):
        self.program_result = program_result

        self.root = tk.Tk()
        self.root.title(title)
        self.root.configure(bg='#2b2b2b')
        # --- MODIFICATION 1: Increased window size ---
        self.root.geometry("800x600")

        self.title_font = tkfont.Font(family="Helvetica", size=18, weight="bold")
        self.header_font = tkfont.Font(family="Helvetica", size=12, weight="bold")
        self.label_font = tkfont.Font(family="Helvetica", size=10)
        self.result_font = tkfont.Font(family="Courier", size=24, weight="bold")
        # --- MODIFICATION 2: New font for verdict ---
        self.verdict_font = tkfont.Font(family="Helvetica", size=16, weight="bold")

        self.create_widgets()
        self.root.mainloop()

    def create_widgets(self):
        main_frame = tk.Frame(self.root, bg='#2b2b2b', padx=20, pady=20)
        main_frame.pack(expand=True, fill="both")

        title_label = tk.Label(main_frame, text="Probabilistic Firewall Simulation", font=self.title_font, fg="#cccccc",
                               bg="#2b2b2b")
        title_label.pack(pady=(0, 20))

        io_frame_bg = '#3c3f41'
        io_frame = tk.Frame(main_frame, bg=io_frame_bg, padx=15, pady=15, relief="flat", bd=1)
        io_frame.pack(fill="x", pady=10)
        io_frame.grid_columnconfigure(0, weight=1)
        io_frame.grid_columnconfigure(1, weight=1)

        self.draw_input_state(io_frame, io_frame_bg, self.program_result.initial_state)
        self.draw_final_decision(io_frame, io_frame_bg, self.program_result.final_state)

        # --- MODIFICATION 3: Add the Final Verdict Report Frame ---
        verdict_frame = tk.Frame(main_frame, bg=io_frame_bg, padx=15, pady=15, relief="flat", bd=1)
        verdict_frame.pack(fill="x", pady=(10, 20))
        self.draw_final_verdict(verdict_frame, io_frame_bg, self.program_result.initial_state,
                                self.program_result.final_state)

        # --- Processing Steps Trace ---
        steps_frame = tk.Frame(main_frame, bg='#3c3f41', bd=1, relief="sunken")
        steps_frame.pack(fill="both", expand=True, pady=(0, 0))  # Fill remaining space

        steps_label = tk.Label(steps_frame, text="Firewall Processing Trace:", font=self.header_font, fg="#a9b7c6",
                               bg="#3c3f41")
        steps_label.pack(anchor="w", padx=10, pady=5)

        # Use a scrolled text widget for long traces
        scrolled_text = tk.Text(steps_frame, bg="#2b2b2b", fg="#cccccc", font=self.label_font, relief="flat",
                                wrap="word")
        scrolled_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        trace = ""
        for step_name, state in self.program_result.intermediate_steps:
            relevant_state = {k: v for k, v in state.items() if
                              k in ['ThreatSignature_Intent', 'IntegrityCheck_Intent', 'ThreatSignature',
                                    'IntegrityCheck', 'Decision', 'AttackStatus']}
            state_str = ", ".join([f"{k}:{v}" for k, v in relevant_state.items()])
            trace += f"{step_name.ljust(30)} -> [{state_str}]\n"
        scrolled_text.insert(tk.END, trace)
        scrolled_text.config(state=tk.DISABLED)  # Make text read-only

    def draw_input_state(self, parent_frame, bg_color, state):
        input_frame = tk.Frame(parent_frame, bg=bg_color)
        input_frame.grid(row=0, column=0, sticky="nsew", padx=10)
        tk.Label(input_frame, text="Intended Packet Inputs (from GUI)", font=self.header_font, fg="#a9b7c6",
                 bg=bg_color).pack(pady=(0, 10))

        # Threat Signature display
        sig_val = state['ThreatSignature']
        sig_text = "Threat (1)" if sig_val == 1 else "Safe (0)"
        sig_color = COLOR_ATTACK if sig_val == 1 else COLOR_NEUTRAL
        tk.Label(input_frame, text=f"Threat Signature: {sig_text}", font=self.label_font, fg=sig_color,
                 bg=bg_color).pack(anchor="w")

        # Integrity Check display
        int_val = state['IntegrityCheck']
        int_text = "Intact (1)" if int_val == 1 else "Corrupted (0)"
        int_color = COLOR_ATTACK if int_val == 1 else COLOR_NEUTRAL
        tk.Label(input_frame, text=f"Integrity Check: {int_text}", font=self.label_font, fg=int_color,
                 bg=bg_color).pack(anchor="w")

        is_attack_input_status = 1 if state.get('ThreatSignature') == 1 and state.get('IntegrityCheck') == 1 else 0
        attack_text = "-> INTENDED ATTACK SCENARIO <-" if is_attack_input_status == 1 else "-> INTENDED CLEAN SCENARIO <-"
        attack_color = COLOR_ATTACK if is_attack_input_status == 1 else COLOR_ALLOW
        tk.Label(input_frame, text=attack_text, font=self.label_font, fg=attack_color, bg=bg_color, pady=10).pack(
            anchor="w")

    def draw_final_decision(self, parent_frame, bg_color, state):
        output_frame = tk.Frame(parent_frame, bg=bg_color)
        output_frame.grid(row=0, column=1, sticky="nsew", padx=10)
        tk.Label(output_frame, text="Firewall Decision (Probabilistic)", font=self.header_font, fg="#a9b7c6",
                 bg=bg_color).pack(pady=(0, 10))

        decision = state.get('Decision', 0)  # 0=ALLOW, 1=BLOCK
        # AttackStatus here reflects the status of the packet *as it reached the firewall*
        is_attack_on_firewall = state.get('AttackStatus', 0)

        if decision == 1:
            decision_text = "PACKET BLOCKED (1)"
            decision_color = COLOR_BLOCK
        else:
            decision_text = "PACKET ALLOWED (0)"
            decision_color = COLOR_ALLOW

        tk.Label(output_frame, text="Final Decision:", font=self.label_font, fg="#a9b7c6", bg=bg_color).pack(anchor="w")
        tk.Label(output_frame, text=decision_text, font=self.result_font, fg=decision_color, bg=bg_color, pady=5).pack(
            anchor="w")

        defense_status = ""
        defense_color = ""

        # Determine outcome based on what the firewall actually saw
        if is_attack_on_firewall == 1 and decision == 1:
            defense_status = "SUCCESSFUL DEFENSE (True Positive)"
            defense_color = COLOR_ALLOW
        elif is_attack_on_firewall == 1 and decision == 0:
            defense_status = "DEFENSE FAILURE (FALSE NEGATIVE)"
            defense_color = COLOR_ATTACK
        elif is_attack_on_firewall == 0 and decision == 1:
            defense_status = "OVERBLOCK (FALSE POSITIVE)"
            defense_color = COLOR_BLOCK
        else:  # is_attack_on_firewall == 0 and decision == 0
            defense_status = "CLEAN PASS (True Negative)"
            defense_color = COLOR_ALLOW

        tk.Label(output_frame, text="Defense Outcome:", font=self.label_font, fg="#a9b7c6", bg=bg_color, pady=10).pack(
            anchor="w")
        tk.Label(output_frame, text=defense_status, font=self.label_font, fg=defense_color, bg=bg_color).pack(
            anchor="w")

    # --- MODIFICATION 4: New function to draw the Final Verdict ---
    def draw_final_verdict(self, parent_frame, bg_color, initial_state, final_state):
        tk.Label(parent_frame, text="--- Final Defense Verdict ---", font=self.header_font, fg="#a9b7c6",
                 bg=bg_color).pack(pady=(0, 10))

        # Intended state from GUI
        intended_threat = initial_state['ThreatSignature'] == 1 and initial_state['IntegrityCheck'] == 1

        # Actual state as it reached the firewall (after potential quantum attack effects)
        actual_threat_input = final_state.get('ThreatSignature', 0) == 1 and final_state.get('IntegrityCheck', 0) == 1

        # Firewall's final decision
        decision = final_state.get('Decision', 0)  # 0=ALLOW, 1=BLOCK

        verdict_text = ""
        verdict_color = COLOR_NEUTRAL
        report_details = []

        if intended_threat:
            report_details.append("An attack was INTENDED from the source.")
        else:
            report_details.append("A clean packet was INTENDED from the source.")

        if actual_threat_input != intended_threat:
            report_details.append("-> Due to QUANTUM ATTACK effects, the packet's signature changed during transit.")
            if actual_threat_input:
                report_details.append("   It arrived at the firewall looking like a THREAT.")
            else:
                report_details.append("   It arrived at the firewall looking SAFE.")
        else:
            report_details.append("-> The packet's signature remained consistent during transit.")

        # Determine the ultimate outcome based on ACTUAL threat reaching firewall
        if actual_threat_input:  # If the packet *actually* looked like an attack to the firewall
            if decision == 1:  # Firewall blocked it
                verdict_text = "SUCCESSFUL DEFENSE!"
                verdict_color = COLOR_VERDICT_SUCCESS
                report_details.append("\nVERDICT: The QUANTUM FIREWALL successfully BLOCKED the perceived threat.")
            else:  # Firewall allowed it
                verdict_text = "CRITICAL DEFENSE FAILURE!"
                verdict_color = COLOR_VERDICT_FAILURE
                report_details.append(
                    "\nVERDICT: The QUANTUM FIREWALL FAILED to block the perceived threat. System Compromised!")
        else:  # If the packet *actually* looked safe to the firewall
            if decision == 1:  # Firewall blocked it
                verdict_text = "OVERBLOCK WARNING!"
                verdict_color = COLOR_VERDICT_WARNING
                report_details.append(
                    "\nVERDICT: The QUANTUM FIREWALL incorrectly BLOCKED a SAFE packet. Service Interruption.")
            else:  # Firewall allowed it
                verdict_text = "CLEAN PASS!"
                verdict_color = COLOR_VERDICT_SUCCESS
                report_details.append("\nVERDICT: The QUANTUM FIREWALL correctly ALLOWED a clean packet to pass.")

        tk.Label(parent_frame, text=verdict_text, font=self.verdict_font, fg=verdict_color, bg=bg_color, pady=10).pack()

        for detail in report_details:
            tk.Label(parent_frame, text=detail, font=self.label_font, fg="#cccccc", bg=bg_color, wraplength=750,
                     justify="left").pack(anchor="w", padx=10)


if __name__ == '__main__':
    # Dummy data for testing the visualization window directly
    ProgramResult = namedtuple('ProgramResult', ['initial_state', 'final_state', 'intermediate_steps'])

    # --- TEST CASE 1: Intended Attack (1,1), Quantum Attack flips to (0,1), Firewall allows (0) -> FAILURE ---
    # initial_state_for_gui = {'ThreatSignature': 1, 'IntegrityCheck': 1, 'Decision': 0, 'AttackStatus': 0}
    # trace_step1 = {'ThreatSignature_Intent': 1, 'IntegrityCheck_Intent': 1, 'ThreatSignature': 0, 'IntegrityCheck': 1, 'Decision': 0, 'AttackStatus': 0}
    # final_state_from_program = {'ThreatSignature_Intent': 1, 'IntegrityCheck_Intent': 1, 'ThreatSignature': 0, 'IntegrityCheck': 1, 'Decision': 0, 'AttackStatus': 0} # Firewall saw 0,1 (not threat) and allowed
    # dummy_steps = [
    #     ("Initial State (Intended)", initial_state_for_gui),
    #     ("Step 1: ProbabilisticAttackGate", trace_step1),
    #     ("Step 2: EntropyFirewallGate", final_state_from_program)
    # ]
    # result = ProgramResult(initial_state_for_gui, final_state_from_program, dummy_steps)
    # FirewallVisualizationWindow(result, title="Quantum Attack Example (Intended 1,1 -> Actual 0,1 -> FAILED)")

    # --- TEST CASE 2: Intended Clean (0,0), Quantum Attack flips to (1,1), Firewall blocks (1) -> OVERBLOCK ---
    initial_state_for_gui = {'ThreatSignature': 0, 'IntegrityCheck': 0, 'Decision': 0, 'AttackStatus': 0}
    trace_step1 = {'ThreatSignature_Intent': 0, 'IntegrityCheck_Intent': 0, 'ThreatSignature': 1, 'IntegrityCheck': 1,
                   'Decision': 0, 'AttackStatus': 0}
    final_state_from_program = {'ThreatSignature_Intent': 0, 'IntegrityCheck_Intent': 0, 'ThreatSignature': 1,
                                'IntegrityCheck': 1, 'Decision': 1,
                                'AttackStatus': 1}  # Firewall saw 1,1 (threat) and blocked
    dummy_steps = [
        ("Initial State (Intended)", initial_state_for_gui),
        ("Step 1: ProbabilisticAttackGate", trace_step1),
        ("Step 2: EntropyFirewallGate", final_state_from_program)
    ]
    result = ProgramResult(initial_state_for_gui, final_state_from_program, dummy_steps)
    FirewallVisualizationWindow(result, title="Quantum Attack Example (Intended 0,0 -> Actual 1,1 -> OVERBLOCK)")