import syntaxmatrix as smx
from settings.app_settings import *


def create_conversation(streaming=False):

    chat_history = smx.get_chat_history() or []
    sid = smx.get_session_id()
    smiv_index = smx.smiv_index(sid)

    try:
        query, intent = smx.get_text_input_value("user_query")
        if query == "":
            return
        
        query = query.strip()
        chat_history.append(("User", query))
        sources = []

        if intent == "none":   
            context = ""  
        else:   
            q_vec = smx.embed_query(query)
            if q_vec is None:
                return
            
            results = []
            if intent in ["hybrid", "user_docs"]:
                user_hits = smiv_index.search(q_vec, top_k=3)
                if not user_hits:
                    # smx.error("No user documents found. Please upload files.")
                    pass
                results.append("\n### Personal Context (user uploads)\n")
                for hit in user_hits:
                    text = hit["metadata"]["chunk_text"].strip().replace("\n", " ")
                    results.append(f"- {text}\n")
                sources.append("User Docs")

            if intent in ["hybrid", "system_docs"]:
                sys_hits = smx.smpv_search(q_vec, top_k=5)
                if not sys_hits:
                    smx.error("Please contact support.")
                    return
                results.append("### System Context (company docs)\n")
                for hit in sys_hits:
                    text = hit["chunk_text"].strip().replace("\n", " ")
                    results.append(f"- {text}\n")
                sources.append("System Docs")

            context = "".join(results)
        
        conversations = "\n".join([f"{role}: {msg}" for role, msg in chat_history])
        
        if streaming:
            smx.stream_process_query(query, context, conversations, sources)      

        else:
            answer = smx.process_query(query, context, conversations)
        
            if isinstance(answer, str) and answer.strip():
                if sources:
                    src_list = "".join(f"<li>{s}</li>" for s in sources)
                    answer += f"<ul style='margin-top:5px;color:blue;font-size:0.8rem;'>{src_list}</ul>"
                chat_history.append(("Bot", answer))
        
        smx.set_chat_history(chat_history)
        smx.clear_text_input_value("user_query")

    except Exception as e:
        smx.error(f"UI:- {type(e).__name__}: {e}")

# Activate System Widgets (predefined)
smx.text_input(key="user_query", id="user_query", label="Enter query", placeholder="Ask me anything ...")
smx.button(key="submit_query", id="submit_query", label="Submit", callback=lambda: create_conversation(smx.stream()))
smx.file_uploader("user_files", id="user_files", label="Upload PDF files:", accept_multiple_files=True)

# Register Custom Widgets
def clear_chat():
    smx.clear_chat_history()

# Call custom widget 'clear_chat' function
smx.button("clear_chat", "clear_chat", "Clear", clear_chat)


app = smx.app
if __name__ == "__main__":
    smx.run()
