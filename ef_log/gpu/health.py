import os
import sys
import time
import json
import cupy as cp
import numpy as np
from typing import Dict, Tuple, Optional

class GPUHealthMonitor:
    def __init__(self):
        self.warning_temp = 75  # °C
        self.critical_temp = 85  # °C
        self.warning_memory = 0.85  # 85% utilization
        self.critical_memory = 0.95  # 95% utilization
        
    def monitor_memory(self) -> Tuple[bool, Dict]:
        try:
            device = cp.cuda.Device(0)
            free, total = device.mem_info
            used = total - free
            
            utilization = used / total
            status = 'healthy'
            if utilization >= self.critical_memory:
                status = 'critical'
            elif utilization >= self.warning_memory:
                status = 'warning'
            
            results = {
                'total_memory': f"{total / (1024**3):.2f}GB",
                'used_memory': f"{used / (1024**3):.2f}GB",
                'free_memory': f"{free / (1024**3):.2f}GB",
                'utilization': f"{utilization * 100:.1f}%",
                'status': status
            }
            
            return status == 'healthy', results
            
        except Exception as e:
            return False, {'error': str(e)}
    
    def run_stress_test(self, duration: int = 60) -> Tuple[bool, Dict]:
        try:
            size = 4096
            results = {
                'iterations': 0,
                'errors': 0,
                'avg_time': 0.0,
                'max_memory': 0.0,
                'completed': False
            }
            
            start_time = time.time()
            total_time = 0
            
            while time.time() - start_time < duration:
                try:
                    # Allocate large matrices
                    a = cp.random.rand(size, size, dtype=cp.float32)
                    b = cp.random.rand(size, size, dtype=cp.float32)
                    
                    # Matrix multiplication
                    iter_start = time.time()
                    c = cp.matmul(a, b)
                    cp.cuda.Stream.null.synchronize()
                    iter_time = time.time() - iter_start
                    
                    # Update statistics
                    results['iterations'] += 1
                    total_time += iter_time
                    
                    # Check memory usage
                    _, total = cp.cuda.Device(0).mem_info
                    used = total - free
                    memory_usage = used / total
                    results['max_memory'] = max(results['max_memory'], memory_usage)
                    
                    # Clean up
                    del a, b, c
                    cp.get_default_memory_pool().free_all_blocks()
                    
                except Exception as e:
                    results['errors'] += 1
            
            results['completed'] = True
            results['avg_time'] = total_time / results['iterations'] if results['iterations'] > 0 else 0
            results['max_memory'] = f"{results['max_memory'] * 100:.1f}%"
            
            success = results['errors'] == 0 and results['completed']
            return success, results
            
        except Exception as e:
            return False, {'error': str(e)}
    
    def check_compute_stability(self) -> Tuple[bool, Dict]:
        try:
            # Test different precisions
            dtypes = [cp.float32, cp.float64]
            results = {'precision_tests': {}}
            
            for dtype in dtypes:
                type_name = str(dtype).split('.')[-1]
                
                # Generate test data
                a = cp.random.rand(1000, 1000).astype(dtype)
                b = cp.random.rand(1000, 1000).astype(dtype)
                
                # Test operations
                try:
                    # Matrix operations
                    c = cp.matmul(a, b)
                    d = cp.sqrt(cp.abs(c))
                    e = cp.sum(d)
                    
                    # Verify results
                    is_finite = cp.all(cp.isfinite(c)) and cp.all(cp.isfinite(d)) and cp.isfinite(e)
                    
                    results['precision_tests'][type_name] = {
                        'success': True,
                        'finite_check': bool(is_finite)
                    }
                    
                except Exception as e:
                    results['precision_tests'][type_name] = {
                        'success': False,
                        'error': str(e)
                    }
            
            # Check if all tests passed
            all_passed = all(test['success'] and test.get('finite_check', False) 
                           for test in results['precision_tests'].values())
            
            return all_passed, results
            
        except Exception as e:
            return False, {'error': str(e)}
    
    def monitor_temperature(self) -> Tuple[bool, Dict]:
        try:
            # This is a placeholder as CuPy doesn't provide direct temperature access
            # In a real implementation, you would use nvidia-smi or similar
            results = {
                'warning': "Temperature monitoring requires nvidia-smi or similar tool",
                'recommendation': "Use 'nvidia-smi dmon' for temperature monitoring"
            }
            return True, results
            
        except Exception as e:
            return False, {'error': str(e)}

def main(full_check: bool = False):
    monitor = GPUHealthMonitor()
    results = {}
    
    # Memory monitoring
    mem_success, mem_results = monitor.monitor_memory()
    results['memory'] = mem_results
    
    # Temperature monitoring
    temp_success, temp_results = monitor.monitor_temperature()
    results['temperature'] = temp_results
    
    # Compute stability check
    stability_success, stability_results = monitor.check_compute_stability()
    results['stability'] = stability_results
    
    if full_check:
        # Stress test (1 minute)
        stress_success, stress_results = monitor.run_stress_test(60)
        results['stress_test'] = stress_results
    
    # Overall health status
    results['healthy'] = all([mem_success, stability_success])
    
    print(json.dumps(results, indent=2))
    sys.exit(0 if results['healthy'] else 1)

if __name__ == '__main__':
    full_check = '--full' in sys.argv
    main(full_check)