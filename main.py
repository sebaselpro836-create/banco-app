from flask import Flask, render_template_string, request, redirect, session
import json, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "banco_secret"

ARCH_SALDO = "saldo.json"
ARCH_MOV = "mov.json"

USER = "guzman"
PIN = "2014"

# ---------------- ARCHIVOS ----------------
def load_saldo():
    if os.path.exists(ARCH_SALDO):
        with open(ARCH_SALDO) as f:
            return json.load(f).get("saldo", 0)
    return 0

def save_saldo(saldo):
    with open(ARCH_SALDO, "w") as f:
        json.dump({"saldo": saldo}, f)

def load_mov():
    if os.path.exists(ARCH_MOV):
        with open(ARCH_MOV) as f:
            return json.load(f)
    return []

def save_mov(tipo, monto, saldo):
    data = load_mov()
    data.append({
        "tipo": tipo,
        "monto": monto,
        "hora": datetime.now().strftime("%d/%m %H:%M"),
        "saldo": saldo
    })
    with open(ARCH_MOV, "w") as f:
        json.dump(data, f)

# ---------------- DISEÑO ----------------
base = """
<!DOCTYPE html>
<html>
<head>
<title>Banco App</title>
<style>
body {
    background: #0f172a;
    color: white;
    font-family: Arial;
    text-align: center;
}
.container {
    background: #1e293b;
    padding: 20px;
    margin: 40px auto;
    width: 350px;
    border-radius: 15px;
}
input {
    width: 90%;
    padding: 10px;
    margin: 10px;
    border-radius: 8px;
    border: none;
}
button {
    width: 95%;
    padding: 12px;
    margin: 8px;
    border: none;
    border-radius: 10px;
    font-size: 16px;
}
.green { background: #22c55e; }
.red { background: #ef4444; }
.blue { background: #3b82f6; }
.yellow { background: #eab308; }
</style>
</head>
<body>
<div class="container">
{{ content | safe }}
</div>
</body>
</html>
"""

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET","POST"])
def login():
    msg = ""
    if request.method == "POST":
        if request.form["user"] == USER and request.form["pin"] == PIN:
            session["login"] = True
            return redirect("/menu")
        else:
            msg = "Datos incorrectos"

    contenido = f"""
    <h2>INICIAR SESIÓN</h2>
    <form method="POST">
        <input name="user" placeholder="Usuario"><br>
        <input name="pin" type="password" placeholder="PIN"><br>
        <button class="green">Entrar</button>
    </form>
    <p>{msg}</p>
    """

    return render_template_string(base, content=contenido)

# ---------------- MENU ----------------
@app.route("/menu")
def menu():
    if not session.get("login"):
        return redirect("/")

    saldo = load_saldo()

    contenido = f"""
    <h2>BANCO</h2>
    <h1>${saldo}</h1>

    <a href="/depositar"><button class="green">Depositar</button></a>
    <a href="/retirar"><button class="red">Retirar</button></a>
    <a href="/tareas"><button class="blue">Tareas</button></a>
    <a href="/historial"><button class="yellow">Historial</button></a>
    <a href="/logout"><button>Salir</button></a>
    """

    return render_template_string(base, content=contenido)

# ---------------- DEPOSITAR ----------------
@app.route("/depositar", methods=["GET","POST"])
def depositar():
    saldo = load_saldo()
    msg = ""

    if request.method == "POST":
        try:
            m = float(request.form["monto"])
            if m > 0:
                saldo += m
                save_saldo(saldo)
                save_mov("Depósito", m, saldo)
                return redirect("/menu")
        except:
            msg = "Error"

    contenido = f"""
    <h2>Depositar</h2>
    <form method="POST">
        <input name="monto" placeholder="Monto">
        <button class="green">Confirmar</button>
    </form>
    <p>{msg}</p>
    <a href="/menu"><button>Volver</button></a>
    """

    return render_template_string(base, content=contenido)

# ---------------- RETIRAR ----------------
@app.route("/retirar", methods=["GET","POST"])
def retirar():
    saldo = load_saldo()
    msg = ""

    if request.method == "POST":
        try:
            m = float(request.form["monto"])
            if 0 < m <= saldo:
                saldo -= m
                save_saldo(saldo)
                save_mov("Retiro", m, saldo)
                return redirect("/menu")
            else:
                msg = "Monto inválido"
        except:
            msg = "Error"

    contenido = f"""
    <h2>Retirar</h2>
    <form method="POST">
        <input name="monto" placeholder="Monto">
        <button class="red">Confirmar</button>
    </form>
    <p>{msg}</p>
    <a href="/menu"><button>Volver</button></a>
    """

    return render_template_string(base, content=contenido)

# ---------------- TAREAS ----------------
@app.route("/tareas", methods=["GET","POST"])
def tareas():
    saldo = load_saldo()

    tareas = [
        ("Ayudar en casa", 200),
        ("Lavar platos", 500),
        ("Buen examen", 3000)
    ]

    if request.method == "POST":
        total = 0
        for i, (_, val) in enumerate(tareas):
            if request.form.get(f"t{i}"):
                total += val

        if total > 0:
            saldo += total
            save_saldo(saldo)
            save_mov("Recompensas", total, saldo)

        return redirect("/menu")

    checkboxes = ""
    for i, (t, val) in enumerate(tareas):
        checkboxes += f"""
        <label>
        <input type="checkbox" name="t{i}">
        {t} (+${val})
        </label><br>
        """

    contenido = f"""
    <h2>Tareas</h2>
    <form method="POST">
        {checkboxes}
        <button class="green">Confirmar</button>
    </form>
    <a href="/menu"><button>Volver</button></a>
    """

    return render_template_string(base, content=contenido)

# ---------------- HISTORIAL ----------------
@app.route("/historial")
def historial():
    data = reversed(load_mov())

    lista = ""
    for m in data:
        lista += f"<p>{m['hora']} | {m['tipo']} | ${m['monto']}</p>"

    contenido = f"""
    <h2>Historial</h2>
    {lista}
    <a href="/menu"><button>Volver</button></a>
    """

    return render_template_string(base, content=contenido)

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------------- RUN ----------------
if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
