import logging, time
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODELS

log = logging.getLogger(__name__)
client = Groq(api_key=GROQ_API_KEY)

PROMPT = """You are a Dubai property law assistant for internal staff use.

Answer using ONLY the context below. If the context doesn't contain the answer, reply exactly: "I couldn't find this in the indexed legislation."

Rules:
- Lead with the direct answer in one sentence.
- Then give supporting detail only if it changes the practical outcome.
- Cite the article or decree number in the text (e.g. "under Article 14 of Law 26/2007").
- If the context contains conflicting or amended provisions, say so explicitly.
- Never speculate beyond the context. Never give legal advice — state what the legislation says.

CONTEXT:
{context}

QUESTION: {question}

ANSWER:"""

class AllModelsFailed(Exception):
    pass

def _call(model, prompt):
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )
    return resp.choices[0].message.content

def answer(question, chunks):
    if not chunks:
        return "I couldn't find this in the indexed legislation.", None

    context = "\n\n".join(
        f"[{c['source']}, page {c['page']}]\n{c['text']}" for c in chunks
    )
    prompt = PROMPT.format(context=context, question=question)

    errors = []
    for model in GROQ_MODELS:
        for attempt in range(2):
            try:
                return _call(model, prompt), model
            except Exception as e:
                status = getattr(e, "status_code", None)
                if status == 429 and attempt == 0:
                    time.sleep(2)
                    continue
                log.warning("%s failed: %s", model, e)
                errors.append(f"{model}: {type(e).__name__}")
                break

    raise AllModelsFailed("; ".join(errors))