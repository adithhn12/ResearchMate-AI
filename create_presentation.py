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
        # Category badge
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

        # Title text
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

        # Slide Number
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

    # Decorative header banner
    accent_bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.8), Inches(1.2), Inches(0.08))
    accent_bar.fill.solid()
    accent_bar.fill.fore_color.rgb = C_SKY
    accent_bar.line.fill.background()

    # Degree label
    tb_deg = s1.shapes.add_textbox(Inches(0.8), Inches(1.0), Inches(11.0), Inches(0.35))
    tf_deg = tb_deg.text_frame
    p_deg = tf_deg.paragraphs[0]
    r_deg = p_deg.add_run()
    r_deg.text = "MASTER OF COMPUTER APPLICATIONS (MCA) • CAPSTONE PROJECT REVIEW"
    r_deg.font.size = Pt(11)
    r_deg.font.bold = True
    r_deg.font.color.rgb = C_SKY
    r_deg.font.name = "Segoe UI"

    # Main Project Title
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

    # Subtitle
    tb_sub = s1.shapes.add_textbox(Inches(0.8), Inches(2.55), Inches(11.5), Inches(0.5))
    tf_sub = tb_sub.text_frame
    p_s = tf_sub.paragraphs[0]
    r_s = p_s.add_run()
    r_s.text = "AI-Powered Academic Research Assistant & Multi-Paper Analysis Platform"
    r_s.font.size = Pt(19)
    r_s.font.bold = True
    r_s.font.color.rgb = C_TEXT_LIGHT
    r_s.font.name = "Segoe UI"

    # Crisp Tagline
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

    # Metadata Cards (2 columns at bottom)
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
        "This project was engineered to solve the core challenges students and researchers face when synthesizing multiple academic publications. "
        "Over these 10 slides, I will walk you through the problem statement, our architectural solution, "
        "the technology stack, our implemented core modules, the multi-document RAG pipeline, "
        "genuine application screenshots, rigorous test verification, and future enhancements."
    )

    # =========================================================================
    # SLIDE 2: PROBLEM STATEMENT
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_bg(s2)
    add_header(s2, "The Research Bottleneck: Challenges in Multi-Paper Analysis", "Problem Statement", "02 / 10")

    problems = [
        (
            "Manual Literature Ingestion",
            [
                "Weeks spent reading 20+ page academic PDFs manually",
                "Critical findings & hyperparameters easily overlooked in dense text",
                "Severe cognitive fatigue when analyzing dozens of publications"
            ],
            C_AMBER
        ),
        (
            "Fragmented Methodology Comparison",
            [
                "Manual side-by-side note-taking is slow and highly error-prone",
                "Difficult to contrast algorithms, datasets, metrics & benchmark scores",
                "No standardized matrix for comparing differing experimental setups"
            ],
            C_SKY
        ),
        (
            "Multi-Document Context Fragmentation",
            [
                "Standard search tools only retrieve isolated keywords without synthesis",
                "Correlating findings across multiple independent papers is difficult",
                "Lack of structured per-project document workspaces and indexing"
            ],
            C_INDIGO
        ),
        (
            "Generic LLM Hallucinations",
            [
                "Commercial chatbots fabricate non-existent citations & author names",
                "Zero page-level provenance or verifiable source backing",
                "Single-document retrieval bias ignores multi-paper context"
            ],
            C_ROSE
        )
    ]

    coords_2x2 = [
        (Inches(0.8), Inches(1.6), Inches(5.6), Inches(2.45)),
        (Inches(6.8), Inches(1.6), Inches(5.7), Inches(2.45)),
        (Inches(0.8), Inches(4.35), Inches(5.6), Inches(2.45)),
        (Inches(6.8), Inches(4.35), Inches(5.7), Inches(2.45))
    ]

    for idx, (p_title, p_bullets, col) in enumerate(problems):
        x, y, w, h = coords_2x2[idx]
        add_card(s2, x, y, w, h, C_CARD, C_BORDER)
        
        bar = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, Inches(0.1), h)
        bar.fill.solid()
        bar.fill.fore_color.rgb = col
        bar.line.fill.background()

        tb = s2.shapes.add_textbox(x + Inches(0.3), y + Inches(0.18), w - Inches(0.45), h - Inches(0.35))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        r1 = p1.add_run()
        r1.text = f"CHALLENGE 0{idx+1} • {p_title}"
        r1.font.size = Pt(13)
        r1.font.bold = True
        r1.font.color.rgb = col
        r1.font.name = "Segoe UI"

        for b_text in p_bullets:
            p = tf.add_paragraph()
            p.space_before = Pt(8)
            r_dot = p.add_run()
            r_dot.text = "• "
            r_dot.font.bold = True
            r_dot.font.size = Pt(11)
            r_dot.font.color.rgb = col

            r_txt = p.add_run()
            r_txt.text = b_text
            r_txt.font.size = Pt(11)
            r_txt.font.color.rgb = C_TEXT_LIGHT
            r_txt.font.name = "Segoe UI"

    s2.notes_slide.notes_text_frame.text = (
        "In this slide, we examine the fundamental problem motivation. "
        "First, manual paper analysis takes weeks of laborious reading where researchers frequently miss critical methodological nuances. "
        "Second, cross-evaluating multiple papers side-by-side to understand trade-offs between algorithms, datasets, and metrics is highly fragmented. "
        "Third, standard search tools fail to synthesize information across multiple documents simultaneously. "
        "Fourth and most critically, generic AI models like ChatGPT hallucinate non-existent authors, fabricate citations, and cannot provide verifiable PDF page references. "
        "ResearchMate AI was engineered specifically to solve these critical bottlenecks."
    )

    # =========================================================================
    # SLIDE 3: PROPOSED SOLUTION AND OBJECTIVES
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_bg(s3)
    add_header(s3, "Proposed Solution: ResearchMate AI & Core Objectives", "Solution & Goals", "03 / 10")

    # Left Overview Card
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

    # Right Objectives Cards (4 Objectives)
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
        "Here we introduce the proposed solution and core technical objectives of ResearchMate AI. "
        "Our system simplifies academic paper analysis through four distinct engineering objectives: "
        "Objective 1: Drag-and-drop PDF ingestion with automated bibliographic metadata extraction via PyMuPDF. "
        "Objective 2: A strictly grounded multi-document Retrieval Augmented Generation pipeline where every claim links directly to its source paper and exact page number. "
        "Objective 3: Structured comparative matrices across 9 academic axes to provide instant clarity on differing methodologies, algorithms, and benchmarks. "
        "Objective 4: Interactive research analytics providing real-time visibility into collection composition and indexing status."
    )

    # =========================================================================
    # SLIDE 4: SYSTEM ARCHITECTURE
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_bg(s4)
    add_header(s4, "System Architecture: Decoupled Multi-Tier Platform", "Architecture", "04 / 10")

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
                "Asynchronous high-throughput REST API",
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
                "PyMuPDF fast C-level text streaming",
                "1000-char sliding window (200 overlap)",
                "all-MiniLM-L6-v2 384-d dense vectors",
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
        add_card(s4, x_pos, Inches(1.6), Inches(2.8), Inches(4.45), C_CARD, C_BORDER)
        
        header_shape = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, x_pos, Inches(1.6), Inches(2.8), Inches(0.72))
        header_shape.fill.solid()
        header_shape.fill.fore_color.rgb = col
        header_shape.line.fill.background()

        tb_h = s4.shapes.add_textbox(x_pos + Inches(0.12), Inches(1.65), Inches(2.56), Inches(0.62))
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

        tb_b = s4.shapes.add_textbox(x_pos + Inches(0.15), Inches(2.45), Inches(2.5), Inches(3.45))
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

    # Bottom Data Flow Bar
    add_card(s4, Inches(0.8), Inches(6.22), Inches(11.95), Inches(0.78), C_CARD_LIGHT, C_BORDER)
    tb_flow = s4.shapes.add_textbox(Inches(1.0), Inches(6.32), Inches(11.5), Inches(0.58))
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
        "PDF Stream → PyMuPDF Text Extraction → 1000-ch Chunking → all-MiniLM-L6-v2 Embeddings → "
        "ChromaDB Storage → Diversity Retrieval → Gemini Synthesis → Grounded Output with Citations [p. X]"
    )
    r_f2.font.size = Pt(10)
    r_f2.font.color.rgb = C_TEXT_LIGHT
    r_f2.font.name = "Segoe UI"

    s4.notes_slide.notes_text_frame.text = (
        "This slide depicts the architectural blueprint of ResearchMate AI directly derived from our implemented codebase. "
        "The architecture is organized into four distinct tiers: "
        "First, the Client Tier built with React 18, Vite, and Tailwind CSS, featuring rich Recharts visuals and Markdown formatting. "
        "Second, the Application API Tier powered by FastAPI and Python 3.12, providing async endpoints, strict Pydantic validation, and project context isolation. "
        "Third, the Processing and Vector RAG Tier utilizing PyMuPDF for C-level text streaming, a sliding window chunking algorithm, and HuggingFace MiniLM embeddings stored in persistent ChromaDB. "
        "Fourth, the Intelligence & Storage Tier leveraging Google Gemini API with fallback cascade, persistent SQLite via SQLAlchemy, and JSON serialization."
    )

    # =========================================================================
    # SLIDE 5: TECHNOLOGY STACK
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_bg(s5)
    add_header(s5, "Technology Stack: Selected Tools & Technical Roles", "Technology Stack", "05 / 10")

    tech_stack = [
        (
            "Frontend Layer",
            "React 18 • Vite • Tailwind CSS",
            [
                "Modular React 18 SPA with dark navy academic theme",
                "Ultra-fast 3.88s production build via Vite bundler",
                "Interactive Recharts analytics and Lucide React icons"
            ],
            C_SKY
        ),
        (
            "Backend Framework",
            "Python 3.12 • FastAPI • Uvicorn",
            [
                "High-throughput asynchronous REST API endpoints",
                "Strict Pydantic v2 data models & automatic Swagger docs",
                "JWT authentication with secure bcrypt password hashing"
            ],
            C_BLUE
        ),
        (
            "PDF Parsing & Ingestion",
            "PyMuPDF (fitz)",
            [
                "C-accelerated high-speed PDF text stream extraction",
                "Automated title, author, abstract, year & keyword parsing",
                "Zero OCR overhead for digital research publications"
            ],
            C_INDIGO
        ),
        (
            "Vector Embeddings & Storage",
            "all-MiniLM-L6-v2 • ChromaDB",
            [
                "384-dimensional dense semantic vectors via local ONNX",
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
                "Sub-second response latency for interactive RAG Q&A",
                "Strict grounding prompt eliminates fabricated citations"
            ],
            C_AMBER
        ),
        (
            "Persistence & Database",
            "SQLite • SQLAlchemy ORM",
            [
                "Relational user, project, and session storage via SQLAlchemy",
                "Persistent disk storage with migration-free schema integrity",
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
        add_card(s5, x, y, w, h, C_CARD, C_BORDER)

        bar = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, Inches(0.08))
        bar.fill.solid()
        bar.fill.fore_color.rgb = col
        bar.line.fill.background()

        tb = s5.shapes.add_textbox(x + Inches(0.18), y + Inches(0.15), w - Inches(0.36), h - Inches(0.28))
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

    s5.notes_slide.notes_text_frame.text = (
        "Slide 5 outlines the exact, verified technology stack powering ResearchMate AI. "
        "Every library and framework was carefully chosen for performance, reproducibility, and production stability. "
        "On the frontend, React 18 and Vite deliver ultra-fast production builds with Tailwind CSS and Recharts. "
        "On the backend, Python 3.12 and FastAPI provide async performance and Pydantic v2 data serialization. "
        "For PDF handling, PyMuPDF provides high-speed C-level text streaming without heavy dependencies. "
        "For vector search, we use HuggingFace all-MiniLM-L6-v2 via ChromaDB's ONNX runtime, generating 384-dimensional dense vectors locally. "
        "For language reasoning, we integrate the Google Gemini API with a robust multi-model fallback cascade. "
        "Finally, persistence is handled by SQLite and SQLAlchemy with persistent disk mount support."
    )

    # =========================================================================
    # SLIDE 6: CORE MODULES AND FEATURES (4 Core Modules)
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_bg(s6)
    add_header(s6, "Core Modules: 4 Pillars of the Academic Workspace", "Modules & Features", "06 / 10")

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
        add_card(s6, Inches(0.8), y_pos, Inches(6.2), Inches(1.2), C_CARD, C_BORDER)

        bar = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), y_pos, Inches(0.08), Inches(1.2))
        bar.fill.solid()
        bar.fill.fore_color.rgb = col
        bar.line.fill.background()

        tb = s6.shapes.add_textbox(Inches(1.05), y_pos + Inches(0.12), Inches(5.8), Inches(1.0))
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

    # Right: Embedded Genuine Screenshot (Paper Library & Workspace)
    add_card(s6, Inches(7.2), Inches(1.55), Inches(5.33), Inches(5.2), C_CARD_LIGHT, C_BORDER)
    
    tb_img_lbl = s6.shapes.add_textbox(Inches(7.35), Inches(1.65), Inches(5.0), Inches(0.35))
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
        s6.shapes.add_picture(lib_img_path, Inches(7.35), Inches(2.05), width=Inches(5.03))

    tb_cap = s6.shapes.add_textbox(Inches(7.35), Inches(5.85), Inches(5.03), Inches(0.8))
    tf_cap = tb_cap.text_frame
    tf_cap.word_wrap = True
    p_cap = tf_cap.paragraphs[0]
    r = p_cap.add_run()
    r.text = "Live application screenshot: Bibliographic metadata extraction, indexing status badges, and project management."
    r.font.size = Pt(9.5)
    r.font.color.rgb = C_TEXT_MUTED
    r.font.name = "Segoe UI"

    s6.notes_slide.notes_text_frame.text = (
        "Slide 6 details the four core functional modules that constitute ResearchMate AI. "
        "Module 1 is the Research Dashboard: real-time metrics, Recharts publication timeline, and vector indexing breakdown. "
        "Module 2 is the Research Paper Library: researchers upload PDFs, and the system automatically extracts title, authors, abstract, publication year, and keywords, isolating papers per research project. "
        "Module 3 is the AI Research Assistant: enabling multi-turn RAG conversations with selective query scoping and interactive citation verification. "
        "Module 4 is the Paper Comparison Matrix: automatically cross-evaluating multiple papers across 9 formal academic axes. "
        "On the right, we display an authentic screenshot from the running application showing the paper library, indexing badges, and metadata cards."
    )

    # =========================================================================
    # SLIDE 7: AI RESEARCH ASSISTANT & RAG WORKFLOW
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_bg(s7)
    add_header(s7, "AI Research Assistant: Grounded Multi-Doc RAG Workflow", "RAG Pipeline", "07 / 10")

    # Flowchart: 5 Step Cards horizontally across top
    steps = [
        ("Step 1: Ingestion", "PyMuPDF (fitz) extracts text stream & page numbers.", C_SKY),
        ("Step 2: Chunking", "1,000-char sliding window with 200-char overlap.", C_BLUE),
        ("Step 3: Embedding", "all-MiniLM-L6-v2 maps text to 384-d dense vectors.", C_INDIGO),
        ("Step 4: Diversity Search", "Per-paper top-k slicing ensures multi-doc coverage.", C_EMERALD),
        ("Step 5: Synthesis", "Gemini generates cited Markdown with [Paper, p. X].", C_AMBER)
    ]

    card_w = Inches(2.25)
    card_gap = Inches(0.18)
    start_x = Inches(0.8)

    for idx, (st_title, st_desc, col) in enumerate(steps):
        x = start_x + idx * (card_w + card_gap)
        add_card(s7, x, Inches(1.6), card_w, Inches(2.1), C_CARD, C_BORDER)

        bar = s7.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, Inches(1.6), card_w, Inches(0.08))
        bar.fill.solid()
        bar.fill.fore_color.rgb = col
        bar.line.fill.background()

        tb = s7.shapes.add_textbox(x + Inches(0.12), Inches(1.75), card_w - Inches(0.24), Inches(1.8))
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

    # Lower Section: Key Technical Guarantees
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
        add_card(s7, x, Inches(3.95), Inches(3.85), Inches(2.85), C_CARD_LIGHT, C_BORDER)

        bar = s7.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, Inches(3.95), Inches(0.08), Inches(2.85))
        bar.fill.solid()
        bar.fill.fore_color.rgb = col
        bar.line.fill.background()

        tb = s7.shapes.add_textbox(x + Inches(0.2), Inches(4.1), Inches(3.45), Inches(2.55))
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

    s7.notes_slide.notes_text_frame.text = (
        "Slide 7 walks through our custom multi-document Retrieval-Augmented Generation pipeline. "
        "Standard RAG implementations typically suffer from single-document bias: when querying 3 papers, 8 out of 8 retrieved chunks might come from just one paper. "
        "To solve this, our vector store service implements a per-paper retrieval diversity algorithm (`per_paper_k`) that guarantees chunks are retrieved from every selected paper. "
        "The workflow flows in five discrete steps: PyMuPDF extracts text streams; text is chunked into 1000-character windows with 200-character overlap; "
        "HuggingFace MiniLM embeds chunks into 384-dimensional vectors stored in ChromaDB; "
        "balanced similarity retrieval passes context to Google Gemini; and Gemini synthesizes Markdown with strict page citations `[Paper, p. X]`. "
        "In the frontend, these citations render as clickable pill badges: clicking a badge brings up the exact excerpt from the source PDF."
    )

    # =========================================================================
    # SLIDE 8: IMPLEMENTATION & APPLICATION SCREENSHOTS (4 Core Modules)
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_bg(s8)
    add_header(s8, "System Demonstration: Genuine Application Screenshots", "Implementation UI", "08 / 10")

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
        add_card(s8, x, y, w_card, h_card, C_CARD, C_BORDER)

        img_p = os.path.join("presentation_assets", filename)
        if os.path.exists(img_p):
            s8.shapes.add_picture(img_p, x + Inches(0.12), y + Inches(0.12), width=Inches(3.45))

        tb = s8.shapes.add_textbox(x + Inches(3.7), y + Inches(0.15), Inches(1.88), Inches(2.35))
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

    s8.notes_slide.notes_text_frame.text = (
        "Slide 8 showcases genuine, unedited screenshots captured from the running ResearchMate AI platform covering our four core modules. "
        "Top-left: The Research Intelligence Dashboard displaying total papers, projects, and publication year distribution via Recharts. "
        "Top-right: The Paper Library showing automated bibliographic metadata extraction and indexing status badges. "
        "Bottom-left: The AI Research Assistant demonstrating multi-turn RAG conversation with formatted Markdown and verified citation badges. "
        "Bottom-right: The 9-axis Paper Comparison Matrix contrasting machine learning methodologies side-by-side in an aligned table."
    )

    # =========================================================================
    # SLIDE 9: TESTING AND RESULTS
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_bg(s9)
    add_header(s9, "Verification & Results: Rigorous Full-Stack Testing", "Testing & Results", "09 / 10")

    test_cols = [
        (
            "BACKEND PYTEST SUITE",
            "12 / 12 Passed • 8.36 Seconds",
            [
                "Auth API: Registration, JWT login & demo-login verified",
                "Project API: Multi-project context isolation verified",
                "Paper API: PDF upload, PyMuPDF parsing & chunking",
                "Vector Store: ChromaDB persistence & collection isolation",
                "Chat/RAG: Session handling & balanced retrieval diversity",
                "Comparison API: 9-axis comparative matrix generation",
                "Analytics API: Real-time dashboard statistics & distributions"
            ],
            C_EMERALD,
            Inches(0.8)
        ),
        (
            "FRONTEND PRODUCTION BUILD",
            "Vite Optimized • 3.88 Seconds",
            [
                "TypeScript/JSX: Zero build errors or compiler warnings",
                "Vite Asset Bundler: Tree-shaking, splitting & minification",
                "Markdown Engine: react-markdown + remark-gfm rendering",
                "Theme System: Consistent dark navy & light mode styling",
                "Mobile Responsive: Verified at 1440px, 768px, and 375px",
                "SPA Routing: Vercel rewrite configuration verified"
            ],
            C_SKY,
            Inches(4.8)
        ),
        (
            "END-TO-END VERIFICATION",
            "verify_e2e.py • 8/8 Successful",
            [
                "Ingested 3 Papers: Attention, BERT, and LoRA",
                "Multi-Doc RAG: Retrieved 8 chunks across all 3 papers",
                "Citation Check: 100% verified [Paper, p. X] references",
                "Matrix Generated: Side-by-side 9-axis comparative table",
                "ChromaDB Persistence: Verified disk write & query integrity",
                "FastAPI Health & Docs: /health & /docs verified active in prod"
            ],
            C_AMBER,
            Inches(8.8)
        )
    ]

    for title, subtitle, bullets, col, x_pos in test_cols:
        add_card(s9, x_pos, Inches(1.6), Inches(3.7), Inches(5.2), C_CARD, C_BORDER)

        bar = s9.shapes.add_shape(MSO_SHAPE.RECTANGLE, x_pos, Inches(1.6), Inches(3.7), Inches(0.72))
        bar.fill.solid()
        bar.fill.fore_color.rgb = col
        bar.line.fill.background()

        tb_h = s9.shapes.add_textbox(x_pos + Inches(0.15), Inches(1.65), Inches(3.4), Inches(0.62))
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

        tb_b = s9.shapes.add_textbox(x_pos + Inches(0.15), Inches(2.45), Inches(3.4), Inches(4.25))
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

    s9.notes_slide.notes_text_frame.text = (
        "Slide 9 demonstrates our rigorous verification approach. "
        "We do not present hypothetical claims; all numbers reflect actual test execution. "
        "First, our backend test suite executed via pytest covers 12 distinct tests spanning authentication, project isolation, vector storage, RAG Q&A, and comparative analysis, passing completely in 8.36 seconds. "
        "Second, the frontend production build compiled via Vite in 3.88 seconds with zero errors and full mobile responsiveness. "
        "Third, our comprehensive end-to-end verification ingested three actual benchmark research papers: "
        "Attention Is All You Need, BERT, and LoRA. The RAG pipeline retrieved 8 distinct chunks across all three papers without bias, "
        "and constructed a side-by-side 9-axis comparative table. This proves the system is fully operational end-to-end."
    )

    # =========================================================================
    # SLIDE 10: CONCLUSION AND FUTURE ENHANCEMENTS
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_bg(s10)
    add_header(s10, "Conclusion & Future Roadmap", "Summary & Outlook", "10 / 10")

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
                "Production deployed on Vercel & Render"
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
                "Batch Ingestion: Sequential vector embeddings",
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
        add_card(s10, x_pos, Inches(1.6), Inches(3.7), Inches(4.25), C_CARD, C_BORDER)

        bar = s10.shapes.add_shape(MSO_SHAPE.RECTANGLE, x_pos, Inches(1.6), Inches(3.7), Inches(0.08))
        bar.fill.solid()
        bar.fill.fore_color.rgb = col
        bar.line.fill.background()

        tb_h = s10.shapes.add_textbox(x_pos + Inches(0.18), Inches(1.75), Inches(3.34), Inches(0.62))
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

        tb_b = s10.shapes.add_textbox(x_pos + Inches(0.18), Inches(2.45), Inches(3.34), Inches(3.25))
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

    # Bottom Thank You & Q&A Banner
    add_card(s10, Inches(0.8), Inches(6.05), Inches(11.7), Inches(0.95), C_CARD_LIGHT, C_BORDER_ACCENT)
    tb_ty = s10.shapes.add_textbox(Inches(1.0), Inches(6.12), Inches(11.3), Inches(0.8))
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

    s10.notes_slide.notes_text_frame.text = (
        "In conclusion, ResearchMate AI provides a reliable, hallucination-free research platform for analyzing complex academic literature. "
        "Our contributions include a fully functional multi-document RAG assistant with source diversity, guaranteed citation fidelity, automated 9-axis methodology comparison tables, and interactive research analytics. "
        "We are also transparent about our technical constraints: PyMuPDF requires selectable text streams, cloud LLMs are bound by rate quotas, and batch embeddings currently execute sequentially. "
        "Looking forward, our roadmap includes integrated OCR via Tesseract, asynchronous Celery task queues for high-volume indexing, full literature review synthesis, and interactive D3.js citation network visualization. "
        "Thank you respected committee members and faculty guides for your time and guidance. I now welcome your questions, feedback, and discussion."
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
