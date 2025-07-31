import os
import sys
import json
import pkg_resources
import cupy as cp
import numpy as np
from typing import Dict, Tuple, List

class CompatibilityChecker:
    def __init__(self):
        self.required_packages = {
            'cupy-cuda12x': '>=12.0.0',
            'numpy': '>=1.20.0',
            'torch': '>=2.0.0',
            'streamlit': '>=1.0.0',
            'plotly': '>=5.0.0',
            'pandas': '>=1.3.0'
        }
        
        self.cuda_features = [
            'tensor_cores',
            'unified_memory',
            'cooperative_launch',
            'stream_priorities'
        ]
    
    def check_package_versions(self) -> Tuple[bool, Dict]:
        try:
            installed_packages = {pkg.key: pkg.version for pkg in pkg_resources.working_set}
            version_status = {}
            
            for package, required_version in self.required_packages.items():
                if package in installed_packages:
                    pkg_version = installed_packages[package]
                    meets_requirement = pkg_resources.parse_version(pkg_version) >= pkg_resources.parse_version(required_version.replace('>=', ''))
                    version_status[package] = {
                        'installed': pkg_version,
                        'required': required_version,
                        'compatible': meets_requirement
                    }
                else:
                    version_status[package] = {
                        'installed': None,
                        'required': required_version,
                        'compatible': False
                    }
            
            all_compatible = all(status['compatible'] for status in version_status.values())
            return all_compatible, version_status
            
        except Exception as e:
            return False, {'error': str(e)}
    
    def check_cuda_compatibility(self) -> Tuple[bool, Dict]:
        try:
            device = cp.cuda.Device(0)
            attributes = device.attributes
            
            cuda_version = cp.cuda.runtime.runtimeGetVersion()
            driver_version = cp.cuda.runtime.driverGetVersion()
            
            compute_major = attributes['computeCapabilityMajor']
            compute_minor = attributes['computeCapabilityMinor']
            
            status = {
                'cuda': {
                    'version': f"{cuda_version//1000}.{(cuda_version%1000)//10}",
                    'driver': f"{driver_version//1000}.{(driver_version%1000)//10}",
                    'compute_capability': f"{compute_major}.{compute_minor}"
                },
                'features': {}
            }
            
            # Check CUDA features
            status['features'] = {
                'tensor_cores': compute_major >= 7,
                'unified_memory': True,  # Supported since CUDA 6.0
                'cooperative_launch': compute_major >= 6,
                'stream_priorities': attributes.get('streamPrioritiesSupported', 0) == 1
            }
            
            all_features = all(status['features'].values())
            return all_features, status
            
        except Exception as e:
            return False, {'error': str(e)}
    
    def run_compute_test(self) -> Tuple[bool, Dict]:
        try:
            # Test basic operations
            a = cp.random.rand(1000, 1000, dtype=cp.float32)
            b = cp.random.rand(1000, 1000, dtype=cp.float32)
            
            ops_status = {
                'matrix_multiply': True,
                'reduction': True,
                'elementwise': True,
                'memory_transfer': True
            }
            
            try:
                # Matrix multiplication
                c = cp.matmul(a, b)
            except:
                ops_status['matrix_multiply'] = False
            
            try:
                # Reduction
                sum_a = cp.sum(a, axis=0)
            except:
                ops_status['reduction'] = False
            
            try:
                # Elementwise
                d = cp.sqrt(a + b)
            except:
                ops_status['elementwise'] = False
            
            try:
                # Memory transfer
                cpu_array = cp.asnumpy(a)
                gpu_array = cp.asarray(cpu_array)
            except:
                ops_status['memory_transfer'] = False
            
            all_ops_ok = all(ops_status.values())
            return all_ops_ok, ops_status
            
        except Exception as e:
            return False, {'error': str(e)}

def main():
    checker = CompatibilityChecker()
    results = {}
    
    # Check package versions
    pkg_success, pkg_results = checker.check_package_versions()
    results['packages'] = pkg_results
    
    # Check CUDA compatibility
    cuda_success, cuda_results = checker.check_cuda_compatibility()
    results['cuda'] = cuda_results
    
    # Run compute tests
    compute_success, compute_results = checker.run_compute_test()
    results['compute_test'] = compute_results
    
    # Overall compatibility status
    results['compatible'] = all([pkg_success, cuda_success, compute_success])
    
    print(json.dumps(results, indent=2))
    sys.exit(0 if results['compatible'] else 1)

if __name__ == '__main__':
    main()