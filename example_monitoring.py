#!/usr/bin/env python3
"""
Example demonstrating the integrated monitoring, logging, and memory tracking system.
"""

import time
from pathlib import Path
from PIL import Image

# Setup logging first
from core.logging_config import setup_logging, get_logger, log_system_info

# Setup monitoring systems
from core.memory_tracker import get_memory_tracker, memory_report, check_memory_health
from core.performance_monitor import get_performance_monitor, performance_report, performance_health_check

# Main processing modules
from core.image_processor import ImageProcessor
from core.translator import TranslationEngine
from core.ocr_engine import OCREngine


def main():
    """Demonstrate the monitoring system."""
    # Setup logging
    setup_logging(log_level="INFO", log_dir="logs")
    logger = get_logger(__name__)
    
    logger.info("Starting monitoring system demonstration")
    log_system_info()
    
    # Initialize monitoring systems
    memory_tracker = get_memory_tracker()
    perf_monitor = get_performance_monitor()
    
    # Initialize processing components
    logger.info("Initializing processing components...")
    
    with memory_tracker.track_operation("component_initialization"):
        processor = ImageProcessor()
        translator = TranslationEngine()
        ocr = OCREngine()
    
    # Simulate image processing workflow
    test_image_path = "assets/Sports-Research-Omega-3-Fish-Oil-Triple-Strength-180-Softgels-07-29-2025_05_32_PM.png"
    
    if Path(test_image_path).exists():
        logger.info(f"Processing test image: {test_image_path}")
        
        # Monitor the entire workflow
        with perf_monitor.measure_operation("full_image_translation", image_path=test_image_path):
            try:
                # Load image
                with memory_tracker.track_operation("image_loading"):
                    image = Image.open(test_image_path)
                    logger.info(f"Loaded image: {image.size}")
                
                # OCR processing
                with memory_tracker.track_operation("ocr_processing"):
                    text_regions = ocr.detect_text(image, confidence_threshold=0.5)
                    logger.info(f"Detected {len(text_regions)} text regions")
                
                # Translation
                if text_regions:
                    texts = [region.get('text', '') for region in text_regions if region.get('text')]
                    if texts:
                        with memory_tracker.track_operation("batch_translation"):
                            translations = translator.translate_batch(texts[:3], target_lang='uk')  # Limit for demo
                            logger.info(f"Translated {len(translations)} text segments")
                
                # Image processing (simulation - we'll just create a mask)
                with memory_tracker.track_operation("image_processing"):
                    if text_regions:
                        mask = processor.create_enhanced_mask(image, text_regions[:3])  # Limit for demo
                        logger.info("Created processing mask")
                
            except Exception as e:
                logger.error(f"Error during processing: {e}", exc_info=True)
    
    else:
        logger.warning(f"Test image not found: {test_image_path}")
        
        # Simulate some operations for demo
        logger.info("Running simulation operations...")
        
        for i in range(3):
            with perf_monitor.measure_operation(f"simulation_op_{i}", iteration=i):
                time.sleep(0.5)  # Simulate work
                memory_tracker.snapshot(f"simulation_step_{i}")
    
    # Generate reports
    logger.info("=== MEMORY REPORT ===")
    mem_report = memory_report()
    for key, value in mem_report.items():
        logger.info(f"{key}: {value}")
    
    logger.info("=== PERFORMANCE REPORT ===")
    perf_report = performance_report()
    logger.info(f"Total operations: {perf_report['summary']['total_operations']}")
    logger.info(f"Success rate: {perf_report['summary']['success_rate']:.2%}")
    logger.info(f"Average duration: {perf_report['summary']['average_duration']:.3f}s")
    
    # Health checks
    logger.info("=== HEALTH CHECKS ===")
    
    memory_health = check_memory_health()
    logger.info(f"Memory health: {memory_health['status']}")
    if memory_health.get('warnings'):
        for warning in memory_health['warnings']:
            logger.warning(f"Memory: {warning}")
    
    perf_health = performance_health_check()
    logger.info(f"Performance health: {perf_health['status']}")
    if perf_health.get('warnings'):
        for warning in perf_health['warnings']:
            logger.warning(f"Performance: {warning}")
    
    # Export data
    logger.info("Exporting monitoring data...")
    
    try:
        perf_monitor.export_metrics("logs/performance_metrics.json")
        logger.info("Performance metrics exported")
    except Exception as e:
        logger.error(f"Failed to export performance metrics: {e}")
    
    # Cleanup suggestions
    suggestions = memory_tracker.suggest_cleanup()
    if suggestions:
        logger.info("=== CLEANUP SUGGESTIONS ===")
        for suggestion in suggestions:
            logger.info(f"- {suggestion}")
    
    logger.info("Monitoring demonstration completed")


if __name__ == "__main__":
    main()