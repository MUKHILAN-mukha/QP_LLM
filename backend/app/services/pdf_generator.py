import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime

class PDFGenerator:
    def __init__(self):
        self.width, self.height = A4
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()

    def _create_custom_styles(self):
        self.header_style = ParagraphStyle(
            'Header',
            parent=self.styles['Heading1'],
            fontSize=14,
            alignment=TA_CENTER,
            spaceAfter=6,
            fontName='Helvetica-Bold'
        )
        self.sub_header_style = ParagraphStyle(
            'SubHeader',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            spaceAfter=12,
            fontName='Helvetica'
        )
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=14,
            alignment=TA_LEFT,
            fontName='Helvetica'
        )
        self.question_style = ParagraphStyle(
            'Question',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=16,
            spaceAfter=8,
            fontName='Helvetica'
        )
        self.section_header = ParagraphStyle(
            'SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=12,
            alignment=TA_CENTER,
            spaceBefore=12,
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )

    def create_pdf(self, subject_name: str, questions: dict) -> io.BytesIO:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )

        elements = []

        # 1. Header Section (St. Xavier's Style)
        # Roll Number Area
        elements.append(Paragraph("Roll Number: __________________", self.normal_style))
        elements.append(Spacer(1, 12))

        # College Name
        elements.append(Paragraph("St. Xavier's Catholic College of Engineering, Chunkankadai, Nagercoil – 629 003", self.header_style))
        
        # Exam Details
        current_year = datetime.now().year
        exam_title = f"Internal Exam I, {current_year} – {current_year+1} [EVEN]"
        elements.append(Paragraph(exam_title, self.sub_header_style))

        # Meta Details Table
        meta_data = [
            [f"Class: B.Tech. Information Technology", f"Semester: 6"],
            [f"Time: 90 Minutes", f"Course: {subject_name}", "Maximum: 50 Marks"]
        ]
        meta_table = Table(meta_data, colWidths=[2.5*inch, 2.5*inch, 2*inch])
        meta_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 12))

        # 2. Course Outcomes (CO) Table
        # Standard COs for typical IT subjects
        co_data = [
            ["Course Outcomes (COs)"],
            ["CO1", "Explain the terminology and concepts of the subject."],
            ["CO2", "Apply fundamental principles to solve problems."],
            ["CO3", "Analyze complex scenarios using subject knowledge."],
            ["CO4", "Evaluate different approaches and strategies."],
            ["CO5", "Create new solutions based on learned concepts."]
        ]
        co_table = Table(co_data, colWidths=[0.5*inch, 6*inch])
        co_table.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), # Header bold
            ('SPAN', (0,0), (1,0)), # Span title
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('GRID', (0,0), (-1,-1), 0.5, colors.white), # Hidden grid mostly
            ('BOTTOMPADDING', (0,0), (-1,-1), 4), # Reduced padding
        ]))
        elements.append(co_table)
        
        # Bloom's Taxonomy Key
        bt_key = "CL-Cognitive Level; Re-Remember; Un-Understand; Ap-Apply; An-Analyze; Ev-Evaluate; Cr-Create;"
        elements.append(Spacer(1, 8)) # Increased spacing
        elements.append(Paragraph(bt_key, ParagraphStyle('Small', fontSize=9, fontName='Helvetica-Oblique')))
        elements.append(Spacer(1, 12))

        # 3. Questions Section
        # Header Row for Questions
        q_header_data = [["Q.No.", "Question", "Marks", "CL", "CO"]]
        q_header = Table(q_header_data, colWidths=[0.5*inch, 4.5*inch, 0.6*inch, 0.4*inch, 0.4*inch])
        q_header.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('ALIGN', (2,0), (-1,-1), 'CENTER'), # Center marks/CL/CO
            ('LINEBELOW', (0,0), (-1,-1), 1, colors.black),
            ('LINEABOVE', (0,0), (-1,-1), 1, colors.black),
        ]))
        elements.append(q_header)
        elements.append(Spacer(1, 8))

        # Helper to clean question text (remove accidentally generated meta tags and prefixes)
        import re
        def clean_q_text(text):
            # Remove (2 marks), (16 marks)
            text = text.replace("(2 marks)", "").replace("(16 marks)", "")
            # Remove leading "Unit X -" or "Unit X:" prefix
            text = re.sub(r'^Unit\s*\d+\s*[:\-\.]\s*', '', text, flags=re.IGNORECASE)
            # Remove trailing metadata like (Unit: unit 1, Part: part a)
            text = re.sub(r'\s*\(Unit:.*?\)', '', text, flags=re.IGNORECASE)
            text = re.sub(r'\s*\(Part:.*?\)', '', text, flags=re.IGNORECASE)
            text = re.sub(r'\s*\(CO\d+\)', '', text, flags=re.IGNORECASE)
            # Remove (Un CO1), (Re CO2), (Ap CO4) patterns
            text = re.sub(r'\s*\(\w+\s*CO\d+\)', '', text, flags=re.IGNORECASE)
            # Remove (Unit 1), (Unit 2), [Unit 1], [Unit 2] patterns
            text = re.sub(r'\s*[\[\(]Unit\s*\d+[\]\)]', '', text, flags=re.IGNORECASE)
            # Remove leading numbering if captured (e.g. "1. Question")
            text = re.sub(r'^\d+[\.\)]\s*', '', text)
            return text.strip()

        # PART A
        elements.append(Paragraph("Part-A (Questions x 2 Marks)", self.section_header))
        elements.append(Spacer(1, 6))
        
        q_num = 1
        part_a_qs = questions.get('part_a', [])
        
        for q in part_a_qs:
            data = [[
                f"{q_num}.",
                Paragraph(clean_q_text(q['question']), self.question_style),
                "2",
                q.get('cl', 'Re'),
                q.get('co', 'CO1')
            ]]
            t = Table(data, colWidths=[0.5*inch, 4.5*inch, 0.6*inch, 0.4*inch, 0.4*inch])
            t.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('ALIGN', (2,0), (-1,-1), 'CENTER'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ]))
            elements.append(t)
            q_num += 1

        # PART B
        elements.append(Spacer(1, 12))
        elements.append(Paragraph("Part-B (Questions x 16 Marks)", self.section_header))
        elements.append(Spacer(1, 6))
        
        part_b_qs = questions.get('part_b', [])
        
        # Logic: Questions 11, 12, 13, 14...
        # We need to insert (OR) between PAIRS (11 & 12), (13 & 14).
        # But wait, Q.Nos should be 11 (a) OR 11 (b)? 
        # User request: "11 OR 12", "13 OR 14". 
        # So we treat them as individual numbered questions, but grouped.
        
        # Start numbering from 11 for Part B usually? Or continue from Part A?
        # User said "11 OR 12". So Part A probably has 10 questions.
        # If Part A has 10 qs, q_num is now 11. Perfect.
        
        for i, q in enumerate(part_b_qs):
            # Print the question
            data = [[
                f"{q_num}.",
                Paragraph(clean_q_text(q['question']), self.question_style),
                "16",
                q.get('cl', 'Ap'),
                q.get('co', 'CO2')
            ]]
            t = Table(data, colWidths=[0.5*inch, 4.5*inch, 0.6*inch, 0.4*inch, 0.4*inch])
            t.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('ALIGN', (2,0), (-1,-1), 'CENTER'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 12), # More space for 16 marks
            ]))
            elements.append(t)
            
            # OR Logic:
            # If this is an ODD index in the loop (0, 2, 4 -> 1st, 3rd, 5th question in Part B),
            # AND there is a next question, print (OR).
            # Wait, index 0 is Q11. Index 1 is Q12.
            # We want OR between Q11 and Q12.
            # So if (i % 2 == 0) and (i + 1 < len(part_b_qs)), print OR.
            
            if i % 2 == 0 and i + 1 < len(part_b_qs):
                elements.append(Paragraph("(OR)", ParagraphStyle('OR', alignment=TA_CENTER, fontSize=11, fontName='Helvetica-Bold', spaceAfter=12)))
            
            q_num += 1

        doc.build(elements)
        buffer.seek(0)
        return buffer

pdf_generator = PDFGenerator()
