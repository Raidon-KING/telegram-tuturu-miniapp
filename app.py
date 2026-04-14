from flask import Flask

app = Flask(__name__)


@app.route("/")
def index():
    return """
    <html>
        <head>
            <meta charset="utf-8">
            <title>Наш огонёк</title>
            <style>
                body {
                    font-family: sans-serif;
                    background: #0b1020;
                    color: #f5f5f5;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    height: 100vh;
                    margin: 0;
                }
                .fire {
                    font-size: 64px;
                    margin-bottom: 16px;
                }
            </style>
        </head>
        <body>
            <div class="fire">🔥</div>
            <div>Здесь будет расти ваш огонёк от общения ✨</div>
        </body>
    </html>
    """


if __name__ == "__main__":
    app.run(debug=True)