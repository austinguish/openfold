import os
from setuptools import setup, find_packages
from torch.utils.cpp_extension import BuildExtension, HIPExtension

version_dependent_macros = [
    '-DVERSION_GE_1_1',
    '-DVERSION_GE_1_3',
    '-DVERSION_GE_1_5',
]

extra_hip_flags = [
    '-std=c++17',
    '-march=gfx906;gfx90a;gfx942',  # For Vega or newer GPUs
    # 根据您的 GPU 型号调整 -march 参数，例如：
    # '-march=gfx906',  # For Vega or newer GPUs
    # '-march=gfx900',  # For older Vega GPUs
    # '-march=gfx1030', # For RDNA2 GPUs
    # ...
]

modules = [
    HIPExtension(
        name="attn_core_inplace_hip",
        sources=[
            "openfold/utils/kernel/csrc/softmax_hip_kernel.cpp",
        ],
        include_dirs=[
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'openfold/utils/kernel/csrc/'
            )
        ],
        extra_compile_args={
            'cxx': ['-O3'] + version_dependent_macros,
            'hip': (
                ['-O3', '--use_fast_math'] +
                version_dependent_macros +
                extra_hip_flags
            ),
        }
    )
]

setup(
    name='openfold-hip',  # 修改包名，避免与原版冲突
    version='2.0.0-hip',  # 修改版本号
    description='OpenFold with HIP support',
    author='Your Name',  # 修改作者信息
    author_email='your.email@example.com',
    license='Apache License, Version 2.0',
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