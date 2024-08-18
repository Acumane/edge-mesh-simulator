import numpy as num
from bin import core, calc

class Tracer:
    DIM = 3
    def __init__(self, vertices, triangles):
        self.core = core.Tracer(vertices, triangles)

    def trace(self, a, b):
        if not self.core: return None
        
        a, b = num.asarray(a, dtype=num.float32), num.asarray(b, dtype=num.float32)
        assert b.shape[0] == self.DIM and a.shape[0] == self.DIM
        return self.core.trace(a, b)

    @staticmethod
    def getLoss(a, b, results, freq=2.4e9, permittivity=5.31):
        if not results: return None

        losses = {"total_dB": None, "signals": []}
        total = 0

        for kind, *pos in results:
            match kind:
                case 1:
                    loss_dB, delay = calc.directLoss(a, b, freq)
                case 2:
                    edges = [list(e) for e in pos[0]]
                    loss_dB, delay = calc.diffractLoss(a, b, edges, freq)
                case 3:
                    loss_dB, delay = calc.reflectLoss(a, b, list(pos[0]), freq, permittivity)
                case _: return None
            
            losses["signals"].append([loss_dB, delay])
            total += 10 ** (-loss_dB / 10)

        losses["total_dB"] = -10 * num.log10(total)
        return losses
