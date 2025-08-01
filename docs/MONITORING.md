# Monitoring and Logging Guide

## Overview

The image translation system includes comprehensive monitoring, logging, and memory tracking capabilities to help you monitor performance, debug issues, and optimize resource usage.

## Components

### 1. Memory Tracker (`core.memory_tracker`)

Tracks memory usage throughout image processing operations.

#### Features
- Real-time memory monitoring
- Operation-specific memory tracking
- Memory leak detection
- Performance optimization suggestions
- Health checks and thresholds

#### Usage

```python
from core.memory_tracker import get_memory_tracker, memory_report

# Get global tracker
tracker = get_memory_tracker()

# Track an operation
with tracker.track_operation("image_processing"):
    # Your code here
    process_image()

# Get memory report
report = memory_report()
print(f"Current memory: {report['current_memory_mb']:.1f}MB")
```

#### Decorator Usage

```python
from core.memory_tracker import track_memory

@track_memory("my_function")
def process_data():
    # Function automatically tracked
    pass
```

### 2. Performance Monitor (`core.performance_monitor`)

Monitors operation performance and provides detailed analytics.

#### Features
- Operation timing and success tracking
- Performance trend analysis
- Health checks and alerting
- Metrics export and reporting
- Integration with memory tracking

#### Usage

```python
from core.performance_monitor import get_performance_monitor, performance_report

monitor = get_performance_monitor()

# Monitor an operation
with monitor.measure_operation("translation", batch_size=10):
    translate_texts(texts)

# Get performance report
report = performance_report()
print(f"Success rate: {report['summary']['success_rate']:.2%}")
```

#### Decorator Usage

```python
from core.performance_monitor import monitor_performance

@monitor_performance("batch_processing")
def process_batch(items):
    # Function automatically monitored
    pass
```

### 3. Logging System (`core.logging_config`)

Centralized logging configuration with multiple output targets.

#### Features
- Console and file logging
- Rotating log files
- Module-specific log levels
- Error-only logs
- System information logging

#### Setup

```python
from core.logging_config import setup_logging, get_logger

# Setup logging
setup_logging(
    log_level="INFO",
    log_dir="logs",
    console_output=True,
    file_output=True
)

# Use logger
logger = get_logger(__name__)
logger.info("Processing started")
```

#### Log Files

- `logs/app.log` - General application log
- `logs/errors.log` - Error-only log  
- `logs/performance.log` - Performance metrics log

## Integration Example

```python
from core.logging_config import setup_logging, get_logger
from core.memory_tracker import get_memory_tracker
from core.performance_monitor import get_performance_monitor

# Setup
setup_logging()
logger = get_logger(__name__)
memory_tracker = get_memory_tracker()
perf_monitor = get_performance_monitor()

# Combined monitoring
with perf_monitor.measure_operation("image_translation"):
    with memory_tracker.track_operation("image_translation"):
        result = translate_image(image)
        logger.info("Translation completed successfully")
```

## Health Monitoring

### Memory Health Check

```python
from core.memory_tracker import check_memory_health

health = check_memory_health(threshold_mb=1000)
if health['status'] == 'warning':
    for warning in health['warnings']:
        print(f"WARNING: {warning}")
```

### Performance Health Check

```python
from core.performance_monitor import performance_health_check

health = performance_health_check()
if health['status'] == 'warning':
    for warning in health['warnings']:
        print(f"WARNING: {warning}")
```

## Running the Demo

Execute the monitoring demonstration:

```bash
python example_monitoring.py
```

This will:
1. Initialize all monitoring systems
2. Process a test image (if available)
3. Generate comprehensive reports
4. Perform health checks
5. Export metrics to JSON

## Monitoring Best Practices

### 1. Enable Monitoring Early
```python
# At application startup
setup_logging(log_level="INFO")
memory_tracker = get_memory_tracker()
perf_monitor = get_performance_monitor()
```

### 2. Use Context Managers
```python
# Preferred approach
with memory_tracker.track_operation("processing"):
    with perf_monitor.measure_operation("processing"):
        do_work()
```

### 3. Regular Health Checks
```python
# Periodic health monitoring
def check_system_health():
    memory_health = check_memory_health()
    perf_health = performance_health_check()
    
    if memory_health['status'] != 'healthy':
        log_warnings(memory_health['warnings'])
    
    if perf_health['status'] != 'healthy':
        log_warnings(perf_health['warnings'])
```

### 4. Cleanup Management
```python
# Periodic cleanup
tracker = get_memory_tracker()
if len(tracker.snapshots) > 1000:
    tracker.clear_snapshots()

monitor = get_performance_monitor()
if len(monitor.metrics) > 10000:
    monitor.export_metrics("backup.json")
    monitor.clear_metrics()
```

## Configuration

### Environment Variables

```bash
# Optional: Custom log directory
export LOG_DIR="/var/log/imgtranslation"

# Optional: Log level
export LOG_LEVEL="DEBUG"
```

### Programmatic Configuration

```python
# Custom memory tracking
tracker = MemoryTracker(enable_continuous_monitoring=True)

# Custom performance monitoring
monitor = PerformanceMonitor(log_file="custom_perf.log")

# Custom logging
setup_logging(
    log_level="DEBUG",
    log_dir="custom_logs",
    max_file_size=50 * 1024 * 1024,  # 50MB
    backup_count=10
)
```

## Troubleshooting

### High Memory Usage
1. Check memory report for peak usage
2. Review memory tracking snapshots
3. Look for operations with large memory deltas
4. Implement suggested cleanup actions

### Slow Performance
1. Review performance report for slow operations
2. Check for failed operations
3. Monitor memory usage during slow operations
4. Optimize batch sizes and processing parameters

### Log File Issues
1. Ensure log directory permissions
2. Check disk space for log files
3. Adjust log rotation settings
4. Monitor log file sizes

## API Reference

See `docs/API.md` for detailed API documentation of all monitoring components.