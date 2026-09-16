# Clean logging utility for readable terminal output

import os
from datetime import datetime

class EMRLogger:
    """Handles clean, readable logging for EMR script execution."""
    
    def __init__(self, log_dir="downloads/logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # Create log file with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_file = os.path.join(log_dir, f"execution_{timestamp}.log")
        
        # Write header to log file
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write(f"{'='*80}\n")
            f.write(f"EMR Document Downloader - Execution Log\n")
            f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*80}\n\n")
    
    def log(self, message, level="INFO"):
        """Log message to both console and file."""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        
        # Print to console with formatting
        print(log_message)
        
        # Write to file
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + "\n")
    
    def section(self, title):
        """Log a section header."""
        separator = "─" * 80
        self.log(f"\n{separator}")
        self.log(f"  {title}")
        self.log(f"{separator}")
    
    def success(self, message):
        """Log success message with checkmark."""
        self.log(f"✓ {message}")
    
    def info(self, message):
        """Log info message."""
        self.log(f"ℹ {message}")
    
    def warning(self, message):
        """Log warning message."""
        self.log(f"⚠ {message}")
    
    def error(self, message):
        """Log error message."""
        self.log(f"✗ {message}")
    
    def patient_start(self, patient_id, first_name, last_name, current, total):
        """Log patient processing start."""
        self.log(f"\n{'─'*80}")
        self.log(f"[{current}/{total}] Processing Patient: {patient_id} | {first_name} {last_name}")
        self.log(f"{'─'*80}")
    
    def patient_skipped(self, patient_id, first_name, last_name):
        """Log patient being skipped."""
        self.log(f"✓ SKIPPED - Patient {patient_id} ({first_name} {last_name}) already processed with all documents")
    
    def patient_download_start(self, doc_type, patient_name):
        """Log download start for a document type."""
        emoji_map = {
            'Encounter': '🏥',
            'Consent': '📝',
            'Invoice': '💳'
        }
        emoji = emoji_map.get(doc_type, '📄')
        self.log(f"  {emoji} Starting {doc_type} download for {patient_name}...")
    
    def patient_download_complete(self, doc_type, count, patient_name):
        """Log download completion for a document type."""
        self.log(f"  ✓ {doc_type}: Downloaded {count} file(s) for {patient_name}")
    
    def patient_download_failed(self, doc_type, patient_name, error):
        """Log download failure for a document type."""
        self.log(f"  ✗ {doc_type}: Failed for {patient_name} - {error}")
    
    def patient_complete(self, patient_id, first_name, last_name):
        """Log patient processing complete."""
        self.log(f"✓ COMPLETED - Patient {patient_id} ({first_name} {last_name}) all files processed")
    
    def summary(self, total, processed, skipped, total_files):
        """Log execution summary."""
        self.section("EXECUTION SUMMARY")
        self.log(f"Total Patients:      {total}")
        self.log(f"Processed:           {processed}")
        self.log(f"Skipped:             {skipped}")
        self.log(f"Total Files Downloaded: {total_files}")
        self.log(f"\nLog file: {self.log_file}")
        self.log(f"{'='*80}\n")

# Global logger instance
logger = None

def init_logger(log_dir="downloads/logs"):
    """Initialize global logger."""
    global logger
    logger = EMRLogger(log_dir)
    return logger

def get_logger():
    """Get global logger instance."""
    global logger
    if logger is None:
        logger = EMRLogger()
    return logger
