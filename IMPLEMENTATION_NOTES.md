# Dynamic Scheduler Discovery Implementation

## Overview

This implementation enables the DINO Upscale custom node to automatically discover and use any schedulers and samplers that are registered in ComfyUI, including those added by other custom nodes.

## Problem Statement

Previously, the node had hardcoded lists of schedulers and samplers:
- When users installed custom scheduler nodes (e.g., FlowMatchEulerDiscreteScheduler), they wouldn't appear in DINO Upscale's dropdown
- Other built-in samplers (KSampler, KSampler Advanced) automatically showed custom schedulers
- Users had to manually edit the node code to add new schedulers

## Solution

Modified the `INPUT_TYPES()` method to dynamically import scheduler and sampler lists from ComfyUI's sampler registry, matching the behavior of built-in nodes.

### Code Changes

**File: `nodes.py`**

Added dynamic discovery at the beginning of `INPUT_TYPES()`:

```python
@classmethod
def INPUT_TYPES(cls):
    """Define node inputs"""
    # Import scheduler and sampler lists from ComfyUI to automatically include custom ones
    try:
        import comfy.samplers
        scheduler_list = comfy.samplers.KSampler.SCHEDULERS
        sampler_list = comfy.samplers.KSampler.SAMPLERS
    except (ImportError, AttributeError):
        # Fallback to default lists if ComfyUI sampler import fails
        scheduler_list = ["normal", "karras", "exponential", "sgm_uniform", "simple", "ddim_uniform", "beta"]
        sampler_list = ["euler", "euler_a", "heun", "dpm_2", "dpm_2_a", "lms", 
                       "dpm_fast", "dpm_adaptive", "dpmpp_2s_a", "dpmpp_2m", 
                       "dpmpp_2m_sde", "dpmpp_3m_sde", "ddim", "uni_pc", "uni_pc_bh2"]
    
    return {
        "required": {
            ...
            "sampler_name": (sampler_list, {"default": "euler"}),
            "scheduler": (scheduler_list, {"default": "normal"}),
            ...
```

**File: `README.md`**

Added documentation footnote in the parameter table explaining the auto-discovery feature.

## How It Works

1. **ComfyUI Scheduler Registry**: ComfyUI maintains global lists of schedulers and samplers in `comfy.samplers.KSampler.SCHEDULERS` and `comfy.samplers.KSampler.SAMPLERS`

2. **Custom Node Registration**: When custom scheduler nodes load, they register themselves:
   ```python
   from comfy.samplers import SCHEDULER_HANDLERS, SCHEDULER_NAMES
   
   SCHEDULER_HANDLERS["MyScheduler"] = SchedulerHandler(my_handler_func)
   SCHEDULER_NAMES.append("MyScheduler")
   ```

3. **Dynamic Discovery**: Our node imports these lists at runtime, automatically including any custom schedulers/samplers

4. **Fallback**: If ComfyUI imports fail (e.g., during standalone testing), it falls back to sensible defaults

## Benefits

✅ **Automatic Detection**: Custom schedulers/samplers appear immediately after ComfyUI restart  
✅ **No Code Updates**: Users don't need to modify node code  
✅ **Consistency**: Matches behavior of built-in ComfyUI samplers  
✅ **Future-Proof**: Works with any future custom schedulers/samplers  
✅ **Safe Fallback**: Works in standalone/testing environments  

## Testing

1. **Syntax Check**: ✅ Passed
2. **Logic Test**: ✅ Passed (see `test_dynamic_logic.py`)
3. **Integration Test**: To test in ComfyUI:
   - Install a custom scheduler node (e.g., FlowMatchEulerDiscreteScheduler)
   - Restart ComfyUI
   - Open DINO Upscale node
   - Verify custom scheduler appears in dropdown

## Compatibility

- **Backwards Compatible**: Existing workflows continue to work unchanged
- **Forward Compatible**: New schedulers/samplers are automatically detected
- **Fallback Safe**: Works without ComfyUI imports for testing

## References

- ComfyUI samplers: `/mnt/essdee/ComfyUI/comfy/samplers.py`
- Built-in nodes: `/mnt/essdee/ComfyUI/nodes.py`
- Example custom scheduler: `/mnt/essdee/ComfyUI/custom_nodes/erosdiffusion-eulerflowmatchingdiscretescheduler/__init__.py`

## Implementation Date

2025-12-04
