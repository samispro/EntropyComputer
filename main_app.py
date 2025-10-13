# -*- coding: utf-8 -*-
"""
Entropy Computer - Main Application & GUI (CustomTkinter Version)

This script uses CustomTkinter to create a unified desktop interface for the
Entropy Computer simulation, featuring all developed probabilistic gates.
"""
import customtkinter as ctk
import threading
from collections import namedtuple
import numpy as np

# CRITICAL: Ensure all required classes are imported from the updated entropy_computer.py
from entropy_computer import (
    EntropyCore,
    ProbabilisticAdder,
    ProbabilisticGroverSearch,
    EntropyProgram,
    # Renamed in the original import for clarity
    EntropyFirewall as EntropyFirewallGate,
    ProbabilisticAttackGate,
    ProbabilisticAnomalyGate
)
from visualization import VisualizationWindow

# Import the specific visualization windows for complex tabs
try:
    from firewall_visualization import FirewallVisualizationWindow
    from anomaly_visualization import AnomalyVisualizationWindow
except ImportError:
    # If visualization files are missing, set variables to None to trigger a user error message
    FirewallVisualizationWindow = None
    AnomalyVisualizationWindow = None

# --- Global State ---
CORE = None
STATE_VARS = {}


# --- Core Functions ---

def initialize_core():
    """Initializes or re-initializes the Entropy Core based on GUI input."""
    global CORE
    seed_text = STATE_VARS.get("seed_input_var").get() if STATE_VARS.get("seed_input_var") else ""

    seed = None
    if seed_text.strip():
        try:
            # Simplified check for a valid integer seed
            seed = int(seed_text)
        except ValueError:
            STATE_VARS["status_var"].set("Error: Seed must be a valid integer or left blank for a random seed.")
            return

    try:
        CORE = EntropyCore(seed=seed)
        STATE_VARS["status_var"].set(f"Entropy Core Seeded: {CORE.seed}. Ready to run a program.")
    except Exception as e:
        STATE_VARS["status_var"].set(f"Initialization Error: {str(e)}")


def run_program_callback():
    """
    Determines which preset is active, builds the correct program,
    runs the simulation, and launches the visualization.
    """
    if CORE is None:
        STATE_VARS["status_var"].set("Error: Initialize the Entropy Core first!")
        return

    active_tab = STATE_VARS["tab_view"].get()
    program = None
    initial_state_for_vis = None
    VisualizationClass = VisualizationWindow

    try:
        if active_tab == "Probabilistic Adder":
            STATE_VARS["status_var"].set("Running Probabilistic Adder...")

            initial_state = {
                'A': STATE_VARS["A_var"].get(), 'B': STATE_VARS["B_var"].get(), 'Cin': STATE_VARS["Cin_var"].get(),
                'Sum': 0, 'Cout': 0
            }
            initial_state_for_vis = initial_state.copy()
            instructions = [{"gate": ProbabilisticAdder(CORE), "inputs": ['A', 'B', 'Cin'], "outputs": ['Sum', 'Cout']}]
            program = EntropyProgram(instructions, initial_state)

        elif active_tab == "Probabilistic Search":
            STATE_VARS["status_var"].set("Running Probabilistic Search...")

            target_state = {
                'Q1': STATE_VARS["Q1_target_var"].get(), 'Q2': STATE_VARS["Q2_target_var"].get(),
                'Q3': STATE_VARS["Q3_target_var"].get(), 'Q4': STATE_VARS["Q4_target_var"].get()
            }
            initial_state_for_vis = target_state.copy()
            search_steps = STATE_VARS["search_steps_var"].get()

            instructions = [{
                "gate": ProbabilisticGroverSearch(CORE, target_state, search_steps),
                "inputs": [], "outputs": list(target_state.keys())
            }]
            initial_state_template = {key: 0 for key in target_state}
            program = EntropyProgram(instructions, initial_state_template)

        elif active_tab == "Probabilistic Firewall":
            if FirewallVisualizationWindow is None:
                STATE_VARS["status_var"].set("Error: The 'firewall_visualization.py' file is required for this tab.")
                return

            STATE_VARS["status_var"].set("Running Firewall Simulation...")
            VisualizationClass = FirewallVisualizationWindow

            # Inputs from the GUI
            intended_threat = STATE_VARS["ThreatSignature_var"].get()
            intended_integrity = STATE_VARS["IntegrityCheck_var"].get()
            is_quantum_attack = STATE_VARS["quantum_attack_toggle_var"].get()

            # --- FIX: INITIAL STATE FOR VISUALIZATION (Uses GUI names) ---
            # This dictionary must use the keys that firewall_visualization.py expects.
            initial_state_for_vis = {
                'ThreatSignature': intended_threat,  # Key used by visualization
                'IntegrityCheck': intended_integrity,  # Key used by visualization
                'Decision': 0,
                'AttackStatus': 0
            }

            # --- PROGRAM INITIAL STATE (Uses gate argument names) ---
            # This dictionary is used by the EntropyProgram.
            initial_state = {
                'Threat_Intent': intended_threat,
                'Integrity_Intent': intended_integrity,
                'Attack_Enabled_Flag': is_quantum_attack,
                # Actual State (Outputs of the attack gate)
                'Threat_Actual': intended_threat,
                'Integrity_Actual': intended_integrity,
                # Final Outputs
                'Decision': 0,
                'AttackStatus': 0
            }

            instructions = [
                # PHASE 1: ATTACK - Pass all 3 arguments
                {
                    "gate": ProbabilisticAttackGate(CORE),
                    # Input keys must match the three required arguments of ProbabilisticAttackGate.execute()
                    "inputs": ['Threat_Intent', 'Integrity_Intent', 'Attack_Enabled_Flag'],
                    "outputs": ['Threat_Actual', 'Integrity_Actual']
                },
                # PHASE 2: DEFENSE - Firewall acts on the actual packet state
                {
                    "gate": EntropyFirewallGate(CORE),
                    # Firewall takes the two actual packet states
                    "inputs": ['Threat_Actual', 'Integrity_Actual'],
                    "outputs": ['Decision', 'AttackStatus']
                }
            ]

            program = EntropyProgram(instructions, initial_state)

        elif active_tab == "Probabilistic Anomaly Detection":
            if AnomalyVisualizationWindow is None:
                STATE_VARS["status_var"].set("Error: The 'anomaly_visualization.py' file is required for this tab.")
                return

            STATE_VARS["status_var"].set("Running Anomaly Detection Simulation...")
            VisualizationClass = AnomalyVisualizationWindow

            initial_state = {
                'PacketSizeDev': STATE_VARS["PacketSizeDev_var"].get(),
                'TimeDeltaDev': STATE_VARS["TimeDeltaDev_var"].get(),
                'SourceIPEntropy': STATE_VARS["SourceIPEntropy_var"].get(),
                'AnomalyScore': 0.0,
                'AlertDecision': 0
            }
            initial_state_for_vis = initial_state.copy()

            instructions = [{
                "gate": ProbabilisticAnomalyGate(CORE),
                "inputs": ['PacketSizeDev', 'TimeDeltaDev', 'SourceIPEntropy'],
                "outputs": ['AnomalyScore', 'AlertDecision']
            }]

            program = EntropyProgram(instructions, initial_state)

        if program and VisualizationClass:
            program.run()
            STATE_VARS["status_var"].set("Computation complete. Opening visualization...")

            def start_vis():
                ProgramResult = namedtuple('ProgramResult', ['initial_state', 'final_state', 'intermediate_steps'])

                result = ProgramResult(
                    initial_state=initial_state_for_vis,  # PASS THE CORRECTLY MAPPED DICTIONARY
                    final_state=program.final_state,
                    intermediate_steps=program.intermediate_steps
                )

                # Update status bar with results
                if active_tab == "Probabilistic Firewall":
                    decision_text = 'ALLOW' if result.final_state['Decision'] == 1 else 'DENY'
                    STATE_VARS["status_var"].set(
                        f"Firewall complete. Decision: {decision_text}. Final Logged Threat: {result.final_state['AttackStatus']}.")
                elif active_tab == "Probabilistic Anomaly Detection":
                    alert_text = 'ALERT' if result.final_state['AlertDecision'] == 1 else 'NO ALERT'
                    STATE_VARS["status_var"].set(
                        f"Anomaly complete. Score: {result.final_state['AnomalyScore']:.2f}, Alert: {alert_text}.")

                vis_window = VisualizationClass(result, title=f"{active_tab} Result (Seed: {CORE.seed})")

            threading.Thread(target=start_vis, daemon=True).start()

    except Exception as e:
        STATE_VARS["status_var"].set(f"Error during execution: {type(e).__name__}: {str(e)}")


# --- CTk GUI Setup ---

def create_gui():
    """Initializes and runs the CustomTkinter GUI."""
    ctk.set_appearance_mode("Dark")  # Preserving user's last preferred dark mode setting
    ctk.set_default_color_theme("blue")  # Preserving user's last preferred theme

    app = ctk.CTk()
    app.title("Entropy Computer v5.0: Cybersecurity Gates")
    app.geometry("850x650")

    app.grid_columnconfigure(0, weight=1)
    app.grid_rowconfigure(3, weight=1)

    # --- Title ---
    ctk.CTkLabel(app, text="Entropy Computer", font=ctk.CTkFont(size=20, weight="bold")).grid(
        row=0, column=0, padx=20, pady=(10, 5), sticky="ew")

    # --- Control Frame (Seed) ---
    control_frame = ctk.CTkFrame(app)
    control_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
    control_frame.grid_columnconfigure(1, weight=1)

    STATE_VARS["seed_input_var"] = ctk.StringVar()
    ctk.CTkLabel(control_frame, text="Seed (optional):").grid(row=0, column=0, padx=(10, 5), pady=10)
    ctk.CTkEntry(control_frame, textvariable=STATE_VARS["seed_input_var"], width=150).grid(row=0, column=1, padx=5,
                                                                                           pady=10, sticky="w")
    ctk.CTkButton(control_frame, text="Initialize/Reset Core", command=initialize_core).grid(row=0, column=2,
                                                                                             padx=(5, 10), pady=10,
                                                                                             sticky="e")

    # --- Status Bar ---
    STATE_VARS["status_var"] = ctk.StringVar(value="Status: Core not initialized. Enter seed or press Initialize.")
    ctk.CTkLabel(app, textvariable=STATE_VARS["status_var"], anchor="w", fg_color="#333333", text_color="#FFFFFF",
                 corner_radius=5).grid(
        row=2, column=0, padx=20, pady=(0, 10), sticky="ew")

    # --- Tab View for Presets ---
    STATE_VARS["tab_view"] = ctk.CTkTabview(app, segmented_button_selected_color="#50FA7B",
                                            segmented_button_selected_hover_color="#40C862")
    STATE_VARS["tab_view"].grid(row=3, column=0, padx=20, pady=5, sticky="nsew")

    STATE_VARS["tab_view"].add("Probabilistic Adder")
    STATE_VARS["tab_view"].add("Probabilistic Search")
    STATE_VARS["tab_view"].add("Probabilistic Firewall")
    STATE_VARS["tab_view"].add("Probabilistic Anomaly Detection")

    tab_adder = STATE_VARS["tab_view"].tab("Probabilistic Adder")
    tab_search = STATE_VARS["tab_view"].tab("Probabilistic Search")
    tab_firewall = STATE_VARS["tab_view"].tab("Probabilistic Firewall")
    tab_anomaly = STATE_VARS["tab_view"].tab("Probabilistic Anomaly Detection")

    # --- Helper for Radio Buttons ---
    def create_input_frame(parent, text, default_val, desc_0=None, desc_1=None):
        STATE_VARS[f"{text}_var"] = ctk.IntVar(value=default_val)
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        ctk.CTkLabel(frame, text=text, font=ctk.CTkFont(weight="bold")).pack()

        radio_text_0 = f"0{f': {desc_0}' if desc_0 else ''}"
        radio_text_1 = f"1{f': {desc_1}' if desc_1 else ''}"

        ctk.CTkRadioButton(frame, text=radio_text_0, variable=STATE_VARS[f"{text}_var"], value=0).pack(anchor="w",
                                                                                                       padx=20, pady=2)
        ctk.CTkRadioButton(frame, text=radio_text_1, variable=STATE_VARS[f"{text}_var"], value=1).pack(anchor="w",
                                                                                                       padx=20, pady=2)
        return frame

    # --- Configure Adder Tab ---
    tab_adder.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(tab_adder, text="Set Initial State for 1-Bit Full Adder",
                 font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, pady=10)

    adder_input_frame = ctk.CTkFrame(tab_adder)
    adder_input_frame.grid(row=1, column=0, pady=10)

    create_input_frame(adder_input_frame, "A", 0).pack(side="left", padx=20, fill="y")
    create_input_frame(adder_input_frame, "B", 1).pack(side="left", padx=20, fill="y")
    create_input_frame(adder_input_frame, "Cin", 0).pack(side="left", padx=20, fill="y")

    ctk.CTkButton(tab_adder, text="Run Adder Program", command=run_program_callback, height=40).grid(row=2, column=0,
                                                                                                     padx=20, pady=10,
                                                                                                     sticky="ew")

    # --- Configure Search Tab ---
    tab_search.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(tab_search, text="Define Target State (The Needle in the Haystack)",
                 font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, pady=10)

    search_input_frame = ctk.CTkFrame(tab_search)
    search_input_frame.grid(row=1, column=0, pady=5)

    # Qubit Target Variables
    STATE_VARS["Q1_target_var"] = ctk.IntVar(value=0)
    STATE_VARS["Q2_target_var"] = ctk.IntVar(value=1)
    STATE_VARS["Q3_target_var"] = ctk.IntVar(value=1)
    STATE_VARS["Q4_target_var"] = ctk.IntVar(value=0)

    for i, key in enumerate(['Q1', 'Q2', 'Q3', 'Q4']):
        frame = ctk.CTkFrame(search_input_frame, fg_color="transparent")
        ctk.CTkLabel(frame, text=key, font=ctk.CTkFont(weight="bold")).pack()
        ctk.CTkRadioButton(frame, text="0", variable=STATE_VARS[f"{key}_target_var"], value=0).pack(anchor="w", padx=20,
                                                                                                    pady=2)
        ctk.CTkRadioButton(frame, text="1", variable=STATE_VARS[f"{key}_target_var"], value=1).pack(anchor="w", padx=20,
                                                                                                    pady=2)
        frame.pack(side="left", padx=10, fill="y")

    steps_frame = ctk.CTkFrame(tab_search, fg_color="transparent")
    steps_frame.grid(row=2, column=0, pady=5)
    ctk.CTkLabel(steps_frame, text="Search Steps (Iterations):").pack(side="left", padx=5)
    STATE_VARS["search_steps_var"] = ctk.IntVar(value=10)  # Stored as IntVar
    ctk.CTkEntry(steps_frame, textvariable=STATE_VARS["search_steps_var"], width=80).pack(side="left")

    ctk.CTkButton(tab_search, text="Run Search Program", command=run_program_callback, height=40).grid(row=3, column=0,
                                                                                                       padx=20, pady=10,
                                                                                                       sticky="ew")

    # --- Configure Firewall Tab ---
    tab_firewall.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(tab_firewall, text="Simulate Packet Inputs for Firewall Assessment",
                 font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, pady=10)

    # Input frame
    firewall_input_frame = ctk.CTkFrame(tab_firewall)
    firewall_input_frame.grid(row=1, column=0, pady=10)

    # Note: Variable names must match the ones used in run_program_callback
    create_input_frame(firewall_input_frame, "ThreatSignature", 1, desc_0="Safe (0)", desc_1="Threat (1)").pack(
        side="left", padx=20, fill="y")
    create_input_frame(firewall_input_frame, "IntegrityCheck", 1, desc_0="Corrupted (0)", desc_1="Intact (1)").pack(
        side="left", padx=20, fill="y")

    # Quantum Attack Toggle
    STATE_VARS["quantum_attack_toggle_var"] = ctk.IntVar(value=0)  # Default to 0 (Binary/Ordinary)
    toggle_frame = ctk.CTkFrame(tab_firewall)
    toggle_frame.grid(row=2, column=0, pady=10)

    ctk.CTkLabel(toggle_frame, text="Attack Mode:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
    ctk.CTkSwitch(toggle_frame,
                  text="Quantum Attack (Probabilistic Spoofing)",
                  variable=STATE_VARS["quantum_attack_toggle_var"],
                  onvalue=1, offvalue=0).pack(side="left", padx=20)

    ctk.CTkButton(tab_firewall, text="Run Firewall Simulation", command=run_program_callback, height=40).grid(row=3,
                                                                                                              column=0,
                                                                                                              padx=20,
                                                                                                              pady=10,
                                                                                                              sticky="ew")

    # --- Configure Anomaly Detection Tab ---
    tab_anomaly.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(tab_anomaly, text="Simulate Network Traffic Characteristics (for Anomaly Score)",
                 font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, pady=10)

    anomaly_input_frame = ctk.CTkFrame(tab_anomaly)
    anomaly_input_frame.grid(row=1, column=0, pady=10)

    # Note: 1 = HIGH Deviation/Low Entropy (i.e., higher risk)
    create_input_frame(anomaly_input_frame, "PacketSizeDev", 0, desc_0="Normal", desc_1="High Deviation").pack(
        side="left", padx=10, fill="y")
    create_input_frame(anomaly_input_frame, "TimeDeltaDev", 0, desc_0="Consistent", desc_1="Erratic Time").pack(
        side="left", padx=10, fill="y")
    create_input_frame(anomaly_input_frame, "SourceIPEntropy", 0, desc_0="High Entropy (Diverse)",
                       desc_1="Low Entropy (Predictable/Malicious)").pack(side="left", padx=10, fill="y")

    ctk.CTkButton(tab_anomaly, text="Run Anomaly Detection", command=run_program_callback, height=40).grid(row=2,
                                                                                                           column=0,
                                                                                                           padx=20,
                                                                                                           pady=10,
                                                                                                           sticky="ew")

    # --- Final Setup ---
    initialize_core()
    app.mainloop()


if __name__ == "__main__":
    create_gui()