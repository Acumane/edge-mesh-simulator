from mtracer import tracer as Tracer
from mwindow import MurtWindow as Window
from time import time
from attrs import define, Factory as new

"""
MIT License

Copyright (c) 2021 Supawat Tamsri

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
"""

SCENE = "poznan.obj"

@define
class Timer:
    _start: float = new(time)
    def __str__(self):
        return f"{time() - self._start:.4f}s"

my_tracer = Tracer(SCENE)
tx_pos = [0, 15, 0]  # Set transmitting position
rx_pos = [-30, 1.5, 45]  # Set receiving position

timer = Timer()
result = my_tracer.trace(tx_pos, rx_pos)
# [(2, [(-19.24, 8.56, 28.86)]),
#  (3, (-28.94, 4.22, 62.39)),
#  (3, (-70.80, 7.04, 15.22))]
print(f"[{timer}] Tracing complete")

tx_freq = 2.4e9  # 2.4 GHz
permittivity = 5.3  # Concrete
losses = my_tracer.get_total_loss(tx_pos, rx_pos, result, tx_freq, permittivity)
# {'total_dB': 84.3, 'signals': [[95.50, 1.86e-07], [86.63, 2.91e-07], [89.27, 4.12e-07]]}
print(f"[{timer}] Found losses")

vis = Window()
vis.load_scene(name="scene_name", file_path = SCENE)

# convert results to visualised paths
vis.lines_set += Tracer.result_to_lines(result, tx_pos, rx_pos)

vis.run()
