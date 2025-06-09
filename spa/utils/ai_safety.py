# spa/utils/ai_safety.py - AI Safety utilities

class AISafetyValidator:
    """AI safety validation utilities"""
    
    DANGEROUS_PATTERNS = [
        r'delete\s+all',
        r'remove\s+everything',
        r'drop\s+table',
        r'rm\s+-rf',
        r'format\s+.*drive',
        r'<script.*>.*</script>',  # Prevent script injection
        r'javascript:',
        r'onclick\s*=',
        r'onerror\s*=',
        r'onload\s*='
    ]
    
    SAFE_HTML_TAGS = [
        'div', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'section', 'article', 'header', 'footer', 'nav', 'main',
        'ul', 'ol', 'li', 'a', 'img', 'button', 'form', 'input',
        'textarea', 'select', 'option', 'label', 'br', 'hr'
    ]
    
    @classmethod
    def validate_prompt(cls, prompt):
        """Validate user prompt for safety"""
        import re
        
        prompt_lower = prompt.lower()
        
        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, prompt_lower, re.IGNORECASE):
                return False, f"Prompt contains potentially dangerous pattern: {pattern}"
        
        return True, "Prompt is safe"
    
    @classmethod
    def sanitize_html_content(cls, html_content):
        """Sanitize HTML content from AI"""
        import re
        
        # Remove dangerous attributes
        html_content = re.sub(r'on\w+\s*=\s*["\'][^"\']*["\']', '', html_content, flags=re.IGNORECASE)
        
        # Remove javascript: protocols
        html_content = re.sub(r'javascript:', 'data:', html_content, flags=re.IGNORECASE)
        
        # Remove script tags (but keep structure)
        html_content = re.sub(r'<script[^>]*>.*?</script>', '<!-- SCRIPT REMOVED FOR SAFETY -->', html_content, flags=re.DOTALL | re.IGNORECASE)
        
        return html_content
    
    @classmethod
    def validate_ai_response(cls, ai_response):
        """Validate AI response for safety"""
        if not isinstance(ai_response, dict):
            return False, "Response must be a dictionary"
        
        # Check HTML changes for safety
        if 'html_changes' in ai_response:
            for change in ai_response['html_changes']:
                if 'content' in change:
                    content = change['content']
                    if '<script' in content.lower() or 'javascript:' in content.lower():
                        return False, "HTML changes contain potentially unsafe script content"
        
        # Check script changes for safety
        if 'script_changes' in ai_response:
            for change in ai_response['script_changes']:
                if 'content' in change:
                    content = change['content']
                    # Allow only safe JavaScript patterns
                    if any(dangerous in content.lower() for dangerous in ['eval(', 'settimeout(', 'setinterval(']):
                        return False, "Script changes contain potentially unsafe JavaScript"
        
        return True, "AI response is safe"
