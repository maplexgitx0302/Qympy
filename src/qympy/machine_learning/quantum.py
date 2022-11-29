import sympy as sp
from itertools import product
from qympy.quantum_circuit.sp_circuit import Circuit

class AngleEncoding(Circuit):
    def __init__(self, num_qubits, rot_gate="ry"):
        super().__init__(num_qubits)
        for i in range(num_qubits):
            getattr(self, rot_gate)(f"inputs_{i}", i)
        self.qiskit_circuit.barrier()

class SingleRot(Circuit):
    def __init__(self, num_qubits, num_layers=1, prefix="T", 
                rot_mode=['rz', 'ry', 'rz'], ent_mode='cx'):
        super().__init__(num_qubits)
        for l in range(num_layers):
            for q in range(num_qubits):
                for r in range(len(rot_mode)):
                    getattr(self, rot_mode[r])(prefix + f"^{l}_{q},{r}", q)
            for q in range(num_qubits-1):
                getattr(self, ent_mode)(q, q+1)
            self.qiskit_circuit.barrier()

class Measurement():
    def __init__(self, qubits, bases):
        self.qubits = qubits
        self.bases  = bases
    def __call__(self, circuit):
        return sp.Matrix([circuit.measure(q, b) for q, b in product(self.qubits, self.bases)])