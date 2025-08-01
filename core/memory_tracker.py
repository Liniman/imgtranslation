"""
Memory usage tracking and monitoring system for image translation processing.
"""

import psutil
import time
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
import threading
from contextlib import contextmanager

logger = logging.getLogger(__name__)


@dataclass
class MemorySnapshot:
    """Memory usage snapshot at a point in time."""
    timestamp: float
    rss_mb: float  # Resident Set Size in MB
    vms_mb: float  # Virtual Memory Size in MB
    percent: float  # Memory percentage
    available_mb: float  # Available system memory in MB
    operation: str = ""  # Description of operation


class MemoryTracker:
    """Track memory usage throughout image processing operations."""
    
    def __init__(self, enable_continuous_monitoring: bool = False):
        """
        Initialize memory tracker.
        
        Args:
            enable_continuous_monitoring: Enable background memory monitoring
        """
        self.process = psutil.Process()
        self.snapshots: List[MemorySnapshot] = []
        self.peak_memory_mb = 0.0
        self.baseline_memory_mb = 0.0
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        if enable_continuous_monitoring:
            self.start_monitoring()
        
        # Take baseline measurement
        self.baseline_memory_mb = self._get_current_memory().rss_mb
        logger.info(f"Memory tracker initialized. Baseline: {self.baseline_memory_mb:.1f}MB")
    
    def _get_current_memory(self) -> MemorySnapshot:
        """Get current memory usage snapshot."""
        try:
            memory_info = self.process.memory_info()
            system_memory = psutil.virtual_memory()
            
            return MemorySnapshot(
                timestamp=time.time(),
                rss_mb=memory_info.rss / 1024 / 1024,
                vms_mb=memory_info.vms / 1024 / 1024,
                percent=self.process.memory_percent(),
                available_mb=system_memory.available / 1024 / 1024
            )
        except Exception as e:
            logger.warning(f"Failed to get memory info: {e}")
            return MemorySnapshot(
                timestamp=time.time(),
                rss_mb=0.0,
                vms_mb=0.0,
                percent=0.0,
                available_mb=0.0
            )
    
    def snapshot(self, operation: str = "") -> MemorySnapshot:
        """
        Take a memory snapshot.
        
        Args:
            operation: Description of current operation
            
        Returns:
            Memory snapshot
        """
        snapshot = self._get_current_memory()
        snapshot.operation = operation
        
        self.snapshots.append(snapshot)
        
        # Update peak memory
        if snapshot.rss_mb > self.peak_memory_mb:
            self.peak_memory_mb = snapshot.rss_mb
        
        logger.debug(f"Memory snapshot - {operation}: {snapshot.rss_mb:.1f}MB RSS, {snapshot.percent:.1f}%")
        return snapshot
    
    @contextmanager
    def track_operation(self, operation_name: str):
        """
        Context manager to track memory usage of an operation.
        
        Args:
            operation_name: Name of operation being tracked
        """
        start_snapshot = self.snapshot(f"{operation_name} - start")
        start_time = time.time()
        
        try:
            yield self
        finally:
            end_snapshot = self.snapshot(f"{operation_name} - end")
            duration = time.time() - start_time
            memory_delta = end_snapshot.rss_mb - start_snapshot.rss_mb
            
            logger.info(
                f"Operation '{operation_name}' completed in {duration:.2f}s. "
                f"Memory change: {memory_delta:+.1f}MB "
                f"(Start: {start_snapshot.rss_mb:.1f}MB, End: {end_snapshot.rss_mb:.1f}MB)"
            )
    
    def start_monitoring(self, interval: float = 1.0):
        """
        Start continuous memory monitoring in background thread.
        
        Args:
            interval: Monitoring interval in seconds
        """
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        
        def monitor():
            while self.monitoring_active:
                self.snapshot("monitoring")
                time.sleep(interval)
        
        self.monitor_thread = threading.Thread(target=monitor, daemon=True)
        self.monitor_thread.start()
        logger.info(f"Started continuous memory monitoring (interval: {interval}s)")
    
    def stop_monitoring(self):
        """Stop continuous memory monitoring."""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
        logger.info("Stopped continuous memory monitoring")
    
    def get_memory_report(self) -> Dict:
        """
        Generate comprehensive memory usage report.
        
        Returns:
            Dictionary containing memory statistics
        """
        if not self.snapshots:
            return {"error": "No memory snapshots available"}
        
        current = self._get_current_memory()
        
        # Calculate statistics
        rss_values = [s.rss_mb for s in self.snapshots]
        avg_memory = sum(rss_values) / len(rss_values)
        min_memory = min(rss_values)
        max_memory = max(rss_values)
        
        return {
            "current_memory_mb": current.rss_mb,
            "baseline_memory_mb": self.baseline_memory_mb,
            "peak_memory_mb": self.peak_memory_mb,
            "average_memory_mb": avg_memory,
            "min_memory_mb": min_memory,
            "max_memory_mb": max_memory,
            "memory_increase_mb": current.rss_mb - self.baseline_memory_mb,
            "total_snapshots": len(self.snapshots),
            "available_system_memory_mb": current.available_mb,
            "memory_percentage": current.percent,
            "monitoring_active": self.monitoring_active
        }
    
    def check_memory_threshold(self, threshold_mb: float = 1000.0) -> bool:
        """
        Check if memory usage exceeds threshold.
        
        Args:
            threshold_mb: Memory threshold in MB
            
        Returns:
            True if memory usage is above threshold
        """
        current = self._get_current_memory()
        if current.rss_mb > threshold_mb:
            logger.warning(
                f"Memory usage ({current.rss_mb:.1f}MB) exceeds threshold ({threshold_mb:.1f}MB)"
            )
            return True
        return False
    
    def suggest_cleanup(self) -> List[str]:
        """
        Suggest memory cleanup actions based on current usage.
        
        Returns:
            List of cleanup suggestions
        """
        suggestions = []
        current = self._get_current_memory()
        
        if current.rss_mb > 500:
            suggestions.append("Consider processing images in smaller batches")
        
        if current.rss_mb > 1000:
            suggestions.append("Clear image caches and temporary data")
            suggestions.append("Reduce image resolution for processing")
        
        if current.available_mb < 500:
            suggestions.append("System memory is low - consider closing other applications")
        
        if len(self.snapshots) > 1000:
            suggestions.append("Clear memory tracking snapshots")
        
        return suggestions
    
    def clear_snapshots(self):
        """Clear all memory snapshots to free memory."""
        count = len(self.snapshots)
        self.snapshots.clear()
        logger.info(f"Cleared {count} memory snapshots")
    
    def __del__(self):
        """Cleanup when tracker is destroyed."""
        if self.monitoring_active:
            self.stop_monitoring()


# Global memory tracker instance
_global_tracker: Optional[MemoryTracker] = None


def get_memory_tracker() -> MemoryTracker:
    """Get global memory tracker instance."""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = MemoryTracker()
    return _global_tracker


def track_memory(operation: str = ""):
    """
    Decorator to track memory usage of a function.
    
    Args:
        operation: Operation name (uses function name if not provided)
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            tracker = get_memory_tracker()
            op_name = operation or func.__name__
            
            with tracker.track_operation(op_name):
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


# Convenience functions
def memory_snapshot(operation: str = "") -> MemorySnapshot:
    """Take a memory snapshot using global tracker."""
    return get_memory_tracker().snapshot(operation)


def memory_report() -> Dict:
    """Get memory report from global tracker."""
    return get_memory_tracker().get_memory_report()


def check_memory_health(threshold_mb: float = 1000.0) -> Dict:
    """
    Perform memory health check.
    
    Args:
        threshold_mb: Memory threshold for warnings
        
    Returns:
        Health check results
    """
    tracker = get_memory_tracker()
    report = tracker.get_memory_report()
    
    health = {
        "status": "healthy",
        "warnings": [],
        "suggestions": [],
        **report
    }
    
    if report["current_memory_mb"] > threshold_mb:
        health["status"] = "warning"
        health["warnings"].append(f"High memory usage: {report['current_memory_mb']:.1f}MB")
    
    if report["available_system_memory_mb"] < 500:
        health["status"] = "warning"
        health["warnings"].append("Low system memory available")
    
    if health["status"] == "warning":
        health["suggestions"] = tracker.suggest_cleanup()
    
    return health