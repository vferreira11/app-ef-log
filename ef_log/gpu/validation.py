import os
import sys
import time
import json
import cupy as cp
import numpy as np
from typing import Dict, Tuple, Optional

class GPUValidator:
    def __init__(self):
        self.min_vram = 8  # GB
        self.min_compute = 7.0
        self.supported_models = {
            'RTX 3070 Ti': {'vram': 8, 'compute': 8.6},
            'RTX 3080': {'vram': 10, 'compute': 8.6},
            'RTX 3090': {'vram': 24, 'compute': 8.6},
            'RTX 2080 Ti': {'vram': 11, 'compute': 7.5},
            'Tesla T4': {'vram': 16, 'compute': 7.5},
            'Tesla V100': {'vram': 32, 'compute': 7.0}
        }
        
    def validate_hardware(self) -> Tuple[bool, Dict]:
        try:
            device = cp.cuda.Device(0)
            props = cp.cuda.runtime.getDeviceProperties(0)
            
            device_name = props['name'].decode('utf-8')
            total_memory = props['totalGlobalMem'] / (1024**3)  # Convert to GB
            compute_capability = float(f"{props['major']}.{props['minor']}")
            
            # Validate requirements
            meets_vram = total_memory / 1024 >= self.min_vram  # Convert to GB
            meets_compute = compute_capability >= self.min_compute
            is_supported = any(model.lower() in device_name.lower() for model in self.supported_models.keys())
            
            status = {
                'device_name': device_name,
                'total_memory': f"{total_memory:.1f}GB",
                'compute_capability': compute_capability,
                'meets_requirements': all([meets_vram, meets_compute, is_supported]),
                'details': {
                    'vram_check': meets_vram,
                    'compute_check': meets_compute,
                    'model_check': is_supported
                }
            }
            
            return True, status
            
        except Exception as e:
            return False, {'error': str(e)}
    
    def run_benchmark(self) -> Tuple[bool, Dict]:
        try:
            # Matrix multiplication benchmark
            size = 4096
            a = cp.random.rand(size, size, dtype=cp.float32)
            b = cp.random.rand(size, size, dtype=cp.float32)
            
            start = time.time()
            c = cp.matmul(a, b)
            cp.cuda.Stream.null.synchronize()
            compute_time = time.time() - start
            
            # Memory bandwidth test
            data_size = 1000 * 1024 * 1024  # 1GB
            data = cp.random.rand(data_size // 4, dtype=cp.float32)
            
            start = time.time()
            data_copy = cp.copy(data)
            cp.cuda.Stream.null.synchronize()
            memory_time = time.time() - start
            
            memory_bandwidth = data_size / (memory_time * 1e9)  # GB/s
            
            results = {
                'compute_performance': {
                    'matrix_size': size,
                    'time': f"{compute_time:.3f}s",
                    'tflops': 2 * size**3 / (compute_time * 1e12)
                },
                'memory_performance': {
                    'data_size': f"{data_size / 1e9:.1f}GB",
                    'bandwidth': f"{memory_bandwidth:.1f}GB/s"
                }
            }
            
            return True, results
            
        except Exception as e:
            return False, {'error': str(e)}
    
    def validate_cuda_env(self) -> Tuple[bool, Dict]:
        try:
            cuda_version = cp.cuda.runtime.runtimeGetVersion()
            driver_version = cp.cuda.runtime.driverGetVersion()
            
            status = {
                'cuda_version': f"{cuda_version//1000}.{(cuda_version%1000)//10}",
                'driver_version': f"{driver_version//1000}.{(driver_version%1000)//10}",
                'cupy_version': cp.__version__,
                'numpy_version': np.__version__
            }
            
            return True, status
            
        except Exception as e:
            return False, {'error': str(e)}

def main(full_check: bool = False):
    validator = GPUValidator()
    results = {}
    
    # Hardware validation
    hw_success, hw_results = validator.validate_hardware()
    results['hardware'] = hw_results
    
    if not hw_success:
        print(json.dumps(results, indent=2))
        sys.exit(1)
    
    # CUDA environment check
    env_success, env_results = validator.validate_cuda_env()
    results['environment'] = env_results
    
    if full_check and hw_success and env_success:
        try:
            # Try using basic arrays instead of random for benchmark
            a = cp.ones((1000, 1000), dtype=cp.float32)
            b = cp.ones((1000, 1000), dtype=cp.float32)
            start = time.time()
            c = cp.matmul(a, b)
            cp.cuda.Stream.null.synchronize()
            compute_time = time.time() - start
            
            results['benchmark'] = {
                'matrix_multiply': {
                    'size': 1000,
                    'time': f"{compute_time:.3f}s",
                    'tflops': 2 * 1000**3 / (compute_time * 1e12)
                }
            }
        except Exception as e:
            results['benchmark'] = {'error': str(e)}
    
    print(json.dumps(results, indent=2))
    sys.exit(0 if all([hw_success, env_success]) else 1)

if __name__ == '__main__':
    full_check = '--full-check' in sys.argv
    main(full_check)