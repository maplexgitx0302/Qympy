import sympy as sp

class Linear:
    def __init__(self, input_dim, output_dim, prefix="L"):
        self.input_dim  = input_dim
        self.output_dim = output_dim
        self.bias  = sp.Matrix([sp.symbols(f"{prefix}^{i+1}_0", real=True) for i in range(output_dim)])
        self.weight = sp.Matrix([sp.symbols(f"{prefix}^{i+1}_1:{input_dim+1}", real=True) for i in range(output_dim)])
    def __call__(self, x):
        assert len(x) == self.input_dim, f"input dimension not matched: Input={len(x)} | Expected={self.input_dim}"
        return self.weight * x + self.bias