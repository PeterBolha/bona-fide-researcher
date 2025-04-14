class Institution:
    def __init__(self, name: str, ror: str = None, isni: str = None) -> None:
        self.name = name
        # Research Organization Registry ID
        self.ror = ror
        # International Standard Name Identifier
        self.isni = isni

    def __eq__(self, other: "Institution") -> bool:
        if self.ror and other.ror:
            return self.ror == other.ror
        elif self.isni and other.isni:
            return self.isni == other.isni
        else:
            return self.name == other.name

    def __hash__(self) -> int:
        if self.ror:
            return hash(self.ror)
        elif self.isni:
            return hash(self.isni)
        else:
            return hash(self.name)

    def __str__(self) -> str:
        return f"Institution: {self.name} - identifiers: {self.ror} (ROR), {self.isni} (ISNI)"