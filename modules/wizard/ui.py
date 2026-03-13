"""
3-Pane Mission Control UI

Left:   Module navigation + agent list
Center: Chat with wizard (or any agent)
Right:  Live status panel (deployments, integrations, onboarding progress)

Returns HTML that's served from the / endpoint.
"""


def render_dashboard(platform_state: dict) -> str:
    """Render the 3-pane Mission Control UI."""

    modules = platform_state.get("modules", {})
    agents_by_module = platform_state.get("agents_by_module", {})
    integrations = platform_state.get("integrations", {})
    onboarding = platform_state.get("onboarding", {})
    total_agents = platform_state.get("total_agents", 0)
    has_key = platform_state.get("openrouter_configured", False)

    # Build module nav
    module_colors = {
        "foundation": "#3b82f6", "studio": "#8b5cf6", "brand": "#ec4899",
        "research": "#06b6d4", "strategy": "#f59e0b", "operations": "#22c55e",
        "client": "#f97316", "distribution": "#6366f1",
    }

    module_nav = ""
    for name, info in sorted(modules.items()):
        color = module_colors.get(name, "#71717a")
        agents = agents_by_module.get(name, [])
        agent_items = "".join(
            f'<div class="agent-item" data-agent="{a}" onclick="selectAgent(\'{a}\')">{a}</div>'
            for a in sorted(agents)
        )
        module_nav += f"""
        <div class="module-group">
            <div class="module-name" style="border-left-color:{color}" onclick="toggleModule(this)">
                <span class="dot" style="background:{color}"></span>
                {name.title()}
                <span class="badge">{len(agents)}</span>
            </div>
            <div class="agent-list">{agent_items}</div>
        </div>"""

    # Build onboarding steps
    steps = ["welcome", "platform_check", "integrations", "documents", "configuration", "testing", "complete"]
    onboarding_html = ""
    for step in steps:
        info = onboarding.get(step, {"status": "pending"})
        status = info.get("status", "pending")
        icon = {"complete": "✓", "in_progress": "◉", "skipped": "–"}.get(status, "○")
        cls = f"step-{status}"
        label = step.replace("_", " ").title()
        onboarding_html += f'<div class="onboarding-step {cls}"><span>{icon}</span> {label}</div>'

    # Build integration status
    int_html = ""
    if integrations:
        for name, info in integrations.items():
            status = info.get("status", "unknown")
            int_html += f'<div class="int-item"><span class="int-dot {"connected" if status == "configured" else ""}"></span>{name.replace("_"," ").title()}</div>'
    else:
        int_html = '<div class="int-empty">No integrations yet. Ask the wizard to connect Google, Slack, etc.</div>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SpokeStack — Mission Control</title>
<style>
:root {{
    --bg: #09090b; --bg2: #18181b; --bg3: #27272a;
    --border: #27272a; --text: #e4e4e7; --muted: #71717a;
    --accent: #3b82f6; --green: #22c55e; --yellow: #eab308; --red: #ef4444;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family: -apple-system, system-ui, 'Segoe UI', sans-serif; background:var(--bg); color:var(--text); height:100vh; overflow:hidden; }}

/* Layout */
.app {{ display:grid; grid-template-columns:240px 1fr 280px; height:100vh; }}

/* Left Panel — Modules & Agents */
.left {{ background:var(--bg2); border-right:1px solid var(--border); display:flex; flex-direction:column; }}
.left-header {{ padding:1rem; border-bottom:1px solid var(--border); }}
.left-header h2 {{ font-size:.85rem; font-weight:600; color:var(--muted); text-transform:uppercase; letter-spacing:.05em; }}
.left-scroll {{ flex:1; overflow-y:auto; padding:.5rem; }}
.module-group {{ margin-bottom:2px; }}
.module-name {{ display:flex; align-items:center; gap:.5rem; padding:.5rem .75rem; cursor:pointer; border-radius:6px; border-left:3px solid transparent; font-size:.85rem; font-weight:500; }}
.module-name:hover {{ background:var(--bg3); }}
.dot {{ width:6px; height:6px; border-radius:50%; flex-shrink:0; }}
.badge {{ margin-left:auto; font-size:.7rem; color:var(--muted); background:var(--bg3); padding:1px 6px; border-radius:8px; }}
.agent-list {{ display:none; padding-left:1.5rem; }}
.module-group.open .agent-list {{ display:block; }}
.agent-item {{ padding:4px .75rem; font-size:.8rem; color:var(--muted); cursor:pointer; border-radius:4px; }}
.agent-item:hover {{ background:var(--bg3); color:var(--text); }}
.agent-item.active {{ color:var(--accent); }}

/* Center Panel — Chat */
.center {{ display:flex; flex-direction:column; }}
.chat-header {{ padding:.75rem 1.25rem; border-bottom:1px solid var(--border); display:flex; align-items:center; gap:.75rem; }}
.chat-header h2 {{ font-size:.9rem; font-weight:600; }}
.chat-header .agent-badge {{ font-size:.7rem; color:var(--accent); background:var(--accent)15; padding:2px 8px; border-radius:8px; }}
.chat-messages {{ flex:1; overflow-y:auto; padding:1.25rem; display:flex; flex-direction:column; gap:1rem; }}
.msg {{ max-width:85%; padding:.75rem 1rem; border-radius:12px; font-size:.875rem; line-height:1.5; }}
.msg.assistant {{ background:var(--bg2); border:1px solid var(--border); align-self:flex-start; }}
.msg.user {{ background:var(--accent); color:white; align-self:flex-end; }}
.msg.system {{ background:var(--bg3); color:var(--muted); align-self:center; font-size:.8rem; text-align:center; }}
.chat-input {{ padding:1rem 1.25rem; border-top:1px solid var(--border); display:flex; gap:.5rem; }}
.chat-input input {{ flex:1; background:var(--bg2); border:1px solid var(--border); color:var(--text); padding:.625rem 1rem; border-radius:8px; font-size:.875rem; outline:none; }}
.chat-input input:focus {{ border-color:var(--accent); }}
.chat-input button {{ background:var(--accent); color:white; border:none; padding:.625rem 1.25rem; border-radius:8px; font-size:.85rem; cursor:pointer; font-weight:500; }}
.chat-input button:hover {{ opacity:.9; }}
.chat-input button:disabled {{ opacity:.5; cursor:not-allowed; }}
.typing {{ color:var(--muted); font-size:.8rem; padding:0 .5rem; }}

/* Right Panel — Status */
.right {{ background:var(--bg2); border-left:1px solid var(--border); display:flex; flex-direction:column; }}
.right-header {{ padding:1rem; border-bottom:1px solid var(--border); }}
.right-header h2 {{ font-size:.85rem; font-weight:600; color:var(--muted); text-transform:uppercase; letter-spacing:.05em; }}
.right-scroll {{ flex:1; overflow-y:auto; padding:.75rem; }}
.status-section {{ margin-bottom:1.25rem; }}
.status-section h3 {{ font-size:.8rem; color:var(--muted); margin-bottom:.5rem; padding:0 .5rem; }}
.status-card {{ background:var(--bg); border:1px solid var(--border); border-radius:8px; padding:.75rem; margin-bottom:.5rem; }}
.status-row {{ display:flex; justify-content:space-between; align-items:center; font-size:.8rem; }}
.status-row .label {{ color:var(--muted); }}
.status-row .value {{ font-weight:600; }}
.status-row .value.ok {{ color:var(--green); }}
.status-row .value.warn {{ color:var(--yellow); }}
.status-row .value.err {{ color:var(--red); }}
.onboarding-step {{ display:flex; align-items:center; gap:.5rem; padding:4px .75rem; font-size:.8rem; color:var(--muted); }}
.step-complete {{ color:var(--green); }}
.step-in_progress {{ color:var(--accent); }}
.int-item {{ display:flex; align-items:center; gap:.5rem; padding:4px .75rem; font-size:.8rem; }}
.int-dot {{ width:6px; height:6px; border-radius:50%; background:var(--muted); }}
.int-dot.connected {{ background:var(--green); }}
.int-empty {{ padding:.5rem .75rem; font-size:.78rem; color:var(--muted); }}

/* Scrollbar */
::-webkit-scrollbar {{ width:6px; }}
::-webkit-scrollbar-track {{ background:transparent; }}
::-webkit-scrollbar-thumb {{ background:var(--bg3); border-radius:3px; }}
</style>
</head>
<body>
<div class="app">
    <!-- LEFT: Modules & Agents -->
    <div class="left">
        <div class="left-header">
            <h2>Modules</h2>
        </div>
        <div class="left-scroll">
            <div class="module-group open">
                <div class="module-name" style="border-left-color:var(--accent)" onclick="toggleModule(this)">
                    <span class="dot" style="background:var(--accent)"></span>
                    Wizard
                    <span class="badge">concierge</span>
                </div>
                <div class="agent-list">
                    <div class="agent-item active" data-agent="wizard" onclick="selectAgent('wizard')">wizard</div>
                </div>
            </div>
            {module_nav}
        </div>
    </div>

    <!-- CENTER: Chat -->
    <div class="center">
        <div class="chat-header">
            <h2>Mission Control</h2>
            <span class="agent-badge" id="current-agent">wizard</span>
        </div>
        <div class="chat-messages" id="messages">
            <div class="msg system">Welcome to SpokeStack. The wizard will help you get set up.</div>
            <div class="msg assistant">Hey! I'm your SpokeStack setup wizard. I'll help you get everything running.

Let me check your platform status first — one moment...</div>
        </div>
        <div id="typing" class="typing" style="display:none">Wizard is thinking...</div>
        <div class="chat-input">
            <input type="text" id="input" placeholder="Ask the wizard anything..." onkeydown="if(event.key==='Enter')send()" autofocus />
            <button onclick="send()" id="send-btn">Send</button>
        </div>
    </div>

    <!-- RIGHT: Status -->
    <div class="right">
        <div class="right-header">
            <h2>Status</h2>
        </div>
        <div class="right-scroll">
            <div class="status-section">
                <h3>Platform</h3>
                <div class="status-card">
                    <div class="status-row"><span class="label">Agents</span><span class="value ok">{total_agents}</span></div>
                    <div class="status-row"><span class="label">Modules</span><span class="value ok">{len(modules)}</span></div>
                    <div class="status-row"><span class="label">OpenRouter</span><span class="value {'ok' if has_key else 'err'}">{'Connected' if has_key else 'No Key'}</span></div>
                </div>
            </div>
            <div class="status-section">
                <h3>Onboarding</h3>
                {onboarding_html}
            </div>
            <div class="status-section">
                <h3>Integrations</h3>
                {int_html}
            </div>
        </div>
    </div>
</div>

<script>
let currentAgent = 'wizard';
let conversationHistory = [];

function toggleModule(el) {{
    el.parentElement.classList.toggle('open');
}}

function selectAgent(name) {{
    document.querySelectorAll('.agent-item').forEach(e => e.classList.remove('active'));
    document.querySelector(`[data-agent="${{name}}"]`)?.classList.add('active');
    currentAgent = name;
    document.getElementById('current-agent').textContent = name;
    document.getElementById('input').placeholder = `Talk to ${{name}}...`;
}}

async function send() {{
    const input = document.getElementById('input');
    const msg = input.value.trim();
    if (!msg) return;

    input.value = '';
    addMessage('user', msg);

    const typing = document.getElementById('typing');
    const btn = document.getElementById('send-btn');
    typing.style.display = 'block';
    typing.textContent = `${{currentAgent}} is thinking...`;
    btn.disabled = true;

    try {{
        const resp = await fetch('/execute', {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{
                agent_type: currentAgent,
                task: msg,
                tenant_id: 'default',
                user_id: 'user',
                stream: false,
            }}),
        }});

        const data = await resp.json();

        if (resp.ok) {{
            addMessage('assistant', data.output || data.detail || 'No response');
        }} else {{
            addMessage('system', `Error: ${{data.detail || resp.statusText}}`);
        }}
    }} catch (e) {{
        addMessage('system', `Connection error: ${{e.message}}`);
    }}

    typing.style.display = 'none';
    btn.disabled = false;
    input.focus();
}}

function addMessage(role, text) {{
    const container = document.getElementById('messages');
    const div = document.createElement('div');
    div.className = `msg ${{role}}`;
    div.textContent = text;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}}

// Auto-check platform on load
setTimeout(async () => {{
    try {{
        const resp = await fetch('/health');
        const data = await resp.json();
        if (data.openrouter_configured) {{
            addMessage('assistant', `Platform is healthy! ${{data.agents}} agents loaded across ${{data.modules}} modules. OpenRouter is connected.\\n\\nWhat would you like to do?\\n• Connect integrations (Google, Slack, etc.)\\n• Upload documents (brand guides, briefs)\\n• Find the right agent for a task\\n• Just start using an agent`);
        }} else {{
            addMessage('assistant', `Platform is running with ${{data.agents}} agents, but OpenRouter isn't configured yet. Set your OPENROUTER_API_KEY environment variable to enable agent execution.\\n\\nGet a key at: https://openrouter.ai/keys`);
        }}
    }} catch(e) {{}}
}}, 500);
</script>
</body>
</html>"""
