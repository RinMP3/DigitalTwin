import cupy as cp

ALU_KERNEL_CODE = r"""
extern "C" __global__
void alu_stress_kernel(float* data, int iterations) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    float val = data[idx];
    for (int i = 0; i < iterations; i++) {
        val = val * 1.000001f + 0.000001f;
        if (val > 1000.0f) val = 1.0f;
    }
    data[idx] = val;
}
"""

TENSOR_KERNEL_CODE = r"""
#include <mma.h>
using namespace nvcuda;

extern "C" __global__
void tensor_stress_kernel(int iterations) {
    wmma::fragment<wmma::matrix_a, 16, 16, 16, half, wmma::row_major> a_frag;
    wmma::fragment<wmma::matrix_b, 16, 16, 16, half, wmma::col_major> b_frag;
    wmma::fragment<wmma::accumulator, 16, 16, 16, float> c_frag;

    wmma::fill_fragment(a_frag, __float2half(1.0f));
    wmma::fill_fragment(b_frag, __float2half(1.0f));
    wmma::fill_fragment(c_frag, 0.0f);

    #pragma unroll
    for (int i = 0; i < iterations; i++) {
        wmma::mma_sync(c_frag, a_frag, b_frag, c_frag);
    }
}
"""

_alu_module = cp.RawModule(code=ALU_KERNEL_CODE, options=('-std=c++11',), backend='nvrtc')
_alu_kernel = _alu_module.get_function("alu_stress_kernel")

_tensor_module = cp.RawModule(code=TENSOR_KERNEL_CODE, options=('-std=c++11',), backend='nvrtc')
_tensor_kernel = _tensor_module.get_function("tensor_stress_kernel")

def run_alu_stress(iterations: int = 50000) -> float:
    size = 1024 * 1024
    data = cp.ones(size, dtype=cp.float32)
    threads_per_block = 256
    blocks_per_grid = (size + threads_per_block - 1) // threads_per_block
    
    _alu_kernel((blocks_per_grid,), (threads_per_block,), (data, iterations))
    cp.cuda.Stream.null.synchronize()
    
    return float(data.sum())

def run_tensor_stress(iterations: int = 50000) -> float:
    threads_per_block = 32
    blocks_per_grid = 128
    
    _tensor_kernel((blocks_per_grid,), (threads_per_block,), (iterations,))
    cp.cuda.Stream.null.synchronize()
    
    return float(iterations * blocks_per_grid)