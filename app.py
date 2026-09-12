"""
Mikey — private AI web interface.

This Flask app is a thin web UI over a local llama.cpp llama-server.

Expected llama.cpp endpoint:
    http://127.0.0.1:8080/v1/chat/completions

Run:
    python app.py

Then open:
    http://127.0.0.1:5000
"""

import os
import re
import requests
from flask import Flask, jsonify, request, Response

AI_NAME = os.getenv("AI_NAME", "Mikey")
WEB_PORT = int(os.getenv("WEB_PORT", "5000"))
LLAMA_URL = os.getenv(
    "LLAMA_URL",
    "http://127.0.0.1:8080",
)
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.8"))
TOP_P = float(os.getenv("TOP_P", "0.95"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2000"))

app = Flask(__name__)


def clean_response(text: str) -> str:
    """Remove model reasoning tags before showing the answer."""
    if not text:
        return ""
    text = re.sub(r"<think>[\s\S]*?</think>", "", text, flags=re.I)
    text = re.sub(r"<think>[\s\S]*$", "", text, flags=re.I)
    return text.strip()


HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__AI_NAME__</title>
<style>
html,body{
    margin:0;
    padding:0;
    width:100%;
    height:100%;
    background:#0c0c0c;
    color:#cccccc;
}
body{
    font-family:"Cascadia Mono","Cascadia Code",Consolas,
        "Lucida Console","Courier New",monospace;
    font-size:16px;
    font-weight:400;
    overflow:hidden;
}
#cmd{
    position:fixed;
    inset:0;
    padding:5px 6px;
    box-sizing:border-box;
    overflow-y:auto;
    overflow-x:hidden;
    background:#0c0c0c;
    color:#cccccc;
    white-space:pre-wrap;
    word-break:break-word;
    line-height:1.25;
}
.line{
    margin:0;
    padding:0;
    min-height:20px;
}
#inputLine{
    display:flex;
    width:100%;
    margin:0;
    padding:0;
    align-items:flex-start;
}
#prompt{
    flex:none;
    color:#cccccc;
    white-space:pre;
}
#input{
    flex:1;
    width:100%;
    min-width:0;
    margin:0;
    padding:0;
    border:0;
    outline:0;
    background:transparent;
    color:#cccccc;
    font-family:inherit;
    font-size:16px;
    font-weight:400;
    line-height:1.25;
    resize:none;
    overflow:hidden;
    caret-color:#cccccc;
}
#input::selection{
    background:#cccccc;
    color:#0c0c0c;
}
#cmd::-webkit-scrollbar{width:12px}
#cmd::-webkit-scrollbar-track{background:#0c0c0c}
#cmd::-webkit-scrollbar-thumb{background:#3f3f3f}
#cmd::-webkit-scrollbar-thumb:hover{background:#5a5a5a}
#cmd{
    scrollbar-color:#3f3f3f #0c0c0c;
}
</style>
</head>
<body>
<div id="cmd">
<div id="history"></div>
<div id="inputLine">
<span id="prompt">you&gt; </span><textarea id="input" rows="1"
    autocomplete="off" spellcheck="false" autofocus></textarea>
</div>
</div>

<script>
const NAME = "__AI_NAME__";
const cmd = document.getElementById("cmd");
const history = document.getElementById("history");
const input = document.getElementById("input");

let busy = false;

function scrollBottom(){
    cmd.scrollTop = cmd.scrollHeight;
}

function addLine(text){
    const el = document.createElement("div");
    el.className = "line";
    el.textContent = text;
    history.appendChild(el);
    scrollBottom();
    return el;
}

function clean(text){
    if(!text) return "";
    text = text.replace(/<think>[\s\S]*?<\/think>/gi, "");
    text = text.replace(/<think>[\s\S]*$/gi, "");
    return text.trim();
}

function resizeInput(){
    input.style.height = "20px";
    input.style.height = Math.min(input.scrollHeight, 180) + "px";
}

async function sendMessage(){
    if(busy) return;

    const message = input.value.trim();
    if(!message) return;

    busy = true;

    addLine("you> " + message);
    input.value = "";
    resizeInput();

    const thinking = addLine("mikey> ... Thinking");

    try{
        const response = await fetch("/chat", {
            method:"POST",
            headers:{"Content-Type":"application/json"},
            body:JSON.stringify({message})
        });

        const data = await response.json();
        thinking.remove();

        if(!response.ok || data.error){
            addLine("mikey> ERROR: " + (data.error || "Request failed."));
        }else{
            const answer = clean(data.response || "");
            const parts = answer.split("\n");

            if(parts.length === 0 || answer === ""){
                addLine("mikey>");
            }else{
                addLine("mikey> " + parts[0]);
                for(let i = 1; i < parts.length; i++){
                    addLine(parts[i]);
                }
            }
        }
    }catch(error){
        thinking.remove();
        addLine("mikey> ERROR: " + error.message);
    }

    busy = false;
    input.focus();
    scrollBottom();
}

input.addEventListener("input", resizeInput);

input.addEventListener("keydown", (event) => {
    if(event.key === "Enter" && !event.shiftKey){
        event.preventDefault();
        sendMessage();
    }
});

document.addEventListener("click", () => input.focus());

input.focus();
resizeInput();
scrollBottom();
</script>
</body>
</html>
"""


@app.get("/")
def home():
    return Response(
        HTML.replace("__AI_NAME__", AI_NAME),
        mimetype="text/html",
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )


@app.get("/health")
def health():
    return jsonify({
        "status": "ok",
        "service": AI_NAME,
        "llama_url": LLAMA_URL,
    })


@app.post("/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"error": "Empty message"}), 400

    payload = {
        "messages": [{"role": "user", "content": message}],
        "temperature": TEMPERATURE,
        "top_p": TOP_P,
        "max_tokens": MAX_TOKENS,
        "stream": False,
    }

    try:
        response = requests.post(
            f"{LLAMA_URL.rstrip('/')}/v1/chat/completions",
            json=payload,
            timeout=300,
        )
        response.raise_for_status()

        result = response.json()
        answer = (
            result.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )

        return jsonify({"response": clean_response(answer)})

    except requests.RequestException as exc:
        return jsonify({"error": f"llama-server request failed: {exc}"}), 502
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    print(f"{AI_NAME} — private AI")
    print(f"Web UI: http://127.0.0.1:{WEB_PORT}")
    print(f"llama-server: {LLAMA_URL}")
    app.run(
        host="0.0.0.0",
        port=WEB_PORT,
        debug=False,
        threaded=True,
        use_reloader=False,
    )
