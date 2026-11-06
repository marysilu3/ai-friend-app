import os, sqlite3, requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)
DB = os.getenv("CHAT_DB", "chats.db")
def db():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row
    c.execute("""CREATE TABLE IF NOT EXISTS chats(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT NOT NULL,created_at DATETIME DEFAULT CURRENT_TIMESTAMP)""")
    c.execute("""CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY AUTOINCREMENT,chat_id INTEGER NOT NULL,role TEXT NOT NULL,content TEXT NOT NULL,created_at DATETIME DEFAULT CURRENT_TIMESTAMP)""")
    c.commit(); return c
@app.get("/")
def home(): return render_template("index.html")
@app.get("/api/chats")
def chats():
    c=db(); rows=c.execute("SELECT c.id,c.title,c.created_at,(SELECT content FROM messages m WHERE m.chat_id=c.id ORDER BY id DESC LIMIT 1) preview FROM chats c ORDER BY c.id DESC").fetchall(); c.close()
    return jsonify([dict(x) for x in rows])
@app.post("/api/chats")
def new_chat():
    c=db(); cur=c.execute("INSERT INTO chats(title) VALUES(?)",("New chat",)); c.commit(); i=cur.lastrowid; c.close(); return jsonify({"id":i,"title":"New chat"})
@app.get("/api/chats/<int:i>")
def get_chat(i):
    c=db(); row=c.execute("SELECT * FROM chats WHERE id=?",(i,)).fetchone()
    if not row: c.close(); return jsonify({"error":"Not found"}),404
    msgs=c.execute("SELECT role,content FROM messages WHERE chat_id=? ORDER BY id",(i,)).fetchall(); c.close()
    return jsonify({"chat":dict(row),"messages":[dict(x) for x in msgs]})
@app.patch("/api/chats/<int:i>")
def rename(i):
    title=(request.json or {}).get("title","").strip()[:80]
    if not title: return jsonify({"error":"Title required"}),400
    c=db(); c.execute("UPDATE chats SET title=? WHERE id=?",(title,i)); c.commit(); c.close(); return jsonify({"ok":True})
@app.delete("/api/chats/<int:i>")
def delete(i):
    c=db(); c.execute("DELETE FROM messages WHERE chat_id=?",(i,)); c.execute("DELETE FROM chats WHERE id=?",(i,)); c.commit(); c.close(); return jsonify({"ok":True})
@app.delete("/api/chats/<int:i>/messages")
def clear(i):
    c=db(); c.execute("DELETE FROM messages WHERE chat_id=?",(i,)); c.commit(); c.close(); return jsonify({"ok":True})
def ai_reply(history):
    key=os.getenv("AI_API_KEY",""); base=os.getenv("AI_BASE_URL","https://api.openai.com/v1").rstrip("/")
    model=os.getenv("AI_MODEL","gpt-4o-mini")
    if not key: return "Your AI connection is not configured yet. Add your AI_API_KEY to the private .env file on your hosting service, then try again."
    system={"role":"system","content":"You are a warm, thoughtful, cheerful personal AI friend. Listen without judgment, adapt to the user's mood, and reply naturally in the language they use, including Malayalam script, Manglish, English, or a mix. Be honest that you are an AI. Do not claim to replace human relationships or professional help."}
    r=requests.post(base+"/chat/completions",headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"},json={"model":model,"messages":[system]+history[-24:],"temperature":0.8},timeout=60)
    r.raise_for_status(); return r.json()["choices"][0]["message"]["content"].strip()
@app.post("/api/chats/<int:i>/send")
def send(i):
    msg=(request.json or {}).get("message","").strip()
    if not msg: return jsonify({"error":"Message is empty"}),400
    c=db()
    if not c.execute("SELECT id FROM chats WHERE id=?",(i,)).fetchone(): c.close(); return jsonify({"error":"Chat not found"}),404
    c.execute("INSERT INTO messages(chat_id,role,content) VALUES(?,?,?)",(i,"user",msg)); c.commit()
    rows=c.execute("SELECT role,content FROM messages WHERE chat_id=? ORDER BY id",(i,)).fetchall()
    history=[dict(x) for x in rows]
    try: reply=ai_reply(history)
    except Exception as e: reply="Sorry, I couldn't reach the AI service just now. Please check the API configuration and try again."
    c.execute("INSERT INTO messages(chat_id,role,content) VALUES(?,?,?)",(i,"assistant",reply))
    count=c.execute("SELECT COUNT(*) n FROM messages WHERE chat_id=?",(i,)).fetchone()["n"]
    if count==2: c.execute("UPDATE chats SET title=? WHERE id=?",(msg[:36],i))
    c.commit(); c.close(); return jsonify({"reply":reply})
if __name__=="__main__": app.run(host="0.0.0.0",port=int(os.getenv("PORT","5000")),debug=False)
