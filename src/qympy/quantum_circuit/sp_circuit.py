import sympy as sp
import qiskit
from . import sp_gate
from . import sp_func

class Circuit:
    def __init__(self, num_qubits):
        self.num_qubits     = num_qubits
        self.qiskit_circuit = qiskit.circuit.QuantumCircuit(num_qubits)
        self.initial_state  = sp.Matrix([1]+[0]*(2**num_qubits-1))
        self.final_state    = None
        self.gate_list      = []
        self.symbol_set    = set()
        # for quantum machine learning
        self.meas_mode  = None
        self.meas_basis = None
    def evolve_state(self):
        self.final_state = self.initial_state
        gate_flag, gate_buffer = False, [sp_func.identity(2) for _ in range(self.num_qubits)]
        for i in range(len(self.gate_list)):
            if self.gate_list[i].gate_type == "SingleQubitGate":
                gate_flag = True
                wire = self.gate_list[i].wire
                gate_buffer[wire] = self.gate_list[i].matrix * gate_buffer[wire]
                if i == len(self.gate_list)-1:
                    self.final_state = sp_func.kron(*gate_buffer) * self.final_state
            elif self.gate_list[i].gate_type == "TwoQubitGate":
                if gate_flag == True:
                    self.final_state = sp_func.kron(*gate_buffer) * self.final_state
                    gate_flag, gate_buffer = False, [sp_func.identity(2) for _ in range(self.num_qubits)]
                submatrix = self.gate_list[i].submatrix
                wire1, wire2 = self.gate_list[i].wire1, self.gate_list[i].wire2
                wire_min, wire_max = min(wire1, wire2), max(wire1, wire2)
                full_matrix = sp_func.kron(sp_func.identity(2**wire_min), submatrix, sp_func.identity(2**(self.num_qubits-wire_max-1)))
                self.final_state = full_matrix * self.final_state
            else:
                raise TypeError("Unknown gate type : {self.gate_list[i].gate_type}")
    def measure(self, qubit, basis):
        assert self.final_state != None, "Circuit should be evolved before measurement: try Circuit.evolve_state()"
        assert basis in ["X", "Y", "Z"], f"Basis should be X or Y or Z, not {basis}"
        basis_dict = {
            "X": sp.Matrix([[0,1],[1,0],]),
            "Y": sp.Matrix([[0,-sp.I],[sp.I,0],]),
            "Z": sp.Matrix([[1,0],[0,-1],]),
        }
        full_matrix = sp_func.kron(sp_func.identity(2**qubit), basis_dict[basis], sp_func.identity(2**(self.num_qubits-qubit-1)))
        return (sp_func.adjoint(self.final_state) * full_matrix * self.final_state)[0]
    def draw(self, *args, **kwargs):
        return self.qiskit_circuit.draw(*args, **kwargs)
    def _check_wire(self, wire):
        num_qubits = self.num_qubits
        if wire >= num_qubits:
            raise ValueError(f"Wire {wire} is not between 0 to {num_qubits-1} with only {num_qubits} qubit(s).")
    def __add__(self, other):
        assert self.num_qubits >= other.num_qubits, "Composing small circuit with big circuit is not allowed."
        new_circuit = Circuit(self.num_qubits)
        new_circuit.qiskit_circuit = self.qiskit_circuit.compose(other.qiskit_circuit)
        new_circuit.gate_list      = self.gate_list + other.gate_list
        new_circuit.symbol_set     = self.symbol_set.union(other.symbol_set)
        if self.meas_mode != None: new_circuit.meas_mode = self.meas_mode
        elif other.meas_mode != None: new_circuit.meas_mode = other.meas_mode
        if self.meas_basis != None: new_circuit.meas_basis = self.meas_basis
        elif other.meas_basis != None: new_circuit.meas_basis = other.meas_basis
        return new_circuit
    def __call__(self, x):
        subs = {}
        for i in range(len(x)):
            subs[sp.Symbol(f"inputs_{i}", real=True)] = x[i]
        self.evolve_state()
        self.final_state = self.final_state.evalf(subs=subs)
        meas_value = []
        if self.meas_mode == "measure_all":
            for basis in self.meas_basis:
                meas_value += [self.measure(q, basis) for q in range(self.num_qubits)]
        elif self.meas_mode == "measure_single":
            for basis in self.meas_basis:
                meas_value += [self.measure(0, basis)]
        return sp.Matrix(meas_value)
    def h(self, wire):
        self._check_wire(wire)
        self.qiskit_circuit.h(wire)
        self.gate_list.append(sp_gate.H(wire))
    def x(self, wire):
        self._check_wire(wire)
        self.qiskit_circuit.x(wire)
        self.gate_list.append(sp_gate.X(wire))
    def y(self, wire):
        self._check_wire(wire)
        self.qiskit_circuit.y(wire)
        self.gate_list.append(sp_gate.Y(wire))
    def z(self, wire):
        self._check_wire(wire)
        self.qiskit_circuit.z(wire)
        self.gate_list.append(sp_gate.Z(wire))
    def rx(self, theta, wire):
        self._check_wire(wire)
        if type(theta) == str:
            theta = sp.Symbol(theta)
        if type(theta) == sp.Symbol:
            self.qiskit_circuit.rx(qiskit.circuit.Parameter(theta.name), wire)
            self.symbol_set.add(theta)
        else:
            self.qiskit_circuit.rx(theta, wire)
        self.gate_list.append(sp_gate.RX(theta, wire))
    def ry(self, theta, wire):
        self._check_wire(wire)
        if type(theta) == str:
            theta = sp.Symbol(theta)
        if type(theta) == sp.Symbol:
            self.qiskit_circuit.ry(qiskit.circuit.Parameter(theta.name), wire)
            self.symbol_set.add(theta)
        else:
            self.qiskit_circuit.ry(theta, wire)
        self.gate_list.append(sp_gate.RY(theta, wire))
    def rz(self, theta, wire):
        self._check_wire(wire)
        if type(theta) == str:
            theta = sp.Symbol(theta)
        if type(theta) == sp.Symbol:
            self.qiskit_circuit.rz(qiskit.circuit.Parameter(theta.name), wire)
            self.symbol_set.add(theta)
        else:
            self.qiskit_circuit.rz(theta, wire)
        self.gate_list.append(sp_gate.RZ(theta, wire))
    def rxx(self, theta, wire1, wire2):
        self._check_wire(wire1)
        self._check_wire(wire2)
        if type(theta) == str:
            theta = sp.Symbol(theta)
        if type(theta) == sp.Symbol:
            self.qiskit_circuit.rxx(qiskit.circuit.Parameter(theta.name), wire1, wire2)
            self.symbol_set.add(theta)
        else:
            self.qiskit_circuit.rxx(theta, wire1, wire2)
        self.gate_list.append(sp_gate.RXX(theta, wire1, wire2))
    def ryy(self, theta, wire1, wire2):
        self._check_wire(wire1)
        self._check_wire(wire2)
        if type(theta) == str:
            theta = sp.Symbol(theta)
        if type(theta) == sp.Symbol:
            self.qiskit_circuit.ryy(qiskit.circuit.Parameter(theta.name), wire1, wire2)
            self.symbol_set.add(theta)
        else:
            self.qiskit_circuit.ryy(theta, wire1, wire2)
        self.gate_list.append(sp_gate.RYY(theta, wire1, wire2))
    def rzz(self, theta, wire1, wire2):
        self._check_wire(wire1)
        self._check_wire(wire2)
        if type(theta) == str:
            theta = sp.Symbol(theta)
        if type(theta) == sp.Symbol:
            self.qiskit_circuit.rzz(qiskit.circuit.Parameter(theta.name), wire1, wire2)
            self.symbol_set.add(theta)
        else:
            self.qiskit_circuit.rzz(theta, wire1, wire2)
        self.gate_list.append(sp_gate.RZZ(theta, wire1, wire2))
    def swap(self, wire1, wire2):
        self._check_wire(wire1)
        self._check_wire(wire2)
        self.qiskit_circuit.swap(wire1, wire2)
        self.gate_list.append(sp_gate.SWAP(wire1, wire2))
    def cx(self, wire1, wire2):
        self._check_wire(wire1)
        self._check_wire(wire2)
        self.qiskit_circuit.cx(wire1, wire2)
        self.gate_list.append(sp_gate.CX(wire1, wire2))
    def cz(self, wire1, wire2):
        self._check_wire(wire1)
        self._check_wire(wire2)
        self.qiskit_circuit.cz(wire1, wire2)
        self.gate_list.append(sp_gate.CZ(wire1, wire2))