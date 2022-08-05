import sympy as sp
from circuit.circuit import Circuit

class SingleRot(Circuit):
    def __init__(self, num_qubits, num_layers, prefix="theta", 
                 rot_mode=['rz', 'ry', 'rz'], ent_mode='cx'):
        super().__init__(num_qubits)
        for l in range(num_layers):
            for q in range(num_qubits):
                for r in range(len(rot_mode)):
                    symbol_name = prefix + f"{l}{q}{r}"
                    getattr(self, rot_mode[r])(symbol_name, q)
            for q in range(num_qubits-1):
                getattr(self, ent_mode)(q, q+1)
            self.qiskit_circuit.barrier()