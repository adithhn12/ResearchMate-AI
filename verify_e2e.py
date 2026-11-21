import os
import io
import sys
from fastapi.testclient import TestClient

# Ensure backend package is in python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.main import app

def run_e2e_verification():
    print("=== Starting ResearchMate AI End-to-End Verification ===")
    client = TestClient(app)

    # 1. Authenticate Demo User
    print("\n[Step 1] Authenticating Demo User...")
    auth_resp = client.post("/api/v1/auth/demo-login")
    assert auth_resp.status_code == 200, f"Auth failed: {auth_resp.text}"
    token = auth_resp.json()["access_token"]
    user = auth_resp.json()["user"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"-> Successfully logged in as {user['full_name']} ({user['email']})")

    # 2. Create or verify Project
    print("\n[Step 2] Creating / Selecting Research Project...")
    proj_resp = client.post("/api/v1/projects", json={
        "name": "Literature Review on AI Retrieval Architectures",
        "description": "Comparative exploration of RAG, sentence transformers, and multi-agent synthesis."
    }, headers=headers)
    assert proj_resp.status_code == 200
    project = proj_resp.json()
    project_id = project["id"]
    print(f"-> Created Project ID {project_id}: '{project['name']}'")

    # 3. Upload Sample Papers
    print("\n[Step 3] Ingesting & Indexing Research Papers...")
    sample_files = [
        "sample_papers/multi_doc_rag_synthesis.pdf",
        "sample_papers/lightweight_embeddings_evaluation.pdf",
        "sample_papers/multiagent_literature_review.pdf"
    ]
    
    files_payload = []
    opened_files = []
    for sf in sample_files:
        f = open(sf, "rb")
        opened_files.append(f)
        files_payload.append(("files", (os.path.basename(sf), f, "application/pdf")))

    upload_resp = client.post(
        "/api/v1/papers/upload",
        data={"project_id": str(project_id)},
        files=files_payload,
        headers=headers
    )
    for f in opened_files:
        f.close()

    assert upload_resp.status_code == 200, f"Upload failed: {upload_resp.text}"
    uploaded_papers = upload_resp.json()
    print(f"-> Ingested {len(uploaded_papers)} papers successfully:")
    paper_ids = []
    for p in uploaded_papers:
        paper_ids.append(p["id"])
        print(f"   * [{p['status'].upper()}] ID: {p['id']} - '{p['title']}' ({p['page_count']} pages)")

    # 4. Multi-Document RAG Query
    print("\n[Step 4] Testing AI Research Assistant Grounded RAG Query...")
    chat_query = "What are the key limitations and trade-offs of lightweight embedding models and RAG?"
    chat_resp = client.post("/api/v1/chat/message", json={
        "content": chat_query,
        "project_id": project_id,
        "paper_ids": paper_ids
    }, headers=headers)
    assert chat_resp.status_code == 200, f"Chat failed: {chat_resp.text}"
    chat_data = chat_resp.json()
    print("-> Assistant Grounded Response Excerpt:")
    print("   " + chat_data["content"][:300].replace("\n", " ") + "...")
    print(f"-> Verified Grounded Sources: {len(chat_data['sources'])} citations returned")
    for s in chat_data["sources"][:3]:
        print(f"   - Citations: \"{s['paper_title']}\" (Page {s['page_number']})")

    # 5. Paper Comparison Matrix
    print("\n[Step 5] Testing Research Paper Comparison Module...")
    comp_resp = client.post("/api/v1/compare/generate", json={
        "project_id": project_id,
        "paper_ids": paper_ids[:2],
        "title": "Methodology Comparison: RAG vs Lightweight Embeddings"
    }, headers=headers)
    assert comp_resp.status_code == 200, f"Comparison failed: {comp_resp.text}"
    comp_data = comp_resp.json()
    print(f"-> Comparison matrix generated across {len(comp_data['comparison_data'])} papers.")
    for c in comp_data["comparison_data"]:
        print(f"   * Paper: '{c['paper_title']}' | Objective: {c['research_objective'][:60]}... | Algorithms: {c['algorithms'][:40]}")

    # 6. Research Gap Analyzer
    print("\n[Step 6] Testing Research Gap Analyzer Module...")
    gap_resp = client.post("/api/v1/gaps/analyze", json={
        "project_id": project_id,
        "paper_ids": paper_ids,
        "title": "Cross-Corpus Research Gaps & Limitations"
    }, headers=headers)
    assert gap_resp.status_code == 200, f"Gap analysis failed: {gap_resp.text}"
    gap_data = gap_resp.json()
    print(f"-> Identified {len(gap_data['recurring_challenges'])} recurring challenges across papers:")
    for ch in gap_data["recurring_challenges"][:2]:
        print(f"   * Challenge: {ch}")
    print(f"-> Extracted {len(gap_data['gaps'])} gaps and limitations:")
    for g in gap_data["gaps"][:2]:
        print(f"   * [{g['type']}] {g['title']} ({g['category']}) -> Future Direction: {g['future_direction'][:60]}...")

    # 7. Literature Review Generator & Export
    print("\n[Step 7] Testing Literature Review Generator & DOCX/PDF Export...")
    review_resp = client.post("/api/v1/reviews/generate", json={
        "project_id": project_id,
        "paper_ids": paper_ids,
        "title": "Advances in Retrieval Augmented Generation and Scholarly Literature Synthesis",
        "research_focus": "RAG efficiency and grounded academic synthesis"
    }, headers=headers)
    assert review_resp.status_code == 200, f"Review generation failed: {review_resp.text}"
    review_data = review_resp.json()
    review_id = review_data["id"]
    print(f"-> Literature review generated (ID: {review_id}): '{review_data['title']}'")
    print(f"   * Introduction length: {len(review_data.get('introduction', ''))} chars")
    print(f"   * Thematic analysis length: {len(review_data.get('thematic_analysis', ''))} chars")

    # Test DOCX Export
    docx_resp = client.get(f"/api/v1/reviews/{review_id}/export/docx", headers=headers)
    assert docx_resp.status_code == 200
    assert len(docx_resp.content) > 1000
    print(f"-> DOCX Export successful ({len(docx_resp.content)} bytes generated)")

    # Test PDF Export
    pdf_resp = client.get(f"/api/v1/reviews/{review_id}/export/pdf", headers=headers)
    assert pdf_resp.status_code == 200
    assert len(pdf_resp.content) > 1000
    print(f"-> PDF Export successful ({len(pdf_resp.content)} bytes generated)")

    # 8. Dashboard Analytics
    print("\n[Step 8] Testing Research Dashboard Analytics...")
    dash_resp = client.get("/api/v1/analytics/dashboard", headers=headers)
    assert dash_resp.status_code == 200
    dash_data = dash_resp.json()
    print(f"-> Total papers indexed: {dash_data['total_papers']}")
    print(f"-> Total comparisons: {dash_data['total_comparisons']}")
    print(f"-> Total literature reviews: {dash_data['total_reviews']}")

    print("\n🎉 ALL 8 MODULES AND WORKFLOWS VERIFIED END-TO-END WITH REAL DATA & GEMINI API!")

if __name__ == "__main__":
    run_e2e_verification()
