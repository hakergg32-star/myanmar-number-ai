
import os
from collections import Counter
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

PAGE = r"""
<!DOCTYPE html>
<html lang="my">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Myanmar Number AI</title>
<style>
*{box-sizing:border-box}
body{margin:0;background:#080d18;color:#edf2ff;
font-family:Arial,sans-serif;padding:16px}
main{max-width:760px;margin:auto}
h1{color:#f6c453;text-align:center}
.sub{text-align:center;color:#aab7d0}
.card{background:#111b2d;border:1px solid #283953;
border-radius:15px;padding:16px;margin:14px 0}
.tabs{display:flex;gap:8px;flex-wrap:wrap}
button{background:#f6c453;color:#101522;border:0;
padding:12px;border-radius:9px;font-weight:bold;cursor:pointer}
.tabs button{flex:1;min-width:85px}
input,select{width:100%;padding:13px;margin:8px 0;
background:#091221;color:white;border:1px solid #354660;
border-radius:8px;font-size:16px}
.result{font-size:26px;color:#f6c453;font-weight:bold}
.small{font-size:13px;color:#9eacc3}
li{margin:8px 0;overflow-wrap:anywhere}
</style>
</head>
<body>
<main>
<h1>⚡ NUMBER AI LAB</h1>
<p class="sub">Myanmar 2D • 3D • WinGo Analysis</p>

<div class="card">
<h3>① Game ရွေးပါ</h3>
<div class="tabs">
<button onclick="choose('2d')">Myanmar 2D</button>
<button onclick="choose('3d')">Myanmar 3D</button>
<button onclick="choose('wingo')">WinGo</button>
</div>
<p id="gameLabel">Myanmar 2D</p>
</div>

<div class="card">
<h3>② ရလဒ်မှတ်တမ်း ထည့်ပါ</h3>
<label>ထွက်ခဲ့သောဂဏန်း</label>
<input id="number" inputmode="numeric"
placeholder="ဥပမာ 2D = 27 / 3D = 527 / WinGo = 7">
<button onclick="addResult()">မှတ်တမ်းသိမ်းမယ်</button>
<p class="small">2D = 00–99၊ 3D = 000–999၊
WinGo = 0–9 ဟု စစ်ဆေးပါမည်။</p>
</div>

<div class="card">
<h3>③ AI စာရင်းအင်း</h3>
<p>မှတ်တမ်းအရေအတွက်: <span id="count">0</span></p>
<button onclick="analyze()">အချက်အလက် ခွဲခြမ်းစိတ်ဖြာမယ်</button>
<div id="analysis">ရလဒ်တွေထည့်ပြီး Analyze ကိုနှိပ်ပါ။</div>
<p class="small">အတိတ်အချက်အလက်သည် အနာဂတ်ရလဒ်
အာမခံချက် မဟုတ်ပါ။</p>
</div>

<div class="card">
<h3>④ သိမ်းထားသောမှတ်တမ်း</h3>
<button onclick="clearHistory()">မှတ်တမ်းဖျက်မယ်</button>
<ol id="history"></ol>
</div>
</main>

<script>
let game='2d';
let records=JSON.parse(localStorage.getItem('numRecords')||'[]');

function choose(g){
 game=g;
 document.getElementById('gameLabel').textContent=
  g==='2d'?'Myanmar 2D':g==='3d'?'Myanmar 3D':'WinGo';
 document.getElementById('number').placeholder=
  g==='2d'?'ဥပမာ 27':g==='3d'?'ဥပမာ 527':'ဥပမာ 7';
 render();
 document.getElementById('analysis').textContent=
  'ဒီဂိမ်းအတွက် Analyze ကိုနှိပ်ပါ။';
}

function save(){
 localStorage.setItem('numRecords',JSON.stringify(records));
 render();
}

function render(){
 let arr=records.filter(r=>r.game===game);
 document.getElementById('count').textContent=arr.length;
 let list=document.getElementById('history');
 list.replaceChildren();
 arr.slice().reverse().forEach(r=>{
  let li=document.createElement('li');
  li.textContent=r.value+' — '+r.time;
  list.appendChild(li);
 });
}

async function addResult(){
 let input=document.getElementById('number');
 let v=input.value.trim();
 let valid=game==='2d'?/^\\d{1,2}$/.test(v):
  game==='3d'?/^\\d{1,3}$/.test(v):/^[0-9]$/.test(v);
 if(!valid){
  alert('ဂဏန်းကို မှန်ကန်စွာ ထည့်ပါ။');return;
 }
 let max=game==='2d'?99:game==='3d'?999:9;
 if(Number(v)>max){alert('ဂဏန်းအကန့်အသတ် ကျော်နေပါတယ်။');return;}
 let digits=game==='2d'?v.padStart(2,'0'):
  game==='3d'?v.padStart(3,'0'):v;
 records.push({game,value:digits,
  time:new Date().toLocaleString()});
 save();
 input.value='';
 document.getElementById('analysis').textContent=
  'မှတ်တမ်းသိမ်းပြီးပါပြီ။';
}

async function analyze(){
 let arr=records.filter(r=>r.game===game).map(r=>r.value);
 if(arr.length===0){
  document.getElementById('analysis').textContent=
   'အရင်ဆုံး ရလဒ်မှတ်တမ်း ထည့်ပါ။';return;
 }
 let box=document.getElementById('analysis');
 box.textContent='တွက်ချက်နေသည်...';
 try{
  let res=await fetch('/api/analyze',{
   method:'POST',headers:{'Content-Type':'application/json'},
   body:JSON.stringify({game,results:arr})
  });
  let data=await res.json();
  if(!res.ok)throw Error(data.error||'Error');
  box.replaceChildren();
  let title=document.createElement('p');
  title.className='result';
  title.textContent='စုစုပေါင်း '+data.count+' ကြိမ်';
  box.appendChild(title);
  let p=document.createElement('p');
  p.textContent='ဂဏန်းအကြိမ်ရေ (အများဆုံး 5 ခု):';
  box.appendChild(p);
  let ul=document.createElement('ul');
  data.top.forEach(item=>{
   let li=document.createElement('li');
   li.textContent=item.number+' — '+item.count+' ကြိမ်';
   ul.appendChild(li);
  });
  box.appendChild(ul);
  let note=document.createElement('p');
  note.className='small';
  note.textContent=data.note;
  box.appendChild(note);
 }catch(e){
  box.textContent='အမှား: '+e.message;
 }
}

function clearHistory(){
 if(confirm('မှတ်တမ်းအားလုံး ဖျက်မလား?')){
  records=records.filter(r=>r.game!==game);
  save();
  document.getElementById('analysis').textContent='မှတ်တမ်းဖျက်ပြီးပါပြီ။';
 }
}
render();
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(PAGE)

@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True) or {}
    game = data.get("game")
    results = data.get("results", [])

    if game not in ("2d", "3d", "wingo"):
        return jsonify(error="Invalid game"), 400

    if not isinstance(results, list) or len(results) > 5000:
        return jsonify(error="Invalid result list"), 400

    valid = []
    for value in results:
        if not isinstance(value, str):
            continue
        if game == "2d" and value.isdigit() and len(value) == 2:
            valid.append(value)
        elif game == "3d" and value.isdigit() and len(value) == 3:
            valid.append(value)
        elif game == "wingo" and value in list("0123456789"):
            valid.append(value)

    counts = Counter(valid)
    top = [
        {"number": number, "count": count}
        for number, count in counts.most_common(5)
    ]

    return jsonify(
        game=game,
        count=len(valid),
        top=top,
        note="အတိတ်မှတ်တမ်း၏ အကြိမ်ရေကိုသာ ပြထားသည်။ "
             "နောက်ထွက်မည့်ဂဏန်းကို မခန့်မှန်းနိုင်ပါ။"
    )

@app.route("/health")
def health():
    return jsonify(status="ok")

if __name__ == "__main__":
    app.run(host="0.0.0.0",
            port=int(os.environ.get("PORT", 10000)))
