import sys
from collections import defaultdict

class FirstFollowCalculator:
    """
    Clase para calcular los conjuntos FIRST y FOLLOW de una gramática libre de contexto.
    
    Atributos:
        grammar (defaultdict): Diccionario que mapea no terminales a sus producciones.
        first_sets (dict): Conjuntos FIRST para cada símbolo de la gramática.
        follow_sets (defaultdict): Conjuntos FOLLOW para cada no terminal.
        non_terminals (set): Conjunto de símbolos no terminales de la gramática.
        terminals (set): Conjunto de símbolos terminales de la gramática.
        EPSILON (str): Constante que representa la cadena vacía (ε).
        END_MARKER (str): Símbolo especial ($) para marcar el fin de entrada.
        start_symbol (str): Símbolo inicial de la gramática.
    """
    
    def __init__(self):
        """Inicializa el calculador con estructuras de datos vacías."""
        self.grammar = defaultdict(list)
        self.first_sets = {}
        self.follow_sets = defaultdict(set)
        self.non_terminals = set()
        self.terminals = set()
        self.EPSILON = "ε"
        self.END_MARKER = "$"
        self.start_symbol = None

    def parse_grammar(self, filename):
        """
        Analiza una gramática desde un archivo de texto y carga sus producciones.
        
        El formato esperado es:
            NonTerminal -> produccion1 | produccion2 | ...
        Donde cada producción es una secuencia de símbolos separados por espacios.
        """
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                for line_num, line in enumerate(file, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    if '->' not in line:
                        print(f"Error de sintaxis línea {line_num}: Falta '->'")
                        continue
                    
                    lhs, productions = line.split('->', 1)
                    lhs = lhs.strip()
                    
                    if not lhs:
                        print(f"Error línea {line_num}: Lado izquierdo vacío")
                        continue
                    
                    if line_num == 1 and not self.start_symbol:
                        self.start_symbol = lhs
                    
                    self.non_terminals.add(lhs)
                    
                    for prod in productions.split('|'):
                        symbols = [s for s in prod.split() if s]
                        if symbols:
                            self.grammar[lhs].append(symbols)
            
            self._identify_terminals()
            
            if not self.start_symbol and self.non_terminals:
                self.start_symbol = next(iter(self.non_terminals))
            
        except FileNotFoundError:
            print(f"Error: No se pudo abrir el archivo '{filename}'")
            sys.exit(1)

    def _identify_terminals(self):
        """Identifica automáticamente los símbolos terminales de la gramática."""
        all_symbols = set()
        for productions in self.grammar.values():
            for prod in productions:
                all_symbols.update(prod)
        
        self.terminals = {sym for sym in all_symbols 
                         if sym not in self.non_terminals and sym != self.EPSILON}

    def compute_first(self, symbol):
        """
        Calcula el conjunto FIRST para un símbolo usando memoización.
        
        FIRST(símbolo) es el conjunto de terminales que pueden aparecer al inicio
        de cualquier cadena derivada del símbolo.
        """
        if symbol in self.first_sets:
            return self.first_sets[symbol].copy()
        
        result = set()
        
        if symbol in self.terminals or symbol == self.EPSILON:
            result.add(symbol)
            self.first_sets[symbol] = result
            return result.copy()
            
        if symbol not in self.grammar:
            print(f"Advertencia: Símbolo '{symbol}' no definido en la gramática")
            return result.copy()
            
        for production in self.grammar[symbol]:
            if not production:
                result.add(self.EPSILON)
                continue
                
            all_derive_epsilon = True
            for sym in production:
                if sym == symbol:
                    break
                    
                first_of_sym = self.compute_first(sym)
                result.update(first_of_sym - {self.EPSILON})
                
                if self.EPSILON not in first_of_sym:
                    all_derive_epsilon = False
                    break
                    
            if all_derive_epsilon:
                result.add(self.EPSILON)
                
        self.first_sets[symbol] = result
        return result.copy()
        
    def first_of_sequence(self, sequence, start=0):
        """Calcula el conjunto FIRST para una secuencia de símbolos."""
        result = set()
        all_derive_epsilon = True
        
        for i in range(start, len(sequence)):
            sym = sequence[i]
            first_of_sym = self.compute_first(sym)
            
            result.update(first_of_sym - {self.EPSILON})
            
            if self.EPSILON not in first_of_sym:
                all_derive_epsilon = False
                break
                
        if all_derive_epsilon:
            result.add(self.EPSILON)
            
        return result

    def compute_follow(self):
        """Calcula los conjuntos FOLLOW para todos los no terminales."""
        self.follow_sets[self.start_symbol].add(self.END_MARKER)
        
        changed = True
        iteration = 0
        max_iterations = 100
        
        while changed and iteration < max_iterations:
            changed = False
            iteration += 1
            
            for lhs, productions in self.grammar.items():
                for prod in productions:
                    for i, symbol in enumerate(prod):
                        if symbol not in self.non_terminals:
                            continue
                            
                        if i + 1 < len(prod):
                            first_beta = self.first_of_sequence(prod, i + 1)
                            
                            old_size = len(self.follow_sets[symbol])
                            self.follow_sets[symbol].update(first_beta - {self.EPSILON})
                            
                            if self.EPSILON in first_beta:
                                self.follow_sets[symbol].update(self.follow_sets[lhs])
                            
                            if len(self.follow_sets[symbol]) > old_size:
                                changed = True
                        else:
                            old_size = len(self.follow_sets[symbol])
                            self.follow_sets[symbol].update(self.follow_sets[lhs])
                            if len(self.follow_sets[symbol]) > old_size:
                                changed = True
        
        if iteration == max_iterations:
            print("Advertencia: El cálculo de FOLLOW alcanzó el máximo de iteraciones")

    def calculate_all(self):
        """Calcula todos los conjuntos FIRST y FOLLOW de la gramática."""
        for nt in self.non_terminals:
            self.compute_first(nt)
            
        self.compute_follow()
        
    def print_first_sets(self):
        """Imprime los conjuntos FIRST de forma legible."""
        print("\n== Conjuntos FIRST ==")
        for nt in sorted(self.non_terminals):
            firsts = self.first_sets.get(nt, set())
            print(f"FIRST({nt}) = {{ {', '.join(sorted(firsts))} }}")
            
    def print_follow_sets(self):
        """Imprime los conjuntos FOLLOW de forma legible."""
        print("\n== Conjuntos FOLLOW ==")
        for nt in sorted(self.non_terminals):
            follows = self.follow_sets.get(nt, set())
            print(f"FOLLOW({nt}) = {{ {', '.join(sorted(follows))} }}")
            
    def export_first_follow_sets(self, filename):
        """Exporta los conjuntos FIRST y FOLLOW a un archivo."""
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                file.write("== Conjuntos FIRST ==\n")
                for nt in sorted(self.non_terminals):
                    firsts = self.first_sets.get(nt, set())
                    file.write(f"FIRST({nt}) = {{ {', '.join(sorted(firsts))} }}\n")
                    
                file.write("\n== Conjuntos FOLLOW ==\n")
                for nt in sorted(self.non_terminals):
                    follows = self.follow_sets.get(nt, set())
                    file.write(f"FOLLOW({nt}) = {{ {', '.join(sorted(follows))} }}\n")
                    
            print(f"\nResultados exportados a '{filename}'")
            
        except IOError:
            print(f"Error: No se pudo escribir en el archivo '{filename}'")

def main():
    """
    Función principal que ejecuta el cálculo de FIRST y FOLLOW.
    Siempre lee el archivo 'gramatica.txt' en el mismo directorio.
    """
    # Archivo fijo que siempre se leerá
    grammar_file = "gramatica.txt"
    
    calculator = FirstFollowCalculator()
    calculator.parse_grammar(grammar_file)
    calculator.calculate_all()
    
    print(f"\nGramática analizada: {grammar_file}")
    print(f"Símbolo inicial: {calculator.start_symbol}")
    print(f"No terminales: {', '.join(sorted(calculator.non_terminals))}")
    print(f"Terminales: {', '.join(sorted(calculator.terminals))}")
    
    calculator.print_first_sets()
    calculator.print_follow_sets()
    calculator.export_first_follow_sets("first_follow_output.txt")

if __name__ == "__main__":
    main()