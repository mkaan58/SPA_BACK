# spa/utils/performance_monitor.py - Performance monitoring

class AIPerformanceMonitor:
    """Monitor AI operation performance"""
    
    def __init__(self):
        self.operations = []
    
    def start_operation(self, operation_type, context_size=0):
        """Start monitoring an operation"""
        import time
        
        operation = {
            'type': operation_type,
            'start_time': time.time(),
            'context_size': context_size,
            'status': 'running'
        }
        
        self.operations.append(operation)
        return len(self.operations) - 1  # Return operation ID
    
    def end_operation(self, operation_id, success=True, error=None):
        """End monitoring an operation"""
        import time
        
        if operation_id < len(self.operations):
            operation = self.operations[operation_id]
            operation['end_time'] = time.time()
            operation['duration'] = operation['end_time'] - operation['start_time']
            operation['status'] = 'success' if success else 'failed'
            operation['error'] = error
            
            # Log performance
            logger.info(f"AI Operation: {operation['type']} - {operation['duration']:.2f}s - {operation['status']}")
            
            return operation['duration']
        
        return 0
    
    def get_average_duration(self, operation_type):
        """Get average duration for operation type"""
        durations = [
            op['duration'] for op in self.operations 
            if op.get('type') == operation_type and 'duration' in op
        ]
        
        return sum(durations) / len(durations) if durations else 0
    
    def get_performance_stats(self):
        """Get performance statistics"""
        total_operations = len(self.operations)
        successful_operations = len([op for op in self.operations if op.get('status') == 'success'])
        
        return {
            'total_operations': total_operations,
            'successful_operations': successful_operations,
            'success_rate': (successful_operations / total_operations * 100) if total_operations > 0 else 0,
            'average_duration': self.get_average_duration('ai_structural_edit')
        }

# Create global instances
ai_performance_monitor = AIPerformanceMonitor()