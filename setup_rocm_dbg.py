import os
from setuptools import setup, Extension, find_packages
import subprocess
import torch
from torch.utils.cpp_extension import BuildExtension, CppExtension, CUDAExtension, CUDA_HOME

version_dependent_macros = [
    '-DVERSION_GE_1_1',
    '-DVERSION_GE_1_3',
    '-DVERSION_GE_1_5',
]

# Common C++ flags
cpp_flags = ['-O0','-g', '-std=c++17'] + version_dependent_macros

# ROCm-specific flags
hip_flags = [
    '-D__HIP_PLATFORM_AMD__=1',
    '-DUSE_ROCM=1',
    '-DHIPBLAS_V2',
    '-DCUDA_HAS_FP16=1',
    '-D__HIP_NO_HALF_OPERATORS__=1',
    '-D__HIP_NO_HALF_CONVERSIONS__=1',
    '-DHIP_ENABLE_WARP_SYNC_BUILTINS=1',
    '-fPIC',
    '-O0',
    '-g',
]
hipcc_flags = hip_flags + ['-gline-tables-only']

# ROCm architectures to compile for
rocm_archs = [
    'gfx906',  # MI50
    'gfx908',  # MI100
    'gfx90a',  # MI200
    'gfx942'   # MI300
]

arch_flags = [f'--offload-arch={arch}' for arch in rocm_archs]

if torch.version.hip is not None:
    print("Building with ROCm support")
    extension = CUDAExtension(
        name="attn_core_inplace_cuda",
        sources=[
            "openfold/utils/kernel/csrc/softmax_cuda.cpp",
            "openfold/utils/kernel/csrc/softmax_hip_kernel.hip",  # Note the .hip extension
        ],
        include_dirs=[
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'openfold/utils/kernel/csrc/'
            )
        ],
        extra_compile_args={
            'cxx': cpp_flags + hip_flags,
            'nvcc': hipcc_flags + arch_flags + version_dependent_macros
        }
    )
else:
    print("ROCm not found, skipping GPU extension")
    extension = None

modules = [extension] if extension is not None else []

setup(
    name='openfold',
    version='2.0.0',
    description='A PyTorch reimplementation of DeepMind\'s AlphaFold 2',
    author='OpenFold Team',
    author_email='jennifer.wei@omsf.io',
    license='Apache License, Version 2.0',
    url='https://github.com/aqlaboratory/openfold',
    packages=find_packages(exclude=["tests", "scripts"]),
    include_package_data=True,
    package_data={
        "openfold": ['utils/kernel/csrc/*'],
        "": ["resources/stereo_chemical_props.txt"]
    },
    ext_modules=modules,
    cmdclass={'build_ext': BuildExtension},
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.10',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
)