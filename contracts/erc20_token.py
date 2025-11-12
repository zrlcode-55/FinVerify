"""
ERC-20 Token Contract (Simplified Python Model)
For verification experiments
"""


class ERC20Token:
    def __init__(self, initial_supply: int):
        self.total_supply = initial_supply
        self.balances = {}
        self.balances['owner'] = initial_supply

    def transfer(self, from_addr: str, to_addr: str, amount: int) -> bool:
        if self.balances.get(from_addr, 0) < amount:
            return False
        if amount <= 0:
            return False
        
        self.balances[from_addr] = self.balances.get(from_addr, 0) - amount
        self.balances[to_addr] = self.balances.get(to_addr, 0) + amount
        return True


    def mint(self, to_addr: str, amount: int) -> bool:
        # BUG: No authorization check!
        self.total_supply += amount
        self.balances[to_addr] = self.balances.get(to_addr, 0) + amount
        return True


    def burn(self, from_addr: str, amount: int) -> bool:
        if self.balances.get(from_addr, 0) < amount:
            return False
        
        self.balances[from_addr] -= amount
        self.total_supply -= amount
        return True

    def balance_of(self, addr: str) -> int:
        return self.balances.get(addr, 0)

