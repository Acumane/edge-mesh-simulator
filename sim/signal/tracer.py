import numpy as np
from bin import core, calc

DIM = 3
class Tracer:
    def __init__(self, scene_path=None):
        if scene_path is not None:
            vertices, triangles = read(scene_path)  # noqa: F821
            self.core = core.Tracer(vertices, triangles)
        else:
            self.core = None

    def load_scene(self, vertices, triangles):
        if self.core is not None:
            del self.core
        self.core = core.Tracer(vertices, triangles)

    def trace(self, tx_pos, rx_pos):
        if self.core is None:
            return None
        tx_pos, rx_pos = np.array(tx_pos), np.array(rx_pos)
        assert rx_pos.shape[0] == DIM and tx_pos.shape[0] == DIM
        tx_pos, rx_pos = tx_pos.astype("float32"), rx_pos.astype("float32")
        return self.core.trace(tx_pos, rx_pos)

    @staticmethod
    def get_total_loss(tx_pos, rx_pos, results, tx_freq=2.4e9, permittivity=5.31):
        if results is None:
            return None

        losses = {"total_dB": None, "signals": []}
        total_linear = 0
        
        for result in results:
            if result[0] == 1:
                loss_dB, delay = calc.directLoss(tx_pos, rx_pos, tx_freq)
            elif result[0] == 2:
                edges = [list(i) for i in result[1]]
                loss_dB, delay = calc.diffractLoss(
                    tx_pos, rx_pos, edges, tx_freq)
            elif result[0] == 3:
                refPos = list(result[1])
                loss_dB, delay = calc.reflectLoss(tx_pos, rx_pos,
                                    refPos, tx_freq,
                                    permittivity)
            else:
                return None
            losses["signals"].append([loss_dB, delay])
            total_linear += np.power(10, -loss_dB/10)

        losses["total_dB"] = -10*np.log10(total_linear)
        return losses
