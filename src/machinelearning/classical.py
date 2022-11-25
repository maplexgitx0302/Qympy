import sympy as sp

class Linear:
    def __init__(self, input_dim, output_dim, prefix="L"):
        self.input_dim  = input_dim
        self.output_dim = output_dim
        self.weights = [sp.Matrix(sp.symbols(f"{prefix}^{i+1}_0:{input_dim+1}", real=True)) for i in range(output_dim)]
    def __call__(self, x):
        assert len(x) == self.input_dim, f"input dimension not matched: Input={len(x)} | Expected={self.input_dim}"
        x = x.reshape(self.input_dim, 1)
        result = sp.zeros(self.output_dim, 1)
        for neuron in range(self.output_dim):
            weight = sp.Matrix(self.weights[neuron][1:])
            bias   = self.weights[neuron][0]
            result[neuron] += (weight.T * x)[0] + bias
        return result