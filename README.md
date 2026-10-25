# Boolean Expression Compiler Frontend & Backend

A compiler front end and backend supporting relational and logical operators: `>`, `<`, `==`, `!=`, `>=`, `<=`, `&&`, `||`, and `!`. Validates Boolean expressions, respects operator precedence, and visualizes lexical tokens, syntax validation status, and the Abstract Syntax Tree (AST).

---

## 🚀 Features

- **Lexical Analysis (Scanner)**:
  - Identifies numbers, identifiers, boolean literals (`true`/`false`), relational operators (`>`, `<`, `==`, `!=`, `>=`, `<=`), logical operators (`&&`, `||`, `!`), and parentheses (`(`, `)`).
  - Accurate token reporting with lexeme, token type, and source position.
  - Catches unexpected characters and raises descriptive `LexicalError`s.

- **Syntax Analysis & AST Generation (Parser)**:
  - Recursive-descent parser implementing operator precedence and associativity:
    1. Parentheses: `( ... )`
    2. Primary expressions: identifiers, numbers, booleans
    3. Relational operators: `>`, `<`, `==`, `!=`, `>=`, `<=`
    4. Logical NOT: `!` (unary, right-associative)
    5. Logical AND: `&&` (binary, left-associative)
    6. Logical OR: `||` (binary, left-associative)
  - Detailed syntax validation detecting missing operands, unmatched parentheses, and misplaced operators.

- **Backend (Flask Web Framework)**:
  - Lightweight Python backend built with Flask and Flask-CORS.
  - Serves the compiler frontend interface directly.
  - `POST /compile`: Analyzes boolean expressions and returns JSON with tokens, syntax status, and AST.
  - `GET /health`: Health-check endpoint.

- **Interactive Frontend**:
  - Expression playground with live compilation and example presets.
  - Displays token table (Lexeme & Token Type).
  - Visual syntax validation indicator (Valid / Invalid with error messages).
  - Formatted Abstract Syntax Tree (AST) output.

---

## 📁 Project Structure

```
Boolean-compiler-main/
│
├── app.py                  # Flask backend server & API routes
├── requirements.txt        # Python package dependencies
├── README.md               # Project documentation
│
├── frontend/               # User interface
│   ├── index.html          # Web application UI
│   ├── script.js           # Frontend client logic & API connection
│   └── style.css           # Styling
│
├── lexer/                  # Lexical analysis module
│   ├── __init__.py
│   └── lexer.py            # Tokenizer using regular expressions
│
├── parser/                 # Syntax analysis module
│   ├── __init__.py
│   ├── grammar.md          # Grammar definition and precedence specification
│   └── parser.py           # Recursive-descent parser & AST builder
│
└── tests/                  # Automated test suite
    └── test_compiler.py    # 17 comprehensive unit tests
```

---

## 🛠️ Installation & Setup

### 1. Prerequisites
- Python 3.8 or higher

### 2. Install Dependencies
Open a terminal in the project directory and install the requirements:
```bash
pip install -r requirements.txt
```

### 3. Run the Backend Server
```bash
python app.py
```
By default, the server starts on `http://127.0.0.1:5000`.

### 4. Open in Your Browser
Open your browser and navigate to:
```
http://127.0.0.1:5000
```
Or you can directly open `frontend/index.html` in your browser.

---

## 📡 API Reference

### `POST /compile`
Compiles and parses a Boolean expression.

**Request Body:**
```json
{
  "expression": "a > 10 && b < 20"
}
```

**Response (Success - 200 OK):**
```json
{
  "valid": true,
  "tokens": [
    {"lexeme": "a", "type": "IDENTIFIER", "position": 0},
    {"lexeme": ">", "type": "RELATIONAL_OPERATOR", "position": 2},
    {"lexeme": "10", "type": "NUMBER", "position": 4},
    {"lexeme": "&&", "type": "LOGICAL_OPERATOR", "position": 7},
    {"lexeme": "b", "type": "IDENTIFIER", "position": 10},
    {"lexeme": "<", "type": "RELATIONAL_OPERATOR", "position": 12},
    {"lexeme": "20", "type": "NUMBER", "position": 14}
  ],
  "ast": {
    "type": "binary",
    "operator": "&&",
    "left": {
      "type": "binary",
      "operator": ">",
      "left": { "type": "identifier", "value": "a" },
      "right": { "type": "number", "value": "10" }
    },
    "right": {
      "type": "binary",
      "operator": "<",
      "left": { "type": "identifier", "value": "b" },
      "right": { "type": "number", "value": "20" }
    }
  },
  "message": "Expression compiled and parsed successfully."
}
```

**Response (Syntax Error - 200 OK):**
```json
{
  "valid": false,
  "error": "Syntax Error: Expected an identifier, number, Boolean, or '(', found 'end of input'",
  "tokens": [
    {"lexeme": "a", "type": "IDENTIFIER", "position": 0},
    {"lexeme": ">", "type": "RELATIONAL_OPERATOR", "position": 2}
  ],
  "ast": null
}
```

---

## 🧪 Running Tests

To run the automated test suite:
```bash
python -m unittest discover -s tests -v
```
All 17 unit tests verify tokenization, operator precedence rules, syntax error detection, and Flask endpoints.
