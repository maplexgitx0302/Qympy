import sympy as sp
from qympy.quantum_circuit.sp_circuit import Circuit

class Measurement(Circuit):
    def __init__(self, num_qubits, meas_mode, meas_basis):
        super().__init__(num_qubits)
        self.meas_mode = meas_mode
        self.meas_basis = meas_basis

class AngleEncoding(Circuit):
    def __init__(self, num_qubits, rot_gate="ry"):
        super().__init__(num_qubits)
        for i in range(num_qubits):
            getattr(self, rot_gate)(sp.Symbol(f"inputs_{i}", real=True), i)

class SingleRot(Circuit):
    def __init__(self, num_qubits, num_layers=1, prefix="T", 
                rot_mode=['rz', 'ry', 'rz'], ent_mode='cx'):
        super().__init__(num_qubits)
        for l in range(num_layers):
            for q in range(num_qubits):
                for r in range(len(rot_mode)):
                    theta = sp.Symbol(prefix + f"^{l}_{q},{r}", real=True)
                    getattr(self, rot_mode[r])(theta, q)
            for q in range(num_qubits-1):
                getattr(self, ent_mode)(q, q+1)
            self.qiskit_circuit.barrier()