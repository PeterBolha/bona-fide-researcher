class Institution:
    def __init__(self, name: str, ror: str = None, isni: str = None) -> None:
        self.name = name
        # Research Organization Registry ID
        self.ror = ror
        # International Standard Name Identifier
        self.isni = isni

    def __str__(self) -> str:
        return f"Institution: {self.name} - identifiers: {self.ror} (ROR), {self.isni} (ISNI)"