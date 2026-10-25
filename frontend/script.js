// Boolean Expression Compiler - Frontend JavaScript

// Change this URL if your team's Flask route is different.
const API_URL = "/compile";

const form = document.getElementById("compile-form");
const expressionInput = document.getElementById("expression");
const clearButton = document.getElementById("clear-btn");

const message = document.getElementById("message");
const tokensOutput = document.getElementById("tokens-output");
const syntaxOutput = document.getElementById("syntax-output");
const astOutput = document.getElementById("ast-output");

function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, character => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    }[character]));
}

function showMessage(text, type = "") {
    message.className = `message ${type}`.trim();
    message.textContent = text;
}

function resetResults() {
    tokensOutput.innerHTML =
        '<p class="placeholder">No tokens yet</p>';

    syntaxOutput.innerHTML =
        '<p class="placeholder">Waiting for analysis</p>';

    astOutput.textContent = "No tree generated";
    astOutput.className = "placeholder";
}

function displayTokens(tokens) {
    if (!Array.isArray(tokens) || tokens.length === 0) {
        tokensOutput.innerHTML =
            '<p class="placeholder">No token data returned</p>';
        return;
    }

    let html = `
        <table class="result-table">
            <thead>
                <tr>
                    <th>LEXEME</th>
                    <th>TOKEN TYPE</th>
                </tr>
            </thead>
            <tbody>
    `;

    tokens.forEach(token => {
        const lexeme = token.lexeme ?? token.value ?? "";
        const type = token.type ?? token.token_type ?? "TOKEN";

        html += `
            <tr>
                <td>${escapeHtml(lexeme)}</td>
                <td>${escapeHtml(type)}</td>
            </tr>
        `;
    });

    html += "</tbody></table>";
    tokensOutput.innerHTML = html;
}

function displaySyntax(data) {
    const valid = Boolean(
        data.valid ?? data.is_valid ?? data.success
    );

    const error = data.error ?? data.message ?? "";

    if (valid) {
        syntaxOutput.innerHTML = `
            <div class="syntax-valid">
                <strong>✓ Valid Expression</strong>
                ${error ? `<p>${escapeHtml(error)}</p>` : ""}
            </div>
        `;
    } else {
        syntaxOutput.innerHTML = `
            <div class="syntax-invalid">
                <strong>✕ Invalid Expression</strong>
                ${error ? `<p>${escapeHtml(error)}</p>` : ""}
            </div>
        `;
    }
}

function displayAST(ast) {
    if (ast === undefined || ast === null || ast === "") {
        astOutput.textContent = "No AST data returned";
        return;
    }

    astOutput.className = "";
    astOutput.textContent =
        typeof ast === "string"
            ? ast
            : JSON.stringify(ast, null, 2);
}

form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const expression = expressionInput.value.trim();

    if (!expression) {
        showMessage(
            "Please enter a Boolean expression before compiling.",
            "error"
        );
        expressionInput.focus();
        return;
    }

    resetResults();

    showMessage(
        "Sending expression to the compiler backend..."
    );

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                expression: expression
            })
        });

        if (!response.ok) {
            throw new Error(
                `Server returned status ${response.status}.`
            );
        }

        const data = await response.json();

        displayTokens(data.tokens ?? data.token_list);
        displaySyntax(data);
        displayAST(data.ast ?? data.parse_tree);

        showMessage(
            "Analysis completed. Results received from the backend.",
            "success"
        );

    } catch (error) {
        showMessage(
            "Could not connect to the compiler backend. " +
            "Make sure the Flask server is running and its POST /compile " +
            "route returns JSON. Details: " + error.message,
            "error"
        );
    }
});

// Fill the input box when an example is clicked.
document.querySelectorAll(".example-btn").forEach(button => {
    button.addEventListener("click", function () {
        expressionInput.value = this.dataset.expression;
        expressionInput.focus();
    });
});

// Clear the input and results.
clearButton.addEventListener("click", function () {
    expressionInput.value = "";
    resetResults();

    showMessage(
        "Enter an expression and connect the compiler backend to view results."
    );

    expressionInput.focus();
});
