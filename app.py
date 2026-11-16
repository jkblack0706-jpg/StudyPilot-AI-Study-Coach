import os, json, re, urllib.request, urllib.error
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

app = FastAPI(title="StudyPilot AI Study Coach")
class StudyRequest(BaseModel):
    topic: str = Field(min_length=3, max_length=160)
    goal: str = "Prepare for an exam"
    level: str = "Intermediate"
    minutes: int = Field(default=30, ge=10, le=180)
    mode: str = "demo"

def gemini(role, text):
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key:
        raise HTTPException(503, "AI key is not configured. Try Offline demo.")
    model = os.getenv("GEMINI_MODEL", "gemini-3-flash")
    url = "https://generativelanguage.googleapis.com/v1beta/models/" + model + ":generateContent"
    payload = json.dumps({"system_instruction":{"parts":[{"text":role+" Be accurate, concise and do not invent sources."}]},"contents":[{"parts":[{"text":text}]}],"generationConfig":{"maxOutputTokens":1200}}).encode()
    req = urllib.request.Request(url, payload, {"Content-Type":"application/json","x-goog-api-key":key})
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            data = json.load(res)
        return "\n".join(p.get("text","") for c in data.get("candidates",[]) for p in c.get("content",{}).get("parts",[]))
    except urllib.error.HTTPError as e:
        raise HTTPException(502, "Gemini API returned HTTP "+str(e.code))
    except Exception:
        raise HTTPException(502, "Gemini service unavailable")

@app.get("/health")
def health():
    return {"status":"ok","ai_configured":bool(os.getenv("GEMINI_API_KEY"))}

@app.post("/api/study")
def study(req:StudyRequest):
    topic=req.topic.strip()
    if req.level not in ("Beginner","Intermediate","Advanced") or req.mode not in ("demo","ai"):
        raise HTTPException(422,"Invalid options")
    if req.mode=="demo":
        plan=f"# Study plan: {topic}\n\n1. Foundations ({req.minutes//4} minutes): define the essential terms.\n2. Example: work through one example.\n3. Active recall: explain from memory.\n4. Review: identify your gaps."
        lesson=f"## Lesson scaffold: {topic}\n\nExplain the concept in your own words, check your class notes, and compare a correct and incorrect example. Demo output is generic and not live AI."
        quiz=[{"question":f"Define {topic}.","answer":"Explain the key concept in your own words."},{"question":f"Give an example of {topic}.","answer":"Identify where it applies and why."},{"question":"What misconception should you avoid?","answer":"Check your notes for a common mistake."}]
        review="Demo mode: the four stages were generated with built-in templates, not an AI model."
    else:
        context=f"Topic: {topic}. Goal: {req.goal}. Level: {req.level}. Available study time: {req.minutes} minutes."
        plan=gemini("Planner agent: create a useful time-boxed Markdown study outline.",context)
        lesson=gemini("Tutor agent: explain this topic with an example using Markdown.",context+"\nPlan: "+plan)
        raw=gemini("Quiz Maker agent: output ONLY valid JSON array of 3 objects with question and answer string fields.",context+"\nLesson: "+lesson)
        try:
            raw=re.sub(r"^\x60\x60\x60(?:json)?\s*|\s*\x60\x60\x60$","",raw.strip(),flags=re.I)
            parsed=json.loads(raw)
            if isinstance(parsed,dict): parsed=parsed.get("questions",[])
            quiz=[{"question":str(q["question"]),"answer":str(q["answer"])} for q in parsed[:3]]
            if len(quiz)<3: raise ValueError()
        except Exception:
            raise HTTPException(502,"Quiz agent returned invalid structured data; please retry.")
        review=gemini("Reviewer agent: assess accuracy, risks and study gaps in 120 words.",context+"\nPlan: "+plan+"\nLesson: "+lesson+"\nQuiz: "+json.dumps(quiz))
    trace=[{"agent":agent,"status":"demo complete" if req.mode=="demo" else "complete"} for agent in ("Planner","Tutor","Quiz Maker","Reviewer")]
    return {"topic":topic,"mode":req.mode,"plan":plan,"lesson":lesson,"quiz":quiz,"review":review,"trace":trace,"timestamp":datetime.now(timezone.utc).isoformat()}

PAGE = r"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>StudyPilot | AI Study Coach</title>
<style>body{margin:0;background:#0b1220;color:#e8eef8;font:16px system-ui,sans-serif}header,main{max-width:1050px;margin:auto;padding:24px}header{display:flex;align-items:center;justify-content:space-between}h1{font-size:44px;margin:10px 0}h2{color:#96b9ff}.muted{color:#a3afc3}.card{background:#16223a;padding:24px;border:1px solid #344361;border-radius:16px;margin:20px 0}input,select,button{font:inherit;padding:12px;border-radius:9px;border:1px solid #62718c}input,select{background:#0d172a;color:white;box-sizing:border-box;width:100%;margin:6px 0 15px}label{font-weight:600}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:15px}button{background:#75a8ff;color:#09172b;cursor:pointer;font-weight:700}button:disabled{opacity:.6}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:inherit;line-height:1.65}.tabs{display:flex;flex-wrap:wrap;gap:8px}.tabs button{background:#273653;color:#e7eefd}.tabs button.active{background:#75a8ff;color:#081522}article{margin-top:18px}small{color:#a5b5d2}details{margin:12px 0}a{color:#9fc3ff}@media(max-width:650px){.grid{grid-template-columns:1fr}h1{font-size:34px}}</style></head>
<body><header><strong>✦ StudyPilot</strong><span class="muted">Jalen Black · AI Study Coach</span></header><main><h1>Study smarter with an AI agent team.</h1><p class="muted">Planner → Tutor → Quiz Maker → Reviewer. Generate a plan, explanation, quiz and quality review.</p>
<section class="card"><form id="form"><div class="grid"><div><label>Study topic<input id="topic" required minlength="3" value="SQL joins"></label></div><div><label>Learning goal<input id="goal" value="Prepare for a database exam"></label></div><div><label>Level<select id="level"><option>Beginner</option><option selected>Intermediate</option><option>Advanced</option></select></label></div><div><label>Minutes<input id="minutes" type="number" min="10" max="180" value="30"></label></div></div><label>Generation mode<select id="mode"><option value="demo">Offline demo (no API key)</option><option value="ai">Live Gemini AI</option></select></label><button type="submit" id="submit">Generate my study session</button><p id="status" aria-live="polite"></p></form></section>
<section id="output" hidden><div class="card"><h2 id="sessionTitle"></h2><p id="trace" class="muted"></p><div class="tabs" id="tabs"></div><article id="view"></article><button id="download" type="button">Download study notes (.md)</button></div></section><footer class="muted">Live AI requires a server-configured Gemini API key. Demo results are templates and are labeled accordingly.</footer></main>
<script>let result=null,tab="plan";const $=id=>document.getElementById(id);const esc=s=>String(s??"").replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;");const labels={plan:"Study Plan",lesson:"Lesson",quiz:"Quiz",review:"Review",trace:"Agent Trace"};function show(t){tab=t;$("tabs").innerHTML=Object.keys(labels).map(k=>'<button class="'+(k===t?"active":"")+'" data-tab="'+k+'">'+labels[k]+'</button>').join("");$("tabs").querySelectorAll("button").forEach(b=>b.onclick=()=>show(b.dataset.tab));let html="";if(t==="quiz")html=result.quiz.map((q,i)=>'<details><summary>'+esc((i+1)+". "+q.question)+'</summary><p>'+esc(q.answer)+'</p></details>').join("");else if(t==="trace")html=result.trace.map(a=>'<p>✓ '+esc(a.agent)+" — "+esc(a.status)+"</p>").join("");else html="<pre>"+esc(result[t])+"</pre>";$("view").innerHTML=html;} $("form").addEventListener("submit",async e=>{e.preventDefault();$("submit").disabled=true;$("status").textContent="Running agent pipeline…";try{const r=await fetch("/api/study",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({topic:$("topic").value,goal:$("goal").value,level:$("level").value,minutes:Number($("minutes").value),mode:$("mode").value})});const data=await r.json();if(!r.ok)throw new Error(typeof data.detail==="string"?data.detail:"Request failed");result=data;$("sessionTitle").textContent=data.topic+" · "+(data.mode==="demo"?"Offline demonstration":"Live Gemini AI");$("trace").textContent=data.trace.map(a=>a.agent).join(" → ");$("output").hidden=false;show("plan");$("status").textContent="Study session generated.";}catch(err){$("status").textContent="Error: "+err.message}finally{$("submit").disabled=false}});$("download").onclick=()=>{if(!result)return;const txt=[result.plan,result.lesson,"# Quiz",...result.quiz.map((q,i)=>(i+1)+". "+q.question+"\nAnswer: "+q.answer),"# Review",result.review].join("\n\n");const a=document.createElement("a");a.href=URL.createObjectURL(new Blob([txt],{type:"text/markdown"}));a.download="StudyPilot-notes.md";a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)};</script></body></html>"""
@app.get("/",response_class=HTMLResponse)
def home():
    return PAGE
