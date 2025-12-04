# Dynamic Scheduler and Sampler Discovery

## Summary

Updated the DINO Upscale custom node to dynamically discover available schedulers and samplers from ComfyUI, just like the built-in samplers (KSampler, KSampler Advanced, SamplerCustomAdvanced).

## Problem

The node had a hardcoded list of schedulers:
```python
"scheduler": (["normal", "karras", "exponential", "sgm_uniform", "simple", "ddim_uniform", "beta"], {...})
```

This meant:
- New custom schedulers (like FlowMatchEulerDiscreteScheduler) wouldn't appear in the dropdown
- Users had to manually update the node code to add new schedulers
- The node was inconsistent with ComfyUI's built-in samplers

## Solution

The built-in samplers use `comfy.samplers.KSampler.SCHEDULERS` and `comfy.samplers.KSampler.SAMPLERS`, which are dynamically populated lists that include:
1. All built-in schedulers/samplers
2. Any custom schedulers/samplers registered by custom nodes at import time

### How Custom Nodes Register Schedulers

Custom nodes (like erosDiffusion's FlowMatchEulerDiscreteScheduler) register their schedulers like this:

```python
from comfy.samplers import SchedulerHandler, SCHEDULER_HANDLERS, SCHEDULER_NAMES

# Define the scheduler function
def my_scheduler_handler(model_sampling, steps):
    # ... scheduler logic ...
    return sigmas

# Register it
if "MyScheduler" not in SCHEDULER_HANDLERS:
    handler = SchedulerHandler(handler=my_scheduler_handler, use_ms=True)
    SCHEDULER_HANDLERS["MyScheduler"] = handler
    SCHEDULER_NAMES.append("MyScheduler")
```

When ComfyUI loads, all custom nodes are imported, and they add their schedulers to the global registry. Then `comfy.samplers.KSampler.SCHEDULERS` points to this complete list.

## Changes Made

Modified `nodes.py` in the `INPUT_TYPES` method:

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
            # ...
            "sampler_name": (sampler_list, {"default": "euler"}),
            "scheduler": (scheduler_list, {"default": "normal"}),
            # ...
        }
    }
```

## Benefits

1. **Automatic Discovery**: Any custom scheduler or sampler installed in ComfyUI will automatically appear in the dropdown
2. **Consistency**: Matches the behavior of KSampler, KSampler Advanced, and SamplerCustomAdvanced
3. **Future-Proof**: No need to update the node when new schedulers are added
4. **Fallback Safety**: If ComfyUI imports fail (e.g., when testing outside ComfyUI), it falls back to a sensible default list

## Testing

To verify the custom scheduler is available, restart ComfyUI after installing any custom scheduler node. The DINO Upscale node's scheduler dropdown should now include all registered schedulers.

Example with FlowMatchEulerDiscreteScheduler:
- Before: Only shows 7 built-in schedulers
- After: Shows all built-in schedulers + "FlowMatchEulerDiscreteScheduler" + any other custom schedulers

## References

- ComfyUI samplers: `/mnt/essdee/ComfyUI/comfy/samplers.py`
- Built-in nodes: `/mnt/essdee/ComfyUI/nodes.py`
- Example custom scheduler: `/mnt/essdee/ComfyUI/custom_nodes/erosdiffusion-eulerflowmatchingdiscretescheduler/__init__.py`
