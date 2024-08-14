from dotenv import dotenv_values as loadenv

config = loadenv(".env")
WIDTH = int(config.get("WIDTH") or 150)
DEPTH = int(config.get("DEPTH") or 200)
TICKS = int(config.get("TICKS") or 50)
MQ_LOGS = bool(config.get("MQ_LOGS") or False)
COMM = config.get("COMM") or "BLE"
MQ_URI = config.get("MQ_URI") or "localhost"
NODES = int(config.get("NODES") or 30)
