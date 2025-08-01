"""
Performance monitoring and logging system for image translation operations.
"""

import time
import logging
import functools
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from contextlib import contextmanager
import threading
import json
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Performance metric data point."""
    operation: str
    duration: float
    timestamp: float
    memory_start: Optional[float] = None
    memory_end: Optional[float] = None
    memory_peak: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class PerformanceMonitor:
    """Monitor and log performance metrics for image translation operations."""
    
    def __init__(self, log_file: Optional[str] = None):
        """
        Initialize performance monitor.
        
        Args:
            log_file: Optional file path to write performance logs
        """
        self.metrics: List[PerformanceMetric] = []
        self.operation_counts: Dict[str, int] = {}
        self.operation_totals: Dict[str, float] = {}
        self.log_file = log_file
        self._lock = threading.Lock()
        
        # Setup performance logger
        self.perf_logger = logging.getLogger(f"{__name__}.performance")
        if log_file:
            handler = logging.FileHandler(log_file)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.perf_logger.addHandler(handler)
            self.perf_logger.setLevel(logging.INFO)
    
    def record_metric(self, metric: PerformanceMetric):
        """Record a performance metric."""
        with self._lock:
            self.metrics.append(metric)
            
            # Update aggregates
            op = metric.operation
            self.operation_counts[op] = self.operation_counts.get(op, 0) + 1
            self.operation_totals[op] = self.operation_totals.get(op, 0.0) + metric.duration
            
            # Log the metric
            log_msg = f"Performance: {op} completed in {metric.duration:.3f}s"
            if metric.memory_start and metric.memory_end:
                memory_delta = metric.memory_end - metric.memory_start
                log_msg += f" (memory: {memory_delta:+.1f}MB)"
            
            if not metric.success:
                log_msg += f" [FAILED: {metric.error_message}]"
            
            if metric.success:
                self.perf_logger.info(log_msg)
            else:
                self.perf_logger.error(log_msg)
    
    @contextmanager
    def measure_operation(self, operation_name: str, **metadata):
        """
        Context manager to measure operation performance.
        
        Args:
            operation_name: Name of the operation
            **metadata: Additional metadata to record
        """
        from .memory_tracker import get_memory_tracker
        
        start_time = time.time()
        start_memory = None
        peak_memory = None
        success = True
        error_message = None
        
        # Get memory tracker if available
        try:
            memory_tracker = get_memory_tracker()
            start_memory = memory_tracker.snapshot(f"{operation_name}_start").rss_mb
        except Exception:
            pass
        
        try:
            yield
        except Exception as e:
            success = False
            error_message = str(e)
            raise
        finally:
            duration = time.time() - start_time
            end_memory = None
            
            # Get final memory measurement
            try:
                if memory_tracker:
                    end_memory = memory_tracker.snapshot(f"{operation_name}_end").rss_mb
                    peak_memory = memory_tracker.peak_memory_mb
            except Exception:
                pass
            
            # Record the metric
            metric = PerformanceMetric(
                operation=operation_name,
                duration=duration,
                timestamp=start_time,
                memory_start=start_memory,
                memory_end=end_memory,
                memory_peak=peak_memory,
                success=success,
                error_message=error_message,
                metadata=metadata
            )
            
            self.record_metric(metric)
    
    def get_operation_stats(self, operation: str) -> Dict[str, Any]:
        """
        Get statistics for a specific operation.
        
        Args:
            operation: Operation name
            
        Returns:
            Dictionary with operation statistics
        """
        with self._lock:
            metrics = [m for m in self.metrics if m.operation == operation]
            
            if not metrics:
                return {"error": f"No metrics found for operation: {operation}"}
            
            durations = [m.duration for m in metrics]
            successes = [m for m in metrics if m.success]
            failures = [m for m in metrics if not m.success]
            
            stats = {
                "operation": operation,
                "total_calls": len(metrics),
                "successful_calls": len(successes),
                "failed_calls": len(failures),
                "success_rate": len(successes) / len(metrics) if metrics else 0,
                "total_duration": sum(durations),
                "average_duration": sum(durations) / len(durations),
                "min_duration": min(durations),
                "max_duration": max(durations),
            }
            
            # Memory statistics if available
            memory_metrics = [m for m in metrics if m.memory_start and m.memory_end]
            if memory_metrics:
                memory_deltas = [m.memory_end - m.memory_start for m in memory_metrics]
                stats["memory_stats"] = {
                    "average_memory_delta": sum(memory_deltas) / len(memory_deltas),
                    "max_memory_delta": max(memory_deltas),
                    "min_memory_delta": min(memory_deltas)
                }
            
            return stats
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        with self._lock:
            if not self.metrics:
                return {"error": "No performance metrics available"}
            
            # Overall statistics
            total_operations = len(self.metrics)
            successful_operations = len([m for m in self.metrics if m.success])
            total_duration = sum(m.duration for m in self.metrics)
            
            # Operation-specific stats
            operation_stats = {}
            for op in set(m.operation for m in self.metrics):
                operation_stats[op] = self.get_operation_stats(op)
            
            # Top slowest operations
            slowest = sorted(self.metrics, key=lambda m: m.duration, reverse=True)[:10]
            
            # Recent failures
            recent_failures = [
                m for m in sorted(self.metrics, key=lambda m: m.timestamp, reverse=True)[:50]
                if not m.success
            ]
            
            return {
                "summary": {
                    "total_operations": total_operations,
                    "successful_operations": successful_operations,
                    "failed_operations": total_operations - successful_operations,
                    "success_rate": successful_operations / total_operations,
                    "total_duration": total_duration,
                    "average_duration": total_duration / total_operations
                },
                "operation_stats": operation_stats,
                "slowest_operations": [
                    {
                        "operation": m.operation,
                        "duration": m.duration,
                        "timestamp": m.timestamp,
                        "success": m.success
                    } for m in slowest
                ],
                "recent_failures": [
                    {
                        "operation": m.operation,
                        "duration": m.duration,
                        "error": m.error_message,
                        "timestamp": m.timestamp
                    } for m in recent_failures
                ]
            }
    
    def export_metrics(self, filepath: str):
        """
        Export metrics to JSON file.
        
        Args:
            filepath: Path to export file
        """
        with self._lock:
            data = {
                "export_timestamp": time.time(),
                "metrics": [
                    {
                        "operation": m.operation,
                        "duration": m.duration,
                        "timestamp": m.timestamp,
                        "memory_start": m.memory_start,
                        "memory_end": m.memory_end,
                        "memory_peak": m.memory_peak,
                        "success": m.success,
                        "error_message": m.error_message,
                        "metadata": m.metadata
                    } for m in self.metrics
                ]
            }
            
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Exported {len(self.metrics)} metrics to {filepath}")
    
    def clear_metrics(self):
        """Clear all stored metrics."""
        with self._lock:
            count = len(self.metrics)
            self.metrics.clear()
            self.operation_counts.clear()
            self.operation_totals.clear()
            logger.info(f"Cleared {count} performance metrics")
    
    def get_health_check(self) -> Dict[str, Any]:
        """
        Perform performance health check.
        
        Returns:
            Health check results
        """
        with self._lock:
            if not self.metrics:
                return {"status": "no_data", "message": "No performance data available"}
            
            # Recent metrics (last 10 operations)
            recent_metrics = sorted(self.metrics, key=lambda m: m.timestamp, reverse=True)[:10]
            recent_failures = [m for m in recent_metrics if not m.success]
            
            # Average performance
            recent_durations = [m.duration for m in recent_metrics]
            avg_duration = sum(recent_durations) / len(recent_durations)
            
            status = "healthy"
            warnings = []
            
            # Check failure rate
            if len(recent_failures) / len(recent_metrics) > 0.2:  # >20% failure rate
                status = "warning"
                warnings.append(f"High failure rate: {len(recent_failures)}/{len(recent_metrics)} recent operations failed")
            
            # Check performance degradation
            if avg_duration > 10.0:  # Average operation takes >10 seconds
                status = "warning"
                warnings.append(f"Slow performance: average operation takes {avg_duration:.2f}s")
            
            # Check for long-running operations
            slow_ops = [m for m in recent_metrics if m.duration > 30.0]
            if slow_ops:
                status = "warning"
                warnings.append(f"Found {len(slow_ops)} operations taking >30s")
            
            return {
                "status": status,
                "warnings": warnings,
                "recent_metrics_count": len(recent_metrics),
                "recent_failure_count": len(recent_failures),
                "average_duration": avg_duration,
                "total_metrics": len(self.metrics)
            }


# Global performance monitor instance
_global_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance."""
    global _global_monitor
    if _global_monitor is None:
        log_file = "logs/performance.log"
        _global_monitor = PerformanceMonitor(log_file)
    return _global_monitor


def monitor_performance(operation_name: str = "", **metadata):
    """
    Decorator to monitor performance of a function.
    
    Args:
        operation_name: Operation name (uses function name if not provided)
        **metadata: Additional metadata to record
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            monitor = get_performance_monitor()
            op_name = operation_name or func.__name__
            
            with monitor.measure_operation(op_name, **metadata):
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


# Convenience functions
def measure_operation(operation_name: str, **metadata):
    """Context manager for measuring operation performance."""
    return get_performance_monitor().measure_operation(operation_name, **metadata)


def performance_report() -> Dict[str, Any]:
    """Get performance report from global monitor."""
    return get_performance_monitor().get_performance_report()


def performance_health_check() -> Dict[str, Any]:
    """Get performance health check from global monitor."""
    return get_performance_monitor().get_health_check()