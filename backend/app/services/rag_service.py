import logging
import re
import requests
import json
import time
import random
from typing import List, Dict, Optional
from app.config import settings
from app.services.vector_store import vector_store

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        self.ollama_url = f"{settings.OLLAMA_BASE_URL}/api/generate"
        self.model = settings.OLLAMA_MODEL

    def _query_llm(self, prompt: str, system_prompt: str = "") -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": 0.4, # Increased for better variety
                "top_p": 0.9,
            }
        }
        
        retries = 2
        retry_delay = 2 # seconds
        
        for attempt in range(retries):
            try:
                # Increased timeout to 120s for complex multi-unit queries
                response = requests.post(self.ollama_url, json=payload, timeout=120)
                response.raise_for_status()
                result = response.json().get("response", "")
                
                # Clean up <think> tags if present
                result = re.sub(r'<think>.*?</think>', '', result, flags=re.DOTALL).strip()
                return str(result)
                
            except requests.exceptions.ConnectionError:
                logger.error("Cannot connect to Ollama. Make sure Ollama is running.")
                return "I apologize, but I cannot connect to the local AI service. Please ensure Ollama is running."
                
            except requests.exceptions.Timeout:
                logger.warning(f"Ollama request timed out (Attempt {attempt+1}/{retries})")
                if attempt < retries - 1:
                    time.sleep(retry_delay)
                    continue
                return "The AI model is taking quite a while to process this complex request. Please try refreshing in a moment; the answer should appear in your history!"
                
            except Exception as e:
                logger.error(f"LLM Query failed: {e}")
                return f"I apologize, but I encountered an error: {str(e)}"
        
        return "The AI service is currently unavailable. Please try again."

    def generate_response(self, subject_id: int, query: str, history: List[dict] = []) -> dict:
        # 1. Precise Intent and Filter Detection
        # Look for numbers specifically tied to unit keywords: "unit 2", "module 4", "units 1, 2, 3"
        unit_keyword_pattern = r'\b(?:unit|module|chapter|units|modules)\s*[:\.-]?\s*((?:\d+|[ivx]+)(?:\s*(?:and|,|&)\s*(?:\d+|[ivx]+))*)'
        unit_match = re.search(unit_keyword_pattern, query, re.IGNORECASE)
        
        target_units = []
        if unit_match:
            # Extract all digit/roman sequences from the captured list
            raw_vals = re.findall(r'(\d+|[ivx]+)', unit_match.group(1).lower())
            target_units = [f"unit {v}" for v in raw_vals]
            
        # Deduplicate while preserving order
        target_units = list(dict.fromkeys(target_units))
        
        # Look for CO mentions (e.g., "CO1", "CO-2")
        co_match = re.search(r'\b(co)\s*[:\.-]?\s*(\d+)\b', query, re.IGNORECASE)
        target_co = f"co{co_match.group(2)}" if co_match else None
        
        # Look for section/part mentions (e.g., "Part A", "Section B")
        part_match = re.search(r'\b(part|section)\s*[:\.-]?\s*([a-c])\b', query, re.IGNORECASE)
        target_part = part_match.group(2).lower() if part_match else None
        
        # Look for mark mentions
        marks_match = re.search(r'\b(\d+)\s*(marks|mark)\b', query, re.IGNORECASE)
        target_marks = marks_match.group(1) if marks_match else None
        
        # Check for global multi-unit intent
        is_global_multi = any(k in query.lower() for k in ["all units", "mixed", "random", "across units", "from all", "all the unit", "different units"])
        
        should_stratify = is_global_multi or len(target_units) > 1
        
        # Enhance query
        search_query = query
        if target_units: search_query += f" {' '.join(target_units)}"
        if target_part: search_query += f" part {target_part}"

        # 2. Balanced Vector Search (Context Interleaving)
        try:
            if should_stratify:
                logger.info(f"Balanced stratified search: {target_units if target_units else 'all'}")
                unit_pools = {}
                units_to_search = target_units if target_units else [f"unit {i}" for i in range(1, 6)]
                
                for unit_tag in units_to_search:
                    unit_filter = {"unit": unit_tag}
                    if target_part: unit_filter["part"] = f"part {target_part}"
                    if target_co: unit_filter["co"] = target_co
                    
                    unit_docs = vector_store.search(
                        subject_id=subject_id, 
                        query=search_query, 
                        k=15, # Larger pool for variety
                        filter_dict=unit_filter
                    )
                    random.shuffle(unit_docs) # Shuffle each unit pool
                    unit_pools[unit_tag] = unit_docs

                # INTERLEAVE: Take Doc 1 from Unit A, Doc 1 from Unit B, etc.
                # This ensures the LLM attention is forced to see all requested units evenly.
                interleaved_docs = []
                max_docs_per_unit = 5
                for i in range(max_docs_per_unit):
                    for unit_tag in units_to_search:
                        if i < len(unit_pools.get(unit_tag, [])):
                            interleaved_docs.append(unit_pools[unit_tag][i])
                
                docs = interleaved_docs if interleaved_docs else vector_store.search(subject_id, search_query, k=25)
            else:
                # Normal filtering logic (Single Unit)
                filter_dict = {}
                if target_units: filter_dict["unit"] = target_units[0]
                if target_part: filter_dict["part"] = f"part {target_part}"
                if target_co: filter_dict["co"] = target_co
                
                if target_marks and not target_part:
                    if target_marks == "2": filter_dict["part"] = "part a"
                    elif target_marks == "16": filter_dict["part"] = "part b"

                # Deterministic check for "best/toughest" questions
                needs_determinism = any(k in query.lower() for k in ["toughest", "hardest", "most difficult", "complex", "best", "top", "rank", "what is", "define", "explain"])
                
                docs = vector_store.search(subject_id, search_query, k=25, filter_dict=filter_dict if filter_dict else None)
                
                if not needs_determinism:
                    random.shuffle(docs)
                else:
                    logger.info("Deterministic mode enabled: Preserving vector rank order.")

            # Format context
            context_parts = []
            for d in docs:
                meta = d.get("metadata", {})
                source_info = f"[Source: {meta.get('filename', 'Unknown')} | Unit: {meta.get('unit', 'N/A')} | Part: {meta.get('part', 'N/A')}]"
                context_parts.append(f"{source_info}\n{d['text']}")
            
            context_text = "\n\n---\n\n".join(context_parts)
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            docs = []
            context_text = ""
        
        if not context_text:
            return {
                "answer": "❌ **No relevant questions found.**\n\nI couldn't find any questions matching your request in the provided documents.",
                "context_used": []
            }

        # 3. Construct System Prompt with BALANCE & GROUNDING RULES
        is_creative = any(k in query.lower() for k in ["create", "generate", "invent", "analyze", "design", "make"])

        system_rules = [
            "You are 'ExamGen AI', a helpful and intelligent university exam assistant.",
            "Your main goal is to extract or generate questions based on the provided documents.",
        ]
        
        if is_creative:
            system_rules.extend([
                "MODE: CREATIVE / GENERATIVE",
                "1. Analyze the provided context and synthesized NEW questions.",
                "2. You can rephrase and restructure content to create original questions.",
                "3. specific formatting (Part A/B) still applies."
            ])
        else:
             system_rules.extend([
                "MODE: STRICT EXTRACTION (GROUNDING)",
                "1. ONLY use the provided context. Do NOT generate new questions or use outside knowledge.",
                "2. COPY questions exactly as they appear in the text.",
                "3. If a question isn't in the context, politely explain you can't find it in the uploaded documents."
            ])

        common_rules = [
            "4. 'Part A' refers to 2-mark questions, and 'Part B' refers to 16-mark questions.",
            "5. Provide answers in a clean, professional numbered list.",
            "6. BALANCE RULE: If multiple units are requested, ensure equal representation.",
        ]
        system_rules.extend(common_rules)
        
        if target_units:
            units_str = " and ".join([u.upper() for u in target_units])
            system_rules.append(f"Focus specifically on providing questions from {units_str}.")
        if target_part:
            system_rules.append(f"Search only for {target_part.upper()} questions.")
        
        system_prompt = "\n".join(system_rules)

        # 4. Generate Response
        prompt = f"Context from uploaded documents:\n{context_text}\n\nUser Question: {query}\n\nResponse (balanced list):"
        answer = self._query_llm(prompt, system_prompt)

        return {
            "answer": answer,
            "context_used": docs
        }

    def generate_structured_exam(self, subject_id: int, unit_count: int = 5) -> dict:
        """
        Generates a full exam paper structure with Part A (2 marks) and Part B (16 marks).
        Strictly enforces the St. Xavier's format with CL and CO mapping.
        """
        
        # 1. Define the System Prompt for JSON Structure
        system_prompt = """
        You are an expert exam setter for St. Xavier's Catholic College of Engineering.
        Your task is to generate a question paper in strict JSON format.
        
        STRUCTURE REQUIRED:
        {
            "part_a": [
                {"question": "Define...", "cl": "Re", "co": "CO1"},
                {"question": "What is...", "cl": "Un", "co": "CO1"}
                ... (10 questions total, 2 from each Unit 1-5)
            ],
            "part_b": [
                {"question": "Explain detailed...", "cl": "Ap", "co": "CO2"},
                ... (5 questions total, 1 from each Unit 1-5)
            ]
        }
        
        RULES:
        1. "part_a": Generate 10 questions (2 Marks). MUST cover all units equally.
        2. "part_b": Generate 5 detailed questions (16 Marks). MUST cover all units.
        3. "cl": Cognitive Level (Re=Remember, Un=Understand, Ap=Apply, An=Analyze, Ev=Evaluate, Cr=Create).
        4. "co": Course Outcome (CO1, CO2, CO3, CO4, CO5). Map Unit 1->CO1, Unit 2->CO2, etc.
        5. OUTPUT JSON ONLY. No markdown, no conversational text.
        """
        
        # 2. Retrieve Context (Global Search)
        # We need a broad context covering all units to ensure the LLM has material.
        # Stratified search for all 5 units.
        all_docs = []
        for i in range(1, 6):
            unit_docs = vector_store.search(subject_id, f"unit {i} important questions definitions", k=5, filter_dict={"unit": f"unit {i}"})
            all_docs.extend(unit_docs)
        
        # Shuffle context for variety
        random.shuffle(all_docs)
        
        # Limit context size to avoid context window overflow (top 20 chunks)
        context_text = "\n".join([d['text'] for d in all_docs[:25]])
        
        prompt = f"""
        Context from Course Notes:
        {context_text}
        
        TASK:
        Generate a full internal exam question paper based on the above context.
        Follow the JSON structure strictly.
        """
        
        # 3. Query LLM
        response_json_str = self._query_llm(prompt, system_prompt)
        
        # 4. Parse JSON
        try:
            # Clean potential markdown wrappers
            clean_json = re.sub(r'```json\s*|\s*```', '', response_json_str).strip()
            data = json.loads(clean_json)
            return data
        except json.JSONDecodeError:
            logger.error(f"Failed to parse Exam JSON: {response_json_str}")
            return {
                "part_a": [{"question": "Error generating exam. Please try again.", "cl": "N/A", "co": "N/A"}],
                "part_b": []
            }

rag_service = RAGService()
