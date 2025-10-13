# -*- coding: utf-8 -*-
"""
Entropy Computer Core Logic

This file contains the heart of the Entropy Computer simulation.
It defines the core components:
1.  EntropyCore: The "processor" that generates random states based on various entropy sources.
2.  EntropyLogicGate: A base class for probabilistic logic gates.
3.  Probabilistic Gates (AND, OR, NOT, ADD, GROVER, FIREWALL, ANOMALY): Implementations of logic gates whose outputs
    are not deterministic, governed by the entropy from the core.
4.  EntropyProgram: A container to execute a sequence of these probabilistic instructions.

The novelty of this concept lies in moving away from the deterministic, binary
logic of classical computers. Instead of a clock tick, we have an "entropy tick."
Instead of guaranteed outputs (1 AND 1 is always 1), we have probable outputs.
This model could be conceptually useful for problems that are inherently probabilistic,
like simulations in quantum mechanics, complex system modeling, or even certain
types of AI, where randomness and exploration are key features.
"""

import os
import random
import time
import numpy as np


# --- Core Components ---

class EntropyCore:
    """
    The central processing unit of the Entropy Computer.
    Instead of a deterministic clock, it uses a flow of entropy to drive computations.
    """

    def __init__(self, seed=None):
        """
        Initializes the entropy core.
        A seed can be provided for reproducible "entropy flows."
        """
        self.seed = seed if seed is not None else int.from_bytes(os.urandom(8), 'big')
        self.random_source = random.Random(self.seed)
        self.thermal_noise_level = 0.1
        print(f"Entropy Core initialized with seed: {self.seed}")

    def get_entropy_tick(self):
        """
        Generates a "tick" of entropy. This is the fundamental driving force.
        It combines system randomness with simulated thermal noise.
        Returns a float between 0.0 and 1.0.
        """
        # 1. High-quality system randomness
        system_rand = self.random_source.random()

        # 2. Simulated thermal noise (a small random fluctuation)
        noise = (self.random_source.random() - 0.5) * self.thermal_noise_level

        # Combine and clamp the value between 0.0 and 1.0
        entropy_value = np.clip(system_rand + noise, 0.0, 1.0)
        return entropy_value

    def get_binary_result(self, probability_of_one: float) -> int:
        """
        Returns 1 with the given probability, otherwise 0.
        This is the standard function for probabilistic binary output.
        """
        return 1 if self.random_source.random() < probability_of_one else 0


class EntropyLogicGate:
    """
    Base class for a probabilistic logic gate.
    """

    def __init__(self, core: EntropyCore):
        self.core = core

    def execute(self, *inputs):
        raise NotImplementedError("This method should be implemented by subclasses.")


# --- 1. Foundational Logic Gates ---

class EntropyAND(EntropyLogicGate):
    """
    A probabilistic AND gate with a 10% chance of error (flip) based on entropy.
    """

    def execute(self, a, b):
        ideal_result = a and b
        entropy = self.core.get_entropy_tick()

        # If ideal_result is 1 (True), error is a False Negative (flips to 0) if entropy is low.
        if ideal_result == 1:
            # 10% chance to flip to 0 if entropy is very low (vulnerable state)
            return 1 if entropy > 0.1 else 0
        # If ideal_result is 0 (False), error is a False Positive (flips to 1) if entropy is high.
        else:
            # 10% chance to flip to 1 if entropy is very high (noisy state)
            return 0 if entropy < 0.9 else 1


class EntropyOR(EntropyLogicGate):
    """
    A probabilistic OR gate with a 10% chance of error (flip) based on entropy.
    """

    def execute(self, a, b):
        ideal_result = a or b
        entropy = self.core.get_entropy_tick()

        if ideal_result == 1:
            return 1 if entropy > 0.1 else 0
        else:
            return 0 if entropy < 0.9 else 1


class EntropyNOT(EntropyLogicGate):
    """
    A probabilistic NOT gate. 5% chance the NOT operation fails due to low entropy.
    """

    def execute(self, a):
        ideal_result = 1 - a
        entropy = self.core.get_entropy_tick()
        # 95% chance to return the correct flipped bit, 5% chance to fail (return a).
        return ideal_result if entropy > 0.05 else a


# --- 2. Complex & Advanced Gates ---

class ProbabilisticAdder(EntropyLogicGate):
    """
    A simple 1-bit probabilistic full adder.
    """

    def __init__(self, core: EntropyCore):
        super().__init__(core)
        self.e_and = EntropyAND(core)
        self.e_or = EntropyOR(core)

    def probabilistic_xor(self, a, b):
        ideal_result = a ^ b
        entropy = self.core.get_entropy_tick()
        # 15% chance for the XOR operation to flip (fail).
        return ideal_result if entropy > 0.15 else (1 - ideal_result)

    def execute(self, a, b, carry_in):
        # Sum = (A XOR B) XOR CarryIn
        sum1 = self.probabilistic_xor(a, b)
        final_sum = self.probabilistic_xor(sum1, carry_in)

        # CarryOut = (A AND B) OR (CarryIn AND (A XOR B))
        and1 = self.e_and.execute(a, b)
        and2 = self.e_and.execute(carry_in, sum1)
        final_carry = self.e_or.execute(and1, and2)

        # The Adder returns both outputs as a tuple
        return final_sum, final_carry


class ProbabilisticGroverSearch(EntropyLogicGate):
    """
    Simulates a probabilistic quantum search (analogous to Grover's algorithm).
    """

    def __init__(self, core: EntropyCore, target_state: dict, steps: int = 10):
        super().__init__(core)
        self.target_state = target_state
        self.target_items = sorted(target_state.items())

        # Logic for calculating optimal steps remains here but the gate uses provided steps.
        num_qubits = len(target_state)
        num_states = 2 ** num_qubits
        optimal_steps = int(np.sqrt(num_states))
        self.steps = max(1, steps)
        self.num_states = num_states

        print(f"Grover Search initialized: {num_qubits} qubits, {num_states} states, "
              f"{self.steps} iterations (optimal: {optimal_steps})")

    def execute(self, *inputs):
        # --- [Grover's Amplitude Amplification Logic] ---
        initial_prob = 1.0 / self.num_states
        theta = np.arcsin(np.sqrt(initial_prob))
        angle_after_iterations = (2 * self.steps + 1) * theta
        success_prob = (np.sin(angle_after_iterations)) ** 2

        # Add small entropy-based noise
        entropy_noise = (self.core.get_entropy_tick() - 0.5) * 0.05
        final_success_prob = np.clip(success_prob + entropy_noise, 0.0, 1.0)

        # --- [Probabilistic Outcome Determination] ---
        outcome = self.core.random_source.random()

        if outcome < final_success_prob:
            # Success: Return the target state
            final_state = {key: value for key, value in self.target_items}
            print("✓ Target state found!")
        else:
            # Failure: Return a random non-target state
            attempts = 0
            while attempts < 100:
                random_state = {}
                for key, _ in self.target_items:
                    random_state[key] = self.core.random_source.randint(0, 1)

                is_target = all(random_state[k] == v for k, v in self.target_items)
                if not is_target:
                    final_state = random_state
                    print("✗ Search converged to non-target state")
                    break
                attempts += 1
            else:
                final_state = {key: value for key, value in self.target_items}

        # Output the final state dictionary values in the order of the keys
        return tuple(final_state[key] for key, _ in self.target_items)


# --- 3. Cybersecurity Gates ---

class ProbabilisticAttackGate(EntropyLogicGate):
    """
    Simulates an attacker attempting to spoof a packet.
    If 'Quantum Attack' is enabled (input 2 is 1), the threat/integrity states
    have a probability of flipping (spoofing successfully).
    """

    def execute(self, threat_input: int, integrity_input: int, quantum_attack_enabled: int):

        spoof_prob = 0.4  # Base 40% chance of spoofing

        # Entropy modulates the spoofing success: low entropy (predictable system)
        # gives the attacker a slight advantage.
        entropy = self.core.get_entropy_tick()
        spoof_mod = (1 - entropy) * 0.2  # Adds up to 20% if entropy is 0
        final_spoof_prob = np.clip(spoof_prob + spoof_mod, 0.4, 0.6)  # Clamped between 40% and 60%

        modified_threat = threat_input
        modified_integrity = integrity_input

        if quantum_attack_enabled == 1:
            # 1. Threat Spoofing (1 -> 0)
            if threat_input == 1:
                # Does the attacker successfully spoof the threat signature?
                if self.core.get_binary_result(final_spoof_prob) == 1:
                    modified_threat = 0  # Successful spoofing

            # 2. Integrity Repair (0 -> 1)
            if integrity_input == 0:
                # Does the attacker successfully repair the integrity check?
                if self.core.get_binary_result(final_spoof_prob) == 1:
                    modified_integrity = 1  # Successful integrity repair

        # Note: If quantum_attack_enabled is 0, the outputs simply equal the inputs.
        return modified_threat, modified_integrity


class EntropyFirewall(EntropyLogicGate):
    """
    Simulates a firewall whose decision is subject to an error rate tied to entropy.
    If the classical decision is DENY, entropy can cause a False Allow (failure).
    """

    def execute(self, threat_state: int, integrity_state: int):

        # Classical Firewall Logic: DENY if Threat=1 AND Integrity=0
        classical_deny = (threat_state == 1 and integrity_state == 0)

        # Decision (1=ALLOW, 0=DENY)
        firewall_decision = 0 if classical_deny else 1

        # Entropy Modulation for Failure (False Allow)
        if classical_deny:
            # Error Probability (False Allow) is inversely proportional to Entropy
            # Low Entropy (e.g., system overload/predictability) increases failure chance.
            max_error_prob = 0.25  # Max 25% chance of False Allow
            entropy = self.core.get_entropy_tick()

            # P_error is high when E_t is low
            p_error = max_error_prob * (1 - entropy)

            # Check if the error occurs
            if self.core.get_binary_result(p_error) == 1:
                firewall_decision = 1  # FALSE ALLOW (Firewall Failure)

        return firewall_decision, threat_state  # Returns Decision and the threat state for logging


class ProbabilisticAnomalyGate(EntropyLogicGate):
    """
    Simulates an IDS that generates a probabilistic anomaly score and a
    binary Alert decision modulated by system entropy.
    """

    def execute(self, packet_size_dev: int, time_delta_dev: int, source_ip_entropy: int):

        # 1. Base Anomaly Score Calculation
        # Inputs are 1 (Suspicious) or 0 (Normal). Max base score is 3.0.
        raw_score = packet_size_dev + time_delta_dev + source_ip_entropy
        base_anomaly_prob = raw_score / 3.0  # Base probability [0.0 to 1.0]

        # 2. Entropy Modulation
        entropy = self.core.get_entropy_tick()

        # Entropy effect: Low entropy (E_t < 0.5) tends to amplify the score slightly,
        # modeling over-alerting due to system instability.
        entropy_mod = (0.5 - entropy) * 0.1  # Max +/- 5% modulation

        final_anomaly_score = np.clip(base_anomaly_prob + entropy_mod, 0.0, 1.0)

        # 3. Probabilistic Alert Decision
        # Decision is NOT a simple threshold cut, but a probabilistic chance based on the score level.
        threshold = 0.6

        if final_anomaly_score > threshold:
            # High Suspicion: High chance of alerting (80%)
            prob_alert = 0.8
        else:
            # Low Suspicion: Low chance of alerting (20%)
            prob_alert = 0.2

        # The final alert is determined probabilistically (this is where FP/FN happen)
        alert_decision = self.core.get_binary_result(prob_alert)

        # Returns the continuous score and the final binary alert decision
        return final_anomaly_score, alert_decision


# --- 4. Program Execution Container ---

class EntropyProgram:
    """
    Represents a program to be run on the Entropy Computer.
    It's a sequence of instructions (gates) to be executed.
    """

    def __init__(self, instructions, initial_state):
        self.instructions = instructions
        self.initial_state = initial_state
        self.final_state = {}
        self.intermediate_steps = []

    def run(self):
        """
        Executes the program and records the state evolution.
        """
        current_state = self.initial_state.copy()
        self.intermediate_steps.append(("Initial State", current_state.copy()))

        for i, instruction in enumerate(self.instructions):
            gate = instruction['gate']
            inputs = [current_state[key] for key in instruction['inputs']]
            output_keys = instruction['outputs']

            # Execute the gate
            results = gate.execute(*inputs)

            # Handle single or multiple outputs
            if not isinstance(results, tuple):
                results = (results,)

            # Ensure the number of results matches the expected output keys
            if len(output_keys) != len(results):
                raise ValueError(
                    f"Gate {gate.__class__.__name__} returned {len(results)} outputs, but expected {len(output_keys)}")

            # Update state
            for key, value in zip(output_keys, results):
                # Ensure the value is cast to the correct type (int for binary states, float for scores)
                if isinstance(current_state.get(key), int) or key.endswith('_state') or key.endswith('_decision'):
                    current_state[key] = int(value)
                else:
                    current_state[key] = value

            self.intermediate_steps.append(
                (f"Step {i + 1}: {gate.__class__.__name__}", current_state.copy())
            )

        self.final_state = current_state
        return self.final_state