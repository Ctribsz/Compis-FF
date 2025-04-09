import sys
from collections import defaultdict

class FirstFollowCalculator:
    def __init__(self):
        self.grammar = defaultdict(list)  # No terminal -> lista de producciones (cada producción es una lista de símbolos)
        self.first_sets = {}              # Mapeo de símbolos a sus conjuntos FIRST
        self.follow_sets = defaultdict(set)  # Mapeo de no terminales a sus conjuntos FOLLOW
        self.non_terminals = set()        # Conjunto de símbolos no terminales
        self.terminals = set()            # Conjunto de símbolos terminales
        self.EPSILON = "ε"                # Símbolo para epsilon
        self.END_MARKER = "$"             # Marcador de fin de entrada
        self.start_symbol = None          # Símbolo inicial de la gramática

    def parse_grammar(self, filename):
        """Lee la gramática desde un archivo de texto."""
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                
            # Asumir que el primer símbolo es el inicial o permitir especificarlo
            first_line = True
                
            for line in lines:
                line = line.strip()
                if not line:  # Ignorar líneas vacías
                    continue
                    
                tokens = line.split()
                lhs = tokens[0]  # Lado izquierdo (no terminal)
                
                if first_line:
                    self.start_symbol = lhs
                    first_line = False
                    
                if tokens[1] != "->":
                    print(f"Error de sintaxis: se esperaba '->' en: {line}")
                    continue
                    
                self.non_terminals.add(lhs)
                
                # Procesar producciones (pueden contener alternativas con '|')
                current_production = []
                for token in tokens[2:]:
                    if token == "|":
                        if current_production:
                            self.grammar[lhs].append(current_production)
                            current_production = []
                    else:
                        current_production.append(token)
                        
                if current_production:  # Añadir la última producción
                    self.grammar[lhs].append(current_production)
            
            # Detectar terminales automáticamente
            all_symbols = set()
            for lhs, rules in self.grammar.items():
                for rule in rules:
                    for sym in rule:
                        all_symbols.add(sym)
                        
            self.terminals = {sym for sym in all_symbols 
                            if sym not in self.non_terminals and sym != self.EPSILON}
                
        except FileNotFoundError:
            print(f"Error: No se pudo abrir el archivo '{filename}'")
            sys.exit(1)
            
        # Si no se especificó un símbolo inicial, usar el primero disponible
        if not self.start_symbol and self.non_terminals:
            self.start_symbol = next(iter(self.non_terminals))
            
    def compute_first(self, symbol):
        """Calcula el conjunto FIRST para un símbolo dado."""
        if symbol in self.first_sets:
            return self.first_sets[symbol]
            
        result = set()
        
        # Caso 1: Si es terminal o epsilon, el conjunto FIRST es el símbolo mismo
        if symbol in self.terminals or symbol == self.EPSILON:
            result.add(symbol)
            self.first_sets[symbol] = result
            return result
            
        # Caso 2: Si es no terminal
        if symbol not in self.grammar:
            print(f"Error: Símbolo '{symbol}' no definido en la gramática")
            self.first_sets[symbol] = result
            return result
            
        # Para cada producción del no terminal
        for production in self.grammar[symbol]:
            # Si la producción está vacía (deriva a epsilon)
            if not production:
                result.add(self.EPSILON)
                continue
                
            add_epsilon = True
            
            # Para cada símbolo en la producción
            for sym in production:
                # Evitar recursión infinita
                if sym == symbol:
                    break
                    
                # Obtener el conjunto FIRST del símbolo actual
                first_of_sym = self.compute_first(sym)
                
                # Añadir todos los símbolos excepto epsilon
                for terminal in first_of_sym:
                    if terminal != self.EPSILON:
                        result.add(terminal)
                
                # Si el símbolo no puede derivar en epsilon, no seguir
                if self.EPSILON not in first_of_sym:
                    add_epsilon = False
                    break
            
            # Si todos los símbolos de la producción pueden derivar en epsilon
            if add_epsilon:
                result.add(self.EPSILON)
                
        self.first_sets[symbol] = result
        return result
        
    def first_of_sequence(self, sequence, start=0):
        """Calcula el conjunto FIRST para una secuencia de símbolos."""
        result = set()
        add_epsilon = True
        
        for i in range(start, len(sequence)):
            first_of_sym = self.compute_first(sequence[i])
            
            # Añadir todo menos epsilon
            for terminal in first_of_sym:
                if terminal != self.EPSILON:
                    result.add(terminal)
            
            # Si el símbolo no puede derivar a epsilon, no seguir
            if self.EPSILON not in first_of_sym:
                add_epsilon = False
                break
                
        if add_epsilon:
            result.add(self.EPSILON)
            
        return result
        
    def compute_follow(self):
        """Calcula los conjuntos FOLLOW para todos los no terminales."""
        # Regla 1: Añadir el marcador de fin al símbolo inicial
        self.follow_sets[self.start_symbol].add(self.END_MARKER)
        
        changed = True
        while changed:
            changed = False
            
            # Para cada producción en la gramática
            for lhs, productions in self.grammar.items():
                for prod in productions:
                    for i, symbol in enumerate(prod):
                        # Solo nos interesan los no terminales
                        if symbol not in self.non_terminals:
                            continue
                            
                        # Caso donde hay símbolos después del no terminal
                        if i + 1 < len(prod):
                            # Regla 2: First de lo que sigue menos epsilon
                            first_beta = self.first_of_sequence(prod, i + 1)
                            
                            old_size = len(self.follow_sets[symbol])
                            for t in first_beta:
                                if t != self.EPSILON:
                                    self.follow_sets[symbol].add(t)
                                    
                            # Si lo que sigue puede derivar a epsilon, aplicar Regla 3
                            if self.EPSILON in first_beta:
                                old_follow_size = len(self.follow_sets[symbol])
                                self.follow_sets[symbol].update(self.follow_sets[lhs])
                                if len(self.follow_sets[symbol]) > old_follow_size:
                                    changed = True
                                    
                            if len(self.follow_sets[symbol]) > old_size:
                                changed = True
                        else:
                            # Regla 3: Si es el último símbolo, añadir Follow del lado izquierdo
                            old_size = len(self.follow_sets[symbol])
                            self.follow_sets[symbol].update(self.follow_sets[lhs])
                            if len(self.follow_sets[symbol]) > old_size:
                                changed = True
                                
    def calculate_all(self):
        """Calcula todos los conjuntos FIRST y FOLLOW."""
        # Calcular FIRST para todos los no terminales
        for nt in self.non_terminals:
            self.compute_first(nt)
            
        # Calcular FOLLOW para todos los no terminales
        self.compute_follow()
        
    def print_first_sets(self):
        """Muestra los conjuntos FIRST."""
        print("\n== FIRST Sets ==")
        for nt in sorted(self.non_terminals):
            firsts = self.first_sets.get(nt, set())
            print(f"FIRST({nt}) = {{ {' '.join(sorted(firsts))} }}")
            
    def print_follow_sets(self):
        """Muestra los conjuntos FOLLOW."""
        print("\n== FOLLOW Sets ==")
        for nt in sorted(self.non_terminals):
            follows = self.follow_sets.get(nt, set())
            print(f"FOLLOW({nt}) = {{ {' '.join(sorted(follows))} }}")
            
    def export_first_follow_sets(self, filename):
        """Exporta los conjuntos FIRST y FOLLOW a un archivo."""
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                file.write("== FIRST Sets ==\n")
                for nt in sorted(self.non_terminals):
                    firsts = self.first_sets.get(nt, set())
                    file.write(f"FIRST({nt}) = {{ {' '.join(sorted(firsts))} }}\n")
                    
                file.write("\n== FOLLOW Sets ==\n")
                for nt in sorted(self.non_terminals):
                    follows = self.follow_sets.get(nt, set())
                    file.write(f"FOLLOW({nt}) = {{ {' '.join(sorted(follows))} }}\n")
                    
            print(f"\nConjuntos FIRST y FOLLOW exportados a '{filename}'")
            
        except IOError:
            print(f"Error: No se pudo escribir en el archivo '{filename}'")

def main():
    if len(sys.argv) > 1:
        grammar_file = sys.argv[1]
    else:
        grammar_file = "gramatica.txt"  # Archivo por defecto
        
    calculator = FirstFollowCalculator()
    calculator.parse_grammar(grammar_file)
    calculator.calculate_all()
    calculator.print_first_sets()
    calculator.print_follow_sets()
    calculator.export_first_follow_sets("first_follow_output.txt")

if __name__ == "__main__":
    main()
