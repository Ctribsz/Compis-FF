# 🎓 Calculadora de Conjuntos FIRST y FOLLOW

Este proyecto es una herramienta educativa desarrollada en Python que calcula los conjuntos **FIRST** y **FOLLOW** para una gramática libre de contexto (GLC). Es ideal para estudiantes de compiladores, teoría de lenguajes y análisis sintáctico.

---

## 📁 Estructura del Proyecto

```
Compis-FF/
│
├── gramatica.txt               # Archivo con la definición de la gramática (entrada)
├── FF.py                       # Código fuente principal
├── first_follow_output.txt     # Archivo generado con los conjuntos FIRST y FOLLOW
└── README.md                   # Este documento
```

---

## 📝 Formato del Archivo `gramatica.txt`

Cada línea representa una producción gramatical en el siguiente formato:

```
NoTerminal -> símbolo1 símbolo2 ... símboloN | alternativa1 | ...
```

- Se permite más de una alternativa por producción, separadas con `|`.
- El símbolo `ε` (epsilon) representa la cadena vacía.
- El primer símbolo no terminal leído será considerado como **símbolo inicial**.

### ✅ Ejemplo:

```txt
E -> T E'
E' -> + T E' | ε
T -> F T'
T' -> * F T' | ε
F -> ( E ) | id
```

---

## 🚀 Cómo Ejecutar

### Requisitos

- Python 3.6 o superior

### Desde la terminal o consola:

```bash
python3 FF.py
```
---

## ⚙️ Funcionalidades

- ✅ Lectura de gramática desde archivo
- ✅ Cálculo de conjuntos **FIRST** y **FOLLOW** para cada no terminal
- ✅ Impresión en consola de los resultados
- ✅ Exportación automática a archivo `first_follow_output.txt`

---

## 📌 Ejemplo de Salida

### En consola:

```
Gramática analizada: gramatica.txt
Símbolo inicial: E
No terminales: E, E', F, T, T'
Terminales: (, ), *, +, id

== Conjuntos FIRST ==
FIRST(E) = { (, id }
FIRST(E') = { +, ε }
FIRST(F) = { (, id }
FIRST(T) = { (, id }
FIRST(T') = { *, ε }

== Conjuntos FOLLOW ==
FOLLOW(E) = { $, ) }
FOLLOW(E') = { $, ) }
FOLLOW(F) = { $, ), *, + }
FOLLOW(T) = { $, ), + }
FOLLOW(T') = { $, ), + }

Resultados exportados a 'first_follow_output.txt'
```

### En el archivo `first_follow_output.txt` se guarda lo mismo.

---

## 🧠 Reglas Utilizadas

### Cálculo de FIRST:
1. Si el símbolo es un terminal, su FIRST es él mismo.
2. Si el símbolo es un no terminal:
   - Se agregan los FIRST de cada producción.
   - Si una producción deriva a `ε`, se incluye `ε`.
3. Si en una producción todos los símbolos pueden derivar en `ε`, se incluye `ε` en el FIRST.

### Cálculo de FOLLOW:
1. Al símbolo inicial se le agrega `$`.
2. Si después de un no terminal viene un símbolo, se agregan los FIRST del símbolo siguiente (sin `ε`).
3. Si al no terminal le sigue algo que puede derivar a `ε` o es el último símbolo, se agrega el FOLLOW del lado izquierdo.

---

## 🧪 Casos Soportados

- Gramáticas con múltiples alternativas por producción
- Producciones recursivas
- Derivaciones que incluyen `ε`
- Símbolo inicial implícito (el primero leído)

---

## 💾 Exportación

Los resultados de los conjuntos FIRST y FOLLOW se guardan automáticamente en:

```
first_follow_output.txt
```

Puedes abrirlo con cualquier editor de texto para revisión o entrega.

---

## 📌 Notas Técnicas

- Los terminales se detectan automáticamente como todos los símbolos que no son no terminales.
- El símbolo `ε` es tratado especialmente en el análisis.
- `$` se utiliza como marcador de fin de entrada (FOLLOW del símbolo inicial).
- El programa evita recursiones infinitas y errores comunes de gramática malformada.

---

## 👨‍💻 Autor

Desarrollado con fines académicos y educativos.

Andy Fernando 
Christian Echeverría 
Davis Roldan

> Si encontraste útil este proyecto o lo estás usando en tu curso de compiladores, ¡dale una estrella si lo subes a GitHub y compártelo con tus compañeros!

---

## 📃 Licencia

Este proyecto está disponible bajo la Licencia MIT. Puedes modificarlo, usarlo y distribuirlo libremente para fines educativos.

---
