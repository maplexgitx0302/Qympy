import sympy as sp
import qiskit
import foundation.gate as gate
from foundation.functions import *

class Circuit:
    def __init__(self, num_qubits):
        self.num_qubits     = num_qubits
        self.qiskit_circuit = qiskit.circuit.QuantumCircuit(num_qubits)
        self.initial_state  = sp.Matrix([1]+[0]*(2**num_qubits-1))
        self.final_state    = None
        self.gate_list      = []
        self.symbol_list    = []
    def evolve_state(self):
        self.final_state = self.initial_state
        gate_flag, gate_buffer = False, [identity(2) for _ in range(self.num_qubits)]
        for i in range(len(self.gate_list)):
            if self.gate_list[i].gate_type == "SingleQubitGate":
                gate_flag = True
                wire = self.gate_list[i].wire
                gate_buffer[wire] = self.gate_list[i].matrix * gate_buffer[wire]
                if i == len(self.gate_list)-1:
                    self.final_state = kron(*gate_buffer) * self.final_state
            elif self.gate_list[i].gate_type == "TwoQubitGate":
                if gate_flag == True:
                    self.final_state = kron(*gate_buffer) * self.final_state
                    gate_flag, gate_buffer = False, [identity(2) for _ in range(self.num_qubits)]
                submatrix = self.gate_list[i].submatrix
                wire1, wire2 = self.gate_list[i].wire1, self.gate_list[i].wire2
                wire_min, wire_max = min(wire1, wire2), max(wire1, wire2)
                full_matrix = kron(identity(2**wire_min), submatrix, identity(2**(self.num_qubits-wire_max-1)))
                self.final_state = full_matrix * self.final_state
            else:
                raise TypeError("Unknown gate type : {self.gate_list[i].gate_type}")
    def measure(self, qubit, basis):
        assert self.final_state != None, "Circuit should be evolved before measurement: try Circuit.evolve_state()"
        assert basis in ["X", "Y", "Z"], "Basis should be X or Y or Z"
        basis_dict = {
            "X": sp.Matrix([[0,1],[1,0],]),
            "Y": sp.Matrix([[0,-sp.I],[sp.I,0],]),
            "Z": sp.Matrix([[1,0],[0,-1],]),
        }
        full_matrix = kron(identity(2**qubit), basis_dict[basis], identity(2**(self.num_qubits-qubit-1)))
        return adjoint(self.final_state) * full_matrix * self.final_state
    def _check_wire(self, wire):
        num_qubits = self.num_qubits
        if wire >= num_qubits:
            raise ValueError(f"Wire {wire} is not between 0 to {num_qubits-1} with only {num_qubits} qubit(s).")
    def h(self, wire):
        self._check_wire(wire)
        self.qiskit_circuit.h(wire)
        self.gate_list.append(gate.H(wire))
    def x(self, wire):
        self._check_wire(wire)
        self.qiskit_circuit.x(wire)
        self.gate_list.append(gate.X(wire))
    def y(self, wire):
        self._check_wire(wire)
        self.qiskit_circuit.y(wire)
        self.gate_list.append(gate.Y(wire))
    def z(self, wire):
        self._check_wire(wire)
        self.qiskit_circuit.z(wire)
        self.gate_list.append(gate.Z(wire))
    def rx(self, symbol_name, wire):
        self._check_wire(wire)
        self.qiskit_circuit.rx(qiskit.circuit.Parameter(symbol_name), wire)
        self.gate_list.append(gate.RX(symbol_name, wire))
        if symbol_name not in self.symbol_list:
            self.symbol_list.append(symbol_name)
    def ry(self, symbol_name, wire):
        self._check_wire(wire)
        self.qiskit_circuit.ry(qiskit.circuit.Parameter(symbol_name), wire)
        self.gate_list.append(gate.RY(symbol_name, wire))
        if symbol_name not in self.symbol_list:
            self.symbol_list.append(symbol_name)
    def rz(self, symbol_name, wire):
        self._check_wire(wire)
        self.qiskit_circuit.rz(qiskit.circuit.Parameter(symbol_name), wire)
        self.gate_list.append(gate.RZ(symbol_name, wire))
        if symbol_name not in self.symbol_list:
            self.symbol_list.append(symbol_name)
    def swap(self, wire1, wire2):
        self._check_wire(wire1)
        self._check_wire(wire2)
        self.qiskit_circuit.swap(wire1, wire2)
        self.gate_list.append(gate.SWAP(wire1, wire2))
    def cx(self, wire1, wire2):
        self._check_wire(wire1)
        self._check_wire(wire2)
        self.qiskit_circuit.cx(wire1, wire2)
        self.gate_list.append(gate.CX(wire1, wire2))
    def cz(self, wire1, wire2):
        self._check_wire(wire1)
        self._check_wire(wire2)
        self.qiskit_circuit.cz(wire1, wire2)
        self.gate_list.append(gate.CZ(wire1, wire2))