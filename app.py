import os
import sys
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Ensure current directory is on sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from lexer.lexer import tokenize, LexicalError
from parser.parser import parse_tokens

FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
CORS(app)


@app.route("/")
def index():
    """Serve the frontend index.html page."""
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:filename>")
def static_files(filename):
    """Serve frontend static assets like CSS and JS files."""
    return send_from_directory(FRONTEND_DIR, filename)


@app.route("/compile", methods=["POST"])
def compile_expression():
    """
    Compiler backend endpoint.
    Receives JSON: {"expression": "..."}
    Returns tokens, syntax validation status, and AST.
    """
    data = request.get_json(silent=True) or {}
    expression = data.get("expression")

    if expression is None:
        return jsonify({
            "valid": False,
            "error": "No 'expression' field provided in request body.",
            "tokens": [],
            "ast": None
        }), 200

    expression = expression.strip()
    if not expression:
        return jsonify({
            "valid": False,
            "error": "Expression cannot be empty.",
            "tokens": [],
            "ast": None
        }), 200

    tokens = []
    # 1. Lexical Analysis
    try:
        tokens = tokenize(expression)
    except LexicalError as err:
        return jsonify({
            "valid": False,
            "error": f"Lexical Error: {str(err)}",
            "tokens": tokens,
            "ast": None
        }), 200
    except Exception as err:
        return jsonify({
            "valid": False,
            "error": f"Lexer Error: {str(err)}",
            "tokens": tokens,
            "ast": None
        }), 200

    # 2. Syntax Analysis & AST Generation
    try:
        ast = parse_tokens(tokens)
        return jsonify({
            "valid": True,
            "tokens": tokens,
            "ast": ast,
            "message": "Expression compiled and parsed successfully."
        }), 200
    except SyntaxError as err:
        return jsonify({
            "valid": False,
            "error": f"Syntax Error: {str(err)}",
            "tokens": tokens,
            "ast": None
        }), 200
    except Exception as err:
        return jsonify({
            "valid": False,
            "error": f"Parser Error: {str(err)}",
            "tokens": tokens,
            "ast": None
        }), 200


@app.route("/health", methods=["GET"])
def health():
    """Simple health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "Boolean Expression Compiler Backend",
        "version": "1.0.0"
    }), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"==================================================")
    print(f" Boolean Expression Compiler Backend is running! ")
    print(f" Web UI: http://127.0.0.1:{port}                 ")
    print(f" API:    http://127.0.0.1:{port}/compile         ")
    print(f"==================================================")
    app.run(host="0.0.0.0", port=port, debug=True)
