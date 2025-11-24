import os
import json
import random
import uuid
import datetime
import traceback
import re
from flask import Flask, render_template_string, request, jsonify, session
import google.generativeai as genai

# --- FLASK APP CONFIGURATION ---
app = Flask(__name__)
app.secret_key = os.urandom(24)

# GLOBAL STORAGE
active_simulations = {}
CHAOS_ENABLED = False

# --- HTML TEMPLATE ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PROJECT MIRAGE | Next-Gen Chaos Engine</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: {
                        sans: ['Inter', 'sans-serif'],
                        mono: ['JetBrains Mono', 'monospace'],
                    },
                    colors: {
                        glass: "rgba(255, 255, 255, 0.05)",
                        glassBorder: "rgba(255, 255, 255, 0.1)",
                        neonGreen: "#39ff14",
                        neonRed: "#ff073a",
                    },
                    animation: {
                        'blob': 'blob 7s infinite',
                    },
                    keyframes: {
                        blob: {
                            '0%': { transform: 'translate(0px, 0px) scale(1)' },
                            '33%': { transform: 'translate(30px, -50px) scale(1.1)' },
                            '66%': { transform: 'translate(-20px, 20px) scale(0.9)' },
                            '100%': { transform: 'translate(0px, 0px) scale(1)' },
                        }
                    }
                }
            }
        }
    </script>
    <style>
        body {
            background-color: #050505;
            color: #e2e8f0;
            overflow-x: hidden;
        }
        .glass-panel {
            background: rgba(20, 20, 25, 0.7);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }
        .input-glass {
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: #a5d6ff;
        }
        .input-glass:focus {
            border-color: #39ff14;
            box-shadow: 0 0 15px rgba(57, 255, 20, 0.2);
            outline: none;
        }
        .btn-neon {
            background: linear-gradient(45deg, #1a472a, #2ea043);
            border: 1px solid #3fb950;
            box-shadow: 0 0 10px rgba(63, 185, 80, 0.3);
            transition: all 0.3s ease;
        }
        .btn-neon:hover {
            box-shadow: 0 0 20px rgba(63, 185, 80, 0.6);
            transform: translateY(-1px);
        }
        /* Toggle Switch */
        .toggle-checkbox:checked {
            right: 0;
            border-color: #39ff14;
        }
        .toggle-checkbox:checked + .toggle-label {
            background-color: #39ff14;
        }
        
        /* Background Blobs */
        .blob-bg {
            position: absolute;
            filter: blur(80px);
            z-index: -1;
            opacity: 0.4;
        }
    </style>
</head>
<body class="min-h-screen flex flex-col items-center p-6 relative">

    <!-- Background Effects -->
    <div class="blob-bg bg-purple-900 w-96 h-96 rounded-full top-0 left-0 animate-blob"></div>
    <div class="blob-bg bg-blue-900 w-96 h-96 rounded-full bottom-0 right-0 animate-blob animation-delay-2000"></div>
    <div class="blob-bg bg-green-900 w-80 h-80 rounded-full top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 animate-blob animation-delay-4000"></div>

    <header class="w-full max-w-6xl mb-10 flex justify-between items-end border-b border-white/10 pb-4">
        <div>
            <h1 class="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-blue-500 tracking-tighter">PROJECT MIRAGE</h1>
            <p class="text-gray-400 mt-1 font-mono text-sm tracking-widest">AI-POWERED CHAOS SIMULATION ENGINE // v3.0</p>
        </div>
        <div class="flex items-center gap-2 text-xs font-mono text-gray-500">
            <span class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
            SYSTEM ONLINE
        </div>
    </header>

    <main class="w-full max-w-6xl grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        <!-- LEFT: CONFIGURATION (7 Cols) -->
        <div class="lg:col-span-7 space-y-6">
            
            <!-- API Key Section -->
            <div class="glass-panel p-6 rounded-xl">
                <div class="flex justify-between items-center mb-4">
                    <h2 class="text-lg font-semibold text-white flex items-center gap-2">
                        <svg class="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11.536 9.636a1.003 1.003 0 00-.707-.293h-2.414a1 1 0 01-.707-.293l-1.414-1.414a1 1 0 010-1.414l1.414-1.414a1.003 1.003 0 01.707-.293h3.172a1 1 0 00.707-.293l.828-.828A1 1 0 0115 7z"></path></svg>
                        ACCESS CREDENTIALS
                    </h2>
                    <span class="text-xs text-gray-500 border border-gray-700 px-2 py-1 rounded">SECURE</span>
                </div>
                <input type="password" id="apiKey" class="w-full input-glass rounded-lg p-4 text-white font-mono text-sm transition" placeholder="Enter Gemini API Key..." value="">
            </div>

            <!-- Schema Editor -->
            <div class="glass-panel p-6 rounded-xl flex flex-col h-[500px]">
                <div class="flex justify-between items-center mb-4">
                    <h2 class="text-lg font-semibold text-white flex items-center gap-2">
                        <svg class="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"></path></svg>
                        TARGET SCHEMA
                    </h2>
                    <div class="flex gap-2">
                        <button class="text-xs bg-white/5 hover:bg-white/10 px-3 py-1 rounded transition">Load Sample</button>
                        <button class="text-xs bg-white/5 hover:bg-white/10 px-3 py-1 rounded transition">Clear</button>
                    </div>
                </div>
                <textarea id="jsonInput" class="flex-1 w-full input-glass rounded-lg p-4 text-sm text-blue-300 font-mono resize-none" spellcheck="false">
{
    "user_id": "usr_8821",
    "username": "GhostInShell",
    "account_balance": 4500.50,
    "is_verified": true,
    "last_login": "2025-11-20T14:00:00Z",
    "roles": ["admin", "editor"]
}</textarea>
                
                <button onclick="deployMirage()" id="deployBtn" class="w-full mt-6 btn-neon text-white font-bold py-4 rounded-lg tracking-widest flex justify-center items-center gap-3 group">
                    <svg class="w-5 h-5 group-hover:rotate-90 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.384-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"></path></svg>
                    INITIALIZE SHADOW NODE
                </button>
            </div>
        </div>

        <!-- RIGHT: MONITORING (5 Cols) -->
        <div class="lg:col-span-5 space-y-6">
            
            <!-- System Logs -->
            <div class="glass-panel p-6 rounded-xl h-[300px] flex flex-col">
                <h2 class="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                    SYSTEM LOGS
                </h2>
                <div id="consoleOutput" class="flex-1 bg-black/40 rounded-lg p-4 font-mono text-xs overflow-y-auto text-gray-300 border border-white/5">
                    <div class="text-green-500">>> System Initialized.</div>
                    <div class="text-gray-500">>> Waiting for schema input...</div>
                </div>
            </div>

            <!-- Live Test Panel -->
            <div class="glass-panel p-6 rounded-xl relative overflow-hidden">
                <div class="absolute top-0 right-0 p-4">
                    <div class="flex items-center gap-2">
                        <span class="text-xs font-bold text-gray-400">CHAOS MODE</span>
                        <div class="relative inline-block w-10 mr-2 align-middle select-none transition duration-200 ease-in">
                            <input type="checkbox" name="toggle" id="chaosToggle" class="toggle-checkbox absolute block w-5 h-5 rounded-full bg-white border-4 appearance-none cursor-pointer"/>
                            <label for="chaosToggle" class="toggle-label block overflow-hidden h-5 rounded-full bg-gray-700 cursor-pointer"></label>
                        </div>
                    </div>
                </div>

                <h2 class="text-lg font-semibold text-white mb-6 flex items-center gap-2">
                    <svg class="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                    LIVE TEST ZONE
                </h2>

                <div class="flex gap-2 mb-4">
                    <button onclick="testEndpoint()" class="flex-1 bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 rounded-lg transition shadow-lg shadow-blue-900/20">
                        GET /api/mirage
                    </button>
                    <a href="/api/mirage" target="_blank" class="px-4 py-3 bg-white/10 hover:bg-white/20 text-white rounded-lg flex items-center transition">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>
                    </a>
                </div>

                <div class="bg-black/60 p-4 rounded-lg border border-white/10 h-48 overflow-auto">
                    <pre id="apiResponse" class="text-xs text-green-400 font-mono">Waiting for request...</pre>
                </div>
            </div>

        </div>
    </main>

    <script>
        function log(msg, type='info') {
            const consoleEl = document.getElementById('consoleOutput');
            const div = document.createElement('div');
            div.className = type === 'error' ? 'text-red-500 mt-1' : 'text-gray-300 mt-1';
            div.innerText = '>> ' + msg;
            consoleEl.appendChild(div);
            consoleEl.scrollTop = consoleEl.scrollHeight;
        }

        async function deployMirage() {
            const apiKey = document.getElementById('apiKey').value;
            const jsonSchema = document.getElementById('jsonInput').value;
            const btn = document.getElementById('deployBtn');

            if (!apiKey) { log("ERROR: API Key missing.", 'error'); return; }

            const originalText = btn.innerHTML;
            btn.innerHTML = '<span class="animate-spin">⚙️</span> PROCESSING...';
            btn.disabled = true;
            log("Sending schema to Neural Engine...");

            try {
                const response = await fetch('/deploy', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ api_key: apiKey, schema: jsonSchema })
                });
                const data = await response.json();

                if (data.success) {
                    log("SUCCESS: Logic compiled.");
                    log("Shadow Node active.");
                } else {
                    log("FAILURE: " + data.error, 'error');
                }
            } catch (err) {
                log("NETWORK ERROR: " + err.message, 'error');
            } finally {
                btn.innerHTML = 'RE-INITIALIZE';
                btn.disabled = false;
            }
        }

        async function testEndpoint() {
            const resEl = document.getElementById('apiResponse');
            const chaos = document.getElementById('chaosToggle').checked;
            resEl.innerText = "Fetching...";
            resEl.style.color = "#a5d6ff";
            
            // Sync chaos state
            try {
                await fetch('/api/chaos', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ enabled: chaos })
                });
            } catch(e) { console.log("Chaos sync failed"); }

            try {
                const start = Date.now();
                const response = await fetch('/api/mirage');
                const text = await response.text();
                const duration = Date.now() - start;
                
                if (response.status === 500) {
                    resEl.style.color = "#ff073a";
                    resEl.innerText = `HTTP 500 (Chaos Mode) - ${duration}ms\n${text}`;
                } else {
                    resEl.style.color = "#39ff14";
                    try { resEl.innerText = JSON.stringify(JSON.parse(text), null, 2); } 
                    catch(e) { resEl.innerText = text; }
                }
            } catch (err) { resEl.innerText = "Network Error"; }
        }
    </script>
</body>
</html>
"""

# --- AI LOGIC CLEANER ---
def clean_ai_code(raw_text):
    """
    Strictly extracts Python code from AI response.
    Removes Markdown, explanations, and whitespace.
    """
    # 1. Extract code inside ```python ... ``` or ``` ... ```
    code_match = re.search(r'```(?:python)?(.*?)```', raw_text, re.DOTALL)
    if code_match:
        code = code_match.group(1)
    else:
        code = raw_text

    # 2. Remove lines that aren't code (basic heuristic)
    lines = code.splitlines()
    clean_lines = []
    for line in lines:
        # Remove lines that look like conversational filler (e.g., "Here is the code")
        stripped = line.strip()
        if stripped.lower().startswith("here is") or stripped.lower().startswith("i have generated"):
            continue
        clean_lines.append(line)
    
    return "\n".join(clean_lines).strip()

def get_ai_logic(api_key, schema_str):
    genai.configure(api_key=api_key)
    
    # Tries to find a valid model automatically
    model_name = 'gemini-1.5-flash-latest'
    try:
        # Simple model fallback logic
        found_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if found_models:
             # Prefer flash, else take first available
            flash_models = [m for m in found_models if 'flash' in m]
            model_name = flash_models[0] if flash_models else found_models[0]
    except:
        pass # Fallback to hardcoded string

    model = genai.GenerativeModel(model_name)
    
    prompt = f"""
    You are a code generation engine. 
    Input Schema: {schema_str}
    
    Task: Write the BODY of a Python function that generates a dictionary called `data` matching the schema with random values.
    
    Constraints:
    1. Do NOT write 'def function_name():'.
    2. Do NOT write markdown.
    3. ONLY write the code inside the function.
    4. Use 'random' and 'datetime' libraries.
    5. Final line MUST be 'return data'.
    """
    
    try:
        response = model.generate_content(prompt)
        return clean_ai_code(response.text)
    except Exception as e:
        return f"# Error: {str(e)}"

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/deploy', methods=['POST'])
def deploy():
    data_in = request.json
    api_key = data_in.get('api_key')
    schema = data_in.get('schema')
    
    if not api_key: return jsonify({"success": False, "error": "API Key Missing"})

    # 1. Get Clean Code
    code_body = get_ai_logic(api_key, schema)
    
    # 2. Construct Function
    # We wrap the AI's code inside a real function definition
    full_code = "def dynamic_generator():\n"
    full_code += "    import random, datetime, uuid\n"
    # Indent every line of the AI's body by 4 spaces
    for line in code_body.splitlines():
        full_code += f"    {line}\n"

    # 3. Compile
    try:
        local_ns = {}
        # We print the code to console for debugging if it fails
        print("--- COMPILING AI CODE ---")
        print(full_code)
        print("-------------------------")
        
        exec(full_code, {}, local_ns)
        active_simulations['default'] = local_ns['dynamic_generator']
        return jsonify({"success": True})
    except Exception as e:
        print(f"COMPILATION ERROR: {e}")
        return jsonify({"success": False, "error": f"Syntax Error: {e}"})

@app.route('/api/chaos', methods=['POST'])
def toggle_chaos():
    global CHAOS_ENABLED
    data = request.json
    CHAOS_ENABLED = data.get('enabled', False)
    return jsonify({"success": True, "chaos": CHAOS_ENABLED})

@app.route('/api/mirage')
def mock_api():
    # Chaos Mode
    # Chaos Mode
    if CHAOS_ENABLED and random.random() < 0.5:
        return jsonify({"error": "🔥 CHAOS MODE: 500 Server Error Simulated"}), 500
    
    func = active_simulations.get('default')
    if not func: return jsonify({"error": "Not Deployed"}), 404
    
    try:
        return jsonify(func())
    except Exception as e:
        return jsonify({"error": f"Runtime Error: {str(e)}"}), 500

if __name__ == '__main__':
    print("🔮 Project Mirage v2.1 Running on http://localhost:5000")
    app.run(debug=True, port=5000)