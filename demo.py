from flask import Flask, Response, request, jsonify, send_from_directory
import anthropic
import json
import os

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Bunch — Speed to Lead Demo</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: Arial, sans-serif; background: #F4F6F9; color: #1A1A1A; }

header {
  background: #1E3A5F; padding: 16px 40px;
  display: flex; align-items: center; justify-content: space-between;
}
header .logo { color: #fff; font-size: 18px; font-weight: 700; letter-spacing: 1px; }
header .logo span { color: #E8722E; }
header .tag { color: #A8BCCF; font-size: 12px; }

.container { max-width: 1140px; margin: 32px auto; padding: 0 24px; }

.intro {
  background: #1E3A5F; color: #fff;
  border-radius: 10px; padding: 22px 30px; margin-bottom: 28px;
}
.intro h1 { font-size: 20px; margin-bottom: 6px; }
.intro p { color: #A8BCCF; font-size: 13px; line-height: 1.6; max-width: 720px; }
.stat {
  display: inline-block;
  background: rgba(232,114,46,0.18); border: 1px solid #E8722E;
  color: #E8722E; font-size: 11px; font-weight: 700;
  border-radius: 4px; padding: 3px 10px; margin-top: 10px; letter-spacing: 0.5px;
}

.grid { display: grid; grid-template-columns: 380px 1fr; gap: 24px; }

.card {
  background: #fff; border-radius: 10px; padding: 26px;
  box-shadow: 0 2px 12px rgba(30,58,95,0.07);
}
.card-title {
  font-size: 11px; font-weight: 700; color: #1E3A5F;
  text-transform: uppercase; letter-spacing: 1px;
  margin-bottom: 20px; padding-bottom: 10px;
  border-bottom: 2px solid #E8722E;
  display: flex; align-items: center; gap: 8px;
}
.dot { width: 7px; height: 7px; background: #E8722E; border-radius: 50%; }

label {
  display: block; font-size: 11px; font-weight: 700; color: #888;
  text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 5px;
}
input, select {
  width: 100%; padding: 10px 12px;
  border: 1.5px solid #DDE3EB; border-radius: 6px;
  font-size: 13.5px; font-family: Arial, sans-serif;
  color: #1A1A1A; background: #FAFBFC; margin-bottom: 14px;
  transition: border-color 0.2s; -webkit-appearance: none;
}
input:focus, select:focus { outline: none; border-color: #1E3A5F; background: #fff; }

.api-hint { font-size: 11px; color: #999; margin-top: -10px; margin-bottom: 14px; }

.btn {
  width: 100%; padding: 13px;
  background: #E8722E; color: #fff; border: none;
  border-radius: 6px; font-size: 14px; font-weight: 700;
  cursor: pointer; transition: background 0.2s;
  display: flex; align-items: center; justify-content: center; gap: 8px;
}
.btn:hover { background: #D4621F; }
.btn:disabled { background: #B0BCC8; cursor: not-allowed; }
.btn.secondary {
  background: #fff; color: #1E3A5F;
  border: 1.5px solid #DDE3EB; font-size: 13px; margin-top: 10px;
}
.btn.secondary:hover { background: #F4F6F9; }

.spinner {
  width: 16px; height: 16px;
  border: 2px solid rgba(255,255,255,0.4); border-top-color: #fff;
  border-radius: 50%; animation: spin 0.7s linear infinite; display: none;
}
@keyframes spin { to { transform: rotate(360deg); } }

.error-msg {
  color: #D64545; font-size: 12px; padding: 10px 12px;
  background: #FFF0F0; border-radius: 6px; margin-top: 10px; display: none;
}

/* ── Right panel ───────────────────────── */
.right-panel { display: flex; flex-direction: column; }

/* Phase 0: empty */
.empty-state {
  flex: 1; display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  text-align: center; padding: 60px 20px; color: #B0BCC8;
}
.empty-state .icon { font-size: 42px; margin-bottom: 14px; }
.empty-state p { font-size: 13px; line-height: 1.7; }

/* Phase 1: conversation */
.chat-wrap { display: none; flex-direction: column; height: 100%; }

.chat-header {
  display: flex; align-items: center; justify-content: space-between;
  padding-bottom: 12px; margin-bottom: 0; border-bottom: 1px solid #EEF0F4;
}
.chat-header-left { display: flex; align-items: center; gap: 10px; }
.avatar {
  width: 36px; height: 36px; background: #1E3A5F;
  border-radius: 50%; display: flex; align-items: center; justify-content: center;
  color: #E8722E; font-weight: 700; font-size: 14px;
}
.chat-name { font-size: 13px; font-weight: 700; color: #1E3A5F; }
.chat-sub { font-size: 11px; color: #999; }

.online-dot {
  width: 8px; height: 8px; background: #27AE60;
  border-radius: 50%; animation: pulse 2s infinite;
}
@keyframes pulse {
  0%,100% { opacity: 1; } 50% { opacity: 0.4; }
}

/* WhatsApp chat area */
.chat-messages {
  flex: 1; overflow-y: auto; padding: 16px 0;
  display: flex; flex-direction: column; gap: 10px;
  min-height: 320px; max-height: 400px;
  background: #ECE5DD; border-radius: 8px; margin: 12px 0; padding: 16px;
}

.msg-row { display: flex; }
.msg-row.bill { justify-content: flex-start; }
.msg-row.lead { justify-content: flex-end; }

.bubble {
  max-width: 78%; padding: 10px 13px;
  font-size: 13.5px; line-height: 1.5; border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.1); position: relative;
}
.msg-row.bill .bubble {
  background: #fff; border-radius: 0 8px 8px 8px; color: #1A1A1A;
}
.msg-row.bill .bubble::before {
  content: ''; position: absolute; top: 0; left: -7px;
  border-width: 0 7px 7px 0; border-style: solid;
  border-color: transparent #fff transparent transparent;
}
.msg-row.lead .bubble {
  background: #DCF8C6; border-radius: 8px 0 8px 8px; color: #1A1A1A;
}
.msg-row.lead .bubble::after {
  content: ''; position: absolute; top: 0; right: -7px;
  border-width: 0 0 7px 7px; border-style: solid;
  border-color: transparent transparent transparent #DCF8C6;
}
.bubble .msg-time { font-size: 10px; color: #999; text-align: right; margin-top: 4px; }

.typing-indicator { display: none; align-items: center; gap: 4px; padding: 10px 13px; background: #fff; border-radius: 0 8px 8px 8px; width: fit-content; box-shadow: 0 1px 2px rgba(0,0,0,0.1); }
.typing-indicator span { width: 6px; height: 6px; background: #999; border-radius: 50%; animation: bounce 1.2s infinite; }
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce { 0%,60%,100% { transform: translateY(0); } 30% { transform: translateY(-5px); } }

/* Quick replies */
.quick-replies {
  display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 10px;
}
.qr-btn {
  padding: 6px 12px; background: #fff;
  border: 1.5px solid #DDE3EB; border-radius: 16px;
  font-size: 12px; color: #1E3A5F; cursor: pointer;
  transition: all 0.15s; white-space: nowrap;
}
.qr-btn:hover { background: #EDF1F5; border-color: #1E3A5F; }
.qr-label { font-size: 11px; color: #999; margin-bottom: 6px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }

/* Input row */
.chat-input-row { display: flex; gap: 8px; align-items: center; }
.chat-input {
  flex: 1; padding: 10px 14px;
  border: 1.5px solid #DDE3EB; border-radius: 20px;
  font-size: 13.5px; font-family: Arial, sans-serif;
  background: #FAFBFC; outline: none; margin-bottom: 0;
  transition: border-color 0.2s;
}
.chat-input:focus { border-color: #1E3A5F; background: #fff; }
.send-btn {
  width: 40px; height: 40px; background: #E8722E;
  border: none; border-radius: 50%; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: background 0.2s; flex-shrink: 0;
}
.send-btn:hover { background: #D4621F; }
.send-btn svg { width: 16px; height: 16px; fill: #fff; }
.send-btn:disabled { background: #CCC; cursor: not-allowed; }

/* Outcome banners */
.outcome { display: none; border-radius: 10px; padding: 20px 24px; margin-top: 14px; }
.outcome.converted {
  background: #F0FFF4; border: 1.5px solid #27AE60;
}
.outcome.handoff {
  background: #F0F4FF; border: 1.5px solid #1E3A5F;
}
.outcome-header {
  display: flex; align-items: center; gap: 10px; margin-bottom: 10px;
}
.outcome-icon { font-size: 22px; }
.outcome-title { font-size: 14px; font-weight: 700; }
.outcome.converted .outcome-title { color: #27AE60; }
.outcome.handoff .outcome-title { color: #1E3A5F; }
.outcome-body { font-size: 13px; color: #555; line-height: 1.6; }
.outcome-body strong { color: #1A1A1A; }

/* Brief card */
.brief-card {
  background: #fff; border-radius: 8px; padding: 14px 16px;
  margin-top: 12px; border-left: 3px solid #E8722E;
}
.brief-label {
  font-size: 10px; font-weight: 700; color: #E8722E;
  text-transform: uppercase; letter-spacing: 0.7px; margin-bottom: 8px;
}
.brief-row { font-size: 12.5px; color: #444; margin-bottom: 4px; line-height: 1.5; }
.brief-row strong { color: #1A1A1A; font-weight: 700; }

/* Flow diagram */
.flow { display: flex; align-items: center; gap: 0; margin: 12px 0 0 0; flex-wrap: wrap; }
.flow-step {
  font-size: 11px; font-weight: 700; color: #fff;
  background: #1E3A5F; border-radius: 4px; padding: 4px 10px; white-space: nowrap;
}
.flow-step.active { background: #E8722E; }
.flow-step.done { background: #27AE60; }
.flow-arrow { color: #B0BCC8; font-size: 14px; padding: 0 4px; }

@media (max-width: 840px) { .grid { grid-template-columns: 1fr; } }
</style>
</head>
<body>

<header>
  <div class="logo">BUNCH <span>|</span> Growth Demo</div>
  <div class="tag">Bucket 1 — Speed to Lead: End-to-End Flow</div>
</header>

<div class="container">
  <div class="intro">
    <h1>New Lead → AI Conversation → Converted or Routed</h1>
    <p>
      A lead submits their details through a partner form. Bill responds within 60 seconds,
      holds the conversation, and either converts them to self-serve checkout — or hands off
      to a human with a full brief. No cold calls. No wasted time.
    </p>
    <div class="flow">
      <div class="flow-step" id="step1">Lead submits form</div>
      <div class="flow-arrow">→</div>
      <div class="flow-step" id="step2">Bill messages in 60s</div>
      <div class="flow-arrow">→</div>
      <div class="flow-step" id="step3">Conversation</div>
      <div class="flow-arrow">→</div>
      <div class="flow-step" id="step4a">Converted</div>
      <div class="flow-arrow" style="color:#B0BCC8">or</div>
      <div class="flow-step" id="step4b">Human briefed</div>
    </div>
  </div>

  <div class="grid">

    <!-- LEFT: Form -->
    <div class="card">
      <div class="card-title"><span class="dot"></span>Lead Details</div>

      <label>First Name</label>
      <input type="text" id="name" value="James">

      <label>Postcode</label>
      <input type="text" id="postcode" value="E1 6RF">

      <label>Property Type</label>
      <select id="property_type">
        <option>1-bed flat</option>
        <option selected>2-bed flat</option>
        <option>3-bed flat</option>
        <option>2-bed house</option>
        <option>3-bed house</option>
        <option>4-bed house</option>
        <option>Studio flat</option>
        <option>HMO / shared house</option>
      </select>

      <label>Number of Occupants</label>
      <select id="occupants">
        <option>1 person</option>
        <option selected>2 people</option>
        <option>3 people</option>
        <option>4 people</option>
        <option>5+ people</option>
      </select>

      <label>Anthropic API Key</label>
      <input type="password" id="api_key" placeholder="sk-ant-...">
      <div class="api-hint">Not stored. Used only for this request.</div>

      <button class="btn" id="generateBtn" onclick="startConversation()">
        <div class="spinner" id="spinner"></div>
        <span id="btnText">Start Flow</span>
      </button>
      <button class="btn secondary" id="resetBtn" onclick="reset()" style="display:none">
        ↺ &nbsp;Reset with new lead
      </button>

      <div class="error-msg" id="errorMsg"></div>

      <div style="margin-top:20px; padding-top:16px; border-top:1px solid #EEF0F4;">
        <div class="card-title" style="margin-bottom:10px; border:none; padding:0;"><span class="dot"></span>What this shows</div>
        <div style="font-size:12px; color:#666; line-height:1.7;">
          <b style="color:#1E3A5F;">Bill</b> handles the full conversation — no human needed unless the lead explicitly asks for one, or gets stuck.<br><br>
          Use the <b style="color:#1E3A5F;">quick replies</b> to simulate a lead's responses, or type your own.
        </div>
      </div>
    </div>

    <!-- RIGHT: Chat -->
    <div class="card right-panel">
      <div class="card-title"><span class="dot"></span>Live Conversation</div>

      <!-- Empty state -->
      <div class="empty-state" id="emptyState">
        <div class="icon">💬</div>
        <p>Fill in the lead details and click <strong>Start Flow</strong>.<br>
        Bill's opening message appears here — exactly what lands<br>
        on the lead's phone within 60 seconds of form submission.</p>
      </div>

      <!-- Chat UI -->
      <div class="chat-wrap" id="chatWrap">
        <div class="chat-header">
          <div class="chat-header-left">
            <div class="avatar">B</div>
            <div>
              <div class="chat-name">Bill · Bunch</div>
              <div class="chat-sub">AI energy assistant</div>
            </div>
          </div>
          <div class="online-dot"></div>
        </div>

        <div class="chat-messages" id="chatMessages">
          <div class="msg-row bill" id="typingRow" style="display:none">
            <div class="typing-indicator" id="typingIndicator">
              <span></span><span></span><span></span>
            </div>
          </div>
        </div>

        <div id="quickRepliesWrap">
          <div class="qr-label">Quick replies — tap to send as the lead</div>
          <div class="quick-replies" id="quickReplies">
            <button class="qr-btn" onclick="sendQuickReply(this)">How long does it take?</button>
            <button class="qr-btn" onclick="sendQuickReply(this)">Is my data safe?</button>
            <button class="qr-btn" onclick="sendQuickReply(this)">How much will I actually save?</button>
            <button class="qr-btn" onclick="sendQuickReply(this)">Do I need my account number?</button>
            <button class="qr-btn" onclick="sendQuickReply(this)">Sounds good, how do I sign up?</button>
            <button class="qr-btn" onclick="sendQuickReply(this)">Can I speak to someone?</button>
          </div>
        </div>

        <div class="chat-input-row" id="chatInputRow">
          <input class="chat-input" id="chatInput" placeholder="Type a reply as James…" onkeydown="if(event.key==='Enter') sendMessage()">
          <button class="send-btn" id="sendBtn" onclick="sendMessage()">
            <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
          </button>
        </div>

        <!-- Outcome: Converted -->
        <div class="outcome converted" id="outcomeConverted">
          <div class="outcome-header">
            <div class="outcome-icon">✅</div>
            <div class="outcome-title">Converted — no human involved</div>
          </div>
          <div class="outcome-body">
            Bill guided the lead to self-serve checkout. <strong>Hello Bill handles the rest autonomously</strong> — switching, setting up direct debits, managing providers. The sales team never needed to pick up the phone.
          </div>
        </div>

        <!-- Outcome: Handoff -->
        <div class="outcome handoff" id="outcomeHandoff">
          <div class="outcome-header">
            <div class="outcome-icon">📋</div>
            <div class="outcome-title">Routing to human — brief ready</div>
          </div>
          <div class="outcome-body">
            The lead asked to speak to someone. Instead of a cold call, the agent gets <strong>a full brief</strong> — everything Bill learned in the conversation.
          </div>
          <div class="brief-card">
            <div class="brief-label">Agent Brief</div>
            <div id="briefContent"></div>
          </div>
        </div>

      </div>
    </div>

  </div>
</div>

<script>
let conversationHistory = [];
let leadData = {};
let flowEnded = false;

function now() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function addBubble(text, sender) {
  const messages = document.getElementById('chatMessages');
  const row = document.createElement('div');
  row.className = `msg-row ${sender}`;
  row.innerHTML = `<div class="bubble">${text.replace(/\n/g, '<br>')}<div class="msg-time">${now()}</div></div>`;
  messages.appendChild(row);
  messages.scrollTop = messages.scrollHeight;
}

function showTyping() {
  const row = document.getElementById('typingRow');
  row.style.display = 'flex';
  document.getElementById('typingIndicator').style.display = 'flex';
  const messages = document.getElementById('chatMessages');
  messages.appendChild(row);
  messages.scrollTop = messages.scrollHeight;
}

function hideTyping() {
  const row = document.getElementById('typingRow');
  row.style.display = 'none';
  document.getElementById('typingIndicator').style.display = 'none';
}

function setFlowStep(step) {
  ['step1','step2','step3','step4a','step4b'].forEach(id => {
    const el = document.getElementById(id);
    el.className = 'flow-step';
  });
  if (step === 'message')  { document.getElementById('step1').className = 'flow-step done'; document.getElementById('step2').className = 'flow-step active'; }
  if (step === 'chat')     { document.getElementById('step1').className = 'flow-step done'; document.getElementById('step2').className = 'flow-step done'; document.getElementById('step3').className = 'flow-step active'; }
  if (step === 'converted'){ ['step1','step2','step3'].forEach(id => document.getElementById(id).className = 'flow-step done'); document.getElementById('step4a').className = 'flow-step done'; }
  if (step === 'handoff')  { ['step1','step2','step3'].forEach(id => document.getElementById(id).className = 'flow-step done'); document.getElementById('step4b').className = 'flow-step done'; }
}

async function startConversation() {
  const name   = document.getElementById('name').value.trim();
  const post   = document.getElementById('postcode').value.trim();
  const prop   = document.getElementById('property_type').value;
  const occ    = document.getElementById('occupants').value;
  const apiKey = document.getElementById('api_key').value.trim();

  if (!name || !post) { showError('Enter a name and postcode.'); return; }
  if (!apiKey)         { showError('Enter your Anthropic API key.'); return; }

  leadData = { name, postcode: post, property_type: prop, occupants: occ, api_key: apiKey };
  conversationHistory = [];
  flowEnded = false;

  document.getElementById('errorMsg').style.display = 'none';
  document.getElementById('generateBtn').disabled = true;
  document.getElementById('spinner').style.display = 'block';
  document.getElementById('btnText').textContent = 'Sending...';

  document.getElementById('emptyState').style.display = 'none';
  document.getElementById('chatWrap').style.display = 'flex';
  document.getElementById('chatMessages').innerHTML = '';
  document.getElementById('outcomeConverted').style.display = 'none';
  document.getElementById('outcomeHandoff').style.display = 'none';

  setFlowStep('message');
  showTyping();

  try {
    const res  = await fetch('/generate', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(leadData) });
    const data = await res.json();
    hideTyping();

    if (data.error) { showError(data.error); resetBtn(); return; }

    conversationHistory.push({ role: 'assistant', content: data.message });
    addBubble(data.message, 'bill');
    setFlowStep('chat');
    enableInput();
  } catch(e) {
    hideTyping(); showError('Something went wrong.'); resetBtn();
  }

  document.getElementById('generateBtn').disabled = false;
  document.getElementById('spinner').style.display = 'none';
  document.getElementById('btnText').textContent = 'Start Flow';
  document.getElementById('resetBtn').style.display = 'block';
}

function enableInput() {
  document.getElementById('chatInput').disabled = false;
  document.getElementById('sendBtn').disabled = false;
  document.getElementById('chatInput').focus();
}

function disableInput() {
  document.getElementById('chatInput').disabled = true;
  document.getElementById('sendBtn').disabled = true;
}

async function sendMessage() {
  if (flowEnded) return;
  const input = document.getElementById('chatInput');
  const text  = input.value.trim();
  if (!text) return;

  input.value = '';
  addBubble(text, 'lead');
  conversationHistory.push({ role: 'user', content: text });
  disableInput();
  showTyping();

  try {
    const res  = await fetch('/chat', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ ...leadData, history: conversationHistory })
    });
    const data = await res.json();
    hideTyping();

    if (data.error) { showError(data.error); enableInput(); return; }

    conversationHistory.push({ role: 'assistant', content: data.message });
    addBubble(data.message, 'bill');

    if (data.action === 'converted') {
      flowEnded = true;
      setFlowStep('converted');
      document.getElementById('quickRepliesWrap').style.display = 'none';
      document.getElementById('chatInputRow').style.display = 'none';
      document.getElementById('outcomeConverted').style.display = 'block';
    } else if (data.action === 'handoff') {
      flowEnded = true;
      setFlowStep('handoff');
      document.getElementById('quickRepliesWrap').style.display = 'none';
      document.getElementById('chatInputRow').style.display = 'none';
      document.getElementById('outcomeHandoff').style.display = 'block';
      renderBrief(data.brief);
    } else {
      enableInput();
    }
  } catch(e) {
    hideTyping(); showError('Something went wrong.'); enableInput();
  }
}

function sendQuickReply(btn) {
  if (flowEnded) return;
  document.getElementById('chatInput').value = btn.textContent;
  sendMessage();
}

function renderBrief(brief) {
  const el = document.getElementById('briefContent');
  if (typeof brief === 'string') {
    el.innerHTML = `<div class="brief-row">${brief.replace(/\n/g, '<br>')}</div>`;
  } else {
    el.innerHTML = `
      <div class="brief-row"><strong>Lead:</strong> ${brief.name || leadData.name}</div>
      <div class="brief-row"><strong>Property:</strong> ${brief.property || leadData.property_type + ', ' + leadData.postcode}</div>
      <div class="brief-row"><strong>Discussed:</strong> ${brief.discussed || '—'}</div>
      <div class="brief-row"><strong>Sentiment:</strong> ${brief.sentiment || '—'}</div>
      <div class="brief-row"><strong>Suggested approach:</strong> ${brief.approach || '—'}</div>
    `;
  }
}

function showError(msg) {
  const el = document.getElementById('errorMsg');
  el.textContent = msg; el.style.display = 'block';
}

function resetBtn() {
  document.getElementById('generateBtn').disabled = false;
  document.getElementById('spinner').style.display = 'none';
  document.getElementById('btnText').textContent = 'Start Flow';
}

function reset() {
  document.getElementById('emptyState').style.display = 'flex';
  document.getElementById('chatWrap').style.display = 'none';
  document.getElementById('resetBtn').style.display = 'none';
  document.getElementById('quickRepliesWrap').style.display = 'block';
  document.getElementById('chatInputRow').style.display = 'flex';
  conversationHistory = []; flowEnded = false;
  setFlowStep('');
}
</script>
</body>
</html>
"""

SYSTEM_PROMPT = """You are Alex, an AI energy and bills assistant for a UK utility management company. You're in a WhatsApp conversation with a new lead.

The company helps UK renters manage all their household bills in one place — energy, broadband, council tax. Leads sign up at the company's website.

Your goal: answer their questions honestly and guide them toward completing sign-up. Do not be pushy.

Rules:
- Keep every message to 2–3 sentences maximum
- Be warm, direct, and knowledgeable about UK energy bills
- Never make up specific numbers unless asked — then give a realistic estimate
- If they're clearly ready to sign up: tell them to head to the sign-up page and sign off warmly
- If they explicitly ask for a call, or ask to speak to a person, or seem frustrated after multiple exchanges: trigger a handoff

At the end of EVERY response, output a JSON block on a new line in this exact format:
{"action": "continue", "message": "your message here"}

For a conversion:
{"action": "converted", "message": "your final message here"}

For a handoff:
{"action": "handoff", "message": "your final message here", "brief": {"name": "lead name", "property": "property + postcode", "discussed": "what they asked about", "sentiment": "how they seemed", "approach": "what the agent should lead with"}}

Only output the JSON — no extra commentary."""


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@app.route('/generate', methods=['POST'])
def generate():
    data   = request.json
    api_key = data.get('api_key') or os.environ.get('ANTHROPIC_API_KEY', '')
    if not api_key:
        return jsonify({'error': 'No API key provided.'})

    try:
        client = anthropic.Anthropic(api_key=api_key)
        prompt = f"""You are Alex, an AI energy and bills assistant for a UK utility management company. A new lead just submitted their details via a partner form. Send them a WhatsApp message — this will arrive on their phone within 60 seconds.

Lead:
- Name: {data['name']}
- Postcode: {data['postcode']}
- Property: {data['property_type']}
- Occupants: {data['occupants']}

Write the opening WhatsApp message. Rules:
- 3 sentences max
- Reference their area (infer neighbourhood from postcode) and property type
- Include a specific realistic annual overpayment estimate in £ for their property size
- One clear next step: reply with any questions or head to the sign-up page
- Sign off as Alex
- Warm and direct, not corporate. One emoji max or none."""

        msg = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=220,
            messages=[{"role": "user", "content": prompt}]
        )
        return jsonify({'message': msg.content[0].text})

    except anthropic.AuthenticationError:
        return jsonify({'error': 'Invalid API key.'})
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/chat', methods=['POST'])
def chat():
    data    = request.json
    api_key = data.get('api_key') or os.environ.get('ANTHROPIC_API_KEY', '')
    history = data.get('history', [])

    if not api_key:
        return jsonify({'error': 'No API key provided.'})

    context = (f"Lead context: {data['name']}, {data['property_type']} in {data['postcode']}, "
               f"{data['occupants']}.")

    messages = [{"role": "user", "content": context + " Start of conversation:"}] + history

    try:
        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=350,
            system=SYSTEM_PROMPT,
            messages=messages
        )
        raw = msg.content[0].text.strip()

        # Extract JSON from the response
        json_start = raw.rfind('{')
        json_end   = raw.rfind('}') + 1
        if json_start == -1:
            return jsonify({'action': 'continue', 'message': raw})

        parsed  = json.loads(raw[json_start:json_end])
        message = parsed.get('message', raw[:json_start].strip() or raw)
        action  = parsed.get('action', 'continue')
        brief   = parsed.get('brief', None)

        return jsonify({'message': message, 'action': action, 'brief': brief})

    except anthropic.AuthenticationError:
        return jsonify({'error': 'Invalid API key.'})
    except json.JSONDecodeError:
        return jsonify({'action': 'continue', 'message': raw})
    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    print("\n  Speed-to-Lead Demo")
    print("  ─────────────────────────────")
    print("  Running at: http://localhost:5050")
    print("  Press Ctrl+C to stop\n")
    app.run(debug=False, port=5050)
