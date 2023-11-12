from app.blockchain_modules.UdocoinMiner import UdocoinMiner

MINER = UdocoinMiner(1)
MINER_THREAD = MINER.continuous_mining()