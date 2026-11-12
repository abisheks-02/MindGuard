from copy import deepcopy
from pathlib import Path
from shutil import copy2

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(r"C:\Projects\MindGuard")
TEMPLATE = ROOT / "PRS-Front_Page_Template.docx"
OUTPUT = ROOT / "MindGuard_PRS_Report_Completed.docx"


def set_run_font(run, size=12, bold=False, color=None):
    run.font.name = "Times New Roman"
    run._element.rPr.rFonts.set(qn("w:ascii"), "Times New Roman")
    run._element.rPr.rFonts.set(qn("w:hAnsi"), "Times New Roman")
    run.font.size = Pt(size)
    run.bold = bold
    if color:
        run.font.color.rgb = RGBColor(*color)


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def set_cell_margins(cell, top=90, start=100, bottom=90, end=100):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for m, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{m}"))
        if node is None:
            node = OxmlElement(f"w:{m}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def set_borders(table):
    tbl_pr = table._tbl.tblPr
    borders = tbl_pr.first_child_found_in("w:tblBorders")
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        element = borders.find(qn(f"w:{edge}"))
        if element is None:
            element = OxmlElement(f"w:{edge}")
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), "6")
        element.set(qn("w:space"), "0")
        element.set(qn("w:color"), "D9D9D9")


def setup_styles(doc):
    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Times New Roman"
    normal._element.rPr.rFonts.set(qn("w:ascii"), "Times New Roman")
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Times New Roman")
    normal.font.size = Pt(12)
    normal.paragraph_format.line_spacing = 1.15
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    for style_name, size in (("Heading 1", 13), ("Heading 2", 12), ("Heading 3", 12)):
        try:
            style = styles[style_name]
        except KeyError:
            style = styles.add_style(style_name, WD_STYLE_TYPE.PARAGRAPH)
        style.font.name = "Times New Roman"
        style._element.rPr.rFonts.set(qn("w:ascii"), "Times New Roman")
        style._element.rPr.rFonts.set(qn("w:hAnsi"), "Times New Roman")
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor(0, 0, 0)
        style.paragraph_format.space_before = Pt(12)
        style.paragraph_format.space_after = Pt(6)
        style.paragraph_format.keep_with_next = True


def add_page_number(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run()
    set_run_font(run, 10)
    fld_char1 = OxmlElement("w:fldChar")
    fld_char1.set(qn("w:fldCharType"), "begin")
    instr_text = OxmlElement("w:instrText")
    instr_text.set(qn("xml:space"), "preserve")
    instr_text.text = "PAGE"
    fld_char2 = OxmlElement("w:fldChar")
    fld_char2.set(qn("w:fldCharType"), "end")
    run._r.append(fld_char1)
    run._r.append(instr_text)
    run._r.append(fld_char2)


def replace_placeholders(doc):
    replacements = {
        "<< Project Title in CAPS  >>": "MINDGUARD AI PLATFORM FOR TANGLISH DISTRESS RISK DETECTION AND WELLBEING SUPPORT",
        "SDG : << �.>>": "SDG : 3 - GOOD HEALTH AND WELL BEING",
        "<< Title of your Project work>>": "MINDGUARD AI PLATFORM FOR TANGLISH DISTRESS RISK DETECTION AND WELLBEING SUPPORT",
    }
    for paragraph in doc.paragraphs:
        for old, new in replacements.items():
            if old in paragraph.text:
                # Template placeholder text is split across runs. Replacing the
                # paragraph text preserves the paragraph's alignment and layout
                # while reliably replacing the visible placeholder.
                paragraph.text = paragraph.text.replace(old, new)
                for run in paragraph.runs:
                    set_run_font(run, 12, bold=run.bold)


def add_heading(doc, text, level=1):
    p = doc.add_paragraph(style=f"Heading {level}")
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run(text.upper() if level == 1 else text)
    set_run_font(r, 13 if level == 1 else 12, bold=True)
    return p


def add_body(doc, text, indent=False):
    p = doc.add_paragraph(style="Normal")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if indent:
        p.paragraph_format.first_line_indent = Inches(0.25)
    r = p.add_run(text)
    set_run_font(r)
    return p


def add_bullet(doc, text):
    p = doc.add_paragraph(style="Normal")
    p.paragraph_format.left_indent = Inches(0.28)
    p.paragraph_format.first_line_indent = Inches(-0.18)
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run("• " + text)
    set_run_font(r)
    return p


def add_numbered(doc, text):
    p = doc.add_paragraph(style="Normal")
    p.paragraph_format.left_indent = Inches(0.3)
    p.paragraph_format.first_line_indent = Inches(-0.2)
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run("• " + text)
    set_run_font(r)
    return p


def add_table(doc, headers, rows, widths=None):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.autofit = False
    set_borders(table)
    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ""
        if widths:
            cell.width = Inches(widths[i])
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        set_cell_shading(cell, "1F4E78")
        set_cell_margins(cell)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(header)
        set_run_font(r, 10, bold=True, color=(255, 255, 255))
    set_repeat_table_header(table.rows[0])
    for row_index, row in enumerate(rows):
        cells = table.add_row().cells
        for i, value in enumerate(row):
            if widths:
                cells[i].width = Inches(widths[i])
            cells[i].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            set_cell_margins(cells[i])
            if row_index % 2 == 1:
                set_cell_shading(cells[i], "F3F7FA")
            p = cells[i].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if i == 0 and len(str(value)) < 10 else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(str(value))
            set_run_font(r, 10)
    doc.add_paragraph()
    return table


def add_chapter_start(doc, number, title):
    doc.add_page_break()
    add_heading(doc, f"{number}. {title}")


def add_content(doc):
    add_chapter_start(doc, 1, "Introduction")
    add_body(doc, "MindGuard is a web-based research prototype that supports early, non-clinical identification of distress-related language in Tamil-English code-mixed text, commonly called Tanglish. The platform combines a user check-in interface, text-risk analysis, an empathetic support conversation pathway, self-guided wellbeing tools, mood reflection, and a supervised escalation design. It is intended to help a user pause, reflect, and seek appropriate human support; it does not diagnose a mental-health condition, replace a qualified professional, or autonomously contact emergency services.", True)
    add_body(doc, "Tamil-English code-mixed communication is frequent in informal online spaces and presents challenges for conventional English-only natural-language systems. Informal spelling, transliteration, code switching, and short context-dependent expressions can obscure meaning. MindGuard therefore focuses on an explainable, safety-oriented severity workflow with four labels: Normal, Mild, Moderate, and Severe. The application gives users a calm, accessible interface and provides crisis-resource guidance when a high-risk statement is detected.", True)
    add_heading(doc, "1.1 Need for the System", 2)
    add_body(doc, "Existing generic sentiment tools are poorly matched to Tanglish distress expressions and can misread negation, spelling variants, or informal Romanized Tamil. A project solution should make the language scope explicit, avoid unsupported medical claims, and preserve human review for severe-risk signals. The design also needs transparent privacy controls because free-text check-ins may contain sensitive personal information.", True)
    add_heading(doc, "1.2 Project Context", 2)
    add_body(doc, "The project aligns with Sustainable Development Goal 3, Good Health and Well Being, by demonstrating a responsible digital wellbeing-support workflow. It follows the principle that AI for health must be designed with human wellbeing, privacy, accountability, transparency, and equity in view. MindGuard is consequently documented as a supervised pilot/research prototype, with clear deployment limitations.", True)

    add_chapter_start(doc, 2, "Problem Definition Scope and Objectives")
    add_heading(doc, "2.1 Problem Definition", 2)
    add_body(doc, "People may express distress in mixed Tamil-English language without using formal clinical terms. A simple keyword detector can miss phrasing, incorrectly flag harmless messages, or fail to distinguish a remote negation from an immediate self-harm statement. At the same time, any system that processes such text must not overstate its reliability or present automated output as medical advice. The problem is to build a usable web platform that analyses Tanglish text conservatively, offers supportive next steps, and exposes clear privacy and safety boundaries.", True)
    add_heading(doc, "2.2 Scope", 2)
    add_bullet(doc, "Analyse user-entered Tamil, English, and Tanglish text into Normal, Mild, Moderate, or Severe categories.")
    add_bullet(doc, "Provide an explanation-oriented result, a guided check-in, mood journey view, weekly reflection, self-guided grounding tools, and wellbeing games.")
    add_bullet(doc, "Offer a streamed supportive chat interface and location-aware crisis guidance as informational support.")
    add_bullet(doc, "Provide a personal support-plan workflow and a trusted-contact design that requires genuine user consent and verified delivery before any real notification is claimed.")
    add_bullet(doc, "Support a clinician-style dashboard only as a project feature; production role-based access and clinical governance remain future work.")
    add_heading(doc, "2.3 Out of Scope", 2)
    add_bullet(doc, "Clinical diagnosis, treatment recommendations, or replacement of counselling, medical care, or emergency response.")
    add_bullet(doc, "Automatic real-world emergency or trusted-contact notification in the current prototype.")
    add_bullet(doc, "Validated performance claims across all Indian languages, demographics, or clinical populations.")
    add_heading(doc, "2.4 Objectives", 2)
    objectives = [
        "To design a responsive, accessible, and professional wellbeing-support interface for user check-ins.",
        "To implement a layered Tanglish text-analysis workflow that handles lexical signals, local context, and abstention for weak evidence.",
        "To provide safe, non-diagnostic support features including reflection, guided breathing, grounding, journaling, and a personal support plan.",
        "To implement privacy-aware backend APIs with versioned routes, rate limiting, controlled CORS, and configuration-based production safety gates.",
        "To document limitations and a deployment roadmap for clinician validation, human review, operational escalation, and data protection.",
    ]
    for item in objectives:
        add_numbered(doc, item)

    add_chapter_start(doc, 3, "Literature Survey")
    add_heading(doc, "3.1 Code Mixed Tamil English Language Resources", 2)
    add_body(doc, "Code-mixed Tamil-English text is difficult to process because it combines languages, informal grammar, transliteration, and spelling variation. Chakravarthi et al. created a Tamil-English code-mixed sentiment corpus of 15,744 YouTube comments and highlighted the scarcity of annotated resources for low-resource languages. Such work motivates language-aware rather than English-only preprocessing. Related Dravidian shared tasks also demonstrate the need for careful evaluation when social-media language is informal and context dependent.", True)
    add_heading(doc, "3.2 Responsible AI for Health", 2)
    add_body(doc, "WHO guidance emphasizes that AI for health should be governed around human autonomy, wellbeing and safety, transparency, accountability, inclusiveness, and responsiveness. These principles inform MindGuard's non-diagnostic positioning, human-review requirement for severe signals, visible crisis guidance, and privacy-by-design direction. They also require that any future evaluation use representative data and examine harms such as false negatives, false positives, bias, and over-reliance.", True)
    add_heading(doc, "3.3 Privacy and Data Protection", 2)
    add_body(doc, "The Digital Personal Data Protection Act, 2023 establishes a legal framework for processing digital personal data in India. The project therefore specifies explicit consent, minimum necessary data collection, encryption-oriented utilities, privacy controls, and a default approach in which chat content is not retained. A production implementation would still require legal review, approved notices, retention schedules, access controls, incident procedures, and a real data-subject-rights workflow.", True)
    add_heading(doc, "3.4 Research Gap", 2)
    add_body(doc, "The reviewed work supports language-aware modelling and ethical governance, but a practical student project must connect these concerns to a usable product workflow. MindGuard addresses this gap by combining Tanglish-aware analysis with a user-facing self-care journey, a clear non-clinical disclaimer, and engineering controls that prevent a local demonstration configuration from being mistaken for a production service.", True)

    add_chapter_start(doc, 4, "Requirement Analysis")
    add_heading(doc, "4.1 Stakeholders", 2)
    add_table(doc, ["Stakeholder", "Need"], [
        ["User", "A calm, readable interface to check in, understand a non-clinical risk signal, and access immediate self-support tools."],
        ["Project team", "Maintainable frontend, versioned APIs, tests, configuration controls, and reproducible local setup."],
        ["Supervisor or evaluator", "Traceable requirements, stated limitations, implementation evidence, and a clear testing plan."],
        ["Future clinician or reviewer", "Human-review workflow, explainable indicators, role-based access, auditability, and validated thresholds before real use."],
    ], [1.55, 5.65])
    add_heading(doc, "4.2 Functional Requirements", 2)
    add_table(doc, ["ID", "Functional Requirement", "Priority"], [
        ["FR1", "Accept a text check-in in English, Tamil, or Tanglish and return a four-level severity result.", "High"],
        ["FR2", "Show the result with supportive, non-diagnostic next-step guidance and a crisis-resource route for severe signals.", "High"],
        ["FR3", "Provide mood tracking, a journey view, weekly reflection, and a saved personal support plan.", "High"],
        ["FR4", "Provide guided breathing, grounding, journaling, gratitude, Focus Match, and Quiet Count tools.", "Medium"],
        ["FR5", "Support a streamed conversation endpoint for the check-in experience.", "Medium"],
        ["FR6", "Provide privacy controls and a route for data-related requests.", "High"],
        ["FR7", "Expose health, analysis, chat, mood, voice, quest, indicators, escalation, trajectory, authentication, and privacy API routes under /api/v1.", "High"],
    ], [0.6, 5.35, 1.25])
    add_heading(doc, "4.3 Non Functional Requirements", 2)
    add_table(doc, ["Category", "Requirement"], [
        ["Usability", "High-contrast solid surfaces, readable text, mobile-aware navigation, and plain-language safety messaging."],
        ["Safety", "No diagnostic claim; severe signals require review; fallback/abstention behavior must not silently convert weak evidence into a confident result."],
        ["Privacy", "Do not retain chat content by default; use configuration gates, controlled CORS, and encrypted storage utilities for sensitive fields."],
        ["Reliability", "Health endpoint, exception handling, offline unit tests, and safe fallbacks when optional models are unavailable."],
        ["Maintainability", "React component structure, FastAPI routers, service interfaces, Pydantic settings, SQLAlchemy models, and versioned API routes."],
        ["Performance", "The core lexical/context path must remain available in local fallback mode; heavyweight models are optional and hardware-dependent."],
    ], [1.35, 5.85])
    add_heading(doc, "4.4 Hardware and Software Requirements", 2)
    add_table(doc, ["Type", "Requirement"], [
        ["Client", "Modern desktop or mobile browser with network access to the local or deployed API."],
        ["Frontend", "React 19, Vite, React Router, Tailwind CSS, Recharts, Zustand, Axios, and Lucide icons."],
        ["Backend", "Python 3.12 compatible runtime, FastAPI, Uvicorn, SQLAlchemy, Pydantic Settings, SlowAPI, and required NLP libraries."],
        ["Database", "SQLite for local development; managed PostgreSQL is required for production deployment."],
        ["Optional ML hardware", "A compatible GPU and approximately 8-12 GB RAM/VRAM are required to load the Llama 3.2 3B path; fallback analysis supports lower-resource demonstration environments."],
    ], [1.55, 5.65])

    add_chapter_start(doc, 5, "Proposed Methodology and System Design")
    add_heading(doc, "5.1 Methodology", 2)
    add_body(doc, "MindGuard uses a layered and conservative workflow. First, the input gate validates and normalizes user text. A Tanglish-aware lexical detector checks known high-precision patterns and spelling variants. A local context analyser scopes negation near relevant terms, while the embedding k-nearest-neighbour component abstains when it has no meaningful similarity anchor. The ensemble combines available evidence, preserves explicit first-person self-harm signals, and flags severe output for review. The user interface then presents non-clinical guidance, a self-care option, or a crisis-resource route appropriate to the result.", True)
    add_heading(doc, "5.2 High Level Architecture", 2)
    add_table(doc, ["Layer", "Components", "Responsibility"], [
        ["Presentation", "React/Vite pages, hooks, Zustand state, responsive layout", "Check-in, journey, tools, reflection, support plan, settings, and dashboard navigation."],
        ["API Gateway", "FastAPI, CORS middleware, rate limiter, exception handler", "Versioned HTTP APIs, request validation, error handling, and local health reporting."],
        ["Application Services", "Detection, chatbot, escalation, voice, tracking, privacy services", "Business logic behind router interfaces and dependency injection."],
        ["Data", "SQLAlchemy models, SQLite development database", "Mood logs, alerts, consent, wellness plans, trusted contacts, feedback, and related application records."],
        ["Optional models", "Lexicon, context analyser, embedding kNN, Llama, Whisper", "Risk-signal analysis, conversational support, and speech-to-text where the required models are available."],
    ], [1.25, 2.35, 3.6])
    add_heading(doc, "5.3 Data Flow", 2)
    for text in [
        "The user enters a message through the Check In page.",
        "The frontend sends the request through the API client to a versioned FastAPI route.",
        "The backend validates input, invokes the detection service, and returns severity, confidence, explanatory signals, and review status.",
        "The frontend renders supportive next steps and records user-selected mood/reflection data only through the configured persistence mechanism.",
        "A severe result routes the user to crisis guidance and records a review-oriented signal; the prototype does not claim automatic external notification.",
    ]:
        add_numbered(doc, text)
    add_heading(doc, "5.4 Safety and Privacy Design", 2)
    add_body(doc, "The system distinguishes support from diagnosis. Runtime validation rejects an unsafe production configuration that uses demo authentication, mock escalation, local database settings, retained chat content, default secrets, or local-only CORS origins. The chat router is configured not to persist the message text by default. These controls reduce risk during development, but a real deployment still requires clinician validation, a staffed human escalation workflow, legal approval, audit logging, authentication, role-based access control, data-retention implementation, and incident response procedures.", True)

    add_chapter_start(doc, 6, "Implementation")
    add_heading(doc, "6.1 Frontend Implementation", 2)
    add_body(doc, "The frontend is implemented as a React single-page application built with Vite. A common layout provides a persistent navigation structure and responsive mobile navigation. The design uses solid surfaces and high-contrast typography instead of glassmorphism so that headings, card content, forms, charts, and controls remain legible. Routes expose Explore, Check In, Journey, Tools, Weekly Reflection, Support Plan, Settings, and Clinical View pages.", True)
    add_table(doc, ["Feature", "Implementation Summary"], [
        ["Check In", "Text input and streamed supportive response path connected to the /api/v1/chat/stream interface."],
        ["Journey", "Mood history and trajectory visualisation with a wellness-plan view."],
        ["Tools", "Guided breathing, 5-4-3-2-1 grounding, thought-reset journal, gratitude prompt, Focus Match, and Quiet Count."],
        ["Weekly Reflection", "Five-point mood, energy, and sleep check-ins with helpful factors and an intention saved locally for the user."],
        ["Support Plan", "Personal reminders, small next actions, contact planning, and India-focused emergency resource guidance."],
        ["Settings and Privacy", "High-contrast theme presentation, consent-oriented controls, trusted-contact setup flow, and data/privacy navigation."],
    ], [1.55, 5.65])
    add_heading(doc, "6.2 Backend Implementation", 2)
    add_body(doc, "The backend follows a FastAPI application-factory pattern. Routers are mounted beneath /api/v1 and delegate to service implementations through dependency injection. The lifespan hook configures logging, validates runtime settings, creates development tables, loads optional model components, and wires the services. Pydantic settings externalize deployment-sensitive values. SQLAlchemy provides the data-model abstraction, with SQLite used locally and PostgreSQL identified as the production target.", True)
    add_table(doc, ["Route Group", "Purpose"], [
        ["/health", "Reports service availability for local monitoring."],
        ["/analyze", "Receives text for the detection-service workflow."],
        ["/chat", "Provides the streamed support-chat route."],
        ["/mood and /trajectory", "Supports mood records and trend data."],
        ["/quest", "Supports gamified wellbeing tasks."],
        ["/voice", "Provides a speech-to-text pathway when Whisper is available."],
        ["/escalation", "Contains the escalation workflow; current mock delivery is explicitly gated away from production."],
        ["/privacy and /auth", "Supports privacy-facing and authentication-related workflows."],
    ], [2.0, 5.2])
    add_heading(doc, "6.3 Detection Implementation", 2)
    add_body(doc, "The detection module includes input validation, lexicon matching, context analysis, embedding kNN support, a hybrid sentiment component, and ensemble resolution. Recent safety changes ensure that phrase matching compares correctly sized token windows, that negation is scoped near the risk expression, and that low-similarity kNN evidence is treated as uncertain rather than as a false vote. Explicit high-precision severe patterns receive review-oriented handling rather than being diluted by abstaining components.", True)
    add_heading(doc, "6.4 Testing", 2)
    add_body(doc, "The project includes offline backend tests for the detection ensemble, lexicon behavior, and regression cases. A frontend production build is used to verify that the React bundle compiles. Local smoke testing covers the health route, normal text, severe text, CORS behavior, and the streaming chat contract. Test results should be repeated after each model, ruleset, or interface change; benchmark metrics must not be represented as clinical validation.", True)

    add_chapter_start(doc, 7, "Conclusion")
    add_body(doc, "MindGuard demonstrates an end-to-end approach for Tanglish-aware wellbeing support: a readable React interface, a FastAPI service layer, conservative multi-signal text analysis, guided self-care features, and explicit safety and privacy boundaries. The project addresses the practical need to support mixed Tamil-English text without presenting automated output as a medical decision. It also turns safety requirements into engineering controls through abstention behavior, non-retention of chat content by default, production configuration gates, and a stated human-review requirement for severe signals.", True)
    add_heading(doc, "7.1 Future Enhancements", 2)
    for text in [
        "Create a representative, independently labelled Tanglish evaluation set and conduct clinical and subgroup validation before any public deployment.",
        "Replace demonstration authentication with secure identity management, role-based access, audit logs, account recovery, and tested authorization boundaries.",
        "Implement a consented, verified trusted-contact delivery service with delivery acknowledgements, staffing, operating hours, and documented failure paths.",
        "Use managed PostgreSQL, a secrets manager, encrypted transport, retention/deletion workflows, backups, monitoring, CI, security scanning, and rollback procedures.",
        "Conduct clinician review of crisis wording, translation quality, threshold choices, and local resource information before deployment beyond a supervised pilot.",
    ]:
        add_numbered(doc, text)

    add_chapter_start(doc, 8, "References")
    references = [
        "Chakravarthi, B. R., Muralidaran, V., Priyadharshini, R., & McCrae, J. P. (2020). Corpus creation for sentiment analysis in code-mixed Tamil-English text. Proceedings of the 1st Joint Workshop on Spoken Language Technologies for Under-resourced Languages, 202-210. https://aclanthology.org/2020.sltu-1.28/",
        "Ravikiran, M., Chakravarthi, B. R., Madasamy, A. K., Sivanesan, S., Rajalakshmi, R., Thavareesan, S., Ponnusamy, R., & Mahadevan, S. (2022). Findings of the shared task on offensive span identification from code-mixed Tamil-English comments. Proceedings of DravidianLangTech. https://aclanthology.org/2022.dravidianlangtech-1.40/",
        "World Health Organization. (2021). Ethics and governance of artificial intelligence for health: WHO guidance. https://www.who.int/publications/i/item/9789240029200",
        "World Health Organization. (2023). WHO calls for safe and ethical AI for health. https://www.who.int/news/item/16-05-2023-who-calls-for-safe-and-ethical-ai-for-health",
        "Government of India, Ministry of Law and Justice. (2023). The Digital Personal Data Protection Act, 2023. https://www.meity.gov.in/static/uploads/2024/02/Digital-Personal-Data-Protection-Act-2023.pdf",
        "FastAPI. (n.d.). FastAPI documentation. https://fastapi.tiangolo.com/",
        "React. (n.d.). React documentation. https://react.dev/",
        "Vite. (n.d.). Vite documentation. https://vite.dev/",
        "SQLAlchemy. (n.d.). SQLAlchemy documentation. https://docs.sqlalchemy.org/",
        "MindGuard project repository. (2026). Architecture, implementation, and production-readiness documentation. Internal project documentation.",
    ]
    for ref in references:
        p = add_body(doc, ref)
        p.paragraph_format.left_indent = Inches(0.3)
        p.paragraph_format.first_line_indent = Inches(-0.3)

    add_chapter_start(doc, 9, "Annexure I Outcome Specific Supporting Evidence")
    add_heading(doc, "A. Feature to Requirement Traceability", 2)
    add_table(doc, ["Requirement", "Implemented Evidence"], [
        ["Tanglish text analysis", "Detection service combines input validation, lexical matching, local context checks, embedding support, and ensemble resolution."],
        ["Readable wellbeing interface", "High-contrast solid UI, responsive layout, check-in, journey, tools, reflection, support plan, and settings routes."],
        ["Self-support features", "Guided breathing, grounding, journal prompts, gratitude activity, Focus Match, Quiet Count, and weekly reflection."],
        ["Privacy and safety", "Default no-chat-retention setting, runtime production validation, CORS configuration, rate limiting, non-diagnostic messaging, and review-oriented severe signals."],
        ["Maintainability", "React page/component structure, FastAPI router/service separation, Pydantic configuration, SQLAlchemy models, versioned APIs, and automated tests."],
    ], [2.0, 5.2])
    add_heading(doc, "B. Prototype Deployment Statement", 2)
    add_body(doc, "This report documents a final-year project prototype. The system is appropriate for demonstration and supervised research use only. It must not be deployed as a clinical diagnostic, autonomous crisis-response, or emergency-notification service without representative clinical validation, human operational coverage, security and privacy approval, lawful data-governance controls, verified contact-delivery integration, and written organizational sign-off.", True)
    add_heading(doc, "C. Suggested Demonstration Sequence", 2)
    for text in [
        "Open Explore and identify the available wellbeing features.",
        "Use Check In to enter a normal Tanglish message and observe the non-clinical result presentation.",
        "Open Tools and demonstrate one guided regulation activity and one wellbeing game.",
        "Open Weekly Reflection and save a private reflection entry.",
        "Open Support Plan to demonstrate the planning workflow and resource guidance.",
        "Use the API health endpoint and the offline test suite as technical evidence. Do not demonstrate or claim live emergency contact delivery.",
    ]:
        add_numbered(doc, text)


def main():
    if not TEMPLATE.exists():
        raise FileNotFoundError(TEMPLATE)
    copy2(TEMPLATE, OUTPUT)
    doc = Document(OUTPUT)
    setup_styles(doc)
    replace_placeholders(doc)

    # Preserve the supplied contents table while making its heading row explicit.
    if doc.tables:
        set_repeat_table_header(doc.tables[0].rows[0])
    # The supplied cover uses one institutional logo image; provide meaningful
    # alternative text in the completed copy for accessibility.
    for element in doc.element.body.iter():
        if element.tag == qn("wp:docPr") and not element.get("descr"):
            element.set("descr", "Karunya Institute of Technology and Sciences logo")

    # Retain the institutional cover/certificate/declaration/contents pages.
    # Keep student, register number, and supervisor fields untouched for the student to complete.
    for section in doc.sections:
        footer = section.footer
        if footer.paragraphs and not footer.paragraphs[0].text.strip():
            add_page_number(footer.paragraphs[0])

    add_content(doc)
    settings = doc.settings.element
    update_fields = OxmlElement("w:updateFields")
    update_fields.set(qn("w:val"), "true")
    settings.append(update_fields)
    doc.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    main()
