"""
Cross-Chain Bridge Contract (Simplified Python Model)

Note: this is a simplified model for verification purposes
      real implementation would need more error handling etc
"""


class BridgeChainA:  # source chain
    def __init__(self):
        self.locked = 0
        self.nonces = set()

    def lock(self, amount: int, nonce: int) -> bool:
        if amount <= 0:
            return False
        if nonce in self.nonces:
            return False  # Replay protection - important!!
        
        self.locked += amount
        self.nonces.add(nonce)  # remember we processed this
        return True


    def unlock(self, amount: int, nonce: int) -> bool:
        if amount <= 0 or amount > self.locked:
            return False
        if nonce in self.nonces:
            return False
        
        self.locked -= amount
        self.nonces.add(nonce)
        return True



class BridgeChainB:
    def __init__(self):
        self.minted = 0
        self.processed = set()


    def mint(self, amount: int, message_hash: str) -> bool:
        if amount <= 0:
            return False
        # BUG: Missing replay protection! 
        # TODO: should check if message_hash already processed
        # if message_hash in self.processed:
        #     return False
        
        self.minted += amount
        # self.processed.add(message_hash)  # Should do this! bug here
        return True

    def burn(self, amount: int) -> bool:
        if amount <= 0 or amount > self.minted:
            return False
        
        self.minted -= amount
        return True



class BuggyBridge:
    """Bridge without replay protection - for demonstrating bugs"""
    def __init__(self):
        self.chain_a = BridgeChainA()
        self.chain_b_locked = 0
        self.chain_b_minted = 0

    def lock_and_mint(self, amount: int):
        self.chain_b_locked += amount
        self.chain_b_minted += amount


    def mint_again(self, amount: int):
        # BUG: Can mint without lock!
        self.chain_b_minted += amount

