import streamlit as st, os, sys, time
sys.path.append("app")
from app.ingest import ingest, collection
from app.retrieve import retrieve
from app.generate import answer

st.set_page_config(page_title="Property Law Assistant", page_icon="📄", layout="wide")

st.markdown("""
<style>
    [data-testid="stChatMessage"] p { 
        font-family: Georgia, 'Times New Roman', serif; 
        line-height: 1.65; 
        font-size: 1.02rem;
    }
    [data-testid="stSidebar"] { border-right: 1px solid rgba(255,255,255,0.08); }
    footer, #MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

if "history" not in st.session_state:
    st.session_state.history = []

with st.sidebar:
    st.header("Documents")
    files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)
    if files and st.button("Ingest", use_container_width=True):
        os.makedirs("data", exist_ok=True)
        bar = st.progress(0.0)
        for i, f in enumerate(files):
            path = f"data/{f.name}"
            with open(path, "wb") as out:
                out.write(f.getbuffer())
            try:
                n = ingest(path, f.name)
                st.caption(f"✓ {f.name} — {n} chunks")
            except Exception as e:
                st.error(f"✗ {f.name}: {e}")
            bar.progress((i + 1) / len(files))

    metas = collection.get()["metadatas"]
    docs = sorted({m["source"] for m in metas}) if metas else []
    st.caption(f"{len(docs)} documents · {len(metas)} chunks indexed")
    picked = st.multiselect("Search within", docs, default=docs)
    show_debug = st.toggle("Show retrieved chunks", value=False)

st.title("Property Law Assistant")
st.caption("Answers grounded in Dubai real estate legislation. English translations — Arabic text is authoritative.")

for turn in st.session_state.history:
    with st.chat_message(turn["role"]):
        st.markdown(turn["content"])

if q := st.chat_input("Ask about tenancy law, rent increases, eviction notice..."):
    st.session_state.history.append({"role": "user", "content": q})
    with st.chat_message("user"):
        st.markdown(q)

    with st.chat_message("assistant"):
        with st.spinner("Searching legislation..."):
            t0 = time.time()
            chunks = retrieve(q, sources=picked or None)
            reply, model_used = answer(q, chunks)
            elapsed = time.time() - t0

        st.markdown(reply)

        if chunks:
            srcs = sorted({f"{c['source']} (p.{c['page']})" for c in chunks})
            st.caption(f"Sources: {' · '.join(srcs)} — {elapsed:.1f}s")

        if show_debug and chunks:
            with st.expander("Retrieved context"):
                for i, c in enumerate(chunks, 1):
                    st.caption(f"**{i}. {c['source']} — page {c['page']}**")
                    st.text(c["text"][:400])

    st.session_state.history.append({"role": "assistant", "content": reply})