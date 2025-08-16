# error_types.py - Comprehensive Error Handling for GemFinder

from enum import Enum
import time
from typing import Dict, Any, Optional

class ErrorType(Enum):
    """Comprehensive error types for all scraper and API operations"""
    
    # 🌐 Network Level Errors
    SITE_DOWN = "SITE_DOWN"
    DNS_ERROR = "DNS_ERROR"
    CONNECTION_TIMEOUT = "CONNECTION_TIMEOUT"
    READ_TIMEOUT = "READ_TIMEOUT"
    SSL_ERROR = "SSL_ERROR"
    NETWORK_UNREACHABLE = "NETWORK_UNREACHABLE"
    
    # 🚫 HTTP Level Errors
    ACCESS_DENIED = "ACCESS_DENIED"          # 401/403
    NOT_FOUND = "NOT_FOUND"                  # 404
    RATE_LIMITED = "RATE_LIMITED"            # 429
    BLOCKED = "BLOCKED"                      # Bot detection/Captcha
    REDIRECT_ERROR = "REDIRECT_ERROR"        # Too many redirects
    SERVER_ERROR = "SERVER_ERROR"            # 5xx errors
    
    # 🔍 Scraping Level Errors
    SELECTOR_NOT_FOUND = "SELECTOR_NOT_FOUND"
    STRUCTURE_CHANGED = "STRUCTURE_CHANGED"
    NO_RESULTS = "NO_RESULTS"
    PARSING_ERROR = "PARSING_ERROR"
    UNEXPECTED_FORMAT = "UNEXPECTED_FORMAT"
    DATA_INCOMPLETE = "DATA_INCOMPLETE"
    
    # ⚙️ Technical Level Errors
    BROWSER_ERROR = "BROWSER_ERROR"          # Selenium issues
    MEMORY_ERROR = "MEMORY_ERROR"
    SCRIPT_TIMEOUT = "SCRIPT_TIMEOUT"        # JavaScript timeout
    ENCODING_ERROR = "ENCODING_ERROR"
    DEPENDENCY_ERROR = "DEPENDENCY_ERROR"    # Missing packages
    
    # 🔑 API Level Errors
    API_KEY_INVALID = "API_KEY_INVALID"
    API_QUOTA_EXCEEDED = "API_QUOTA_EXCEEDED"
    API_DEPRECATED = "API_DEPRECATED"
    API_MAINTENANCE = "API_MAINTENANCE"
    API_RESPONSE_INVALID = "API_RESPONSE_INVALID"
    
    # 🎵 Music Platform Specific Errors
    SEARCH_TERMS_INVALID = "SEARCH_TERMS_INVALID"
    REGION_BLOCKED = "REGION_BLOCKED"
    AGE_RESTRICTED = "AGE_RESTRICTED"
    PREMIUM_REQUIRED = "PREMIUM_REQUIRED"
    
    # ⚡ General Errors
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    CONFIG_ERROR = "CONFIG_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"

class ScraperError:
    """Structured error reporting for scrapers and APIs"""
    
    def __init__(
        self,
        error_type: ErrorType,
        platform: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        timestamp: Optional[float] = None
    ):
        self.error_type = error_type
        self.platform = platform
        self.message = message
        self.details = details or {}
        self.timestamp = timestamp or time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for logging/storage"""
        return {
            "error_type": self.error_type.value,
            "platform": self.platform,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp
        }
    
    def get_user_message(self) -> str:
        """Get user-friendly error message"""
        return ERROR_MESSAGES.get(self.error_type, f"Error on {self.platform}: {self.message}")
    
    def is_retryable(self) -> bool:
        """Check if this error type is worth retrying"""
        return self.error_type in RETRYABLE_ERRORS
    
    def get_severity(self) -> str:
        """Get error severity level"""
        if self.error_type in CRITICAL_ERRORS:
            return "CRITICAL"
        elif self.error_type in WARNING_ERRORS:
            return "WARNING"
        else:
            return "ERROR"

# User-friendly error messages
ERROR_MESSAGES = {
    # Network
    ErrorType.SITE_DOWN: "🔴 Website is currently unavailable",
    ErrorType.DNS_ERROR: "🌐 Cannot resolve website address",
    ErrorType.CONNECTION_TIMEOUT: "⏱️ Connection timeout - website is slow",
    ErrorType.READ_TIMEOUT: "📡 Data transfer timeout",
    ErrorType.SSL_ERROR: "🔒 Security certificate problem",
    
    # HTTP
    ErrorType.ACCESS_DENIED: "🚫 Access denied by website",
    ErrorType.NOT_FOUND: "❌ Page not found",
    ErrorType.RATE_LIMITED: "🐌 Too many requests - please wait",
    ErrorType.BLOCKED: "🤖 Bot detection activated",
    ErrorType.SERVER_ERROR: "⚡ Server error on website",
    
    # Scraping
    ErrorType.SELECTOR_NOT_FOUND: "🔍 Website layout changed - selector missing",
    ErrorType.STRUCTURE_CHANGED: "🔄 Website structure has changed",
    ErrorType.NO_RESULTS: "📭 No search results found",
    ErrorType.PARSING_ERROR: "🔧 Data extraction failed",
    ErrorType.UNEXPECTED_FORMAT: "📄 Unexpected data format",
    
    # Technical
    ErrorType.BROWSER_ERROR: "🌐 Browser automation failed",
    ErrorType.MEMORY_ERROR: "💾 Not enough memory",
    ErrorType.SCRIPT_TIMEOUT: "⏰ JavaScript execution timeout",
    ErrorType.ENCODING_ERROR: "📝 Text encoding problem",
    
    # API
    ErrorType.API_KEY_INVALID: "🔑 Invalid API key",
    ErrorType.API_QUOTA_EXCEEDED: "📊 API quota exceeded",
    ErrorType.API_DEPRECATED: "🏗️ API version outdated",
    ErrorType.API_MAINTENANCE: "🔧 API under maintenance",
    
    # Platform specific
    ErrorType.REGION_BLOCKED: "🌍 Content blocked in your region",
    ErrorType.AGE_RESTRICTED: "🔞 Age restricted content",
    ErrorType.PREMIUM_REQUIRED: "💎 Premium subscription required",
    
    # General
    ErrorType.UNKNOWN_ERROR: "❓ Unknown error occurred",
    ErrorType.CONFIG_ERROR: "⚙️ Configuration problem",
    ErrorType.VALIDATION_ERROR: "✏️ Invalid search parameters"
}

# Retryable errors (worth attempting again)
RETRYABLE_ERRORS = {
    ErrorType.CONNECTION_TIMEOUT,
    ErrorType.READ_TIMEOUT,
    ErrorType.RATE_LIMITED,
    ErrorType.SERVER_ERROR,
    ErrorType.API_MAINTENANCE,
    ErrorType.NETWORK_UNREACHABLE
}

# Critical errors (require immediate attention)
CRITICAL_ERRORS = {
    ErrorType.STRUCTURE_CHANGED,
    ErrorType.API_DEPRECATED,
    ErrorType.SELECTOR_NOT_FOUND,
    ErrorType.DEPENDENCY_ERROR
}

# Warning errors (minor issues)
WARNING_ERRORS = {
    ErrorType.NO_RESULTS,
    ErrorType.REGION_BLOCKED,
    ErrorType.PREMIUM_REQUIRED
}

def create_error(
    error_type: ErrorType,
    platform: str,
    message: str,
    **details
) -> ScraperError:
    """Helper function to create structured errors"""
    return ScraperError(error_type, platform, message, details)

def log_error(error: ScraperError) -> None:
    """Log structured error (can be extended for external logging)"""
    severity = error.get_severity()
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(error.timestamp))
    
    print(f"[{timestamp}] {severity} - {error.platform}: {error.error_type.value}")
    print(f"  Message: {error.message}")
    if error.details:
        print(f"  Details: {error.details}")
    print()