import re

# Restricted patterns: prompt injections, secret sniffing, harmful commands
BLOCKED_PATTERNS = [
    r"ignore (all )?previous instructions",
    r"reveal (the )?system prompt",
    r"show me (the )?api[-_]?key",
    r"groq_api_key",
    r"pinecone_api_key",
    r"token\.json",
    r"credentials\.json",
    r"bypass security",
    r"delete repository"
]

def apply_input_guardrail(query: str) -> tuple[bool, str]:
    """Checks if the user input violates safety or prompt injection rules."""
    q_lower = query.lower().strip()
    
    # Check 1: Empty or extremely long queries (DoS / Token flood)
    if len(query) > 3000:
        return False, "⚠️ Guardrail Alert: Input exceeds safe limit of 3,000 characters."
    
    # Check 2: Prompt injections & sensitive file snooping
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, q_lower):
            return False, "🛡️ Security Guardrail: Action blocked. Prompt injection or access to internal credentials is not allowed."
            
    return True, "Passed"

def validate_rag_response(context: str, response: str) -> str:
    """Prevents hallucination when RAG retrieved nothing useful."""
    if not context.strip() or "koi specific information nahi mili" in context.lower():
        return "🛡️ Fact-Check Guardrail: The uploaded document does not contain this information. Generation blocked to prevent hallucination."
    return response