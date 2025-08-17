"""
Async tasks for marker generation
"""
from backend.core.celery_app import celery_app
from celery import Task
import logging
import time

logger = logging.getLogger(__name__)

class CallbackTask(Task):
    """Task with callbacks"""
    def on_success(self, retval, task_id, args, kwargs):
        """Success callback"""
        logger.info(f"Task {task_id} succeeded with result: {retval}")
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Failure callback"""
        logger.error(f"Task {task_id} failed with exception: {exc}")

@celery_app.task(base=CallbackTask, bind=True, name='generate_batch_markers')
def generate_batch_markers_async(self, batch_config):
    """Generate batch of markers asynchronously"""
    try:
        from aruco_generator.aruco import ArUCOGenerator
        from aruco_generator.lightburn import LightBurnExporter
        from backend.repositories.marker_repository import MarkerRepository
        from backend.services.marker_service import MarkerService
        
        # Update task state
        self.update_state(state='PROCESSING', meta={'current': 0, 'total': len(batch_config)})
        
        # Initialize services
        aruco_gen = ArUCOGenerator()
        lightburn_exporter = LightBurnExporter()
        marker_repository = MarkerRepository()
        marker_service = MarkerService(aruco_gen, lightburn_exporter, marker_repository)
        
        results = []
        for i, config in enumerate(batch_config):
            # Update progress
            self.update_state(
                state='PROCESSING',
                meta={'current': i + 1, 'total': len(batch_config)}
            )
            
            # Generate markers
            result = marker_service.generate_markers(config)
            results.append(result)
            
            # Simulate some processing time
            time.sleep(0.5)
        
        return {
            'status': 'completed',
            'results': results,
            'total': len(results)
        }
        
    except Exception as e:
        logger.error(f"Batch generation failed: {e}")
        raise

@celery_app.task(bind=True, name='export_markers_async')
def export_markers_async(self, data, formats):
    """Export markers in multiple formats asynchronously"""
    try:
        from backend.services.export_service import ExportService
        
        # Update task state
        self.update_state(state='PROCESSING', meta={'current': 0, 'total': len(formats)})
        
        export_service = ExportService()
        results = []
        
        for i, format_name in enumerate(formats):
            # Update progress
            self.update_state(
                state='PROCESSING',
                meta={'current': i + 1, 'total': len(formats)}
            )
            
            # Export in format
            if format_name == 'lightburn':
                file_data, filename = export_service.export_lightburn(data)
            elif format_name == 'svg':
                file_data, filename = export_service.export_svg(data)
            elif format_name == 'pdf':
                file_data, filename = export_service.export_pdf(data)
            elif format_name == 'dxf':
                file_data, filename = export_service.export_dxf(data)
            else:
                continue
            
            results.append({
                'format': format_name,
                'filename': filename,
                'status': 'success'
            })
        
        return {
            'status': 'completed',
            'exports': results
        }
        
    except Exception as e:
        logger.error(f"Export failed: {e}")
        raise

@celery_app.task(name='cleanup_old_markers')
def cleanup_old_markers():
    """Clean up old marker data periodically"""
    try:
        from datetime import datetime, timedelta
        from backend.repositories.marker_repository import MarkerRepository
        
        repository = MarkerRepository()
        
        # Clean up markers older than 7 days
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        
        # This would normally interact with database
        # For now, just log the action
        logger.info(f"Cleaning up markers older than {cutoff_date}")
        
        return {'status': 'completed', 'message': 'Cleanup completed'}
        
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        raise