import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # --- PALETTE (Dark Navy Academic SaaS) ---
    C_BG = RGBColor(11, 17, 32)         # Deep Navy (#0B1120)
    C_CARD = RGBColor(30, 41, 59)       # Slate 800 (#1E293B)
    C_CARD_LIGHT = RGBColor(15, 23, 42) # Navy 900 (#0F172A)
    C_BORDER = RGBColor(51, 65, 85)     # Slate 700 (#334155)
    C_BORDER_ACCENT = RGBColor(14, 116, 144) # Cyan 700
    C_TEXT_WHITE = RGBColor(255, 255, 255)
    C_TEXT_LIGHT = RGBColor(241, 245, 249) # Slate 100
    C_TEXT_MUTED = RGBColor(148, 163, 184) # Slate 400
    C_TEXT_DIM = RGBColor(100, 116, 139)   # Slate 500
    
    # Accents
    C_SKY = RGBColor(56, 189, 248)      # Sky Blue (#38BDF8)
    C_BLUE = RGBColor(37, 99, 235)      # Academic Blue (#2563EB)
    C_INDIGO = RGBColor(129, 140, 248)  # Indigo Accent (#818CF8)
    C_EMERALD = RGBColor(52, 211, 153)  # Emerald (#34D399)
    C_AMBER = RGBColor(251, 191, 36)    # Amber (#FBBF24)
    C_ROSE = RGBColor(244, 63, 94)      # Rose (#F43F5E)

    def set_bg(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = C_BG
        bg.line.fill.background()
        return bg

    def add_header(slide, title, category, slide_num_str):
        cat_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.45), Inches(3.2), Inches(0.35))
        cat_box.fill.solid()
        cat_box.fill.fore_color.rgb = RGBColor(15, 23, 42)
        cat_box.line.color.rgb = C_BORDER
        cat_box.line.width = Pt(1)
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        tf_cat.margin_left = tf_cat.margin_right = tf_cat.margin_top = tf_cat.margin_bottom = 0
        p_c = tf_cat.paragraphs[0]
        p_c.alignment = PP_ALIGN.CENTER
        run_c = p_c.add_run()
        run_c.text = category.upper()
        run_c.font.size = Pt(10)
        run_c.font.bold = True
        run_c.font.color.rgb = C_SKY
        run_c.font.name = "Segoe UI"

        tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.85), Inches(10.5), Inches(0.65))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        run = p.add_run()
        run.text = title
        run.font.size = Pt(22)
        run.font.bold = True
        run.font.color.rgb = C_TEXT_WHITE
        run.font.name = "Segoe UI"

        tb_num = slide.shapes.add_textbox(Inches(11.2), Inches(0.5), Inches(1.3), Inches(0.4))
        tf_num = tb_num.text_frame
        tf_num.margin_left = tf_num.margin_right = tf_num.margin_top = tf_num.margin_bottom = 0
        p_n = tf_num.paragraphs[0]
        p_n.alignment = PP_ALIGN.RIGHT
        run_n = p_n.add_run()
        run_n.text = slide_num_str
        run_n.font.size = Pt(12)
        run_n.font.bold = True
        run_n.font.color.rgb = C_TEXT_DIM
        run_n.font.name = "Segoe UI"

    def add_card(slide, left, top, width, height, bg_col=C_CARD, border_col=C_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_col
        card.line.color.rgb = border_col
        card.line.width = Pt(1)
        return card

    # =========================================================================
    # SLIDE 1: TITLE SLIDE
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_bg(s1)

    accent_bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.8), Inches(1.2), Inches(0.08))
    accent_bar.fill.solid()
    accent_bar.fill.fore_color.rgb = C_SKY
    accent_bar.line.fill.background()

    tb_deg = s1.shapes.add_textbox(Inches(0.8), Inches(1.0), Inches(11.0), Inches(0.35))
    tf_deg = tb_deg.text_frame
    p_deg = tf_deg.paragraphs[0]
    r_deg = p_deg.add_run()
    r_deg.text = "MASTER OF COMPUTER APPLICATIONS (MCA) • CAPSTONE PROJECT REVIEW"
    r_deg.font.size = Pt(11)
    r_deg.font.bold = True
    r_deg.font.color.rgb = C_SKY
    r_deg.font.name = "Segoe UI"

    tb_title = s1.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(11.5), Inches(1.1))
    tf_title = tb_title.text_frame
    tf_title.word_wrap = True
    p_t = tf_title.paragraphs[0]
    r_t1 = p_t.add_run()
    r_t1.text = "ResearchMate "
    r_t1.font.size = Pt(40)
    r_t1.font.bold = True
    r_t1.font.color.rgb = C_TEXT_WHITE
    r_t1.font.name = "Segoe UI"
    r_t2 = p_t.add_run()
    r_t2.text = "AI"
    r_t2.font.size = Pt(40)
    r_t2.font.bold = True
    r_t2.font.color.rgb = C_SKY
    r_t2.font.name = "Segoe UI"

    tb_sub = s1.shapes.add_textbox(Inches(0.8), Inches(2.55), Inches(11.5), Inches(0.5))
    tf_sub = tb_sub.text_frame
    p_s = tf_sub.paragraphs[0]
    r_s = p_s.add_run()
    r_s.text = "AI-Powered Academic Research Assistant & Multi-Paper Analysis Platform"
    r_s.font.size = Pt(19)
    r_s.font.bold = True
    r_s.font.color.rgb = C_TEXT_LIGHT
    r_s.font.name = "Segoe UI"

    tb_desc = s1.shapes.add_textbox(Inches(0.8), Inches(3.2), Inches(11.5), Inches(0.6))
    tf_desc = tb_desc.text_frame
    tf_desc.word_wrap = True
    p_d = tf_desc.paragraphs[0]
    r_d = p_d.add_run()
    r_d.text = "Full-Stack Multi-Document RAG Platform with Verified Page Citations & 9-Axis Cross-Paper Comparative Analysis."
    r_d.font.size = Pt(13)
    r_d.font.bold = True
    r_d.font.color.rgb = C_SKY
    r_d.font.name = "Segoe UI"

    card_meta1 = add_card(s1, Inches(0.8), Inches(4.3), Inches(5.6), Inches(2.5), C_CARD_LIGHT, C_BORDER)
    tb_m1 = s1.shapes.add_textbox(Inches(1.1), Inches(4.5), Inches(5.0), Inches(2.1))
    tf_m1 = tb_m1.text_frame
    tf_m1.word_wrap = True

    p_m1_h = tf_m1.paragraphs[0]
    r = p_m1_h.add_run()
    r.text = "CANDIDATE INFORMATION"
    r.font.size = Pt(11)
    r.font.bold = True
    r.font.color.rgb = C_SKY
    r.font.name = "Segoe UI"

    p_m1_1 = tf_m1.add_paragraph()
    p_m1_1.space_before = Pt(10)
    r = p_m1_1.add_run()
    r.text = "Student Name: "
    r.font.bold = True
    r.font.size = Pt(12)
    r.font.color.rgb = C_TEXT_LIGHT
    r = p_m1_1.add_run()
    r.text = "Adith [Register No. / Roll No.]"
    r.font.size = Pt(12)
    r.font.color.rgb = C_TEXT_WHITE

    p_m1_2 = tf_m1.add_paragraph()
    p_m1_2.space_before = Pt(8)
    r = p_m1_2.add_run()
    r.text = "Program: "
    r.font.bold = True
    r.font.size = Pt(12)
    r.font.color.rgb = C_TEXT_LIGHT
    r = p_m1_2.add_run()
    r.text = "Master of Computer Applications (MCA) — Sem III"
    r.font.size = Pt(12)
    r.font.color.rgb = C_TEXT_WHITE

    card_meta2 = add_card(s1, Inches(6.8), Inches(4.3), Inches(5.7), Inches(2.5), C_CARD_LIGHT, C_BORDER)
    tb_m2 = s1.shapes.add_textbox(Inches(7.1), Inches(4.5), Inches(5.1), Inches(2.1))
    tf_m2 = tb_m2.text_frame
    tf_m2.word_wrap = True

    p_m2_h = tf_m2.paragraphs[0]
    r = p_m2_h.add_run()
    r.text = "ACADEMIC INSTITUTION & SUPERVISION"
    r.font.size = Pt(11)
    r.font.bold = True
    r.font.color.rgb = C_SKY
    r.font.name = "Segoe UI"

    p_m2_1 = tf_m2.add_paragraph()
    p_m2_1.space_before = Pt(10)
    r = p_m2_1.add_run()
    r.text = "Department: "
    r.font.bold = True
    r.font.size = Pt(12)
    r.font.color.rgb = C_TEXT_LIGHT
    r = p_m2_1.add_run()
    r.text = "Department of Computer Applications"
    r.font.size = Pt(12)
    r.font.color.rgb = C_TEXT_WHITE

    p_m2_2 = tf_m2.add_paragraph()
    p_m2_2.space_before = Pt(8)
    r = p_m2_2.add_run()
    r.text = "Institution: "
    r.font.bold = True
    r.font.size = Pt(12)
    r.font.color.rgb = C_TEXT_LIGHT
    r = p_m2_2.add_run()
    r.text = "[University / Institution Name Placeholder]"
    r.font.size = Pt(12)
    r.font.color.rgb = C_TEXT_WHITE

    p_m2_3 = tf_m2.add_paragraph()
    p_m2_3.space_before = Pt(8)
    r = p_m2_3.add_run()
    r.text = "Project Mentor: "
    r.font.bold = True
    r.font.size = Pt(12)
    r.font.color.rgb = C_TEXT_LIGHT
    r = p_m2_3.add_run()
    r.text = "[Faculty Guide / Supervisor Name] • 2025–2026"
    r.font.size = Pt(12)
    r.font.color.rgb = C_TEXT_WHITE

    s1.notes_slide.notes_text_frame.text = (
        "Good morning respected evaluators, professors, and committee members. "
        "Welcome to the capstone presentation for ResearchMate AI — an AI-powered academic research assistant and multi-paper analysis platform. "
        "Over these 12 slides, I will walk you through our formal problem statements, proposed solution and objectives, "
        "project scope, end-to-end system workflow, decoupled architecture, technology stack, core modules, "
        "multi-document RAG pipeline, genuine application screenshots, test verification, and future roadmap."
    )

    # =========================================================================
    # SLIDE 2: PROBLEM STATEMENT (Actual Problem Statements)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_bg(s2)
    add_header(s2, "Problem Statements: Core Gaps in Academic Paper Analysis", "Problem Statements", "02 / 12")

    problem_statements = [
        (
            "PS-01 • Unstructured Multi-PDF Knowledge Extraction",
            [
                "Academic findings and metadata are locked inside unstructured multi-page PDFs",
                "Manual extraction of titles, authors, abstracts & methods does not scale"
            ],
            C_AMBER
        ),
        (
            "PS-02 • Unverifiable Claims & Citation Hallucination",
            [
                "Generic LLMs fabricate paper titles, author names, and unsupported claims",
                "Lack of page-level provenance ([Paper, p. X]) prevents scholarly verification"
            ],
            C_ROSE
        ),
        (
            "PS-03 • Single-Document Retrieval Bias in Standard RAG",
            [
                "Naive vector similarity search over-retrieves chunks from one dominant paper",
                "Cross-paper queries fail without balanced per-paper retrieval diversity"
            ],
            C_SKY
        ),
        (
            "PS-04 • Absence of Structured Cross-Paper Synthesis",
            [
                "No automated way to contrast Objectives, Algorithms, Datasets & Metrics side-by-side",
                "Researchers lack isolated per-project workspaces with live indexing analytics"
            ],
            C_INDIGO
        )
    ]

    coords_2x2 = [
        (Inches(0.8), Inches(1.65), Inches(5.6), Inches(2.4)),
        (Inches(6.8), Inches(1.65), Inches(5.7), Inches(2.4)),
        (Inches(0.8), Inches(4.35), Inches(5.6), Inches(2.4)),
        (Inches(6.8), Inches(4.35), Inches(5.7), Inches(2.4))
    ]

    for idx, (ps_title, ps_bullets, col) in enumerate(problem_statements):
        x, y, w, h = coords_2x2[idx]
        add_card(s2, x, y, w, h, C_CARD, C_BORDER)
        
        bar = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, Inches(0.1), h)
        bar.fill.solid()
        bar.fill.fore_color.rgb = col
        bar.line.fill.background()

        tb = s2.shapes.add_textbox(x + Inches(0.3), y + Inches(0.22), w - Inches(0.45), h - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        r1 = p1.add_run()
        r1.text = ps_title
        r1.font.size = Pt(13)
        r1.font.bold = True
        r1.font.color.rgb = col
        r1.font.name = "Segoe UI"

        for b_text in ps_bullets:
            p = tf.add_paragraph()
            p.space_before = Pt(12)
            r_dot = p.add_run()
            r_dot.text = "• "
            r_dot.font.bold = True
            r_dot.font.size = Pt(11.5)
            r_dot.font.color.rgb = col

            r_txt = p.add_run()
            r_txt.text = b_text
            r_txt.font.size = Pt(11.5)
            r_txt.font.color.rgb = C_TEXT_LIGHT
            r_txt.font.name = "Segoe UI"

    s2.notes_slide.notes_text_frame.text = (
        "Slide 2 defines the four concrete problem statements that ResearchMate AI addresses. "
        "Problem Statement 1: Academic knowledge is locked inside unstructured PDFs, making manual metadata entry and cross-reading slow and error-prone. "
        "Problem Statement 2: Generic AI chatbots hallucinate citations and lack page-level provenance, making them unreliable for academic work. "
        "Problem Statement 3: Standard vector search suffers from single-document bias when querying multiple papers, failing to retrieve balanced evidence across sources. "
        "Problem Statement 4: Researchers lack an automated, structured matrix to compare objectives, algorithms, datasets, metrics, and results side-by-side."
    )

    # =========================================================================
    # SLIDE 3: PROPOSED SOLUTION AND OBJECTIVES
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_bg(s3)
    add_header(s3, "Proposed Solution: ResearchMate AI & Core Objectives", "Solution & Goals", "03 / 12")

    add_card(s3, Inches(0.8), Inches(1.6), Inches(4.5), Inches(5.2), C_CARD_LIGHT, C_BORDER_ACCENT)
    tb_sol = s3.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(4.1), Inches(4.8))
    tf_sol = tb_sol.text_frame
    tf_sol.word_wrap = True

    p = tf_sol.paragraphs[0]
    r = p.add_run()
    r.text = "THE RESEARCHMATE PARADIGM"
    r.font.size = Pt(12)
    r.font.bold = True
    r.font.color.rgb = C_SKY
    r.font.name = "Segoe UI"

    pillars = [
        ("Isolated Project Workspaces", "Isolates PDF papers and local vector collections by research topic or course domain."),
        ("Grounded Multi-Doc RAG", "Retrieves balanced chunks across multiple papers with verified [Paper, p. X] page citations."),
        ("Automated Comparative Matrix", "Generates structured 9-axis comparative tables contrasting algorithms, datasets & metrics.")
    ]

    for pil_title, pil_desc in pillars:
        p_t = tf_sol.add_paragraph()
        p_t.space_before = Pt(16)
        r = p_t.add_run()
        r.text = f"✔  {pil_title}"
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = C_EMERALD
        r.font.name = "Segoe UI"

        p_d = tf_sol.add_paragraph()
        p_d.space_before = Pt(3)
        r = p_d.add_run()
        r.text = pil_desc
        r.font.size = Pt(10.5)
        r.font.color.rgb = C_TEXT_LIGHT
        r.font.name = "Segoe UI"

    objectives = [
        ("1. Automated Ingestion & Metadata Extraction", "Extracts text streams, titles, authors, abstract, year & keywords via PyMuPDF.", C_SKY),
        ("2. Grounded Multi-Doc RAG with Page Citations", "Conversational Q&A across multi-paper corpuses with 100% verified [p. X] page citations.", C_BLUE),
        ("3. Structured 9-Axis Cross-Paper Comparison", "Constructs comparative matrices for Objectives, Methodologies, Datasets, Metrics & Results.", C_INDIGO),
        ("4. Interactive Analytics & Research Workspace", "Visualizes publication year distributions, indexing statuses, and project activity.", C_EMERALD)
    ]

    for idx, (obj_title, obj_desc, col) in enumerate(objectives):
        y_pos = Inches(1.6 + idx * 1.33)
        add_card(s3, Inches(5.6), y_pos, Inches(6.9), Inches(1.2), C_CARD, C_BORDER)

        bar = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(5.6), y_pos, Inches(0.08), Inches(1.2))
        bar.fill.solid()
        bar.fill.fore_color.rgb = col
        bar.line.fill.background()

        tb_o = s3.shapes.add_textbox(Inches(5.85), y_pos + Inches(0.14), Inches(6.5), Inches(0.92))
        tf_o = tb_o.text_frame
        tf_o.word_wrap = True

        p_o1 = tf_o.paragraphs[0]
        r_o1 = p_o1.add_run()
        r_o1.text = obj_title
        r_o1.font.size = Pt(12)
        r_o1.font.bold = True
        r_o1.font.color.rgb = C_TEXT_WHITE
        r_o1.font.name = "Segoe UI"

        p_o2 = tf_o.add_paragraph()
        p_o2.space_before = Pt(4)
        r_o2 = p_o2.add_run()
        r_o2.text = f"•  {obj_desc}"
        r_o2.font.size = Pt(11)
        r_o2.font.color.rgb = C_TEXT_MUTED
        r_o2.font.name = "Segoe UI"

    s3.notes_slide.notes_text_frame.text = (
        "Slide 3 presents our proposed solution and four core engineering objectives. "
        "Objective 1: Single-pass PDF ingestion with automated bibliographic metadata extraction via PyMuPDF and Gemini refinement. "
        "Objective 2: Strictly grounded multi-document RAG where every claim links directly to its source paper and exact page number. "
        "Objective 3: Automated 9-axis comparison matrices contrasting methodologies, algorithms, datasets, and evaluation metrics. "
        "Objective 4: Interactive analytics dashboard tracking paper timelines, vector indexing status, and project activity."
    )

    # =========================================================================
    # SLIDE 4: PROJECT SCOPE (New Slide)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_bg(s4)
    add_header(s4, "Project Scope: Functional Coverage & System Boundaries", "Project Scope", "04 / 12")

    scope_cards = [
        (
            "IN-SCOPE • DELIVERED FUNCTIONALITY",
            "Verified & Implemented System Capabilities",
            [
                "JWT Authentication, Demo Login & User-Isolated Workspaces",
                "Multi-PDF Upload with Single-Pass PyMuPDF Text Extraction",
                "Token-Aligned Chunking (180 words) & Metadata Refinement",
                "Local 384-d all-MiniLM-L6-v2 Singleton ONNX Embeddings",
                "ChromaDB Persistent Collections with Per-Paper Diversity",
                "Grounded Gemini RAG Q&A + Clickable [Paper, p. X] Citations",
                "9-Axis Cross-Paper Comparison Matrix & Recharts Analytics"
            ],
            C_EMERALD,
            Inches(0.8),
            Inches(6.1)
        ),
        (
            "OUT-OF-SCOPE • SYSTEM BOUNDARIES",
            "Explicitly Excluded from Current Release",
            [
                "OCR for Scanned / Image-Only PDFs (Requires selectable text)",
                "Automated Scraping of External Sites (Scholar / IEEE / arXiv)",
                "Real-Time Multi-User Collaborative Editing in Shared Projects",
                "Automated Literature Review Synthesis & Word/PDF Export",
                "Local Self-Hosted LLM Inference (Uses Google Gemini API)"
            ],
            C_AMBER,
            Inches(7.2),
            Inches(5.3)
        )
    ]

    for title, subtitle, bullets, col, x_pos, width in scope_cards:
        add_card(s4, x_pos, Inches(1.6), width, Inches(5.2), C_CARD, C_BORDER)

        bar = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, x_pos, Inches(1.6), width, Inches(0.08))
        bar.fill.solid()
        bar.fill.fore_color.rgb = col
        bar.line.fill.background()

        tb_h = s4.shapes.add_textbox(x_pos + Inches(0.25), Inches(1.8), width - Inches(0.5), Inches(0.7))
        tf_h = tb_h.text_frame
        tf_h.word_wrap = True
        p_th = tf_h.paragraphs[0]
        r = p_th.add_run()
        r.text = title
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = col
        r.font.name = "Segoe UI"

        p_sub = tf_h.add_paragraph()
        p_sub.space_before = Pt(2)
        r = p_sub.add_run()
        r.text = subtitle
        r.font.size = Pt(10)
        r.font.color.rgb = C_TEXT_MUTED
        r.font.name = "Segoe UI"

        tb_b = s4.shapes.add_textbox(x_pos + Inches(0.25), Inches(2.55), width - Inches(0.5), Inches(4.05))
        tf_b = tb_b.text_frame
        tf_b.word_wrap = True

        for b_idx, bullet in enumerate(bullets):
            p = tf_b.paragraphs[0] if b_idx == 0 else tf_b.add_paragraph()
            p.space_before = Pt(9)
            r_dot = p.add_run()
            r_dot.text = "✔  " if col == C_EMERALD else "•  "
            r_dot.font.bold = True
            r_dot.font.size = Pt(10.5)
            r_dot.font.color.rgb = col

            r_txt = p.add_run()
            r_txt.text = bullet
            r_txt.font.size = Pt(10.5)
            r_txt.font.color.rgb = C_TEXT_LIGHT
            r_txt.font.name = "Segoe UI"

    s4.notes_slide.notes_text_frame.text = (
        "Slide 4 clearly defines the project scope and boundaries. "
        "On the left, everything in-scope is fully implemented and tested: JWT authentication, project isolation, multi-PDF upload, "
        "single-pass PyMuPDF parsing, singleton ONNX MiniLM embeddings, ChromaDB vector indexing, grounded multi-document RAG with clickable page citations, "
        "the 9-axis comparison matrix, and Recharts analytics. "
        "On the right, we explicitly state system boundaries: scanned image-only PDFs without selectable text require OCR (out of scope), "
        "and external web scraping or multi-user live co-editing are outside this release."
    )

    # =========================================================================
    # SLIDE 5: END-TO-END WORKFLOW (New Slide)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_bg(s5)
    add_header(s5, "End-to-End System Workflow: User & Data Pipeline", "System Workflow", "05 / 12")

    workflow_stages = [
        (
            "01 • AUTH & PROJECT",
            "Workspace Initialization",
            [
                "Sign in via JWT or Demo Login",
                "Create isolated research project",
                "Binds dedicated ChromaDB collection"
            ],
            C_SKY,
            Inches(0.8), Inches(1.6)
        ),
        (
            "02 • MULTI-PDF UPLOAD",
            "Ingestion & Validation",
            [
                "Upload multiple PDFs in UploadModal",
                "Validate .pdf & %PDF- magic header",
                "Stream files to disk safely"
            ],
            C_BLUE,
            Inches(4.8), Inches(1.6)
        ),
        (
            "03 • PARSE & CHUNK",
            "PyMuPDF + Gemini Metadata",
            [
                "Single-pass page & text extraction",
                "Extract & refine title, authors, year",
                "Split into 180-word chunks (35 overlap)"
            ],
            C_INDIGO,
            Inches(8.8), Inches(1.6)
        ),
        (
            "04 • VECTOR INDEXING",
            "Singleton ONNX + ChromaDB",
            [
                "Singleton all-MiniLM-L6-v2 embeds batches",
                "Upsert 384-d vectors in batches of 16",
                "Persist chunks in SQLite & ChromaDB"
            ],
            C_EMERALD,
            Inches(0.8), Inches(4.05)
        ),
        (
            "05 • GROUNDED RAG Q&A",
            "Scoped Inquiry & Citations",
            [
                "Select all or specific indexed papers",
                "Per-paper diversity retrieval (per_paper_k)",
                "Gemini answers with clickable [p. X] pills"
            ],
            C_AMBER,
            Inches(4.8), Inches(4.05)
        ),
        (
            "06 • MATRIX & ANALYTICS",
            "Synthesis & Visualization",
            [
                "Select 2+ papers for 9-axis comparison",
                "Generate structured methodology table",
                "View Recharts trends on Dashboard"
            ],
            C_ROSE,
            Inches(8.8), Inches(4.05)
        )
    ]

    for st_tag, st_title, st_bullets, col, x, y in workflow_stages:
        w, h = Inches(3.7), Inches(2.2)
        add_card(s5, x, y, w, h, C_CARD, C_BORDER)

        bar = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, Inches(0.08))
        bar.fill.solid()
        bar.fill.fore_color.rgb = col
        bar.line.fill.background()

        tb = s5.shapes.add_textbox(x + Inches(0.18), y + Inches(0.14), w - Inches(0.36), h - Inches(0.24))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        r1 = p1.add_run()
        r1.text = st_tag
        r1.font.size = Pt(9.5)
        r1.font.bold = True
        r1.font.color.rgb = col
        r1.font.name = "Segoe UI"

        p2 = tf.add_paragraph()
        p2.space_before = Pt(2)
        r2 = p2.add_run()
        r2.text = st_title
        r2.font.size = Pt(12)
        r2.font.bold = True
        r2.font.color.rgb = C_TEXT_WHITE
        r2.font.name = "Segoe UI"

        for b_text in st_bullets:
            p = tf.add_paragraph()
            p.space_before = Pt(4)
            r_dot = p.add_run()
            r_dot.text = "• "
            r_dot.font.bold = True
            r_dot.font.size = Pt(10)
            r_dot.font.color.rgb = col

            r_txt = p.add_run()
            r_txt.text = b_text
            r_txt.font.size = Pt(10)
            r_txt.font.color.rgb = C_TEXT_LIGHT
            r_txt.font.name = "Segoe UI"

    # Bottom Workflow Summary Banner
    add_card(s5, Inches(0.8), Inches(6.42), Inches(11.7), Inches(0.6), C_CARD_LIGHT, C_BORDER_ACCENT)
    tb_wf = s5.shapes.add_textbox(Inches(1.0), Inches(6.5), Inches(11.3), Inches(0.45))
    tf_wf = tb_wf.text_frame
    tf_wf.word_wrap = True
    p_wf = tf_wf.paragraphs[0]
    p_wf.alignment = PP_ALIGN.CENTER
    r_wf1 = p_wf.add_run()
    r_wf1.text = "END-TO-END FLOW:  "
    r_wf1.font.size = Pt(10)
    r_wf1.font.bold = True
    r_wf1.font.color.rgb = C_SKY
    r_wf1.font.name = "Segoe UI"

    r_wf2 = p_wf.add_run()
    r_wf2.text = "Login → Create Project → Upload PDFs → PyMuPDF Parse → ONNX Embed & ChromaDB Index → Multi-Doc RAG Q&A → 9-Axis Matrix"
    r_wf2.font.size = Pt(10)
    r_wf2.font.color.rgb = C_TEXT_LIGHT
    r_wf2.font.name = "Segoe UI"

    s5.notes_slide.notes_text_frame.text = (
        "Slide 5 illustrates the complete end-to-end application workflow from the moment a researcher logs in to generating comparative insights. "
        "Stage 1: The user authenticates via JWT and selects or creates an isolated project. "
        "Stage 2: Multiple PDFs are uploaded and validated for valid PDF headers. "
        "Stage 3: PyMuPDF parses pages and metadata in a single pass, refined by Gemini, and splits text into 180-word chunks. "
        "Stage 4: Our singleton ONNX MiniLM session embeds chunks in small 16-item batches into ChromaDB while saving chunks in SQLite. "
        "Stage 5: In the AI Research Assistant, the user scopes papers and asks questions answered with clickable page citations. "
        "Stage 6: The researcher generates 9-axis comparison tables and monitors project analytics on the Dashboard."
    )

    # =========================================================================
    # SLIDE 6: SYSTEM ARCHITECTURE
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_bg(s6)
    add_header(s6, "System Architecture: Decoupled Multi-Tier Platform", "Architecture", "06 / 12")

    layers = [
        (
            "1. CLIENT TIER",
            "React 18 SPA • Vite",
            [
                "Tailwind CSS dark SaaS interface",
                "Interactive Recharts analytics visuals",
                "React Markdown + Remark GFM",
                "Axios client with JWT token auth"
            ],
            C_SKY,
            Inches(0.8)
        ),
        (
            "2. APPLICATION API",
            "FastAPI • Python 3.12",
            [
                "Threadpool-backed REST endpoints",
                "Strict Pydantic v2 data validation",
                "Project-level context isolation layer",
                "Uvicorn ASGI production server"
            ],
            C_BLUE,
            Inches(3.85)
        ),
        (
            "3. PROCESSING & RAG",
            "PyMuPDF • ChromaDB • ONNX",
            [
                "PyMuPDF single-pass text extraction",
                "180-word chunks (35-word overlap)",
                "Singleton ONNX all-MiniLM-L6-v2",
                "ChromaDB persistent vector collections"
            ],
            C_INDIGO,
            Inches(6.9)
        ),
        (
            "4. INTELLIGENCE & STORAGE",
            "Gemini API • SQLite • ORM",
            [
                "Google Gemini with multi-model fallback",
                "Grounded prompt with [p. X] citations",
                "SQLite + SQLAlchemy persistent ORM",
                "Fast JSON API response serialization"
            ],
            C_EMERALD,
            Inches(9.95)
        )
    ]

    for title, subtitle, bullets, col, x_pos in layers:
        add_card(s6, x_pos, Inches(1.6), Inches(2.8), Inches(4.45), C_CARD, C_BORDER)
        
        header_shape = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, x_pos, Inches(1.6), Inches(2.8), Inches(0.72))
        header_shape.fill.solid()
        header_shape.fill.fore_color.rgb = col
        header_shape.line.fill.background()

        tb_h = s6.shapes.add_textbox(x_pos + Inches(0.12), Inches(1.65), Inches(2.56), Inches(0.62))
        tf_h = tb_h.text_frame
        tf_h.word_wrap = True
        p_th = tf_h.paragraphs[0]
        r = p_th.add_run()
        r.text = title
        r.font.size = Pt(10.5)
        r.font.bold = True
        r.font.color.rgb = C_TEXT_WHITE
        r.font.name = "Segoe UI"

        p_sub = tf_h.add_paragraph()
        r = p_sub.add_run()
        r.text = subtitle
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(224, 242, 254)
        r.font.name = "Segoe UI"

        tb_b = s6.shapes.add_textbox(x_pos + Inches(0.15), Inches(2.45), Inches(2.5), Inches(3.45))
        tf_b = tb_b.text_frame
        tf_b.word_wrap = True

        for b_idx, bullet in enumerate(bullets):
            p = tf_b.paragraphs[0] if b_idx == 0 else tf_b.add_paragraph()
            p.space_before = Pt(10)
            r_bullet = p.add_run()
            r_bullet.text = "• "
            r_bullet.font.bold = True
            r_bullet.font.size = Pt(10.5)
            r_bullet.font.color.rgb = col
            
            r_text = p.add_run()
            r_text.text = bullet
            r_text.font.size = Pt(10.5)
            r_text.font.color.rgb = C_TEXT_LIGHT
            r_text.font.name = "Segoe UI"

    add_card(s6, Inches(0.8), Inches(6.22), Inches(11.95), Inches(0.78), C_CARD_LIGHT, C_BORDER)
    tb_flow = s6.shapes.add_textbox(Inches(1.0), Inches(6.32), Inches(11.5), Inches(0.58))
    tf_flow = tb_flow.text_frame
    tf_flow.word_wrap = True
    p_f = tf_flow.paragraphs[0]
    r_f1 = p_f.add_run()
    r_f1.text = "DATA PIPELINE:  "
    r_f1.font.size = Pt(10.5)
    r_f1.font.bold = True
    r_f1.font.color.rgb = C_SKY
    r_f1.font.name = "Segoe UI"

    r_f2 = p_f.add_run()
    r_f2.text = (
        "PDF Stream → PyMuPDF Single-Pass Parse → 180-word Chunking → Singleton ONNX MiniLM → "
        "ChromaDB Storage → Diversity Retrieval → Gemini Synthesis → Cited Output [p. X]"
    )
    r_f2.font.size = Pt(10)
    r_f2.font.color.rgb = C_TEXT_LIGHT
    r_f2.font.name = "Segoe UI"

    s6.notes_slide.notes_text_frame.text = (
        "This slide depicts the architectural blueprint of ResearchMate AI directly derived from our implemented codebase. "
        "The architecture is organized into four distinct tiers: Client Tier (React 18 + Vite + Tailwind), Application API Tier (FastAPI + Python 3.12), "
        "Processing & RAG Tier (PyMuPDF + singleton ONNX all-MiniLM-L6-v2 + ChromaDB), and Intelligence & Storage Tier (Google Gemini API + SQLite/SQLAlchemy)."
    )

    # =========================================================================
    # SLIDE 7: TECHNOLOGY STACK
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_bg(s7)
    add_header(s7, "Technology Stack: Selected Tools & Technical Roles", "Technology Stack", "07 / 12")

    tech_stack = [
        (
            "Frontend Layer",
            "React 18 • Vite • Tailwind CSS",
            [
                "Modular React 18 SPA with dark navy academic theme",
                "Fast production build via Vite asset bundler",
                "Interactive Recharts analytics and Lucide React icons"
            ],
            C_SKY
        ),
        (
            "Backend Framework",
            "Python 3.12 • FastAPI • Uvicorn",
            [
                "High-throughput REST API with OpenAPI / Swagger docs",
                "Strict Pydantic v2 data models & validation",
                "JWT authentication with secure password hashing"
            ],
            C_BLUE
        ),
        (
            "PDF Parsing & Ingestion",
            "PyMuPDF (fitz)",
            [
                "Single-pass C-accelerated PDF text stream extraction",
                "Automated title, author, abstract, year & keyword parsing",
                "Header & encrypted/empty PDF validation"
            ],
            C_INDIGO
        ),
        (
            "Vector Embeddings & Storage",
            "all-MiniLM-L6-v2 • ChromaDB",
            [
                "Singleton ONNX 384-d dense vectors (1-thread, low-RAM)",
                "Zero PyTorch dependency on Windows/Linux environments",
                "ChromaDB PersistentClient with isolated project collections"
            ],
            C_EMERALD
        ),
        (
            "Generative AI & LLM",
            "Google Gemini API (Flash Cascade)",
            [
                "Cascading fallback: Flash-Lite → 3.8-Flash → Flash",
                "Reused singleton GenAI client for low latency",
                "Strict grounding prompt eliminates fabricated citations"
            ],
            C_AMBER
        ),
        (
            "Persistence & Database",
            "SQLite • SQLAlchemy ORM",
            [
                "Relational user, project, paper, and session storage",
                "Persistent disk storage with clean schema integrity",
                "Fast serialization with Pydantic response models"
            ],
            C_ROSE
        )
    ]

    coords_6 = [
        (Inches(0.8), Inches(1.6), Inches(3.7), Inches(2.45)),
        (Inches(4.8), Inches(1.6), Inches(3.7), Inches(2.45)),
        (Inches(8.8), Inches(1.6), Inches(3.7), Inches(2.45)),
        (Inches(0.8), Inches(4.35), Inches(3.7), Inches(2.45)),
        (Inches(4.8), Inches(4.35), Inches(3.7), Inches(2.45)),
        (Inches(8.8), Inches(4.35), Inches(3.7), Inches(2.45))
    ]

    for idx, (t_cat, t_name, t_bullets, col) in enumerate(tech_stack):
        x, y, w, h = coords_6[idx]
        add_card(s7, x, y, w, h, C_CARD, C_BORDER)

        bar = s7.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, Inches(0.08))
        bar.fill.solid()
        bar.fill.fore_color.rgb = col
        bar.line.fill.background()

        tb = s7.shapes.add_textbox(x + Inches(0.18), y + Inches(0.15), w - Inches(0.36), h - Inches(0.28))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        r1 = p1.add_run()
        r1.text = t_cat.upper()
        r1.font.size = Pt(9.5)
        r1.font.bold = True
        r1.font.color.rgb = col
        r1.font.name = "Segoe UI"

        p2 = tf.add_paragraph()
        p2.space_before = Pt(2)
        r2 = p2.add_run()
        r2.text = t_name
        r2.font.size = Pt(12)
        r2.font.bold = True
        r2.font.color.rgb = C_TEXT_WHITE
        r2.font.name = "Segoe UI"

        for b_text in t_bullets:
            p_b = tf.add_paragraph()
            p_b.space_before = Pt(4)
            r_dot = p_b.add_run()
            r_dot.text = "• "
            r_dot.font.bold = True
            r_dot.font.size = Pt(10)
            r_dot.font.color.rgb = col

            r_txt = p_b.add_run()
            r_txt.text = b_text
            r_txt.font.size = Pt(10)
            r_txt.font.color.rgb = C_TEXT_LIGHT
            r_txt.font.name = "Segoe UI"

    s7.notes_slide.notes_text_frame.text = (
        "Slide 7 outlines the exact technology stack powering ResearchMate AI. "
        "React 18 and Vite on the frontend; Python 3.12 and FastAPI on the backend; PyMuPDF for single-pass PDF extraction; "
        "a memory-optimized singleton ONNX all-MiniLM-L6-v2 runtime with ChromaDB; Google Gemini API with fallback cascade; and SQLite + SQLAlchemy."
    )

    # =========================================================================
    # SLIDE 8: CORE MODULES AND FEATURES (4 Core Modules)
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_bg(s8)
    add_header(s8, "Core Modules: 4 Pillars of the Academic Workspace", "Modules & Features", "08 / 12")

    modules = [
        (
            "1. Research Dashboard & Analytics",
            "Real-time collection statistics • Recharts publication year timeline • Ingestion & indexing status breakdown • Recent activity streams.",
            C_SKY
        ),
        (
            "2. Research Paper Library",
            "Multi-PDF upload • Automated bibliographic extraction (Title, Authors, Abstract, Year) • Search & filter • Project-level isolation.",
            C_BLUE
        ),
        (
            "3. AI Research Assistant (RAG)",
            "Multi-document Q&A • 'Reset to All' scope toggle • Balanced retrieval diversity • Clickable [Paper, p. X] citation modals.",
            C_INDIGO
        ),
        (
            "4. Paper Comparison Matrix",
            "9-axis comparative synthesis: Objectives, Methodologies, Algorithms, Datasets, Metrics, and Results contrasted side-by-side.",
            C_EMERALD
        )
    ]

    for idx, (m_title, m_desc, col) in enumerate(modules):
        y_pos = Inches(1.55 + idx * 1.32)
        add_card(s8, Inches(0.8), y_pos, Inches(6.2), Inches(1.2), C_CARD, C_BORDER)

        bar = s8.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), y_pos, Inches(0.08), Inches(1.2))
        bar.fill.solid()
        bar.fill.fore_color.rgb = col
        bar.line.fill.background()

        tb = s8.shapes.add_textbox(Inches(1.05), y_pos + Inches(0.12), Inches(5.8), Inches(1.0))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        r1 = p1.add_run()
        r1.text = m_title
        r1.font.size = Pt(12)
        r1.font.bold = True
        r1.font.color.rgb = C_TEXT_WHITE
        r1.font.name = "Segoe UI"

        p2 = tf.add_paragraph()
        p2.space_before = Pt(4)
        r2 = p2.add_run()
        r2.text = f"•  {m_desc}"
        r2.font.size = Pt(10)
        r2.font.color.rgb = C_TEXT_MUTED
        r2.font.name = "Segoe UI"

    add_card(s8, Inches(7.2), Inches(1.55), Inches(5.33), Inches(5.2), C_CARD_LIGHT, C_BORDER)
    
    tb_img_lbl = s8.shapes.add_textbox(Inches(7.35), Inches(1.65), Inches(5.0), Inches(0.35))
    tf_img_lbl = tb_img_lbl.text_frame
    p_il = tf_img_lbl.paragraphs[0]
    r = p_il.add_run()
    r.text = "APPLICATION UI • RESEARCH PAPER LIBRARY"
    r.font.size = Pt(10)
    r.font.bold = True
    r.font.color.rgb = C_SKY
    r.font.name = "Segoe UI"

    lib_img_path = os.path.join("presentation_assets", "2_library.png")
    if os.path.exists(lib_img_path):
        s8.shapes.add_picture(lib_img_path, Inches(7.35), Inches(2.05), width=Inches(5.03))

    tb_cap = s8.shapes.add_textbox(Inches(7.35), Inches(5.85), Inches(5.03), Inches(0.8))
    tf_cap = tb_cap.text_frame
    tf_cap.word_wrap = True
    p_cap = tf_cap.paragraphs[0]
    r = p_cap.add_run()
    r.text = "Live application screenshot: Bibliographic metadata extraction, indexing status badges, and project management."
    r.font.size = Pt(9.5)
    r.font.color.rgb = C_TEXT_MUTED
    r.font.name = "Segoe UI"

    s8.notes_slide.notes_text_frame.text = (
        "Slide 8 details the four core functional modules of ResearchMate AI: Research Dashboard & Analytics, "
        "Research Paper Library, AI Research Assistant (RAG), and the 9-Axis Paper Comparison Matrix, "
        "alongside an authentic screenshot of the Paper Library."
    )

    # =========================================================================
    # SLIDE 9: AI RESEARCH ASSISTANT & RAG PIPELINE
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_bg(s9)
    add_header(s9, "AI Research Assistant: Grounded Multi-Doc RAG Pipeline", "RAG Pipeline", "09 / 12")

    steps = [
        ("Step 1: Ingestion", "PyMuPDF single-pass text & page extraction.", C_SKY),
        ("Step 2: Chunking", "180-word sliding window (35-word overlap).", C_BLUE),
        ("Step 3: Embedding", "Singleton ONNX MiniLM 384-d dense vectors.", C_INDIGO),
        ("Step 4: Diversity Search", "Per-paper top-k slicing ensures multi-doc coverage.", C_EMERALD),
        ("Step 5: Synthesis", "Gemini generates cited Markdown with [Paper, p. X].", C_AMBER)
    ]

    card_w = Inches(2.25)
    card_gap = Inches(0.18)
    start_x = Inches(0.8)

    for idx, (st_title, st_desc, col) in enumerate(steps):
        x = start_x + idx * (card_w + card_gap)
        add_card(s9, x, Inches(1.6), card_w, Inches(2.1), C_CARD, C_BORDER)

        bar = s9.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, Inches(1.6), card_w, Inches(0.08))
        bar.fill.solid()
        bar.fill.fore_color.rgb = col
        bar.line.fill.background()

        tb = s9.shapes.add_textbox(x + Inches(0.12), Inches(1.75), card_w - Inches(0.24), Inches(1.8))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        r1 = p1.add_run()
        r1.text = st_title
        r1.font.size = Pt(11)
        r1.font.bold = True
        r1.font.color.rgb = col
        r1.font.name = "Segoe UI"

        p2 = tf.add_paragraph()
        p2.space_before = Pt(6)
        r2 = p2.add_run()
        r2.text = f"•  {st_desc}"
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = C_TEXT_LIGHT
        r2.font.name = "Segoe UI"

    guarantees = [
        (
            "Source Diversity Algorithm",
            [
                "Eliminates single-paper retrieval dominance",
                "Applies per-paper chunk slicing (per_paper_k)",
                "Guarantees balanced context across all selected papers"
            ],
            C_SKY
        ),
        (
            "Strict Grounding & Anti-Hallucination",
            [
                "Requires explicit [Paper Title, p. X] page citation",
                "Explicitly acknowledges missing info rather than guessing",
                "Zero fabricated citations or non-existent authors"
            ],
            C_INDIGO
        ),
        (
            "Interactive Citation Inspector",
            [
                "Clickable citation badges rendered in chat UI",
                "Opens modal with original paper name & exact page number",
                "Displays verbatim source passage retrieved from ChromaDB"
            ],
            C_EMERALD
        )
    ]

    for idx, (g_title, g_bullets, col) in enumerate(guarantees):
        x = Inches(0.8 + idx * 4.05)
        add_card(s9, x, Inches(3.95), Inches(3.85), Inches(2.85), C_CARD_LIGHT, C_BORDER)

        bar = s9.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, Inches(3.95), Inches(0.08), Inches(2.85))
        bar.fill.solid()
        bar.fill.fore_color.rgb = col
        bar.line.fill.background()

        tb = s9.shapes.add_textbox(x + Inches(0.2), Inches(4.1), Inches(3.45), Inches(2.55))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        r1 = p1.add_run()
        r1.text = g_title
        r1.font.size = Pt(12)
        r1.font.bold = True
        r1.font.color.rgb = C_TEXT_WHITE
        r1.font.name = "Segoe UI"

        for b_text in g_bullets:
            p = tf.add_paragraph()
            p.space_before = Pt(8)
            r_dot = p.add_run()
            r_dot.text = "• "
            r_dot.font.bold = True
            r_dot.font.size = Pt(10.5)
            r_dot.font.color.rgb = col

            r_txt = p.add_run()
            r_txt.text = b_text
            r_txt.font.size = Pt(10.5)
            r_txt.font.color.rgb = C_TEXT_LIGHT
            r_txt.font.name = "Segoe UI"

    s9.notes_slide.notes_text_frame.text = (
        "Slide 9 details our multi-document RAG pipeline: single-pass ingestion, 180-word chunking aligned to MiniLM's 256-token window, "
        "singleton ONNX embeddings, per-paper diversity retrieval, and Gemini synthesis with clickable citation badges."
    )

    # =========================================================================
    # SLIDE 10: IMPLEMENTATION & APPLICATION SCREENSHOTS
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_bg(s10)
    add_header(s10, "System Demonstration: Genuine Application Screenshots", "Implementation UI", "10 / 12")

    shots = [
        (
            "1. Research Dashboard",
            [
                "Real-time paper & project analytics",
                "Recharts publication year trends",
                "Vector indexing status indicators"
            ],
            "1_dashboard.png",
            Inches(0.8), Inches(1.55)
        ),
        (
            "2. Paper Library",
            [
                "Multi-file PDF upload with drag & drop",
                "Automated bibliographic metadata",
                "Search, filter & project scoping"
            ],
            "2_library.png",
            Inches(6.8), Inches(1.55)
        ),
        (
            "3. AI Research Assistant (RAG)",
            [
                "Multi-doc Q&A with Markdown",
                "Scope toggle: Reset to All vs Selected",
                "Clickable [Paper, p. X] citation badges"
            ],
            "3_assistant.png",
            Inches(0.8), Inches(4.35)
        ),
        (
            "4. Paper Comparison Matrix",
            [
                "9-axis comparative synthesis table",
                "Contrasts datasets, models & results",
                "Side-by-side multi-paper alignment"
            ],
            "4_comparison.png",
            Inches(6.8), Inches(4.35)
        )
    ]

    for title, bullets, filename, x, y in shots:
        w_card = Inches(5.7)
        h_card = Inches(2.65)
        add_card(s10, x, y, w_card, h_card, C_CARD, C_BORDER)

        img_p = os.path.join("presentation_assets", filename)
        if os.path.exists(img_p):
            s10.shapes.add_picture(img_p, x + Inches(0.12), y + Inches(0.12), width=Inches(3.45))

        tb = s10.shapes.add_textbox(x + Inches(3.7), y + Inches(0.15), Inches(1.88), Inches(2.35))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        r1 = p1.add_run()
        r1.text = title
        r1.font.size = Pt(11)
        r1.font.bold = True
        r1.font.color.rgb = C_SKY
        r1.font.name = "Segoe UI"

        for b_text in bullets:
            p = tf.add_paragraph()
            p.space_before = Pt(6)
            r_dot = p.add_run()
            r_dot.text = "• "
            r_dot.font.bold = True
            r_dot.font.size = Pt(9.5)
            r_dot.font.color.rgb = C_SKY

            r_txt = p.add_run()
            r_txt.text = b_text
            r_txt.font.size = Pt(9.5)
            r_txt.font.color.rgb = C_TEXT_LIGHT
            r_txt.font.name = "Segoe UI"

    s10.notes_slide.notes_text_frame.text = (
        "Slide 10 showcases genuine screenshots captured from the running ResearchMate AI application across all four core modules."
    )

    # =========================================================================
    # SLIDE 11: TESTING AND RESULTS
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_bg(s11)
    add_header(s11, "Verification & Results: Rigorous Full-Stack Testing", "Testing & Results", "11 / 12")

    test_cols = [
        (
            "BACKEND PYTEST SUITE",
            "15 / 15 Passed • 43.91 Seconds",
            [
                "Auth & Health APIs: /health, /docs, JWT & demo login",
                "Project API: Multi-project context isolation verified",
                "Upload Pipeline: Multi-PDF ingestion & error handling",
                "Singleton ONNX: Session & tokenizer reused across calls",
                "Vector Store: ChromaDB persistence & collection isolation",
                "Chat/RAG: Balanced per-paper retrieval & citations",
                "Analytics API: Dashboard statistics & distributions"
            ],
            C_EMERALD,
            Inches(0.8)
        ),
        (
            "FRONTEND PRODUCTION BUILD",
            "Vite Optimized • 7.47 Seconds",
            [
                "JSX / Module Bundle: 2,847 modules compiled cleanly",
                "Markdown Engine: react-markdown + remark-gfm rendering",
                "Upload UX: Surfaces backend errors & partial failures",
                "Theme System: Consistent dark navy & light mode styling",
                "Mobile Responsive: Verified at 1440px, 768px, and 375px",
                "SPA Routing: Vercel rewrite configuration verified"
            ],
            C_SKY,
            Inches(4.8)
        ),
        (
            "END-TO-END VERIFICATION",
            "Multi-Paper RAG & Citation Check",
            [
                "Ingested Benchmark Papers: Attention, BERT, and LoRA",
                "Multi-Doc RAG: Retrieved balanced chunks across papers",
                "Citation Check: 100% verified [Paper, p. X] references",
                "Matrix Generated: Side-by-side 9-axis comparative table",
                "ChromaDB Persistence: Verified disk write & query integrity",
                "Error Handling: Verified 400/422 responses on bad PDFs"
            ],
            C_AMBER,
            Inches(8.8)
        )
    ]

    for title, subtitle, bullets, col, x_pos in test_cols:
        add_card(s11, x_pos, Inches(1.6), Inches(3.7), Inches(5.2), C_CARD, C_BORDER)

        bar = s11.shapes.add_shape(MSO_SHAPE.RECTANGLE, x_pos, Inches(1.6), Inches(3.7), Inches(0.72))
        bar.fill.solid()
        bar.fill.fore_color.rgb = col
        bar.line.fill.background()

        tb_h = s11.shapes.add_textbox(x_pos + Inches(0.15), Inches(1.65), Inches(3.4), Inches(0.62))
        tf_h = tb_h.text_frame
        tf_h.word_wrap = True
        p_th = tf_h.paragraphs[0]
        r = p_th.add_run()
        r.text = title
        r.font.size = Pt(11)
        r.font.bold = True
        r.font.color.rgb = C_TEXT_WHITE
        r.font.name = "Segoe UI"

        p_sub = tf_h.add_paragraph()
        r = p_sub.add_run()
        r.text = subtitle
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(241, 245, 249)
        r.font.name = "Segoe UI"

        tb_b = s11.shapes.add_textbox(x_pos + Inches(0.15), Inches(2.45), Inches(3.4), Inches(4.25))
        tf_b = tb_b.text_frame
        tf_b.word_wrap = True

        for b_idx, bullet in enumerate(bullets):
            p = tf_b.paragraphs[0] if b_idx == 0 else tf_b.add_paragraph()
            p.space_before = Pt(6)
            r_b = p.add_run()
            r_b.text = "• "
            r_b.font.bold = True
            r_b.font.size = Pt(9.5)
            r_b.font.color.rgb = col
            
            r_txt = p.add_run()
            r_txt.text = bullet
            r_txt.font.size = Pt(9.5)
            r_txt.font.color.rgb = C_TEXT_LIGHT
            r_txt.font.name = "Segoe UI"

    s11.notes_slide.notes_text_frame.text = (
        "Slide 11 presents our verified test results: 15 out of 15 backend pytest tests passed in 43.91 seconds "
        "(including singleton ONNX reuse, multi-PDF upload, and error-handling tests), and the Vite frontend production build "
        "compiled 2,847 modules cleanly in 7.47 seconds."
    )

    # =========================================================================
    # SLIDE 12: CONCLUSION AND FUTURE ENHANCEMENTS
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    set_bg(s12)
    add_header(s12, "Conclusion & Future Roadmap", "Summary & Outlook", "12 / 12")

    concl_cards = [
        (
            "PROJECT CONTRIBUTIONS",
            "Delivered Full-Stack Features",
            [
                "Production full-stack AI research platform",
                "Grounded multi-doc RAG with source diversity",
                "Zero hallucinations via page provenance [p. X]",
                "Automated 9-axis paper comparison matrix",
                "Interactive Recharts research analytics dashboard",
                "Singleton low-RAM ONNX embedding pipeline"
            ],
            C_SKY,
            Inches(0.8)
        ),
        (
            "CURRENT LIMITATIONS",
            "Technical Constraints",
            [
                "Digital PDFs: Selectable text only (no OCR yet)",
                "API Quotas: Bound by Google Gemini rate limits",
                "Free-Tier RAM: Large batches constrained by 512 MB",
                "Token Limits: 20+ papers need progressive summarization"
            ],
            C_AMBER,
            Inches(4.8)
        ),
        (
            "FUTURE ENHANCEMENTS",
            "Academic Roadmap",
            [
                "OCR Integration: Tesseract for scanned papers",
                "Async Queues: Celery + Redis background workers",
                "Automated Literature Review: 8-section synthesis & export",
                "Citation Graph: Interactive D3.js visual network"
            ],
            C_EMERALD,
            Inches(8.8)
        )
    ]

    for title, subtitle, bullets, col, x_pos in concl_cards:
        add_card(s12, x_pos, Inches(1.6), Inches(3.7), Inches(4.25), C_CARD, C_BORDER)

        bar = s12.shapes.add_shape(MSO_SHAPE.RECTANGLE, x_pos, Inches(1.6), Inches(3.7), Inches(0.08))
        bar.fill.solid()
        bar.fill.fore_color.rgb = col
        bar.line.fill.background()

        tb_h = s12.shapes.add_textbox(x_pos + Inches(0.18), Inches(1.75), Inches(3.34), Inches(0.62))
        tf_h = tb_h.text_frame
        tf_h.word_wrap = True
        p_th = tf_h.paragraphs[0]
        r = p_th.add_run()
        r.text = title
        r.font.size = Pt(11.5)
        r.font.bold = True
        r.font.color.rgb = col
        r.font.name = "Segoe UI"

        p_sub = tf_h.add_paragraph()
        r = p_sub.add_run()
        r.text = subtitle
        r.font.size = Pt(9.5)
        r.font.color.rgb = C_TEXT_MUTED
        r.font.name = "Segoe UI"

        tb_b = s12.shapes.add_textbox(x_pos + Inches(0.18), Inches(2.45), Inches(3.34), Inches(3.25))
        tf_b = tb_b.text_frame
        tf_b.word_wrap = True

        for b_idx, bullet in enumerate(bullets):
            p = tf_b.paragraphs[0] if b_idx == 0 else tf_b.add_paragraph()
            p.space_before = Pt(6)
            r_b = p.add_run()
            r_b.text = "• "
            r_b.font.bold = True
            r_b.font.size = Pt(9.5)
            r_b.font.color.rgb = col
            
            r_text = p.add_run()
            r_text.text = bullet
            r_text.font.size = Pt(9.5)
            r_text.font.color.rgb = C_TEXT_LIGHT
            r_text.font.name = "Segoe UI"

    add_card(s12, Inches(0.8), Inches(6.05), Inches(11.7), Inches(0.95), C_CARD_LIGHT, C_BORDER_ACCENT)
    tb_ty = s12.shapes.add_textbox(Inches(1.0), Inches(6.12), Inches(11.3), Inches(0.8))
    tf_ty = tb_ty.text_frame
    tf_ty.word_wrap = True

    p_ty = tf_ty.paragraphs[0]
    p_ty.alignment = PP_ALIGN.CENTER
    r_ty1 = p_ty.add_run()
    r_ty1.text = "THANK YOU! • QUESTIONS & DISCUSSION\n"
    r_ty1.font.size = Pt(13)
    r_ty1.font.bold = True
    r_ty1.font.color.rgb = C_SKY
    r_ty1.font.name = "Segoe UI"

    r_ty2 = p_ty.add_run()
    r_ty2.text = "ResearchMate AI — AI-Powered Academic Research Assistant & Multi-Paper Analysis Platform • MCA Capstone 2025–2026"
    r_ty2.font.size = Pt(10)
    r_ty2.font.color.rgb = C_TEXT_MUTED
    r_ty2.font.name = "Segoe UI"

    s12.notes_slide.notes_text_frame.text = (
        "In conclusion, ResearchMate AI provides a reliable, hallucination-free research platform for analyzing complex academic literature. "
        "Thank you respected committee members and faculty guides for your time and guidance. I now welcome your questions and discussion."
    )

    out_path = os.path.join(os.getcwd(), "ResearchMate_AI_Presentation.pptx")
    try:
        prs.save(out_path)
        print(f"Successfully generated presentation with {len(prs.slides)} slides at: {out_path}")
        return out_path
    except PermissionError:
        alt_path = os.path.join(os.getcwd(), "ResearchMate_AI_Presentation_Updated.pptx")
        prs.save(alt_path)
        print(f"Notice: {out_path} is locked by PowerPoint. Saved to: {alt_path}")
        return alt_path

if __name__ == "__main__":
    build_presentation()
