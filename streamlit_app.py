import time
import requests
import streamlit as st

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="RAG QA System", page_icon="📄", layout="wide")
st.title("📄 RAG QA System")
st.caption("Upload PDF/TXT, then ask questions from your documents.")

if "uploaded_docs" not in st.session_state:
    st.session_state.uploaded_docs = []   # list of {document_id, filename}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []    # list of (role, text)
if "selected_doc_ids" not in st.session_state:
    st.session_state.selected_doc_ids = []

left, right = st.columns([1, 2])

# -------------------------
# LEFT: Upload + document status
# -------------------------
with left:
    st.subheader("1) Upload document")
    file = st.file_uploader("Choose a PDF or TXT", type=["pdf", "txt"])

    if st.button("Upload", use_container_width=True):
        if not file:
            st.warning("Please choose a file first.")
        else:
            try:
                files = {"file": (file.name, file.getvalue(), file.type or "application/octet-stream")}
                resp = requests.post(f"{API_BASE}/documents/upload", files=files, timeout=120)
                if resp.status_code == 200:
                    data = resp.json()
                    st.success(f"Uploaded: {data['filename']}")
                    st.session_state.uploaded_docs.append(
                        {"document_id": data["document_id"], "filename": data["filename"]}
                    )
                else:
                    st.error(f"Upload failed: {resp.status_code} - {resp.text}")
            except Exception as e:
                st.error(f"Upload error: {e}")

    st.divider()
    st.subheader("2) Documents")

    if not st.session_state.uploaded_docs:
        st.info("No documents uploaded yet.")
    else:
        options = {
            f"{d['filename']} ({d['document_id'][:8]}...)": d["document_id"]
            for d in st.session_state.uploaded_docs
        }

        selected_labels = st.multiselect(
            "Select documents for QA",
            list(options.keys()),
            default=list(options.keys())
        )
        st.session_state.selected_doc_ids = [options[x] for x in selected_labels]

        if st.button("Refresh statuses", use_container_width=True):
            pass

        for d in st.session_state.uploaded_docs:
            doc_id = d["document_id"]
            try:
                r = requests.get(f"{API_BASE}/documents/{doc_id}/status", timeout=30)
                if r.status_code == 200:
                    s = r.json()
                    st.write(f"**{d['filename']}**")
                    st.write(f"- id: `{doc_id}`")
                    st.write(f"- status: `{s['status']}`")
                    if s.get("detail"):
                        st.caption(s["detail"])
                else:
                    st.warning(f"{d['filename']}: status check failed")
            except Exception as e:
                st.warning(f"{d['filename']}: {e}")

# -------------------------
# RIGHT: Chat
# -------------------------
with right:
    st.subheader("3) Chat with your documents")

    for role, text in st.session_state.chat_history:
        with st.chat_message(role):
            st.markdown(text)

    question = st.chat_input("Ask a question about selected documents...")
    if question:
        st.session_state.chat_history.append(("user", question))
        with st.chat_message("user"):
            st.markdown(question)

        if not st.session_state.selected_doc_ids:
            answer_text = "Please upload/select at least one document first."
            st.session_state.chat_history.append(("assistant", answer_text))
            with st.chat_message("assistant"):
                st.markdown(answer_text)
        else:
            payload = {
                "question": question,
                "document_ids": st.session_state.selected_doc_ids,
                "top_k": 4
            }

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    t0 = time.time()
                    try:
                        resp = requests.post(f"{API_BASE}/qa/ask", json=payload, timeout=180)
                        if resp.status_code == 200:
                            data = resp.json()
                            answer = data.get("answer", "")
                            sources = data.get("sources", [])
                            latency = data.get("latency_ms", {})

                            st.markdown(answer if answer else "_No answer returned._")

                            if sources:
                                with st.expander("Sources"):
                                    for i, s in enumerate(sources, 1):
                                        st.markdown(
                                            f"**{i}. doc:** `{s['document_id']}` | "
                                            f"**chunk:** `{s['chunk_id']}` | "
                                            f"**score:** `{s['score']:.4f}`"
                                        )
                                        st.caption(s["text_preview"])

                            if latency:
                                st.caption(
                                    f"Latency (ms) — embed: {latency.get('embedding_ms')}, "
                                    f"retrieve: {latency.get('retrieval_ms')}, "
                                    f"generate: {latency.get('generation_ms')}, "
                                    f"total: {latency.get('total_ms')}"
                                )

                            st.session_state.chat_history.append(("assistant", answer))
                        else:
                            err = f"API error {resp.status_code}: {resp.text}"
                            st.error(err)
                            st.session_state.chat_history.append(("assistant", err))
                    except Exception as e:
                        err = f"Request failed: {e}"
                        st.error(err)
                        st.session_state.chat_history.append(("assistant", err))
                    finally:
                        _ = time.time() - t0